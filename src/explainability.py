class ExplainabilityEngine:
    @staticmethod
    def generate_candidate_explanation(sc: dict) -> dict:
        """
        Generates a detailed, explainable AI recommendation profile for a scored candidate.
        Args:
            sc (dict): A scored candidate dict from the RankingEngine.
        Returns:
            dict: {
                "recommendation": str,       # LLM-style short summary
                "rationales": list of str,    # Bullet points explaining why
                "strengths": list of str,     # Candidate strengths
                "weaknesses": list of str,    # Gaps / Areas of improvement
                "hiring_probability": float,  # Calculated percentage (0-100)
                "rating": str,                # "Strong Hire", "Consider", "Pass"
                "feature_attributions": dict  # Score contribution in percentage
            }
        """
        c = sc["candidate"]
        profile = c.get("profile", {})
        sigs = c.get("redrob_signals", {})
        skills = c.get("skills", [])
        
        yoe = profile.get("years_of_experience", 0)
        final_score = sc["final_score"]
        
        # 1. Feature Attributions (SHAP-inspired contribution of each dimension to final score)
        # Final score was built from: Semantic, Skills, Experience, Behavior, Growth
        # Let's calculate the relative percentage impact of each component
        components = {
            "Semantic Fit": sc["semantic_score"] * 0.40,
            "Skill Match": sc["skills_score"] * 0.25,
            "Experience Match": sc["experience_score"] * 0.15,
            "Behavioral Signals": sc["behavior_score"] * 0.10,
            "Growth Potential": sc["growth_score"] * 0.10
        }
        total_attrib = sum(components.values())
        if total_attrib == 0:
            total_attrib = 1e-9
            
        feature_attributions = {k: round((v / total_attrib) * 100, 1) for k, v in components.items()}
        
        # 2. Key Strengths & Gaps (Weaknesses) Detection
        strengths = []
        weaknesses = []
        rationales = []
        
        # Skill check
        jd_struct = sc["jd_struct"]
        required_skills = jd_struct.get("required_skills", [])
        preferred_skills = jd_struct.get("preferred_skills", [])
        
        cand_skills_lower = [s.get("name", "").lower() for s in skills]
        
        # Analyze skill matches
        matched_reqs = []
        missing_reqs = []
        for req in required_skills:
            if any(req.lower() in cs or cs in req.lower() for cs in cand_skills_lower):
                matched_reqs.append(req)
            else:
                missing_reqs.append(req)
                
        matched_prefs = []
        for pref in preferred_skills:
            if any(pref.lower() in cs or cs in pref.lower() for cs in cand_skills_lower):
                matched_prefs.append(pref)
                
        # Generate strengths based on rules
        if matched_reqs:
            strengths.append(f"Strong match with required skills: {', '.join(matched_reqs[:4])}")
            rationales.append(f"✓ {round(sc['skills_score'] * 100)}% skill match with required technologies")
        if matched_prefs:
            strengths.append(f"Possesses nice-to-have skills: {', '.join(matched_prefs[:3])}")
            
        # Experience check
        exp_min = jd_struct["experience_min"]
        exp_max = jd_struct["experience_max"]
        if exp_min <= yoe <= exp_max:
            strengths.append(f"Exactly fits the target experience window ({exp_min}-{exp_max} years) with {yoe} years of experience")
            rationales.append(f"✓ Ideal seniority: {yoe} years of relevant experience")
        elif yoe < exp_min:
            weaknesses.append(f"Slightly underqualified: Has {yoe} years of experience, target is {exp_min} years")
        else:
            strengths.append(f"Extensive seniority: Has {yoe} years of experience (target is {exp_min}-{exp_max} years)")
            
        # Behavioral signals check (GitHub, Certifications, Notice Period)
        github_commits = sigs.get("github_contributions_commits", 0)
        if github_commits >= 400:
            strengths.append(f"Exceptional open-source contributor ({github_commits} GitHub commits)")
            rationales.append(f"✓ Strong ML/software project portfolio and active open-source footprint")
        elif github_commits >= 100:
            strengths.append(f"Active GitHub developer profile ({github_commits} commits)")
            
        certs = sigs.get("recent_certifications", [])
        if certs:
            strengths.append(f"Possesses recent industry certifications: {', '.join(certs)}")
            rationales.append(f"✓ Recent industry-recognized professional certifications")
            
        notice_period = sigs.get("notice_period_days", 90)
        if notice_period <= 30:
            strengths.append(f"Immediate availability: Short notice period of {notice_period} days")
            if notice_period == 0:
                rationales.append("✓ Available to join immediately (0 days notice)")
            else:
                rationales.append(f"✓ Short notice period of {notice_period} days")
        elif notice_period >= 60:
            weaknesses.append(f"Longer notice period: Requires {notice_period} days to join")
            
        if sigs.get("open_to_work_flag"):
            strengths.append("Actively open to new opportunities (Open-To-Work)")
            rationales.append("✓ Actively seeking new opportunities, ensuring high engagement")
            
        # Growth velocity check
        growth_score = sc["growth_score"] * 100
        if growth_score >= 85:
            strengths.append("High career growth velocity with clear promotions and upward mobility")
            rationales.append("✓ Upward career trajectory with quick promotion intervals")
        elif growth_score < 50:
            weaknesses.append("Potential job instability or stagnant career progression pattern")
            
        # Missing skills
        if missing_reqs:
            weaknesses.append(f"Missing core required skills: {', '.join(missing_reqs[:3])}")
            
        # 3. Overall Recommendation and Hiring Probability
        # Scale final score to a realistic hiring probability (e.g. 0.40 to 0.95 -> 40% to 95%)
        hiring_probability = round(final_score * 100, 1)
        
        # Categorize Rating
        if final_score >= 0.78:
            rating = "Strong Hire"
            rec_text = f"Highly recommended candidate. Exceptionally strong semantic alignment ({round(sc['semantic_score']*100)}%) and technical qualifications. Excellent fit for the {jd_struct['title']} role."
        elif final_score >= 0.60:
            rating = "Consider"
            rec_text = f"Solid candidate. Good core skills match with minor gaps (e.g., missing some nice-to-have skills or longer notice period). Worth interviewing."
        else:
            rating = "Pass"
            rec_text = f"Low alignment. Significant skill gaps or experience mismatch. Candidate does not meet the core criteria of this role."
            
        # Fallback rationales if too short
        if len(rationales) < 2:
            rationales.append(f"✓ Strong overall semantic match score of {round(sc['semantic_score']*100)}%")
            
        return {
            "recommendation": rec_text,
            "rationales": rationales,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "hiring_probability": hiring_probability,
            "rating": rating,
            "feature_attributions": feature_attributions
        }
