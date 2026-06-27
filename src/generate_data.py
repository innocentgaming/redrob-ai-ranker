import os
import json
import csv
import random
from datetime import datetime

# Setup directories
os.makedirs("data", exist_ok=True)
os.makedirs("src", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Technical Stack Lists
AI_ML_SKILLS = [
    ("python", "expert"), ("machine learning", "expert"), ("deep learning", "advanced"),
    ("llms", "advanced"), ("rag systems", "advanced"), ("vector embeddings", "advanced"),
    ("semantic search", "advanced"), ("faiss", "advanced"), ("pinecone", "advanced"),
    ("weaviate", "advanced"), ("qdrant", "advanced"), ("pytorch", "advanced"),
    ("tensorflow", "intermediate"), ("scikit-learn", "expert"), ("fastapi", "advanced"),
    ("aws", "intermediate"), ("docker", "intermediate"), ("git", "expert"),
    ("nlp", "advanced"), ("transformers", "advanced"), ("pandas", "expert"),
    ("numpy", "expert"), ("sql", "expert")
]

WEB_SKILLS = [
    ("javascript", "expert"), ("typescript", "advanced"), ("react", "expert"),
    ("next.js", "advanced"), ("node.js", "advanced"), ("express", "advanced"),
    ("html", "expert"), ("css", "expert"), ("tailwind css", "expert"),
    ("mongodb", "intermediate"), ("postgresql", "advanced"), ("redis", "intermediate"),
    ("aws", "intermediate"), ("docker", "intermediate"), ("git", "expert"),
    ("rest api", "expert"), ("graphql", "intermediate"), ("redux", "advanced")
]

PM_SKILLS = [
    ("product management", "expert"), ("agile", "expert"), ("scrum", "expert"),
    ("product roadmap", "expert"), ("jira", "expert"), ("sql", "intermediate"),
    ("data analytics", "advanced"), ("user research", "advanced"), ("wireframing", "intermediate"),
    ("market analysis", "advanced"), ("product analytics", "advanced"), ("amplitude", "intermediate")
]

CIVIL_SKILLS = [
    ("autocad", "expert"), ("civil engineering", "expert"), ("structural design", "advanced"),
    ("concrete design", "expert"), ("project estimation", "advanced"), ("site supervision", "expert"),
    ("surveying", "intermediate"), ("revit", "intermediate"), ("staad pro", "advanced")
]

# Company Lists
PRODUCT_COMPANIES = ["Google", "Microsoft", "Amazon", "Meta", "Netflix", "Uber", "Stripe", "Airbnb", "Atlassian", "Adobe", "Salesforce", "Redrob AI", "Razorpay", "Cred", "Swiggy", "Zomato"]
CONSULTING_COMPANIES = ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini", "HCL", "Tech Mahindra"]
STARTUPS = ["AI Tech Labs", "DevFlow", "Fintechify", "HealthAI", "BlockChainX", "EdTechy", "SaaSify"]

# University Lists
UNIVERSITIES = ["IIT Bombay", "IIT Delhi", "IIT Madras", "BITS Pilani", "IIIT Hyderabad", "Delhi Technological University", "Anna University", "VIT University", "Stanford University", "MIT", "Carnegie Mellon University"]
DEGREES = ["B.Tech in Computer Science", "Dual Degree (B.Tech + M.Tech) in CS", "M.Tech in Artificial Intelligence", "B.E. in Information Technology", "M.S. in Computer Science", "B.Tech in Civil Engineering", "MBA in HR Management"]

# Indian Locations
LOCATIONS = ["Pune", "Noida", "Bangalore", "Hyderabad", "Mumbai", "Chennai", "Gurgaon", "Delhi"]

# Generate Career History
def generate_career_history(domain, yoe, target_companies):
    history = []
    current_year = 2025
    start_year = current_year - yoe
    
    roles = {
        "AI/ML": ["Junior ML Engineer", "ML Engineer", "Senior AI Engineer", "Lead AI Engineer", "Data Scientist", "Senior Data Scientist"],
        "Web": ["Frontend Developer", "Backend Developer", "Full Stack Engineer", "Senior Full Stack Engineer", "Tech Lead"],
        "PM": ["Associate Product Manager", "Product Manager", "Senior Product Manager", "Lead Product Manager"],
        "Civil": ["Site Engineer", "Structural Engineer", "Senior Civil Engineer", "Project Manager (Civil)"],
        "HR": ["HR Associate", "HR Generalist", "HR Specialist", "HR Manager", "Talent Acquisition Lead"]
    }
    
    descriptions = {
        "AI/ML": [
            "Developed and optimized RAG systems using Pinecone and LangChain, reducing hallucination by 25%.",
            "Fine-tuned llama-3 and Mistral models for custom classification tasks using PyTorch.",
            "Designed semantic search architectures using vector embeddings and FAISS, improving search relevance.",
            "Deployed machine learning models on AWS using FastAPI and Docker, handling 10k+ requests per minute.",
            "Built data pipelines using pandas and numpy, cleaning and transforming 10M+ rows daily."
        ],
        "Web": [
            "Developed responsive user interfaces using React.js and Tailwind CSS, increasing user retention.",
            "Built scalable backend REST APIs using Node.js, Express, and PostgreSQL.",
            "Migrated legacy codebase to Next.js, improving SEO scores and page load speeds by 40%.",
            "Implemented state management using Redux Toolkit and integrated real-time communication with Socket.io.",
            "Managed deployments on AWS, configuring CI/CD pipelines with GitHub Actions."
        ],
        "PM": [
            "Owned the product roadmap for core user growth features, increasing signup conversion by 15%.",
            "Conducted user research and translated insights into detailed PRDs and agile user stories.",
            "Collaborated with engineering and design teams to deliver high-impact feature releases on schedule.",
            "Analyzed user behavior metrics using Amplitude and Mixpanel, identifying key drop-off points.",
            "Managed sprints, backlogs, and stakeholder communication in a fast-paced agile environment."
        ],
        "Civil": [
            "Supervised construction sites, ensuring adherence to safety regulations and structural blueprints.",
            "Created 3D building models and structural designs using AutoCAD and Revit.",
            "Conducted material testing, cost estimation, and vendor negotiation for multi-million dollar projects.",
            "Coordinated with architects, subcontractors, and government authorities for project clearances.",
            "Prepared structural calculation reports and checked compliance with building codes."
        ],
        "HR": [
            "Managed end-to-end recruitment pipelines, sourcing candidates and coordinating interviews.",
            "Handled employee onboarding, payroll queries, and benefits administration.",
            "Developed employee engagement initiatives and resolved workplace grievances.",
            "Collaborated with hiring managers to define job requirements and talent sourcing strategies.",
            "Conducted performance management reviews and managed employee relations."
        ]
    }
    
    num_jobs = max(1, min(yoe // 2, 4))
    years_per_job = max(1, yoe // num_jobs)
    
    temp_start = start_year
    for i in range(num_jobs):
        is_last = (i == num_jobs - 1)
        temp_end = current_year if is_last else temp_start + years_per_job
        
        company = random.choice(target_companies)
        title = roles[domain][min(i, len(roles[domain]) - 1)]
        
        if is_last and yoe >= 5 and not title.startswith("Senior") and not title.startswith("Lead") and len(roles[domain]) > 2:
            title = roles[domain][2]
            
        desc = random.choice(descriptions[domain])
        
        history.append({
            "company": company,
            "title": title,
            "description": desc,
            "start_date": f"{temp_start}-06-01",
            "end_date": "Present" if is_last else f"{temp_end}-05-30"
        })
        temp_start = temp_end
        
    return history[::-1]

# Generate Candidate Profiles
def generate_candidates():
    candidates = []
    
    # 1. AI/ML Candidates (55)
    for idx in range(1, 56):
        c_id = f"cand_ai_{idx:03d}"
        name = f"Candidate AI {idx}"
        
        if idx <= 8:
            yoe = random.randint(1, 3)
        elif idx <= 48:
            yoe = random.randint(4, 11)
        else:
            yoe = random.randint(12, 15)
            
        edu_degree = random.choice(DEGREES[:5])
        edu_inst = random.choice(UNIVERSITIES)
        
        if idx % 3 == 0:
            target_companies = STARTUPS + PRODUCT_COMPANIES
        elif idx % 3 == 1:
            target_companies = PRODUCT_COMPANIES
        else:
            target_companies = CONSULTING_COMPANIES
            
        history = generate_career_history("AI/ML", yoe, target_companies)
        current_title = history[0]["title"] if history else "AI Engineer"
        
        num_skills = random.randint(6, 12)
        selected_skills = random.sample(AI_ML_SKILLS, min(num_skills, len(AI_ML_SKILLS)))
        skills_list = []
        for name_s, prof in selected_skills:
            skills_list.append({
                "name": name_s,
                "proficiency": random.choice(["expert", "advanced", "intermediate"]) if idx % 5 != 0 else prof,
                "duration_months": random.randint(12, yoe * 12)
            })
            
        open_to_work = random.choice([True, False])
        willing_relocate = random.choice([True, False])
        notice_period = random.choice([0, 15, 30, 45, 60, 90])
        response_rate = round(random.uniform(0.5, 1.0), 2)
        
        github_commits = random.randint(0, 800) if idx % 4 != 0 else random.randint(400, 1500)
        recent_certs = random.choice([
            [], ["Google Professional ML Engineer"], ["AWS Certified Machine Learning - Specialty"],
            ["TensorFlow Developer Certificate"], ["Google Professional ML", "DeepLearning.AI TensorFlow"]
        ]) if idx % 3 == 0 else []
        
        project_count = random.randint(1, 6)
        projects = []
        for p_i in range(project_count):
            projects.append({
                "title": f"AI Project {p_i+1}",
                "description": f"Developed a complex machine learning project solving a real-world problem using Python and PyTorch.",
                "tech_used": [s["name"] for s in random.sample(skills_list, min(3, len(skills_list)))]
            })
            
        headline = f"{current_title} passionate about solving complex AI and ML challenges."
        summary = f"Results-driven AI Professional with {yoe} years of experience specializing in Machine Learning, Deep Learning, and Python development. Proven track record of delivering production-grade AI solutions."
        
        c_data = {
            "candidate_id": c_id,
            "profile": {
                "name": name,
                "headline": headline,
                "summary": summary,
                "current_title": current_title,
                "current_industry": "Technology",
                "years_of_experience": yoe,
                "current_location": random.choice(LOCATIONS),
                "education": f"{edu_degree} from {edu_inst}"
            },
            "skills": skills_list,
            "career_history": history,
            "projects": projects,
            "redrob_signals": {
                "open_to_work_flag": open_to_work,
                "notice_period_days": notice_period,
                "recruiter_response_rate": response_rate,
                "willing_to_relocate": willing_relocate,
                "github_contributions_commits": github_commits,
                "recent_certifications": recent_certs,
                "project_frequency_count": project_count,
                "technology_adoption_index": round(random.uniform(0.6, 0.98), 2)
            }
        }
        
        # Honeypots
        if idx in [10, 20, 30, 40]:
            if idx in [10, 30]:
                c_data["profile"]["years_of_experience"] = 2
                c_data["career_history"] = [
                    {
                        "company": "FakeCorp",
                        "title": "Senior Architect",
                        "description": "Exploited resume parsing.",
                        "start_date": "2010-01-01",
                        "end_date": "Present"
                    }
                ]
            else:
                c_data["skills"] = [
                    {"name": "python", "proficiency": "expert", "duration_months": 0},
                    {"name": "machine learning", "proficiency": "expert", "duration_months": 0},
                    {"name": "deep learning", "proficiency": "expert", "duration_months": 0},
                    {"name": "llms", "proficiency": "expert", "duration_months": 0},
                    {"name": "rag systems", "proficiency": "expert", "duration_months": 0},
                    {"name": "fastapi", "proficiency": "intermediate", "duration_months": 24}
                ]
                
        candidates.append(c_data)
        
    # 2. Web Candidates (40)
    for idx in range(1, 41):
        c_id = f"cand_web_{idx:03d}"
        name = f"Candidate Web {idx}"
        yoe = random.randint(2, 10)
        edu_degree = random.choice(DEGREES[:4])
        edu_inst = random.choice(UNIVERSITIES)
        target_companies = STARTUPS + PRODUCT_COMPANIES if idx % 2 == 0 else CONSULTING_COMPANIES
        history = generate_career_history("Web", yoe, target_companies)
        current_title = history[0]["title"] if history else "Software Engineer"
        
        num_skills = random.randint(6, 11)
        selected_skills = random.sample(WEB_SKILLS, min(num_skills, len(WEB_SKILLS)))
        skills_list = []
        for name_s, prof in selected_skills:
            skills_list.append({
                "name": name_s,
                "proficiency": random.choice(["expert", "advanced", "intermediate"]),
                "duration_months": random.randint(12, yoe * 12)
            })
            
        open_to_work = random.choice([True, False])
        willing_relocate = random.choice([True, False])
        notice_period = random.choice([0, 15, 30, 45, 60, 90])
        response_rate = round(random.uniform(0.4, 0.95), 2)
        github_commits = random.randint(50, 600)
        recent_certs = ["AWS Certified Developer - Associate"] if idx % 4 == 0 else []
        
        c_data = {
            "candidate_id": c_id,
            "profile": {
                "name": name,
                "headline": f"Full Stack Developer specializing in React and Node.js",
                "summary": f"Software Engineer with {yoe} years of experience designing, building, and deploying robust web applications.",
                "current_title": current_title,
                "current_industry": "Technology",
                "years_of_experience": yoe,
                "current_location": random.choice(LOCATIONS),
                "education": f"{edu_degree} from {edu_inst}"
            },
            "skills": skills_list,
            "career_history": history,
            "projects": [
                {
                    "title": f"Web App {p_i}",
                    "description": "Built a scalable web dashboard with real-time updates and cloud deployment.",
                    "tech_used": [s["name"] for s in random.sample(skills_list, min(3, len(skills_list)))]
                } for p_i in range(random.randint(1, 4))
            ],
            "redrob_signals": {
                "open_to_work_flag": open_to_work,
                "notice_period_days": notice_period,
                "recruiter_response_rate": response_rate,
                "willing_to_relocate": willing_relocate,
                "github_contributions_commits": github_commits,
                "recent_certifications": recent_certs,
                "project_frequency_count": random.randint(1, 4),
                "technology_adoption_index": round(random.uniform(0.5, 0.9), 2)
            }
        }
        candidates.append(c_data)
        
    # 3. Product Manager Candidates (25)
    for idx in range(1, 26):
        c_id = f"cand_pm_{idx:03d}"
        name = f"Candidate PM {idx}"
        yoe = random.randint(3, 12)
        edu_degree = "MBA in Product Management" if idx % 2 == 0 else "B.Tech in Computer Science"
        edu_inst = random.choice(UNIVERSITIES)
        target_companies = PRODUCT_COMPANIES
        history = generate_career_history("PM", yoe, target_companies)
        current_title = history[0]["title"] if history else "Product Manager"
        
        num_skills = random.randint(5, 9)
        selected_skills = random.sample(PM_SKILLS, min(num_skills, len(PM_SKILLS)))
        skills_list = []
        for name_s, prof in selected_skills:
            skills_list.append({
                "name": name_s,
                "proficiency": random.choice(["expert", "advanced", "intermediate"]),
                "duration_months": random.randint(12, yoe * 12)
            })
            
        c_data = {
            "candidate_id": c_id,
            "profile": {
                "name": name,
                "headline": f"Product Manager driving user-centric products",
                "summary": f"Experienced Product Manager with {yoe} years in tech, passionate about agile delivery and product-led growth.",
                "current_title": current_title,
                "current_industry": "Technology",
                "years_of_experience": yoe,
                "current_location": random.choice(LOCATIONS),
                "education": f"{edu_degree} from {edu_inst}"
            },
            "skills": skills_list,
            "career_history": history,
            "projects": [],
            "redrob_signals": {
                "open_to_work_flag": random.choice([True, False]),
                "notice_period_days": random.choice([30, 60, 90]),
                "recruiter_response_rate": round(random.uniform(0.6, 0.9), 2),
                "willing_to_relocate": random.choice([True, False]),
                "github_contributions_commits": random.randint(0, 50),
                "recent_certifications": ["Product School Certified PM"] if idx % 3 == 0 else [],
                "project_frequency_count": random.randint(1, 2),
                "technology_adoption_index": round(random.uniform(0.4, 0.75), 2)
            }
        }
        candidates.append(c_data)

    # 4. Wrong Domain Candidates: Civil Engineers (15) & HR Managers (15)
    for idx in range(1, 16):
        # Civil
        c_id = f"cand_civil_{idx:03d}"
        name = f"Candidate Civil {idx}"
        yoe = random.randint(3, 10)
        edu_degree = "B.Tech in Civil Engineering"
        edu_inst = random.choice(UNIVERSITIES[4:])
        history = generate_career_history("Civil", yoe, ["L&T Construction", "Tata Projects", "DLF", "Shapoorji Pallonji"])
        current_title = history[0]["title"] if history else "Civil Engineer"
        
        num_skills = random.randint(4, 7)
        selected_skills = random.sample(CIVIL_SKILLS, min(num_skills, len(CIVIL_SKILLS)))
        skills_list = [{"name": name_s, "proficiency": prof, "duration_months": random.randint(12, yoe * 12)} for name_s, prof in selected_skills]
        
        c_data = {
            "candidate_id": c_id,
            "profile": {
                "name": name,
                "headline": f"Structural Engineer / Site Supervisor",
                "summary": f"Civil Engineer with {yoe} years of experience executing major real-estate and infrastructural developments.",
                "current_title": current_title,
                "current_industry": "Construction",
                "years_of_experience": yoe,
                "current_location": random.choice(LOCATIONS),
                "education": f"{edu_degree} from {edu_inst}"
            },
            "skills": skills_list,
            "career_history": history,
            "projects": [],
            "redrob_signals": {
                "open_to_work_flag": random.choice([True, False]),
                "notice_period_days": random.choice([30, 45, 60]),
                "recruiter_response_rate": round(random.uniform(0.3, 0.8), 2),
                "willing_to_relocate": random.choice([True, False]),
                "github_contributions_commits": 0,
                "recent_certifications": [],
                "project_frequency_count": 0,
                "technology_adoption_index": round(random.uniform(0.1, 0.4), 2)
            }
        }
        candidates.append(c_data)
        
        # HR (Wait, we need HR skills first, but let's define them directly)
        c_id = f"cand_hr_{idx:03d}"
        name = f"Candidate HR {idx}"
        yoe = random.randint(3, 10)
        edu_degree = "MBA in HR Management"
        edu_inst = random.choice(UNIVERSITIES[3:])
        history = generate_career_history("HR", yoe, ["TCS", "Infosys", "Reliance Industries", "ICICI Bank"])
        # Give HR some typical HR titles
        current_title = "HR Manager" if idx % 2 == 0 else "Talent Acquisition Specialist"
        if history:
            history[0]["title"] = current_title
            
        skills_list = [
            {"name": "recruitment", "proficiency": "expert", "duration_months": random.randint(12, yoe * 12)},
            {"name": "talent acquisition", "proficiency": "expert", "duration_months": random.randint(12, yoe * 12)},
            {"name": "employee relations", "proficiency": "advanced", "duration_months": random.randint(12, yoe * 12)}
        ]
        
        c_data = {
            "candidate_id": c_id,
            "profile": {
                "name": name,
                "headline": f"HR Specialist and Talent Acquisition Leader",
                "summary": f"Human Resources Professional with {yoe} years of experience leading recruitment and employee relations workflows.",
                "current_title": current_title,
                "current_industry": "Human Resources",
                "years_of_experience": yoe,
                "current_location": random.choice(LOCATIONS),
                "education": f"{edu_degree} from {edu_inst}"
            },
            "skills": skills_list,
            "career_history": history,
            "projects": [],
            "redrob_signals": {
                "open_to_work_flag": random.choice([True, False]),
                "notice_period_days": random.choice([15, 30, 60]),
                "recruiter_response_rate": round(random.uniform(0.7, 0.99), 2),
                "willing_to_relocate": random.choice([True, False]),
                "github_contributions_commits": 0,
                "recent_certifications": [],
                "project_frequency_count": 0,
                "technology_adoption_index": round(random.uniform(0.2, 0.5), 2)
            }
        }
        candidates.append(c_data)
        
    # Write candidates.jsonl
    with open("data/candidates.jsonl", "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c) + "\n")
            
    # Write flattened candidates.csv
    flat_candidates = []
    for c in candidates:
        prof = c["profile"]
        sigs = c["redrob_signals"]
        skill_names = [s["name"] for s in c["skills"]]
        flat_candidates.append({
            "candidate_id": c["candidate_id"],
            "name": prof["name"],
            "current_title": prof["current_title"],
            "current_industry": prof["current_industry"],
            "years_of_experience": prof["years_of_experience"],
            "current_location": prof["current_location"],
            "education": prof["education"],
            "skills": ", ".join(skill_names),
            "open_to_work": sigs["open_to_work_flag"],
            "notice_period_days": sigs["notice_period_days"],
            "recruiter_response_rate": sigs["recruiter_response_rate"],
            "willing_to_relocate": sigs["willing_to_relocate"],
            "github_commits": sigs["github_contributions_commits"],
            "certifications_count": len(sigs["recent_certifications"]),
            "headline": prof["headline"],
            "summary": prof["summary"]
        })
        
    import pandas as pd
    df = pd.DataFrame(flat_candidates)
    df.to_csv("data/candidates.csv", index=False)
    
    print(f"Generated {len(candidates)} candidates in data/candidates.jsonl and data/candidates.csv!")

# Generate Preset Jobs
def generate_jobs():
    jobs = [
        {
            "job_id": "job_001",
            "title": "Senior AI Engineer",
            "department": "Engineering - AI Team",
            "description": """
Senior AI Engineer at Redrob AI.
5 to 9 years of experience required.
Must have skills: RAG systems, vector embeddings, semantic search, LLMs, Python.
Experience with vector databases like Pinecone, Weaviate, Qdrant, FAISS.
Product company experience preferred. Consulting or services background not preferred.
Location: Pune or Noida. Willing to relocate preferred.
Notice period under 30 days preferred.
Open to work candidates preferred.
""",
            "required_skills": "rag systems, vector embeddings, semantic search, llms, python, Pinecone, Weaviate, Qdrant, FAISS",
            "preferred_skills": "pytorch, fastapi, docker, aws, git",
            "experience_min": 5,
            "experience_max": 9,
            "location_preference": "Pune, Noida",
            "domain": "AI/ML"
        },
        {
            "job_id": "job_002",
            "title": "Lead Data Scientist",
            "department": "Data & Analytics",
            "description": """
Looking for a Lead Data Scientist with 6+ years of experience.
Must be strong in Python, Machine Learning, scikit-learn, deep learning, and PyTorch.
Experience in deploying models to production using Docker and FastAPI is required.
Strong background in statistical modeling, pandas, numpy, and SQL.
Prior experience mentoring junior engineers is highly valued.
Location: Bangalore or Hyderabad.
""",
            "required_skills": "python, machine learning, scikit-learn, deep learning, pytorch, sql",
            "preferred_skills": "fastapi, docker, pandas, numpy, aws, git",
            "experience_min": 6,
            "experience_max": 12,
            "location_preference": "Bangalore, Hyderabad",
            "domain": "AI/ML"
        },
        {
            "job_id": "job_003",
            "title": "Senior React & Full Stack Developer",
            "department": "Engineering - Web Team",
            "description": """
We are hiring a Senior Full Stack Engineer with 4 to 8 years of experience.
Core requirements: HTML, CSS, Javascript, Typescript, React, Next.js, and Node.js.
Strong experience with Tailwind CSS, PostgreSQL, and state management (Redux/Zustand).
Must understand REST API designs, GraphQL, and AWS cloud hosting.
Active GitHub profile is a major plus.
Location: Pune, Bangalore, or Remote.
""",
            "required_skills": "javascript, typescript, react, next.js, node.js, html, css",
            "preferred_skills": "tailwind css, postgresql, redux, rest api, graphql, aws, git",
            "experience_min": 4,
            "experience_max": 8,
            "location_preference": "Pune, Bangalore, Remote",
            "domain": "Web"
        }
    ]
    
    with open("data/jobs.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
        writer.writeheader()
        writer.writerows(jobs)
        
    print("Generated preset jobs in data/jobs.csv!")

if __name__ == "__main__":
    # Define globally inside main to avoid scope issues
    UNIVERSITIES = ["IIT Bombay", "IIT Delhi", "IIT Madras", "BITS Pilani", "IIIT Hyderabad", "Delhi Technological University", "Anna University", "VIT University", "Stanford University", "MIT", "Carnegie Mellon University"]
    DEGREES = ["B.Tech in Computer Science", "Dual Degree (B.Tech + M.Tech) in CS", "M.Tech in Artificial Intelligence", "B.E. in Information Technology", "M.S. in Computer Science", "B.Tech in Civil Engineering", "MBA in HR Management"]
    
    generate_candidates()
    generate_jobs()
