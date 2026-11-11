
import unittest
import numpy as np

from app.semantic.semantic_analyzer import (
    SemanticAnalyzer,
    SemanticAnalysisError,
)


class MockEmbeddingModel:

    def encode(self, texts, normalize_embeddings=True):

        # Six theme descriptions.
        if isinstance(texts, list):
            return np.array([
                [1.0, 0.0, 0.0],
                [0.9, 0.1, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.5, 0.5, 0.0],
                [0.0, 0.5, 0.5],
            ])

        # Mock embedding for submitted writing.
        return np.array([1.0, 0.0, 0.0])


class TestSemanticAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SemanticAnalyzer(
            model=MockEmbeddingModel()
        )

        self.valid_text = (
            "I enjoy creating unusual things and exploring "
            "new ideas. I love experimenting with art, "
            "design and imagination while finding unique "
            "ways to express myself through creative projects."
        )

    def test_successful_analysis(self):
        result = self.analyzer.analyze(self.valid_text)

        self.assertIn("themes", result)
        self.assertEqual(len(result["themes"]), 3)

    def test_embedding_dimensions(self):
        result = self.analyzer.analyze(self.valid_text)

        self.assertEqual(result["embedding_dimensions"], 3)

    def test_top_theme_is_ranked_correctly(self):
        result = self.analyzer.analyze(self.valid_text)

        self.assertEqual(
            result["themes"][0]["theme"],
            "creative_expression"
        )

    def test_custom_top_k(self):
        result = self.analyzer.analyze(
            self.valid_text,
            top_k=2
        )

        self.assertEqual(len(result["themes"]), 2)

    def test_short_text_is_rejected(self):
        with self.assertRaises(SemanticAnalysisError):
            self.analyzer.analyze("Too short")

    def test_long_text_is_rejected(self):
        with self.assertRaises(SemanticAnalysisError):
            self.analyzer.analyze("A" * 2001)

    def test_invalid_top_k_is_rejected(self):
        with self.assertRaises(SemanticAnalysisError):
            self.analyzer.analyze(
                self.valid_text,
                top_k=10
            )


if __name__ == "__main__":
    unittest.main()
