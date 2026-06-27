import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import numpy as np
import pandas as pd
import json
from src.ranking_engine import RankingEngine
from src.job_analyzer import JobAnalyzer

class RankEvaluator:
    @staticmethod
    def get_ground_truth_relevance(candidate: dict, jd_struct: dict) -> float:
        """
        Defines a scientific ground truth relevance score (0.0 to 3.0) for a candidate:
        - 3.0: Perfect match (correct domain, experience in range, has 80%+ of required skills).
        - 2.0: Good match (correct domain, experience within +/- 1 year of range, has 50%+ of required skills).
        - 1.0: Marginally suitable (correct domain, has some matching skills, but experience is outside range).
        - 0.0: Unsuitable (wrong domain, or honeypot, or has virtually no required skills).
        """
        if RankingEngine.is_honeypot(candidate):
            return 0.0
            
        profile = candidate.get("profile", {})
        title = profile.get("current_title", "").lower()
        industry = profile.get("current_industry", "").lower()
        yoe = profile.get("years_of_experience", 0)
        
        # Check domain suitability
        job_domain = jd_struct["domain"]
        if job_domain == "AI/ML" and not any(w in title or w in industry for w in ["ai", "ml", "machine learning", "llm", "data", "python", "developer", "engineer"]):
            return 0.0
        if job_domain == "Web" and not any(w in title or w in industry for w in ["web", "developer", "engineer", "react", "node", "frontend", "backend", "javascript"]):
            return 0.0
            
        # Skill overlap calculation (ground truth)
        cand_skills = [s.get("name", "").lower() for s in candidate.get("skills", [])]
        req_skills = [s.lower() for s in jd_struct["required_skills"]]
        
        if not req_skills:
            req_overlap_pct = 1.0
        else:
            matches = sum(1 for rs in req_skills if any(rs in cs or cs in rs for cs in cand_skills))
            req_overlap_pct = matches / len(req_skills)
            
        # Experience match
        exp_min = jd_struct["experience_min"]
        exp_max = jd_struct["experience_max"]
        
        # Scoring logic
        if exp_min <= yoe <= exp_max and req_overlap_pct >= 0.8:
            return 3.0
        elif exp_min - 1 <= yoe <= exp_max + 1 and req_overlap_pct >= 0.5:
            return 2.0
        elif req_overlap_pct >= 0.3:
            return 1.0
        else:
            return 0.0

    @staticmethod
    def calculate_ndcg(retrieved_relevances: list, k: int) -> float:
        """
        Calculates NDCG@K (Normalized Discounted Cumulative Gain)
        """
        relevances = retrieved_relevances[:k]
        if not relevances:
            return 0.0
            
        # Calculate DCG
        dcg = sum(rel / np.log2(idx + 2) for idx, rel in enumerate(relevances))
        
        # Calculate Ideal DCG (IDCG)
        ideal_relevances = sorted(retrieved_relevances, reverse=True)[:k]
        idcg = sum(rel / np.log2(idx + 2) for idx, rel in enumerate(ideal_relevances))
        
        if idcg == 0:
            return 0.0
        return float(dcg / idcg)

    @staticmethod
    def calculate_precision_recall_at_k(retrieved_relevances: list, total_relevant_count: int, k: int, relevance_threshold: float = 1.5) -> tuple:
        """
        Calculates Precision@K and Recall@K
        """
        top_k = retrieved_relevances[:k]
        if not top_k:
            return 0.0, 0.0
            
        relevant_retrieved = sum(1 for rel in top_k if rel >= relevance_threshold)
        
        precision = relevant_retrieved / k
        recall = relevant_retrieved / total_relevant_count if total_relevant_count > 0 else 0.0
        
        return float(precision), float(recall)

    @classmethod
    def run_evaluation(cls, candidates: list, jd_text: str) -> dict:
        """
        Runs evaluation on Hybrid Ranker vs a Baseline Keyword-Matching ATS.
        """
        jd_struct = JobAnalyzer.analyze_job_description(jd_text)
        
        # Calculate ground truth relevances for all candidates
        gt_relevances = {}
        for c in candidates:
            gt_relevances[c["candidate_id"]] = cls.get_ground_truth_relevance(c, jd_struct)
            
        total_relevant = sum(1 for rel in gt_relevances.values() if rel >= 1.5)
        
        # 1. Evaluate Hybrid Ranker
        ranker = RankingEngine()
        hybrid_results = ranker.rank_candidates(
            candidates, 
            jd_text, 
            apply_honeypot=True, 
            apply_domain=True, 
            apply_experience_filter=True
        )
        
        hybrid_relevances = [gt_relevances[r["candidate_id"]] for r in hybrid_results]
        
        # 2. Evaluate Baseline Keyword Matcher
        # Heuristic keyword matcher: counts occurrences of required skills in candidate text
        baseline_results = []
        req_skills = [s.lower() for s in jd_struct["required_skills"]]
        
        for c in candidates:
            cid = c["candidate_id"]
            # Exclude honeypots even in baseline to make it fair, or keep them to show how baseline fails
            # Baseline doesn't detect honeypots, so we don't apply it here.
            cand_skills = [s.get("name", "").lower() for s in c.get("skills", [])]
            headline = c.get("profile", {}).get("headline", "").lower()
            summary = c.get("profile", {}).get("summary", "").lower()
            all_text = " ".join(cand_skills) + " " + headline + " " + summary
            
            keyword_score = sum(1 for rs in req_skills if rs in all_text)
            
            baseline_results.append({
                "candidate_id": cid,
                "score": keyword_score
            })
            
        baseline_results.sort(key=lambda x: x["score"], reverse=True)
        baseline_relevances = [gt_relevances[r["candidate_id"]] for r in baseline_results]
        
        # Calculate metrics @5, @10, @20
        metrics = {}
        for k in [5, 10, 20]:
            h_ndcg = cls.calculate_ndcg(hybrid_relevances, k)
            h_prec, h_rec = cls.calculate_precision_recall_at_k(hybrid_relevances, total_relevant, k)
            
            b_ndcg = cls.calculate_ndcg(baseline_relevances, k)
            b_prec, b_rec = cls.calculate_precision_recall_at_k(baseline_relevances, total_relevant, k)
            
            metrics[f"hybrid_k{k}"] = {"ndcg": round(h_ndcg, 4), "precision": round(h_prec, 4), "recall": round(h_rec, 4)}
            metrics[f"baseline_k{k}"] = {"ndcg": round(b_ndcg, 4), "precision": round(b_prec, 4), "recall": round(b_rec, 4)}
            
        metrics["total_candidates"] = len(candidates)
        metrics["total_relevant"] = total_relevant
        
        return metrics

    @classmethod
    def print_evaluation_report(cls, candidates_path: str, jd_text: str):
        candidates = []
        with open(candidates_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    candidates.append(json.loads(line))
                    
        metrics = cls.run_evaluation(candidates, jd_text)
        
        print("\n" + "="*60)
        print("         AI HYBRID RANKER EVALUATION METRICS REPORT         ")
        print("="*60)
        print(f"Total Candidates in Pool: {metrics['total_candidates']}")
        print(f"Total High-Suitability Candidates (Ground Truth): {metrics['total_relevant']}")
        print("-"*60)
        print(f"{'Metric':<15} | {'Baseline Keyword ATS':<20} | {'Our Hybrid AI Ranker':<20} | {'Lift':<8}")
        print("-"*60)
        
        for k in [5, 10, 20]:
            h_ndcg = metrics[f"hybrid_k{k}"]["ndcg"]
            b_ndcg = metrics[f"baseline_k{k}"]["ndcg"]
            ndcg_lift = ((h_ndcg - b_ndcg) / (b_ndcg + 1e-9)) * 100
            print(f"NDCG@{k:<10} | {b_ndcg:<20.4f} | {h_ndcg:<20.4f} | {ndcg_lift:+.1f}%")
            
            h_prec = metrics[f"hybrid_k{k}"]["precision"]
            b_prec = metrics[f"baseline_k{k}"]["precision"]
            prec_lift = ((h_prec - b_prec) / (b_prec + 1e-9)) * 100
            print(f"Precision@{k:<6} | {b_prec:<20.4f} | {h_prec:<20.4f} | {prec_lift:+.1f}%")
            
            h_rec = metrics[f"hybrid_k{k}"]["recall"]
            b_rec = metrics[f"baseline_k{k}"]["recall"]
            rec_lift = ((h_rec - b_rec) / (b_rec + 1e-9)) * 100
            print(f"Recall@{k:<9} | {b_rec:<20.4f} | {h_rec:<20.4f} | {rec_lift:+.1f}%")
            print("-"*60)
            
        print("="*60 + "\n")
        return metrics

if __name__ == "__main__":
    from src.generate_data import generate_jobs
    import os
    
    # Preset Job 1 (Senior AI Engineer)
    JD = """
    Senior AI Engineer at Redrob AI.
    5 to 9 years of experience required.
    Must have skills: RAG systems, vector embeddings, semantic search, LLMs, Python.
    Experience with vector databases like Pinecone, Weaviate, Qdrant, FAISS.
    Product company experience preferred. Consulting or services background not preferred.
    Location: Pune or Noida. Willing to relocate preferred.
    Notice period under 30 days preferred.
    Open to work candidates preferred.
    """
    
    cand_file = "data/candidates.jsonl"
    if not os.path.exists(cand_file):
        print("Data files not found. Run generate_data.py first.")
    else:
        cls = RankEvaluator()
        cls.print_evaluation_report(cand_file, JD)
