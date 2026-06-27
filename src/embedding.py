import os
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingEngine:
    _model = None

    @classmethod
    def get_model(cls):
        """
        Singleton pattern to load SentenceTransformer model once.
        """
        if cls._model is None:
            # We can print for CLI usage
            print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Model loaded successfully!")
        return cls._model

    @classmethod
    def get_embedding(cls, text: str) -> np.ndarray:
        """
        Generates embedding for a single text.
        """
        model = cls.get_model()
        return model.encode(text, convert_to_numpy=True)

    @classmethod
    def get_embeddings(cls, texts: list, batch_size: int = 64) -> np.ndarray:
        """
        Generates embeddings for a list of texts.
        """
        model = cls.get_model()
        return model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)

    @staticmethod
    def candidate_to_text(c: dict) -> str:
        """
        Consolidates a candidate profile into a single rich text block for semantic matching.
        """
        parts = []
        profile = c.get('profile', {})
        
        # Profile headline and summary
        parts.append(profile.get('headline', ''))
        parts.append(profile.get('summary', ''))
        parts.append(f"Current title: {profile.get('current_title', '')}")
        parts.append(f"Industry: {profile.get('current_industry', '')}")
        parts.append(f"Experience: {profile.get('years_of_experience', 0)} years")
        parts.append(f"Education: {profile.get('education', '')}")
        
        # Career History
        for job in c.get('career_history', []):
            parts.append(f"Role: {job.get('title', '')} at {job.get('company', '')}: {job.get('description', '')}")
            
        # Skills
        skill_names = [s.get('name', '') for s in c.get('skills', [])]
        if skill_names:
            parts.append("Skills: " + ", ".join(skill_names))
            
        # Projects
        for proj in c.get('projects', []):
            parts.append(f"Project: {proj.get('title', '')}: {proj.get('description', '')}. Tech: {', '.join(proj.get('tech_used', []))}")
            
        # Certifications
        certs = c.get('redrob_signals', {}).get('recent_certifications', [])
        if certs:
            parts.append("Certifications: " + ", ".join(certs))
            
        return " | ".join([p for p in parts if p])

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Computes cosine similarity between two vectors.
        """
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))
