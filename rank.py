import os
import json
# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd

# Ensure directories are in path
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.ranking_engine import RankingEngine
from src.explainability import ExplainabilityEngine
from src.validator import SubmissionValidator

# ---- Default Hackathon Job Description ----
JD_TEXT = """
Senior AI Engineer at Redrob AI.
5 to 9 years of experience required.
Must have skills: RAG systems, vector embeddings, semantic search, LLMs, Python.
Experience with vector databases like Pinecone, Weaviate, Qdrant, FAISS.
Product company experience preferred. Consulting or services background not preferred.
Location: Pune or Noida. Willing to relocate preferred.
Notice period under 30 days preferred.
Open to work candidates preferred.
"""

def main():
    print("==================================================")
    print("       AI RECRUITER RANKING PIPELINE RUNNER       ")
    print("==================================================")

    # 1. Load candidates and resources
    print("Loading candidates data...")
    candidates = []
    cand_file = "data/candidates.jsonl"
    if not os.path.exists(cand_file):
        print(f"Error: Candidate file '{cand_file}' not found. Please run precompute.py first.")
        return
        
    with open(cand_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    print(f"Total candidates available: {len(candidates)}")

    # 2. Execute Ranking Engine
    print("\nExecuting hybrid AI ranking engine...")
    # Initialize engine (loads ML model if available)
    engine = RankingEngine()
    
    # We apply all core filters (Honeypot, Domain, Experience limits) as per hackathon specification
    ranked_results = engine.rank_candidates(
        candidates, 
        JD_TEXT,
        apply_honeypot=True,
        apply_domain=True,
        apply_experience_filter=True
    )
    
    print(f"Scored {len(ranked_results)} candidates (after filters).")

    # 3. Generate Explainable Recommendations and format output
    print("\nGenerating explainable AI recommendations...")
    submission_rows = []
    
    # We take all ranked candidates (or top 100 as per original hackathon instruction)
    # The original rank.py did: top100 = results[:100]
    # Let's take all scored candidates up to 100
    top_candidates = ranked_results[:100]
    
    for sc in top_candidates:
        # Generate detailed XAI explanation
        xai_profile = ExplainabilityEngine.generate_candidate_explanation(sc)
        
        # Format candidate row for submission.csv
        submission_rows.append({
            "candidate_id": sc["candidate_id"],
            "rank": sc["rank"],
            "final_score": sc["final_score"],
            "skill_score": sc["skills_score"],
            "experience_score": sc["experience_score"],
            "semantic_score": sc["semantic_score"],
            "recommendation": xai_profile["recommendation"]
        })
        
    # 4. Save Submission CSV
    print("\nSaving submission CSV files...")
    df = pd.DataFrame(submission_rows)
    
    # Save to both locations for safety: root directory (submission.csv) and outputs folder (outputs/submission.csv)
    os.makedirs("outputs", exist_ok=True)
    df.to_csv("outputs/submission.csv", index=False)
    df.to_csv("submission.csv", index=False)
    
    print("[OK] Saved submission.csv in root directory!")
    print("[OK] Saved outputs/submission.csv!")

    # 5. Display Top 5 Candidates
    print("\nTop 5 Ranked Candidates:")
    print("-" * 120)
    print(f"{'Rank':<5} | {'Candidate ID':<15} | {'Score':<8} | {'Semantic':<8} | {'Skills':<8} | {'AI Recommendation Summary'}")
    print("-" * 120)
    for row in submission_rows[:5]:
        print(f"{row['rank']:<5} | {row['candidate_id']:<15} | {row['final_score']:<8.4f} | {row['semantic_score']:<8.4f} | {row['skill_score']:<8.4f} | {row['recommendation']}")
    print("-" * 120)

    # 6. Run Submission Validator
    print("\nTriggering submission verification...")
    SubmissionValidator.print_report("submission.csv")

if __name__ == "__main__":
    main()