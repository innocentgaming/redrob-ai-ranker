import os
import json
import pickle
import numpy as np
import pandas as pd
from src.job_analyzer import JobAnalyzer
from src.candidate_analyzer import CandidateAnalyzer
from src.embedding import EmbeddingEngine

WRONG_DOMAINS = [
    'civil engineer', 'civil engineering', 'graphic designer', 'hr manager',
    'accountant', 'mechanical engineer', 'marketing manager',
    'sales manager', 'content writer', 'teacher', 'doctor',
    'project manager', 'business analyst', 'financial analyst',
    'operations manager', 'scrum master', 'customer support',
    'customer success', 'support engineer', 'recruiter', 'talent acquisition'
]

class RankingEngine:
    _ml_model = None
    _model_loaded = False

    def __init__(self, model_path: str = "models/ranking_model.pkl"):
        self.model_path = model_path
        if not RankingEngine._model_loaded:
            if os.path.exists(self.model_path):
                try:
                    with open(self.model_path, "rb") as f:
                        RankingEngine._ml_model = pickle.load(f)
                except Exception as e:
                    print(f"Warning: Could not load ML model: {e}")
            RankingEngine._model_loaded = True
        self.ml_model = RankingEngine._ml_model

    @staticmethod
    def is_honeypot(c: dict) -> bool:
        """
        Detects fraudulent resumes (Honeypots):
        1. Years of experience conflicts with career history start date (e.g. YOE is 2, but history starts 15 years ago).
        2. More than 5 expert skills with 0 months duration.
        """
        profile = c.get('profile', {})
        yoe = profile.get('years_of_experience', 0)
        history = c.get('career_history', [])

        # Check 1: Timeline contradiction
        for job in history:
            start = job.get('start_date', '')
            if start:
                try:
                    start_year = int(start[:4])
                    # If career started more than (yoe + 5) years ago (allowing small overlap/gaps), it's a red flag
                    # Current year is 2025 (matching mock data)
                    current_year = 2025
                    years_in_market = current_year - start_year
                    if yoe > 0 and years_in_market > (yoe + 8):
                        return True
                except ValueError:
                    pass

        # Check 2: Competency exaggeration (5+ expert skills with 0 months duration)
        expert_zero_months = sum(
            1 for s in c.get('skills', [])
            if s.get('proficiency') == 'expert' and s.get('duration_months', 1) == 0
        )
        if expert_zero_months >= 5:
            return True

        return False

    @staticmethod
    def is_wrong_domain(c: dict, job_domain: str) -> bool:
        """
        Checks if candidate is in a completely wrong domain based on current title and history.
        """
        title = c.get('profile', {}).get('current_title', '').lower()
        industry = c.get('profile', {}).get('current_industry', '').lower()
        
        # If the job is in AI/ML or Web and the candidate is a Civil Engineer, exclude
        if job_domain in ["AI/ML", "Web", "PM"] and ("civil" in title or "civil" in industry):
            return True
        # If job is technical and candidate is purely HR
        if job_domain in ["AI/ML", "Web"] and ("hr" in title or "recruitment" in title or "talent" in title):
            return True
            
        # Standard block list
        return any(d in title for d in WRONG_DOMAINS)

    @staticmethod
    def calculate_skills_match(candidate_skills: list, jd_req_skills: list, jd_pref_skills: list) -> float:
        """
        Calculates a normalized score (0.0 - 1.0) representing skill overlap,
        weighted by candidate proficiency and whether it is a required or preferred skill.
        """
        if not jd_req_skills and not jd_pref_skills:
            return 1.0
            
        cand_skill_map = {s.get("name", "").lower(): s for s in candidate_skills}
        
        req_score = 0.0
        req_weight = 0.7
        pref_score = 0.0
        pref_weight = 0.3
        
        # 1. Evaluate Required Skills
        if jd_req_skills:
            req_matches = 0
            total_req_weight = 0.0
            for skill in jd_req_skills:
                skill_lower = skill.lower()
                # Check for direct or partial match
                matched_skill = None
                for c_skill in cand_skill_map:
                    if skill_lower in c_skill or c_skill in skill_lower:
                        matched_skill = cand_skill_map[c_skill]
                        break
                        
                if matched_skill:
                    # Weight by proficiency
                    prof = matched_skill.get("proficiency", "intermediate").lower()
                    prof_mult = 1.0
                    if prof == "expert":
                        prof_mult = 1.2
                    elif prof == "advanced":
                        prof_mult = 1.0
                    elif prof == "intermediate":
                        prof_mult = 0.8
                    else:
                        prof_mult = 0.5
                    
                    req_matches += prof_mult
                total_req_weight += 1.0
                
            req_score = min(1.0, req_matches / total_req_weight) if total_req_weight > 0 else 1.0
            
        # 2. Evaluate Preferred Skills
        if jd_pref_skills:
            pref_matches = 0
            total_pref_weight = 0.0
            for skill in jd_pref_skills:
                skill_lower = skill.lower()
                matched_skill = None
                for c_skill in cand_skill_map:
                    if skill_lower in c_skill or c_skill in skill_lower:
                        matched_skill = cand_skill_map[c_skill]
                        break
                        
                if matched_skill:
                    prof = matched_skill.get("proficiency", "intermediate").lower()
                    prof_mult = 1.0
                    if prof == "expert":
                        prof_mult = 1.2
                    elif prof == "advanced":
                        prof_mult = 1.0
                    elif prof == "intermediate":
                        prof_mult = 0.8
                    else:
                        prof_mult = 0.5
                        
                    pref_matches += prof_mult
                total_pref_weight += 1.0
                
            pref_score = min(1.0, pref_matches / total_pref_weight) if total_pref_weight > 0 else 1.0
        else:
            # If no preferred skills are specified, required skills carry 100% weight
            req_weight = 1.0
            pref_weight = 0.0
            
        return (req_score * req_weight) + (pref_score * pref_weight)

    @staticmethod
    def calculate_experience_match(yoe: float, req_min: int, req_max: int) -> float:
        """
        Calculates closeness of candidate experience to the JD experience range (0.0 - 1.0).
        Applies a penalty for deviations.
        """
        if req_min == 0 and req_max == 20:
            return 1.0 # No experience bounds specified
            
        if req_min <= yoe <= req_max:
            return 1.0
        elif yoe < req_min:
            # Underqualified penalty (steeper)
            diff = req_min - yoe
            return max(0.0, 1.0 - (diff * 0.20))
        else:
            # Overqualified penalty (gentler)
            diff = yoe - req_max
            return max(0.0, 1.0 - (diff * 0.08))

    def rank_candidates(self, candidates: list, jd_text: str, weights: dict = None, 
                        apply_honeypot: bool = True, apply_domain: bool = True, 
                        apply_experience_filter: bool = True, precomputed_embs: np.ndarray = None,
                        precomputed_ids: list = None) -> list:
        """
        Ranks a list of candidates against a job description.
        Returns a sorted list of dictionaries with scores and explanations.
        """
        if weights is None:
            weights = {
                "semantic": 0.40,
                "skills": 0.25,
                "experience": 0.15,
                "behavioral": 0.10,
                "growth": 0.10
            }
            
        # 1. Analyze Job Description
        jd_struct = JobAnalyzer.analyze_job_description(jd_text)
        
        # 2. Get JD Embedding
        jd_emb = EmbeddingEngine.get_embedding(jd_text)
        
        # 3. Resolve Candidate Embeddings (Use precomputed if available, else align or compute on-the-fly)
        cand_embs = precomputed_embs
        
        if cand_embs is None:
            # Try to load precomputed embeddings from disk
            if os.path.exists("embeddings.npy") and os.path.exists("candidate_ids.json"):
                try:
                    loaded_embs = np.load("embeddings.npy")
                    with open("candidate_ids.json", "r") as f:
                        loaded_ids = json.load(f)
                        
                    emb_map = {cid: loaded_embs[idx] for idx, cid in enumerate(loaded_ids)}
                    
                    aligned_embs = []
                    for c in candidates:
                        cid = c.get("candidate_id")
                        if cid in emb_map:
                            aligned_embs.append(emb_map[cid])
                        else:
                            # Self-healing: compute on the fly for missing candidate
                            aligned_embs.append(EmbeddingEngine.get_embedding(EmbeddingEngine.candidate_to_text(c)))
                    cand_embs = np.array(aligned_embs)
                except Exception as e:
                    print(f"Warning: Could not load precomputed embeddings: {e}")
                    cand_embs = None
                    
        if cand_embs is None:
            # Fallback: Batch compute all candidate text representations on-the-fly
            cand_texts = [EmbeddingEngine.candidate_to_text(c) for c in candidates]
            cand_embs = EmbeddingEngine.get_embeddings(cand_texts)
        
        scored_candidates = []
        
        for i, c in enumerate(candidates):
            cid = c.get("candidate_id")
            
            # --- Hard Filters ---
            if apply_honeypot and self.is_honeypot(c):
                continue
                
            if apply_domain and self.is_wrong_domain(c, jd_struct["domain"]):
                continue
                
            yoe = c.get("profile", {}).get("years_of_experience", 0)
            
            # Experience out-of-bounds filter (only if hard filter is enabled)
            # Exclude if YOE is way outside range (e.g. < yoe_min - 3 or > yoe_max + 6)
            if apply_experience_filter and jd_struct["experience_min"] > 0:
                if yoe < max(1, jd_struct["experience_min"] - 3) or yoe > (jd_struct["experience_max"] + 6):
                    continue
            
            # --- Score Component Calculations ---
            
            # 1. Semantic Score
            c_emb = cand_embs[i]
            semantic_score = EmbeddingEngine.cosine_similarity(jd_emb, c_emb)
            # Clip between 0 and 1
            semantic_score = max(0.0, min(1.0, semantic_score))
            
            # 2. Candidate Profile Analysis (gives growth & behavioral potential scores)
            intel_profile = CandidateAnalyzer.analyze_candidate(c)
            
            # 3. Skills Match Score
            skills_score = self.calculate_skills_match(
                c.get("skills", []), 
                jd_struct["required_skills"], 
                jd_struct["preferred_skills"]
            )
            
            # 4. Experience Match Score
            experience_score = self.calculate_experience_match(
                yoe, 
                jd_struct["experience_min"], 
                jd_struct["experience_max"]
            )
            
            # 5. Behavioral Signals Score (from analyzer)
            behavior_score = intel_profile["behavioral_potential_score"] / 100.0
            
            # 6. Growth Potential Score (from analyzer)
            growth_score = intel_profile["growth_score"] / 100.0
            
            # --- Hybrid Scoring Formula ---
            final_score = (
                (semantic_score * weights["semantic"]) +
                (skills_score * weights["skills"]) +
                (experience_score * weights["experience"]) +
                (behavior_score * weights["behavioral"]) +
                (growth_score * weights["growth"])
            )
            
            # --- Machine Learning Reranking (optional feature) ---
            ml_score = final_score # Default
            if self.ml_model is not None:
                # Build feature vector
                features = pd.DataFrame([{
                    "semantic_score": semantic_score,
                    "skills_score": skills_score,
                    "experience_score": experience_score,
                    "behavior_score": behavior_score,
                    "growth_score": growth_score,
                    "years_of_experience": yoe,
                    "skills_count": len(c.get("skills", [])),
                    "github_commits": c.get("redrob_signals", {}).get("github_contributions_commits", 0),
                    "open_to_work": 1 if c.get("redrob_signals", {}).get("open_to_work_flag", False) else 0
                }])
                try:
                    # ML model predicts a continuous rating or probability
                    ml_pred = float(self.ml_model.predict(features)[0])
                    # Restrict prediction to a sensible [0, 1] range and average/blend it
                    ml_score = max(0.0, min(1.0, ml_pred))
                    # Blend 50% Hybrid formula + 50% ML prediction for robust ranking
                    final_score = (final_score * 0.5) + (ml_score * 0.5)
                except Exception as e:
                    pass
            
            scored_candidates.append({
                "candidate_id": cid,
                "candidate": c,
                "final_score": round(final_score, 4),
                "semantic_score": round(semantic_score, 4),
                "skills_score": round(skills_score, 4),
                "experience_score": round(experience_score, 4),
                "behavior_score": round(behavior_score, 4),
                "growth_score": round(growth_score, 4),
                "intel_profile": intel_profile,
                "jd_struct": jd_struct
            })
            
        # Sort candidates in descending order of final score
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Assign ranks
        for idx, sc in enumerate(scored_candidates):
            sc["rank"] = idx + 1
            
        return scored_candidates
