
from sentence_transformers import SentenceTransformer
import numpy as np


class SemanticAnalysisError(Exception):
    """Raised when semantic analysis cannot be completed."""


class SemanticAnalyzer:

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    THEMES = {
        "creative_expression": (
            "Writing about creativity, artistic expression, "
            "design, imagination and making original things."
        ),
        "curiosity_exploration": (
            "Writing about curiosity, discovering new ideas, "
            "learning, exploration and trying unfamiliar things."
        ),
        "nostalgia_memories": (
            "Writing about memories, childhood, the past, "
            "nostalgia and meaningful experiences."
        ),
        "reflection_introspection": (
            "Writing about personal reflections, thoughts, "
            "self-discovery and understanding experiences."
        ),
        "humour_playfulness": (
            "Writing involving humour, jokes, sarcasm, "
            "playfulness and amusing observations."
        ),
        "storytelling": (
            "Writing involving narratives, fictional worlds, "
            "characters, events and imaginative storytelling."
        ),
    }

    def __init__(self, model=None):
        # Dependency injection makes testing easier.
        self.model = model or SentenceTransformer(self.MODEL_NAME)

        self.theme_names = list(self.THEMES.keys())

        descriptions = [
            self.THEMES[theme]
            for theme in self.theme_names
        ]

        self.theme_embeddings = self.model.encode(
            descriptions,
            normalize_embeddings=True
        )

    def analyze(self, text: str, top_k: int = 3):

        if not isinstance(text, str):
            raise SemanticAnalysisError(
                "Writing sample must be text."
            )

        cleaned_text = text.strip()

        if not 100 <= len(cleaned_text) <= 2000:
            raise SemanticAnalysisError(
                "Writing sample must contain between "
                "100 and 2000 characters."
            )

        if not isinstance(top_k, int) or isinstance(top_k, bool):
            raise SemanticAnalysisError(
                "top_k must be an integer."
            )

        if not 1 <= top_k <= len(self.theme_names):
            raise SemanticAnalysisError(
                "Invalid top_k value."
            )

        text_embedding = self.model.encode(
            cleaned_text,
            normalize_embeddings=True
        )

        similarities = np.dot(
            self.theme_embeddings,
            text_embedding
        )

        ranked_indices = np.argsort(similarities)[::-1][:top_k]

        themes = []

        for index in ranked_indices:
            themes.append({
                "theme": self.theme_names[index],
                "similarity_score": round(
                    float(similarities[index]) * 100, 2
                )
            })

        return {
            "model": self.MODEL_NAME,
            "embedding_dimensions": int(len(text_embedding)),
            "themes": themes,
            "interpretation": (
                "These are approximate semantic similarities "
                "between the writing sample and predefined "
                "theme descriptions. They are not personality "
                "scores or probabilities."
            )
        }
