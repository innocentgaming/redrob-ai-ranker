import unittest
import pandas as pd
import os
import sys

# Ensure directories are in path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.job_analyzer import JobAnalyzer
from src.candidate_analyzer import CandidateAnalyzer
from src.ranking_engine import RankingEngine
from src.validator import SubmissionValidator

class TestJobAnalyzer(unittest.TestCase):
    def test_job_analysis_ai(self):
        jd = "Looking for a Senior AI Engineer with 5 to 9 years of experience. Must have Python, RAG systems, and LLMs. Location: Noida."
        result = JobAnalyzer.analyze_job_description(jd)
        
        self.assertEqual(result["title"], "Senior AI Engineer")
        self.assertEqual(result["domain"], "AI/ML")
        self.assertEqual(result["experience_min"], 5)
        self.assertEqual(result["experience_max"], 9)
        self.assertIn("Noida", result["location_preference"])
        self.assertIn("python", result["required_skills"])
        self.assertIn("rag systems", result["required_skills"])

    def test_job_analysis_web(self):
        jd = "React Developer needed with 3+ years experience. Knowledge of Javascript and Next.js is a plus."
        result = JobAnalyzer.analyze_job_description(jd)
        
        self.assertEqual(result["title"], "React Developer")
        self.assertEqual(result["domain"], "Web")
        self.assertEqual(result["experience_min"], 3)
        self.assertIn("react", result["required_skills"])
        self.assertIn("next.js", result["preferred_skills"])

class TestCandidateAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_candidate = {
            "candidate_id": "cand_test_001",
            "profile": {
                "name": "John Doe",
                "headline": "AI Engineer",
                "summary": "Experienced in ML and Python.",
                "current_title": "ML Engineer",
                "current_industry": "Technology",
                "years_of_experience": 6,
                "current_location": "Pune",
                "education": "B.Tech from IIT Bombay"
            },
            "skills": [
                {"name": "python", "proficiency": "expert", "duration_months": 48},
                {"name": "machine learning", "proficiency": "advanced", "duration_months": 36}
            ],
            "career_history": [
                {"company": "Google", "title": "ML Engineer", "description": "Built search models.", "start_date": "2021-01-01", "end_date": "Present"},
                {"company": "TCS", "title": "Junior Developer", "description": "Web dev.", "start_date": "2019-01-01", "end_date": "2020-12-31"}
            ],
            "projects": [
                {"title": "RAG App", "description": "Built a chatbot.", "tech_used": ["python", "llm"]}
            ],
            "redrob_signals": {
                "open_to_work_flag": True,
                "notice_period_days": 30,
                "recruiter_response_rate": 0.9,
                "willing_to_relocate": True,
                "github_contributions_commits": 250,
                "recent_certifications": ["Google Professional ML"],
                "project_frequency_count": 1,
                "technology_adoption_index": 0.85
            }
        }

    def test_candidate_analysis_scores(self):
        scores = CandidateAnalyzer.analyze_candidate(self.mock_candidate)
        
        self.assertGreater(scores["technical_score"], 0)
        self.assertGreater(scores["experience_score"], 0)
        self.assertGreater(scores["growth_score"], 0)
        self.assertGreater(scores["project_quality"], 0)
        self.assertGreater(scores["behavioral_potential_score"], 0)
        
        # John has Google (product) and TCS (consulting) experience, check company score weight indirectly
        self.assertTrue(50 <= scores["experience_score"] <= 100)

class TestRankingEngine(unittest.TestCase):
    def setUp(self):
        # Good candidate
        self.good_cand = {
            "profile": {"years_of_experience": 6, "current_title": "AI Engineer"},
            "career_history": [{"start_date": "2019-01-01"}],
            "skills": [{"name": "python", "proficiency": "expert", "duration_months": 48}]
        }
        
        # Honeypot 1: Timeline contradiction
        self.honeypot_timeline = {
            "profile": {"years_of_experience": 2},
            "career_history": [{"start_date": "2010-01-01"}], # Starts 15 years ago, but YOE listed as 2!
            "skills": []
        }
        
        # Honeypot 2: Competency stuffing (expert skills with 0 months)
        self.honeypot_stuffing = {
            "profile": {"years_of_experience": 5},
            "career_history": [],
            "skills": [
                {"name": "python", "proficiency": "expert", "duration_months": 0},
                {"name": "ml", "proficiency": "expert", "duration_months": 0},
                {"name": "dl", "proficiency": "expert", "duration_months": 0},
                {"name": "llm", "proficiency": "expert", "duration_months": 0},
                {"name": "rag", "proficiency": "expert", "duration_months": 0}
            ]
        }

    def test_honeypot_detection(self):
        self.assertFalse(RankingEngine.is_honeypot(self.good_cand))
        self.assertTrue(RankingEngine.is_honeypot(self.honeypot_timeline))
        self.assertTrue(RankingEngine.is_honeypot(self.honeypot_stuffing))

    def test_wrong_domain(self):
        civil_cand = {
            "profile": {"current_title": "Civil Site Engineer", "current_industry": "Construction"}
        }
        ai_cand = {
            "profile": {"current_title": "Senior AI Architect", "current_industry": "Technology"}
        }
        
        self.assertTrue(RankingEngine.is_wrong_domain(civil_cand, "AI/ML"))
        self.assertFalse(RankingEngine.is_wrong_domain(ai_cand, "AI/ML"))

    def test_experience_match(self):
        # Target: 5 to 9 years
        self.assertEqual(RankingEngine.calculate_experience_match(7, 5, 9), 1.0)
        self.assertLess(RankingEngine.calculate_experience_match(3, 5, 9), 1.0)
        self.assertLess(RankingEngine.calculate_experience_match(12, 5, 9), 1.0)
        
        # Underqualified (3 yrs, target 5) should be penalized more than overqualified (11 yrs, target 9)
        score_under = RankingEngine.calculate_experience_match(3, 5, 9) # 5 - 3 = 2 diff -> 1.0 - 0.4 = 0.6
        score_over = RankingEngine.calculate_experience_match(11, 5, 9) # 11 - 9 = 2 diff -> 1.0 - 0.16 = 0.84
        self.assertLess(score_under, score_over)

    def test_skills_match(self):
        cand_skills = [
            {"name": "python", "proficiency": "expert"},
            {"name": "fastapi", "proficiency": "intermediate"}
        ]
        req_skills = ["python", "rag"]
        pref_skills = ["fastapi"]
        
        score = RankingEngine.calculate_skills_match(cand_skills, req_skills, pref_skills)
        self.assertTrue(0.0 < score < 1.0)

class TestSubmissionValidator(unittest.TestCase):
    def test_validator_with_bad_schema(self):
        # Create a mock invalid dataframe
        bad_df = pd.DataFrame([{
            "candidate_id": "cand_001",
            "rank": 1,
            "final_score": 0.85
            # Missing other required columns
        }])
        
        bad_csv = "outputs/test_bad_submission.csv"
        os.makedirs("outputs", exist_ok=True)
        bad_df.to_csv(bad_csv, index=False)
        
        report = SubmissionValidator.validate_submission(bad_csv)
        self.assertFalse(report["valid"])
        self.assertTrue(any("Missing required columns" in err for err in report["errors"]))
        
        if os.path.exists(bad_csv):
            os.remove(bad_csv)

if __name__ == "__main__":
    unittest.main()
