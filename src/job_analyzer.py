import re

# Standard dictionaries of skills for better matching
SKILL_DICTIONARY = {
    "rag systems": ["rag", "rag systems", "retrieval augmented generation", "llamaindex", "langchain"],
    "vector embeddings": ["embeddings", "vector embeddings", "semantic vectors", "word2vec"],
    "semantic search": ["semantic search", "vector search", "dense retrieval"],
    "llms": ["llm", "llms", "large language models", "gpt", "llama", "mistral", "claude"],
    "python": ["python", "py"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "fastapi": ["fastapi"],
    "aws": ["aws", "amazon web services", "ec2", "s3"],
    "docker": ["docker", "containers"],
    "git": ["git", "github", "gitlab"],
    "nlp": ["nlp", "natural language processing", "spacy", "nltk", "bert"],
    "transformers": ["transformers", "huggingface", "attention mechanisms"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "sql": ["sql", "mysql", "postgresql", "sqlite"],
    "pinecone": ["pinecone"],
    "weaviate": ["weaviate"],
    "qdrant": ["qdrant"],
    "faiss": ["faiss"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "next.js": ["next.js", "nextjs"],
    "node.js": ["node.js", "nodejs"],
    "express": ["express", "expressjs"],
    "html": ["html"],
    "css": ["css"],
    "tailwind css": ["tailwind", "tailwind css", "tailwindcss"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "rest api": ["rest", "rest api", "apis", "restful"],
    "graphql": ["graphql"],
    "redux": ["redux", "redux toolkit"],
    "product management": ["product management", "product manager", "pm"],
    "agile": ["agile", "sprints"],
    "scrum": ["scrum", "scrum master"],
    "product roadmap": ["roadmap", "product roadmap"],
    "jira": ["jira"],
    "data analytics": ["data analytics", "analytics"],
    "user research": ["user research", "interviews"],
    "wireframing": ["wireframing", "figma", "sketch"],
    "market analysis": ["market analysis", "competitor analysis"],
    "product analytics": ["product analytics", "amplitude", "mixpanel"],
    "autocad": ["autocad"],
    "civil engineering": ["civil", "civil engineering"],
    "structural design": ["structural design", "structural engineering"],
    "concrete design": ["concrete", "rcc"],
    "project estimation": ["estimation", "costing", "billing"],
    "site supervision": ["site supervision", "site execution", "safety"],
    "surveying": ["surveying"],
    "recruitment": ["recruitment", "recruiter", "sourcing"],
    "talent acquisition": ["talent acquisition", "ta"],
    "employee relations": ["employee relations", "grievances"],
    "onboarding": ["onboarding"],
    "hris": ["hris", "workday", "bamboohr"]
}

class JobAnalyzer:
    @staticmethod
    def analyze_job_description(jd_text: str) -> dict:
        """
        Parses raw job description text and extracts structured information.
        """
        if not jd_text or not isinstance(jd_text, str):
            return {
                "title": "Software Engineer",
                "required_skills": [],
                "preferred_skills": [],
                "experience_min": 0,
                "experience_max": 20,
                "location_preference": [],
                "domain": "General"
            }
            
        # Security & Efficiency: Sanitize input and limit length to prevent ReDoS / memory exhaustion
        if len(jd_text) > 10000:
            jd_text = jd_text[:10000]
            
        jd_lower = jd_text.lower()
        
        # 1. Title Extraction
        title = "Software Engineer"
        title_patterns = [
            (r"senior ai engineer", "Senior AI Engineer"),
            (r"lead ai engineer", "Lead AI Engineer"),
            (r"ai engineer", "AI Engineer"),
            (r"lead data scientist", "Lead Data Scientist"),
            (r"senior data scientist", "Senior Data Scientist"),
            (r"data scientist", "Data Scientist"),
            (r"senior full stack", "Senior Full Stack Engineer"),
            (r"full stack developer", "Full Stack Developer"),
            (r"react developer", "React Developer"),
            (r"product manager", "Product Manager"),
            (r"civil engineer", "Civil Engineer"),
            (r"hr manager", "HR Manager")
        ]
        for pattern, replacement in title_patterns:
            if re.search(pattern, jd_lower):
                title = replacement
                break
                
        # 2. Domain Classification
        domain = "General"
        if any(w in jd_lower for w in ["ai", "ml", "machine learning", "llm", "rag", "data science", "deep learning"]):
            domain = "AI/ML"
        elif any(w in jd_lower for w in ["react", "node", "javascript", "typescript", "frontend", "backend", "full stack", "css", "html"]):
            domain = "Web"
        elif any(w in jd_lower for w in ["product manager", "roadmap", "prd", "agile", "scrum"]):
            domain = "PM"
        elif any(w in jd_lower for w in ["civil", "construction", "site engineer", "structural", "autocad"]):
            domain = "Civil"
        elif any(w in jd_lower for w in ["recruitment", "talent acquisition", "employee relations", "hr"]):
            domain = "HR"
            
        # 3. Experience Range Extraction
        exp_min = 0
        exp_max = 20
        
        # Look for patterns like "5 to 9 years", "3+ years", "4-8 years", "6+ years"
        range_match = re.search(r"(\d+)\s*(?:to|-)\s*(\d+)\s*years", jd_lower)
        plus_match = re.search(r"(\d+)\+\s*years", jd_lower)
        req_match = re.search(r"(\d+)\s*years?\s*experience\s*(?:required|preferred|needed)", jd_lower)
        
        if range_match:
            exp_min = int(range_match.group(1))
            exp_max = int(range_match.group(2))
        elif plus_match:
            exp_min = int(plus_match.group(1))
            exp_max = exp_min + 5 # Assume 5 years window as default upper bound
        elif req_match:
            exp_min = int(req_match.group(1))
            exp_max = exp_min + 5
            
        # 4. Location Extraction
        locations = []
        indian_cities = ["pune", "noida", "bangalore", "hyderabad", "mumbai", "chennai", "gurgaon", "delhi"]
        for city in indian_cities:
            if city in jd_lower:
                locations.append(city.capitalize())
        if "remote" in jd_lower:
            locations.append("Remote")
            
        # 5. Skills Extraction (Must-have vs Preferred)
        # We split the JD into sections to distinguish required vs preferred if possible
        must_have_skills = []
        preferred_skills = []
        
        # Split into "must have" vs "preferred" sections if key markers exist
        must_have_markers = ["must have", "required", "requirements", "core skills", "essential"]
        preferred_markers = ["preferred", "nice to have", "plus", "optional", "bonus", "desirable"]
        
        # Determine which skills from our dictionary are present in the text
        detected_skills = []
        for skill_name, aliases in SKILL_DICTIONARY.items():
            for alias in aliases:
                # Use word boundary to avoid partial matches
                if re.search(rf"\b{re.escape(alias)}\b", jd_lower):
                    detected_skills.append(skill_name)
                    break
                    
        # Classify detected skills into must-have vs preferred
        sentences = [s.strip() for s in re.split(r'\.\s+|\!\s*|\?\s*|\n', jd_lower) if s.strip()]
        
        for skill in detected_skills:
            # Check if this skill is explicitly mentioned in a preferred context in any sentence
            is_preferred_context = False
            aliases = SKILL_DICTIONARY.get(skill, [skill])
            for sentence in sentences:
                has_alias = any(re.search(rf"\b{re.escape(alias)}\b", sentence) for alias in aliases)
                if has_alias:
                    if any(marker in sentence for marker in preferred_markers):
                        is_preferred_context = True
                        break
            
            is_core = False
            if domain == "AI/ML" and skill in ["python", "machine learning", "llms", "rag systems", "vector embeddings", "semantic search", "pinecone", "weaviate", "faiss"]:
                is_core = True
            elif domain == "Web" and skill in ["javascript", "typescript", "react", "node.js", "html", "css", "next.js"]:
                is_core = True
            elif domain == "PM" and skill in ["product management", "agile", "scrum", "product roadmap", "jira"]:
                is_core = True
            elif domain == "Civil" and skill in ["autocad", "civil engineering", "structural design"]:
                is_core = True
            elif domain == "HR" and skill in ["recruitment", "talent acquisition", "employee relations", "onboarding"]:
                is_core = True
                
            if is_core and not is_preferred_context:
                must_have_skills.append(skill)
            else:
                preferred_skills.append(skill)
                
        # Fallback if both are empty
        if not must_have_skills and detected_skills:
            must_have_skills = detected_skills[:3]
            preferred_skills = detected_skills[3:]
            
        return {
            "title": title,
            "required_skills": list(set(must_have_skills)),
            "preferred_skills": list(set(preferred_skills)),
            "experience_min": exp_min,
            "experience_max": exp_max,
            "location_preference": locations,
            "domain": domain
        }
