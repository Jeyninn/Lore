
"""
LORE.exe - Archetype Matching Engine

Ranks manually designed archetype prototypes against a user's
questionnaire feature scores using weighted cosine similarity.

Similarity is a ranking measure, not a probability or diagnosis.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping


class ArchetypeError(Exception):
    """Base exception for archetype matching."""


class ArchetypeCatalogError(ArchetypeError):
    """Raised when the archetype catalogue is invalid."""


class FeatureVectorError(ArchetypeError):
    """Raised when the feature vector is invalid."""


def default_catalog_path() -> Path:
    """Resolve the catalogue relative to the repository root."""
    repository_root = Path(__file__).resolve().parents[3]
    return repository_root / "ml-service" / "app" / "data" / "archetypes.json"


class ArchetypeMatcher:
    def __init__(self, catalog_path: Path | str | None = None) -> None:
        self.catalog_path = (
            Path(catalog_path) if catalog_path else default_catalog_path()
        )
        self.catalog = self._load_catalog()

        self.version = self.catalog["version"]
        self.feature_schema_version = self.catalog["feature_schema_version"]
        self.score_range = self.catalog["score_range"]
        self.matching_config = self.catalog["matching"]
        self.archetypes = self.catalog["archetypes"]

        self.dimension_weights = self.matching_config["dimension_weights"]
        self.dimensions = list(self.dimension_weights.keys())

        self._validate_catalog()

    def _load_catalog(self) -> dict[str, Any]:
        if not self.catalog_path.is_file():
            raise ArchetypeCatalogError(
                f"Archetype catalogue not found: {self.catalog_path}"
            )

        try:
            with self.catalog_path.open("r", encoding="utf-8") as file:
                catalog = json.load(file)
        except (json.JSONDecodeError, OSError) as exc:
            raise ArchetypeCatalogError(
                f"Could not read archetype catalogue: {exc}"
            ) from exc

        if not isinstance(catalog, dict):
            raise ArchetypeCatalogError(
                "Archetype catalogue root must be a JSON object."
            )

        required = {
            "catalog_id",
            "version",
            "feature_schema_version",
            "score_range",
            "matching",
            "archetypes",
        }

        missing = required - catalog.keys()
        if missing:
            raise ArchetypeCatalogError(
                f"Catalogue is missing fields: {sorted(missing)}"
            )

        return catalog

    def _validate_catalog(self) -> None:
        score_min = self.score_range.get("minimum")
        score_max = self.score_range.get("maximum")

        if (
            not isinstance(score_min, (int, float))
            or isinstance(score_min, bool)
            or not isinstance(score_max, (int, float))
            or isinstance(score_max, bool)
            or score_min >= score_max
        ):
            raise ArchetypeCatalogError("Invalid score range.")

        if not self.dimensions:
            raise ArchetypeCatalogError("No feature dimensions configured.")

        for dimension, weight in self.dimension_weights.items():
            if (
                not isinstance(weight, (int, float))
                or isinstance(weight, bool)
                or not math.isfinite(weight)
                or weight <= 0
            ):
                raise ArchetypeCatalogError(
                    f"Weight for {dimension} must be a positive number."
                )

        top_k = self.matching_config.get("top_k")
        minimum_dimensions = self.matching_config.get(
            "minimum_comparable_dimensions"
        )

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k < 1
            or top_k > len(self.archetypes)
        ):
            raise ArchetypeCatalogError("Invalid top_k configuration.")

        if (
            not isinstance(minimum_dimensions, int)
            or isinstance(minimum_dimensions, bool)
            or not 1 <= minimum_dimensions <= len(self.dimensions)
        ):
            raise ArchetypeCatalogError(
                "Invalid minimum_comparable_dimensions configuration."
            )

        if not isinstance(self.archetypes, list) or not self.archetypes:
            raise ArchetypeCatalogError("No archetypes are configured.")

        seen_ids: set[str] = set()

        for archetype in self.archetypes:
            archetype_id = archetype.get("id")

            if not isinstance(archetype_id, str) or not archetype_id:
                raise ArchetypeCatalogError(
                    "Every archetype must have a non-empty ID."
                )

            if archetype_id in seen_ids:
                raise ArchetypeCatalogError(
                    f"Duplicate archetype ID: {archetype_id}"
                )

            seen_ids.add(archetype_id)

            prototype = archetype.get("prototype")
            if not isinstance(prototype, dict):
                raise ArchetypeCatalogError(
                    f"Missing prototype for {archetype_id}."
                )

            if set(prototype) != set(self.dimensions):
                raise ArchetypeCatalogError(
                    f"Prototype dimensions do not match the feature schema "
                    f"for {archetype_id}."
                )

            for dimension, value in prototype.items():
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or not score_min <= value <= score_max
                ):
                    raise ArchetypeCatalogError(
                        f"Invalid prototype value for "
                        f"{archetype_id}/{dimension}."
                    )

    def _validate_feature_vector(
        self, feature_scores: Mapping[str, Any]
    ) -> dict[str, float | None]:
        if not isinstance(feature_scores, Mapping):
            raise FeatureVectorError("Feature scores must be an object.")

        unknown_dimensions = set(feature_scores) - set(self.dimensions)
        if unknown_dimensions:
            raise FeatureVectorError(
                f"Unknown feature dimensions: {sorted(unknown_dimensions)}"
            )

        minimum = self.score_range["minimum"]
        maximum = self.score_range["maximum"]

        validated: dict[str, float | None] = {}

        for dimension in self.dimensions:
            value = feature_scores.get(dimension)

            if value is None:
                validated[dimension] = None
                continue

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not minimum <= value <= maximum
            ):
                raise FeatureVectorError(
                    f"Invalid score for {dimension}: {value}"
                )

            validated[dimension] = float(value)

        available = sum(value is not None for value in validated.values())
        required = self.matching_config["minimum_comparable_dimensions"]

        if available < required:
            raise FeatureVectorError(
                f"At least {required} feature dimensions are required; "
                f"received {available}."
            )

        return validated

    def _weighted_cosine_similarity(
        self,
        user_vector: Mapping[str, float | None],
        prototype: Mapping[str, float],
    ) -> float:
        """
        Calculate cosine similarity over available dimensions only.

        Multiplying each component by sqrt(weight) implements weighted
        cosine similarity while preserving the standard cosine formula.
        """
        dimensions = [
            dimension
            for dimension in self.dimensions
            if user_vector[dimension] is not None
        ]

        dot_product = 0.0
        user_norm_squared = 0.0
        prototype_norm_squared = 0.0

        for dimension in dimensions:
            weight = float(self.dimension_weights[dimension])
            root_weight = math.sqrt(weight)

            user_value = float(user_vector[dimension]) * root_weight
            prototype_value = float(prototype[dimension]) * root_weight

            dot_product += user_value * prototype_value
            user_norm_squared += user_value**2
            prototype_norm_squared += prototype_value**2

        denominator = math.sqrt(user_norm_squared) * math.sqrt(
            prototype_norm_squared
        )

        if denominator == 0:
            return 0.0

        similarity = dot_product / denominator

        # Guard against floating-point drift.
        return max(0.0, min(1.0, similarity))

    def match(
        self,
        feature_scores: Mapping[str, Any],
        top_k: int | None = None,
    ) -> dict[str, Any]:
        user_vector = self._validate_feature_vector(feature_scores)

        limit = top_k if top_k is not None else self.matching_config["top_k"]

        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not 1 <= limit <= len(self.archetypes)
        ):
            raise FeatureVectorError(
                f"top_k must be between 1 and {len(self.archetypes)}."
            )

        ranked: list[dict[str, Any]] = []

        for archetype in self.archetypes:
            similarity = self._weighted_cosine_similarity(
                user_vector,
                archetype["prototype"],
            )

            ranked.append({
                "id": archetype["id"],
                "name": archetype["name"],
                "tagline": archetype["tagline"],
                "description": archetype["description"],
                "similarity_score": round(similarity * 100, 2),
                "visual": archetype["visual"],
                "keywords": archetype["keywords"],
            })

        # Stable tie-breaking ensures reproducible results.
        ranked.sort(
            key=lambda item: (-item["similarity_score"], item["id"])
        )

        matches = ranked[:limit]

        return {
            "catalog_version": self.version,
            "feature_schema_version": self.feature_schema_version,
            "matching_method": self.matching_config["method"],
            "primary_archetype": matches[0],
            "secondary_archetype": matches[1] if len(matches) > 1 else None,
            "matches": matches,
            "metadata": {
                "compared_dimensions": [
                    dimension
                    for dimension, value in user_vector.items()
                    if value is not None
                ],
                "similarity_interpretation": (
                    "Relative similarity to manually designed archetype "
                    "prototypes. Not a probability or validated personality result."
                ),
            },
        }
