
import unittest

from app.features.feature_extractor import (
    QuestionnaireFeatureExtractor,
    SubmissionValidationError,
)


class TestQuestionnaireFeatureExtractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.extractor = QuestionnaireFeatureExtractor()

    def make_valid_submission(self):
        responses = []

        for question in self.extractor.spec["questions"]:
            responses.append({
                "question_id": question["id"],
                "option_ids": [question["options"][0]["id"]],
            })

        return {
            "questionnaire_version": self.extractor.version,
            "responses": responses,
        }

    def test_valid_submission_returns_all_dimensions(self):
        result = self.extractor.extract(self.make_valid_submission())

        self.assertEqual(result["questionnaire_version"], 1)
        self.assertEqual(
            set(result["feature_scores"].keys()),
            set(self.extractor.dimensions),
        )

        self.assertEqual(result["metadata"]["answered_questions"], 24)

        for score in result["feature_scores"].values():
            if score is not None:
                self.assertGreaterEqual(score, 0)
                self.assertLessEqual(score, 100)

    def test_preference_tags_are_separate_from_scores(self):
        result = self.extractor.extract(self.make_valid_submission())

        self.assertIsInstance(result["preference_tags"], list)
        self.assertIn("cybercore", result["preference_tags"])

    def test_missing_required_question_is_rejected(self):
        submission = self.make_valid_submission()
        submission["responses"].pop()

        with self.assertRaises(SubmissionValidationError):
            self.extractor.extract(submission)

    def test_invalid_option_is_rejected(self):
        submission = self.make_valid_submission()
        submission["responses"][0]["option_ids"] = ["invalid_option"]

        with self.assertRaises(SubmissionValidationError):
            self.extractor.extract(submission)

    def test_wrong_questionnaire_version_is_rejected(self):
        submission = self.make_valid_submission()
        submission["questionnaire_version"] = 99

        with self.assertRaises(SubmissionValidationError):
            self.extractor.extract(submission)

    def test_single_select_rejects_multiple_options(self):
        submission = self.make_valid_submission()
        submission["responses"][0]["option_ids"] = [
            "q01_a",
            "q01_b",
        ]

        with self.assertRaises(SubmissionValidationError):
            self.extractor.extract(submission)

    def test_multi_select_rejects_too_many_options(self):
        submission = self.make_valid_submission()

        # q22 allows a maximum of three selections.
        submission["responses"][21]["option_ids"] = [
            "q22_a",
            "q22_b",
            "q22_c",
            "q22_d",
        ]

        with self.assertRaises(SubmissionValidationError):
            self.extractor.extract(submission)


if __name__ == "__main__":
    unittest.main()
