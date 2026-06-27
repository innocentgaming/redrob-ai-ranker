import re
import numpy as np
from pypdf import PdfReader
from src.job_analyzer import SKILL_DICTIONARY

class PDFResumeParser:
    @classmethod
    def extract_text(cls, pdf_file) -> str:
        """
        Extracts raw text from an uploaded PDF file-like object.
        """
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {e}")

    @classmethod
    def parse_pdf(cls, pdf_file) -> dict:
        """
        Parses a PDF resume file and returns a structured candidate dictionary.
        """
        text = cls.extract_text(pdf_file)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Name extraction (typically the first line or near it)
        name = "Unknown Candidate"
        for line in lines[:3]:
            # Simple check: name should not contain email, phone, or common labels
            if "@" not in line and not re.search(r"\d{4}", line) and len(line) < 50:
                name = line
                break
                
        # 2. Contact Info Extraction
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        email = email_match.group(0) if email_match else "unknown@email.com"
        
        phone_match = re.search(r"\+?\d[\d\s-]{8,14}\d", text)
        phone = phone_match.group(0) if phone_match else "Unknown"
        
        # 3. Skills Extraction
        detected_skills = []
        text_lower = text.lower()
        for skill_name, aliases in SKILL_DICTIONARY.items():
            for alias in aliases:
                # Use word boundary to avoid partial matches
                if re.search(rf"\b{re.escape(alias.lower())}\b", text_lower):
                    # Estimate proficiency based on occurrence context (expert if mentioned near expert/senior)
                    proficiency = "intermediate"
                    # Look around the skill match for proficiency words
                    idx = text_lower.find(alias.lower())
                    if idx != -1:
                        surroundings = text_lower[max(0, idx-50):min(len(text_lower), idx+50)]
                        if any(w in surroundings for w in ["expert", "lead", "principal", "architect"]):
                            proficiency = "expert"
                        elif any(w in surroundings for w in ["senior", "advanced", "strong"]):
                            proficiency = "advanced"
                        elif any(w in surroundings for w in ["junior", "entry", "basic", "learning"]):
                            proficiency = "beginner"
                            
                    detected_skills.append({
                        "name": skill_name,
                        "proficiency": proficiency,
                        "duration_months": 24 # Default assumption
                    })
                    break

        # 4. Years of Experience Extraction
        yoe = 0.0
        # Heuristic 1: Look for explicit years of experience pattern
        exp_patterns = [
            r"(\d+)\+?\s*years?\s*of\s*experience",
            r"(\d+)\+?\s*years?\s*experience",
            r"(\d+)\+?\s*yrs?\s*exp",
            r"experience:\s*(\d+)\+?\s*years"
        ]
        for pattern in exp_patterns:
            exp_match = re.search(pattern, text_lower)
            if exp_match:
                try:
                    yoe = float(exp_match.group(1))
                    break
                except ValueError:
                    pass
                    
        # Heuristic 2: If no explicit pattern, estimate from date ranges (e.g. 2018 - 2022)
        if yoe == 0.0:
            years = [int(y) for y in re.findall(r"\b(20\d{2})\b", text)]
            if len(years) >= 2:
                min_year = min(years)
                # Cap max year at current year 2026
                max_year = min(2026, max(years))
                yoe = float(max_year - min_year)
                # If they spent years in university, subtract some
                if "b.tech" in text_lower or "b.e." in text_lower or "university" in text_lower:
                    yoe = max(0.0, yoe - 4)
            else:
                yoe = 3.0 # Fallback default
                
        # 5. Location Extraction
        location = "Unknown"
        indian_cities = ["pune", "noida", "bangalore", "hyderabad", "mumbai", "chennai", "gurgaon", "delhi"]
        for city in indian_cities:
            if city in text_lower:
                location = city.capitalize()
                break
                
        # 6. Education Extraction
        education = "University Degree"
        edu_keywords = ["iit", "bits pilani", "iiit", "stanford", "mit", "oxford", "harvard", "delhi technological", "anna university", "vit"]
        for edu in edu_keywords:
            if edu in text_lower:
                # Find the sentence containing the education keyword
                idx = text_lower.find(edu)
                surroundings = text[max(0, idx-40):min(len(text), idx+60)].strip().replace("\n", " ")
                education = surroundings
                break
        if education == "University Degree":
            # Heuristic fallback
            if "b.tech" in text_lower:
                education = "B.Tech in Computer Science"
            elif "m.tech" in text_lower:
                education = "M.Tech in AI/CS"
            elif "m.s." in text_lower:
                education = "M.S. in Computer Science"
                
        # 7. Job Title Extraction
        title = "Software Engineer"
        title_patterns = ["ai engineer", "ml engineer", "data scientist", "full stack developer", "frontend developer", "backend engineer", "product manager", "civil engineer", "hr manager"]
        for t in title_patterns:
            if t in text_lower:
                title = t.title()
                break
                
        # 8. Summary / Headline
        headline = f"{title} with {yoe:.1f} years of experience"
        summary = lines[4] if len(lines) > 4 else "Professional profile extracted from resume PDF."
        
        # Adjust skill durations based on YOE
        for s in detected_skills:
            s["duration_months"] = max(12, int(yoe * 12 * 0.6))
            
        custom_id = f"pdf_{np.random.randint(10000, 99999)}"
        
        # Build candidate dict
        return {
            "candidate_id": custom_id,
            "profile": {
                "name": name,
                "headline": headline,
                "summary": summary,
                "current_title": title,
                "current_industry": "Technology" if "tech" in text_lower or "software" in text_lower else "Other",
                "years_of_experience": yoe,
                "current_location": location,
                "education": education
            },
            "skills": detected_skills,
            "career_history": [
                {
                    "company": "Previous Employer",
                    "title": title,
                    "description": "Extracted from resume timeline.",
                    "start_date": f"{int(2026 - yoe)}-06-01",
                    "end_date": "Present"
                }
            ],
            "projects": [],
            "redrob_signals": {
                "open_to_work_flag": True,
                "notice_period_days": 30,
                "recruiter_response_rate": 0.85,
                "willing_to_relocate": True,
                "github_contributions_commits": 120,
                "recent_certifications": [],
                "project_frequency_count": 0,
                "technology_adoption_index": 0.75
            }
        }
