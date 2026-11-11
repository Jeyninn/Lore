
from typing import Any
from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    question_id: str
    option_ids: list[str] = Field(min_length=1)


class AnalyzeRequest(BaseModel):
    questionnaire_version: int = Field(gt=0)
    responses: list[QuestionResponse]

    writing_sample: str | None = None
    consent_to_analyze_writing: bool = False


class ArchetypeResult(BaseModel):
    id: str
    name: str
    tagline: str
    description: str
    similarity_score: float
    visual: dict[str, Any]
    keywords: list[str]


class AnalyzeResponse(BaseModel):
    questionnaire_version: int
    feature_scores: dict[str, int | None]
    preference_tags: list[str]
    primary_archetype: ArchetypeResult
    secondary_archetype: ArchetypeResult | None
    matches: list[ArchetypeResult]
    compared_dimensions: list[str]
    matching_method: str
    writing_analysis: dict[str, Any] | None = None
    lore_profile: dict[str, Any]
