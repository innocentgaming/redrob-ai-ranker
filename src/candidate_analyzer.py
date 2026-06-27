import re
from datetime import datetime

CONSULTING_KEYWORDS = ['tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini', 'hcl', 'tech mahindra', 'services']
PRODUCT_KEYWORDS = ['google', 'microsoft', 'amazon', 'meta', 'netflix', 'uber', 'stripe', 'airbnb', 'atlassian', 'adobe', 'salesforce', 'redrob', 'razorpay', 'cred', 'swiggy', 'zomato', 'product', 'labs', 'tech']

class CandidateAnalyzer:
    @staticmethod
    def analyze_candidate(c: dict) -> dict:
        """
        Analyzes candidate raw data and generates an intelligence profile with sub-scores.
        Returns:
            dict: {
                "technical_score": float (0-100),
                "experience_score": float (0-100),
                "growth_score": float (0-100),
                "project_quality": float (0-100),
                "behavioral_potential_score": float (0-100)
            }
        """
        profile = c.get("profile", {})
        skills = c.get("skills", [])
        history = c.get("career_history", [])
        projects = c.get("projects", [])
        signals = c.get("redrob_signals", {})
        
        yoe = profile.get("years_of_experience", 0)
        
        # 1. Experience Score (0-100)
        # Scaled YOE + Career Stability + Company Reputation
        exp_base = min(100, yoe * 8) # Peak at 12.5 YOE
        
        # Stability: penalize frequent job hopping (e.g. average tenure < 1.5 years)
        stability_score = 100
        if len(history) > 1:
            avg_tenure = yoe / len(history)
            if avg_tenure < 1.0:
                stability_score = 50
            elif avg_tenure < 2.0:
                stability_score = 80
        elif len(history) == 0:
            stability_score = 0
            
        # Company Reputation: Product company experience preferred
        company_score = 70 # Default neutral
        if history:
            prod_count = 0
            cons_count = 0
            for job in history:
                company = job.get("company", "").lower()
                if any(k in company for k in PRODUCT_KEYWORDS):
                    prod_count += 1
                if any(k in company for k in CONSULTING_KEYWORDS):
                    cons_count += 1
            if prod_count > 0 and cons_count == 0:
                company_score = 95
            elif prod_count > cons_count:
                company_score = 85
            elif cons_count > prod_count:
                company_score = 55
                
        experience_score = (exp_base * 0.4) + (stability_score * 0.3) + (company_score * 0.3)
        
        # 2. Technical Score (0-100)
        # Skills density + proficiency + durations
        tech_score = 50 # Base
        if skills:
            skill_values = []
            for s in skills:
                prof = s.get("proficiency", "intermediate").lower()
                dur = s.get("duration_months", 12)
                
                # Weight by proficiency
                prof_weight = 1.0
                if prof == "expert":
                    prof_weight = 1.3
                elif prof in ["advanced", "senior"]:
                    prof_weight = 1.1
                elif prof == "beginner":
                    prof_weight = 0.6
                    
                # Weight by duration
                dur_weight = min(1.5, 0.5 + (dur / 24)) # Max boost at 2 years
                
                skill_values.append(prof_weight * dur_weight)
                
            avg_skill_val = sum(skill_values) / len(skill_values)
            tech_score = min(100, int(avg_skill_val * 60 + len(skills) * 2))
        else:
            tech_score = 0
            
        # 3. Growth Score (0-100)
        # Promotion velocity + Role progression + Career growth pattern
        growth_score = 70 # Base neutral
        
        # Promotion check: Title progression (Junior -> Mid -> Senior -> Lead)
        if len(history) > 1:
            titles = [job.get("title", "").lower() for job in history][::-1] # Chronological order
            progression = 0
            for i in range(len(titles) - 1):
                prev_title = titles[i]
                next_title = titles[i+1]
                
                # Simple advancement detection
                is_prev_junior = any(w in prev_title for w in ["junior", "associate", "intern"])
                is_next_mid = not any(w in next_title for w in ["junior", "associate", "intern", "senior", "lead", "principal"])
                is_next_senior = "senior" in next_title
                is_next_lead = any(w in next_title for w in ["lead", "principal", "manager", "director"])
                is_prev_senior = "senior" in prev_title
                
                if is_prev_junior and is_next_mid:
                    progression += 15
                if (is_prev_junior or is_next_mid) and is_next_senior:
                    progression += 20
                if is_prev_senior and is_next_lead:
                    progression += 25
                    
            growth_score = min(100, growth_score + progression)
            
            # Penalize negative growth (e.g., Senior to Junior) - highly unlikely but check
            if any("junior" in titles[i] and "senior" in titles[i-1] for i in range(1, len(titles))):
                growth_score = max(30, growth_score - 30)
        elif len(history) == 1:
            growth_score = 75 # Single job, steady
        else:
            growth_score = 0
            
        # 4. Project Quality (0-100)
        # Projects count + GitHub commits + Recent Certifications + Complexity
        proj_count = len(projects)
        github_commits = signals.get("github_contributions_commits", 0)
        recent_certs = len(signals.get("recent_certifications", []))
        
        # Scale GitHub contributions (commits)
        github_score = min(100, (github_commits / 400) * 100) # Peak at 400 commits
        
        # Scale projects count
        proj_score = min(100, proj_count * 20)
        
        # Scale certifications
        cert_score = min(100, recent_certs * 35)
        
        # Standard weights
        project_quality = (proj_score * 0.4) + (github_score * 0.4) + (cert_score * 0.2)
        project_quality = max(40, min(100, project_quality)) # Baseline 40 for average resumes
        if len(projects) == 0 and github_commits == 0 and recent_certs == 0:
            project_quality = 10 # Very low projects
            
        # 5. Behavioral/Potential Score (0-100)
        # Learning activity, open-work flag, notice period, willingness to relocate, response rate
        open_work = 100 if signals.get("open_to_work_flag", False) else 50
        relocate = 100 if signals.get("willing_to_relocate", False) else 70
        
        notice_period = signals.get("notice_period_days", 90)
        if notice_period <= 15:
            notice_score = 100
        elif notice_period <= 30:
            notice_score = 90
        elif notice_period <= 60:
            notice_score = 60
        else:
            notice_score = 40
            
        response_rate = signals.get("recruiter_response_rate", 0) * 100
        learning_index = signals.get("technology_adoption_index", 0.5) * 100
        
        behavioral_potential_score = (open_work * 0.2) + (notice_score * 0.25) + (response_rate * 0.2) + (relocate * 0.15) + (learning_index * 0.2)
        behavioral_potential_score = max(0, min(100, behavioral_potential_score))
        
        return {
            "technical_score": round(tech_score, 2),
            "experience_score": round(experience_score, 2),
            "growth_score": round(growth_score, 2),
            "project_quality": round(project_quality, 2),
            "behavioral_potential_score": round(behavioral_potential_score, 2)
        }
