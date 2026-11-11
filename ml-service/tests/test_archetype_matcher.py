
import unittest

from app.engine.archetype_matcher import (
    ArchetypeMatcher,
    FeatureVectorError,
)


class TestArchetypeMatcher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.matcher = ArchetypeMatcher()

    def make_feature_vector(self):
        return {
            "social_energy": 55,
            "curiosity": 95,
            "creativity": 75,
            "spontaneity": 85,
            "reflection": 65,
            "analytical_style": 55,
            "expressiveness": 65,
            "exploration": 95,
        }

    def test_catalog_contains_twelve_archetypes(self):
        self.assertEqual(len(self.matcher.archetypes), 12)

    def test_every_archetype_has_eight_dimensions(self):
        for archetype in self.matcher.archetypes:
            self.assertEqual(
                set(archetype["prototype"]),
                set(self.matcher.dimensions),
            )

    def test_match_returns_primary_and_secondary(self):
        result = self.matcher.match(self.make_feature_vector())

        self.assertIsNotNone(result["primary_archetype"])
        self.assertIsNotNone(result["secondary_archetype"])
        self.assertEqual(len(result["matches"]), 2)

    def test_curious_goblin_is_top_match_for_its_prototype(self):
        curious_goblin = next(
            item for item in self.matcher.archetypes
            if item["id"] == "curious_goblin"
        )

        result = self.matcher.match(curious_goblin["prototype"])

        self.assertEqual(
            result["primary_archetype"]["id"],
            "curious_goblin",
        )
        self.assertAlmostEqual(
            result["primary_archetype"]["similarity_score"],
            100.0,
            places=2,
        )

    def test_null_dimensions_are_ignored(self):
        vector = self.make_feature_vector()
        vector["social_energy"] = None
        vector["reflection"] = None

        result = self.matcher.match(vector)

        self.assertEqual(
            len(result["metadata"]["compared_dimensions"]),
            6,
        )

    def test_too_few_dimensions_are_rejected(self):
        vector = {
            "social_energy": 50,
            "curiosity": 70,
            "creativity": None,
            "spontaneity": None,
            "reflection": None,
            "analytical_style": None,
            "expressiveness": None,
            "exploration": None,
        }

        with self.assertRaises(FeatureVectorError):
            self.matcher.match(vector)

    def test_out_of_range_score_is_rejected(self):
        vector = self.make_feature_vector()
        vector["curiosity"] = 150

        with self.assertRaises(FeatureVectorError):
            self.matcher.match(vector)

    def test_unknown_dimension_is_rejected(self):
        vector = self.make_feature_vector()
        vector["confidence"] = 80

        with self.assertRaises(FeatureVectorError):
            self.matcher.match(vector)

    def test_invalid_top_k_is_rejected(self):
        with self.assertRaises(FeatureVectorError):
            self.matcher.match(self.make_feature_vector(), top_k=20)


if __name__ == "__main__":
    unittest.main()
