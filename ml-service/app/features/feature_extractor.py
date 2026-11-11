
"""
LORE.exe - Deterministic Questionnaire Feature Extractor

Loads a versioned questionnaire specification and converts validated
answers into product-specific feature scores and preference tags.

This module does not perform psychological assessment.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping


class QuestionnaireError(Exception):
    """Base exception for questionnaire processing errors."""


class SpecificationError(QuestionnaireError):
    """Raised when the questionnaire specification is invalid."""


class SubmissionValidationError(QuestionnaireError):
    """Raised when submitted answers do not match the specification."""


def default_spec_path() -> Path:
    """
    Resolve the shared specification from the repository root.

    Expected layout:
        LORE.exe/
            lore-spec/questionnaire.v1.json
            ml-service/app/features/feature_extractor.py
    """
    repository_root = Path(__file__).resolve().parents[3]
    return repository_root / "lore-spec" / "questionnaire.v1.json"


class QuestionnaireFeatureExtractor:
    def __init__(self, spec_path: Path | str | None = None) -> None:
        self.spec_path = Path(spec_path) if spec_path else default_spec_path()
        self.spec = self._load_spec()

        self.version = self.spec["version"]
        self.scoring_config = self.spec["scoring"]
        self.dimensions = self.scoring_config["dimensions"]

        self.questions: dict[str, dict[str, Any]] = {}
        self.options: dict[str, dict[str, Any]] = {}

        self._build_indexes()

    def _load_spec(self) -> dict[str, Any]:
        if not self.spec_path.is_file():
            raise SpecificationError(
                f"Questionnaire specification not found: {self.spec_path}"
            )

        try:
            with self.spec_path.open("r", encoding="utf-8") as file:
                spec = json.load(file)
        except (json.JSONDecodeError, OSError) as exc:
            raise SpecificationError(
                f"Could not read questionnaire specification: {exc}"
            ) from exc

        if not isinstance(spec, dict):
            raise SpecificationError("Specification root must be a JSON object.")

        required_fields = {"spec_id", "version", "scoring", "questions"}
        missing = required_fields - spec.keys()

        if missing:
            raise SpecificationError(
                f"Specification is missing fields: {sorted(missing)}"
            )

        if not isinstance(spec["version"], int) or spec["version"] < 1:
            raise SpecificationError("Specification version must be a positive integer.")

        if not isinstance(spec["questions"], list) or not spec["questions"]:
            raise SpecificationError("Specification must contain questions.")

        return spec

    def _build_indexes(self) -> None:
        seen_option_ids: set[str] = set()

        for question in self.spec["questions"]:
            question_id = question.get("id")

            if not isinstance(question_id, str) or not question_id:
                raise SpecificationError("Every question needs a non-empty ID.")

            if question_id in self.questions:
                raise SpecificationError(f"Duplicate question ID: {question_id}")

            question_type = question.get("type")
            if question_type not in {"single_select", "multi_select"}:
                raise SpecificationError(
                    f"Unsupported question type for {question_id}: {question_type}"
                )

            question_options = question.get("options")
            if not isinstance(question_options, list) or not question_options:
                raise SpecificationError(
                    f"Question {question_id} must contain options."
                )

            self.questions[question_id] = question

            for option in question_options:
                option_id = option.get("id")

                if not isinstance(option_id, str) or not option_id:
                    raise SpecificationError(
                        f"Question {question_id} has an option without an ID."
                    )

                if option_id in seen_option_ids:
                    raise SpecificationError(f"Duplicate option ID: {option_id}")

                weights = option.get("weights", {})
                if not isinstance(weights, dict):
                    raise SpecificationError(
                        f"Weights for option {option_id} must be an object."
                    )

                for dimension, score in weights.items():
                    if dimension not in self.dimensions:
                        raise SpecificationError(
                            f"Unknown scoring dimension '{dimension}' "
                            f"in option {option_id}."
                        )

                    if (
                        isinstance(score, bool)
                        or not isinstance(score, (int, float))
                        or not math.isfinite(score)
                        or not 0 <= score <= 4
                    ):
                        raise SpecificationError(
                            f"Weight for {option_id}/{dimension} must be between 0 and 4."
                        )

                tags = option.get("tags", [])
                if not isinstance(tags, list) or not all(
                    isinstance(tag, str) and tag.strip() for tag in tags
                ):
                    raise SpecificationError(
                        f"Tags for option {option_id} must be non-empty strings."
                    )

                self.options[option_id] = {
                    **option,
                    "_question_id": question_id,
                }
                seen_option_ids.add(option_id)

    def extract(self, submission: Mapping[str, Any]) -> dict[str, Any]:
        """
        Validate a questionnaire submission and calculate its features.

        Expected input:
        {
            "questionnaire_version": 1,
            "responses": [
                {"question_id": "q01", "option_ids": ["q01_a"]},
                ...
            ]
        }
        """
        if not isinstance(submission, Mapping):
            raise SubmissionValidationError("Submission must be a JSON object.")

        submitted_version = submission.get("questionnaire_version")
        if submitted_version != self.version:
            raise SubmissionValidationError(
                f"Questionnaire version mismatch. Expected {self.version}, "
                f"received {submitted_version}."
            )

        responses = submission.get("responses")
        if not isinstance(responses, list):
            raise SubmissionValidationError("'responses' must be a list.")

        selected_options = self._validate_responses(responses)

        dimension_values: dict[str, list[float]] = defaultdict(list)
        preference_tags: set[str] = set()

        for option in selected_options:
            for dimension, value in option.get("weights", {}).items():
                dimension_values[dimension].append(float(value))

            preference_tags.update(option.get("tags", []))

        feature_scores: dict[str, int | None] = {}

        for dimension in self.dimensions:
            values = dimension_values.get(dimension, [])

            if not values:
                feature_scores[dimension] = None
                continue

            mean_score = sum(values) / len(values)
            normalized_score = (
                (mean_score - self.scoring_config["input_min"])
                / (
                    self.scoring_config["input_max"]
                    - self.scoring_config["input_min"]
                )
            ) * (
                self.scoring_config["output_max"]
                - self.scoring_config["output_min"]
            ) + self.scoring_config["output_min"]

            # Explicit half-up rounding avoids Python's banker's rounding.
            feature_scores[dimension] = math.floor(normalized_score + 0.5)

        return {
            "questionnaire_version": self.version,
            "feature_scores": feature_scores,
            "preference_tags": sorted(preference_tags),
            "metadata": {
                "answered_questions": len(responses),
                "total_questions": len(self.questions),
                "scoring_method": self.scoring_config["method"],
                "score_interpretation": (
                    "Entertainment-oriented response-pattern scores; "
                    "not validated psychological measurements."
                ),
            },
        }

    def _validate_responses(
        self, responses: list[Any]
    ) -> list[dict[str, Any]]:
        answered_question_ids: set[str] = set()
        selected_options: list[dict[str, Any]] = []

        for response in responses:
            if not isinstance(response, Mapping):
                raise SubmissionValidationError(
                    "Each response must be a JSON object."
                )

            question_id = response.get("question_id")
            option_ids = response.get("option_ids")

            if question_id not in self.questions:
                raise SubmissionValidationError(
                    f"Unknown question ID: {question_id}"
                )

            if question_id in answered_question_ids:
                raise SubmissionValidationError(
                    f"Duplicate response for question: {question_id}"
                )

            if not isinstance(option_ids, list) or not option_ids:
                raise SubmissionValidationError(
                    f"Question {question_id} must have at least one selected option."
                )

            if not all(isinstance(option_id, str) for option_id in option_ids):
                raise SubmissionValidationError(
                f"Option IDs for question {question_id} must be strings."
                )

            if len(option_ids) != len(set(option_ids)):
                raise SubmissionValidationError(
                    f"Duplicate selected options in question {question_id}."
                )

            question = self.questions[question_id]
            question_type = question["type"]

            if question_type == "single_select" and len(option_ids) != 1:
                raise SubmissionValidationError(
                    f"Question {question_id} requires exactly one option."
                )

            if question_type == "multi_select":
                minimum = question.get("min_selections", 1)
                maximum = question.get("max_selections", len(question["options"]))

                if not minimum <= len(option_ids) <= maximum:
                    raise SubmissionValidationError(
                        f"Question {question_id} requires between "
                        f"{minimum} and {maximum} selections."
                    )

            valid_option_ids = {
                option["id"] for option in question["options"]
            }

            for option_id in option_ids:
                if option_id not in valid_option_ids:
                    raise SubmissionValidationError(
                        f"Option {option_id} does not belong to question {question_id}."
                    )

                selected_options.append(self.options[option_id])

            answered_question_ids.add(question_id)

        required_question_ids = {
            question_id
            for question_id, question in self.questions.items()
            if question.get("required", False)
        }

        missing_questions = required_question_ids - answered_question_ids

        if missing_questions:
            raise SubmissionValidationError(
                "Missing required questions: "
                + ", ".join(sorted(missing_questions))
            )

        minimum_answers = self.spec["completion_rules"].get(
            "required_question_count", len(required_question_ids)
        )

        if len(answered_question_ids) < minimum_answers:
            raise SubmissionValidationError(
                f"At least {minimum_answers} questions must be answered."
            )

        return selected_options
