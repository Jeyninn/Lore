
import unittest
from unittest.mock import patch, Mock
from app.semantic.semantic_analyzer import SemanticAnalysisError
from fastapi.testclient import TestClient

from app.main import app, feature_extractor


class TestLoreAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        # Build a valid submission using the actual questionnaire.
        spec = feature_extractor.spec

        cls.valid_payload = {
            "questionnaire_version": spec["version"],
            "responses": [
                {
                    "question_id": question["id"],
                    "option_ids": [question["options"][0]["id"]]
                }
                for question in spec["questions"]
            ]
        }

        cls.valid_writing_sample = (
            "I enjoy exploring creative ideas, experimenting with "
            "different forms of art and discovering unusual "
            "perspectives. I often find inspiration in music, "
            "stories, design and the little details of everyday "
            "life. I love imagining fictional worlds and expressing "
            "my thoughts through creative projects."
        )

    def test_health_endpoint(self):
        response = self.client.get("/api/ml/v1/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_successful_questionnaire_analysis(self):
        with patch("app.main.get_semantic_analyzer") as mock_analyzer:
            response = self.client.post(
                "/api/ml/v1/analyze",
                json=self.valid_payload
            )

            self.assertEqual(response.status_code, 200)

            # Semantic model should not load for questionnaire-only requests.
            mock_analyzer.assert_not_called()

        result = response.json()

        self.assertIn("feature_scores", result)
        self.assertIn("preference_tags", result)
        self.assertIn("primary_archetype", result)
        self.assertIn("secondary_archetype", result)
        self.assertIn("matches", result)
        self.assertIsNone(result["writing_analysis"])

        self.assertEqual(len(result["feature_scores"]), 8)
        self.assertGreaterEqual(len(result["matches"]), 1)

    def test_missing_required_question(self):
        payload = {
            **self.valid_payload,
            "responses": self.valid_payload["responses"][1:]
        }

        response = self.client.post(
            "/api/ml/v1/analyze",
            json=payload
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_option_id(self):
        payload = {
            **self.valid_payload,
            "responses": [
                dict(response)
                for response in self.valid_payload["responses"]
            ]
        }

        payload["responses"][0]["option_ids"] = ["invalid_option"]

        response = self.client.post(
            "/api/ml/v1/analyze",
            json=payload
        )

        self.assertEqual(response.status_code, 422)

    def test_wrong_questionnaire_version(self):
        payload = {
            **self.valid_payload,
            "questionnaire_version": 999
        }

        response = self.client.post(
            "/api/ml/v1/analyze",
            json=payload
        )

        self.assertEqual(response.status_code, 422)

    def test_empty_option_list_is_rejected(self):
        payload = {
            **self.valid_payload,
            "responses": [
                dict(response)
                for response in self.valid_payload["responses"]
            ]
        }

        payload["responses"][0]["option_ids"] = []

        response = self.client.post(
            "/api/ml/v1/analyze",
            json=payload
        )

        self.assertEqual(response.status_code, 422)

    # NEW TESTS: Writing analysis integration

    def test_writing_without_consent_is_rejected(self):
        payload = {
            **self.valid_payload,
            "writing_sample": self.valid_writing_sample,
            "consent_to_analyze_writing": False
        }

        with patch("app.main.get_semantic_analyzer") as mock_analyzer:
            response = self.client.post(
                "/api/ml/v1/analyze",
                json=payload
            )

            self.assertEqual(response.status_code, 422)
            mock_analyzer.assert_not_called()

    def test_writing_with_consent(self):
        mock_result = {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dimensions": 384,
            "themes": [
                {
                    "theme": "creative_expression",
                    "similarity_score": 85.23
                },
                {
                    "theme": "storytelling",
                    "similarity_score": 79.45
                }
            ],
            "interpretation": "Approximate semantic similarities."
        }

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = mock_result

        payload = {
            **self.valid_payload,
            "writing_sample": self.valid_writing_sample,
            "consent_to_analyze_writing": True
        }

        with patch(
            "app.main.get_semantic_analyzer",
            return_value=mock_analyzer
        ):
            response = self.client.post(
                "/api/ml/v1/analyze",
                json=payload
            )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertIsNotNone(result["writing_analysis"])
        self.assertEqual(
            result["writing_analysis"]["embedding_dimensions"],
            384
        )
        self.assertEqual(
            result["writing_analysis"]["themes"][0]["theme"],
            "creative_expression"
        )

        mock_analyzer.analyze.assert_called_once_with(
            self.valid_writing_sample
        )

    def test_short_writing_sample_is_rejected(self):
        payload = {
            **self.valid_payload,
            "writing_sample": "Too short",
            "consent_to_analyze_writing": True
        }

        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = SemanticAnalysisError(
            "Writing sample must contain between 100 and 2000 characters."
        )

        with patch(
            "app.main.get_semantic_analyzer",
            return_value=mock_analyzer
        ):
            response = self.client.post(
                "/api/ml/v1/analyze",
                json=payload
            )

        # The real SemanticAnalysisError should be used in this test.
        self.assertEqual(response.status_code, 422)

    def test_writing_sample_without_consent_does_not_call_model(self):
        payload = {
            **self.valid_payload,
            "writing_sample": self.valid_writing_sample,
            "consent_to_analyze_writing": False
        }

        with patch("app.main.get_semantic_analyzer") as mock_analyzer:
            response = self.client.post(
                "/api/ml/v1/analyze",
                json=payload
            )

        self.assertEqual(response.status_code, 422)
        mock_analyzer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
