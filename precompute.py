import os
import json
import numpy as np
import pandas as pd
import pickle
from tqdm import tqdm

# Ensure directories are in path
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 1. Trigger Data Generation if needed
print("Checking data files...")
if not os.path.exists("data/candidates.jsonl") or not os.path.exists("data/jobs.csv"):
    print("Candidate dataset or jobs not found. Generating synthetic data...")
    from src.generate_data import generate_candidates, generate_jobs
    # Set mock degrees and universities
    import src.generate_data as gd
    gd.UNIVERSITIES = ["IIT Bombay", "IIT Delhi", "IIT Madras", "BITS Pilani", "IIIT Hyderabad", "Delhi Technological University", "Anna University", "VIT University", "Stanford University", "MIT", "Carnegie Mellon University"]
    gd.DEGREES = ["B.Tech in Computer Science", "Dual Degree (B.Tech + M.Tech) in CS", "M.Tech in Artificial Intelligence", "B.E. in Information Technology", "M.S. in Computer Science", "B.Tech in Civil Engineering", "MBA in HR Management"]
    generate_candidates()
    generate_jobs()
else:
    print("Data files exist! Proceeding.")

from src.embedding import EmbeddingEngine
from src.candidate_analyzer import CandidateAnalyzer
from src.job_analyzer import JobAnalyzer
from src.ranking_engine import RankingEngine

# 2. Load Candidates
print("\nLoading candidates...")
candidates = []
with open('data/candidates.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            candidates.append(json.loads(line))
print(f"Total candidates loaded: {len(candidates)}")

# 3. Generate and Save Embeddings
print("\nGenerating candidate embeddings using Sentence-Transformers...")
texts = []
candidate_ids = []

for c in tqdm(candidates):
    texts.append(EmbeddingEngine.candidate_to_text(c))
    candidate_ids.append(c['candidate_id'])

embeddings = EmbeddingEngine.get_embeddings(texts)

print("Saving embeddings...")
np.save('embeddings.npy', embeddings)
with open('candidate_ids.json', 'w') as f:
    json.dump(candidate_ids, f)
print("Saved embeddings.npy and candidate_ids.json in root directory!")

# 4. Train Machine Learning Ranking Model
print("\nPreparing training data for Machine Learning Ranking Model...")
from sklearn.ensemble import RandomForestRegressor

# Load preset jobs to create training pairs
jobs_df = pd.read_csv("data/jobs.csv")

training_samples = []
for _, job in jobs_df.iterrows():
    jd_text = job["description"]
    jd_struct = JobAnalyzer.analyze_job_description(jd_text)
    jd_emb = EmbeddingEngine.get_embedding(jd_text)
    
    for i, c in enumerate(candidates):
        # Calculate scores using core logic
        c_emb = embeddings[i]
        semantic_score = EmbeddingEngine.cosine_similarity(jd_emb, c_emb)
        semantic_score = max(0.0, min(1.0, semantic_score))
        
        intel_profile = CandidateAnalyzer.analyze_candidate(c)
        
        skills_score = RankingEngine.calculate_skills_match(
            c.get("skills", []), 
            jd_struct["required_skills"], 
            jd_struct["preferred_skills"]
        )
        
        yoe = c.get("profile", {}).get("years_of_experience", 0)
        experience_score = RankingEngine.calculate_experience_match(
            yoe, 
            jd_struct["experience_min"], 
            jd_struct["experience_max"]
        )
        
        behavior_score = intel_profile["behavioral_potential_score"] / 100.0
        growth_score = intel_profile["growth_score"] / 100.0
        
        # Calculate target (hybrid score)
        # We will train the model to predict a robust hybrid fitness score
        # and we inject some noise/adjustments to make it learn candidate quality indicators
        target_score = (
            (semantic_score * 0.40) +
            (skills_score * 0.25) +
            (experience_score * 0.15) +
            (behavior_score * 0.10) +
            (growth_score * 0.10)
        )
        
        # If candidate is a honeypot, their true utility is 0
        if RankingEngine.is_honeypot(c):
            target_score = 0.0
        # If candidate is in the wrong domain, their true utility is extremely low
        if RankingEngine.is_wrong_domain(c, jd_struct["domain"]):
            target_score = min(target_score, 0.1)
            
        training_samples.append({
            "semantic_score": semantic_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "behavior_score": behavior_score,
            "growth_score": growth_score,
            "years_of_experience": yoe,
            "skills_count": len(c.get("skills", [])),
            "github_commits": c.get("redrob_signals", {}).get("github_contributions_commits", 0),
            "open_to_work": 1 if c.get("redrob_signals", {}).get("open_to_work_flag", False) else 0,
            "target": target_score
        })

train_df = pd.DataFrame(training_samples)
X = train_df.drop(columns=["target"])
y = train_df["target"]

print(f"Training dataset size: {X.shape[0]} samples with {X.shape[1]} features.")
print("Training Random Forest Regressor...")
model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
model.fit(X, y)

# Save model
os.makedirs("models", exist_ok=True)
model_path = "models/ranking_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(model, f)
    
print(f"Machine Learning Ranking Model saved successfully to {model_path}!")
print("Precomputation completed! Ready to run rank.py.")