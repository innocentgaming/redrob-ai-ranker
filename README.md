# Redrob Ranker 
 
AI-powered candidate ranking system for India Runs Hackathon 
 
## Setup 
 
pip install -r requirements.txt 
 
## Run 
 
Step 1 - run once to generate embeddings: 
python precompute.py 
 
Step 2 - generate ranked output: 
python rank.py 
 
Output: submission.csv with top 100 ranked candidates
