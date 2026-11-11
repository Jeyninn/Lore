
import unittest

from app.lore.lore_generator import (
    LoreGenerator,
    LoreGenerationError,
)


class TestLoreGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = LoreGenerator()

        self.archetype_result = {
            "primary_archetype": {
                "id": "curious_goblin",
                "name": "Curious Goblin",
                "tagline": "Always exploring",
                "description": "A curious digital explorer.",
            },
            "secondary_archetype": {
                "id": "dreamcore_thinker",
                "name": "Dreamcore Thinker",
            },
        }

        self.feature_scores = {
            "social_energy": 75,
            "curiosity": 90,
            "creativity": 80,
            "spontaneity": 30,
            "reflection": 70,
            "analytical_style": 65,
            "expressiveness": 85,
            "exploration": 95,
        }

    def test_successful_lore_generation(self):
        result = self.generator.generate(
            self.archetype_result,
            self.feature_scores,
            ["music", "digital_art"],
        )

        self.assertEqual(
            result["identity_title"],
            "The Curious Goblin × Dreamcore Thinker",
        )

        self.assertIn("You are The Curious Goblin", result["narrative"])
        self.assertIn("Music", result["aesthetic_identity"])
        self.assertEqual(
            result["metadata"]["generation_method"],
            "deterministic_rule_based",
        )

    def test_lore_without_secondary_archetype(self):
        archetype = {
            "primary_archetype": self.archetype_result[
                "primary_archetype"
            ],
            "secondary_archetype": None,
        }

        result = self.generator.generate(
            archetype,
            self.feature_scores,
        )

        self.assertEqual(
            result["identity_title"],
            "The Curious Goblin",
        )

    def test_lore_without_preference_tags(self):
        result = self.generator.generate(
            self.archetype_result,
            self.feature_scores,
        )

        self.assertEqual(
            result["aesthetic_identity"],
            ["Your aesthetic is still being discovered"],
        )

    def test_optional_writing_themes(self):
        writing_analysis = {
            "themes": [
                {"name": "curiosity_exploration"},
                {"name": "creative_expression"},
            ]
        }

        result = self.generator.generate(
            self.archetype_result,
            self.feature_scores,
            writing_analysis=writing_analysis,
        )

        self.assertEqual(
            len(result["writing_themes"]),
            2,
        )

        self.assertTrue(
            result["metadata"]["writing_sample_used"]
        )

    def test_missing_primary_archetype(self):
        with self.assertRaises(LoreGenerationError):
            self.generator.generate(
                {},
                self.feature_scores,
            )

    def test_invalid_feature_score(self):
        invalid_scores = self.feature_scores.copy()
        invalid_scores["curiosity"] = 150

        with self.assertRaises(LoreGenerationError):
            self.generator.generate(
                self.archetype_result,
                invalid_scores,
            )

    def test_null_feature_scores(self):
        scores = {
            "social_energy": None,
            "curiosity": None,
            "creativity": None,
        }

        result = self.generator.generate(
            self.archetype_result,
            scores,
        )

        self.assertIn("identity_title", result)
        self.assertIn("narrative", result)


if __name__ == "__main__":
    unittest.main()
