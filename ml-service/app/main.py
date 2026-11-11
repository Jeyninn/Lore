
from fastapi import FastAPI, HTTPException

from app.api.schemas import AnalyzeRequest, AnalyzeResponse

from app.features.feature_extractor import (
    QuestionnaireError,
    QuestionnaireFeatureExtractor,
)

from app.engine.archetype_matcher import (
    ArchetypeError,
    ArchetypeMatcher,
)

from app.semantic.semantic_analyzer import (
    SemanticAnalyzer,
    SemanticAnalysisError,
)

from app.lore.lore_generator import (
    LoreGenerator,
    LoreGenerationError,
)


app = FastAPI(
    title="LORE.exe ML Service",
    description="Questionnaire analysis and digital archetype matching API.",
    version="1.0.0",
)


# Initialize engines once.
feature_extractor = QuestionnaireFeatureExtractor()
archetype_matcher = ArchetypeMatcher()
lore_generator = LoreGenerator()

# Load the semantic model only when writing analysis is requested.
semantic_analyzer = None


def get_semantic_analyzer():
    global semantic_analyzer

    if semantic_analyzer is None:
        semantic_analyzer = SemanticAnalyzer()

    return semantic_analyzer


@app.get("/api/ml/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LORE.exe ML Service",
    }


@app.post(
    "/api/ml/v1/analyze",
    response_model=AnalyzeResponse,
)
def analyze_questionnaire(request: AnalyzeRequest):

    try:
        # STEP 1: Prepare questionnaire submission.
        submission = {
            "questionnaire_version": request.questionnaire_version,
            "responses": [
                response.model_dump()
                for response in request.responses
            ],
        }

        # STEP 2: Extract questionnaire features.
        extracted = feature_extractor.extract(submission)

        # STEP 3: Match digital archetypes.
        matched = archetype_matcher.match(
            extracted["feature_scores"]
        )

        # STEP 4: Initialize optional writing analysis.
        writing_analysis = None

        if request.writing_sample is not None:

            print("\n===== FASTAPI SEMANTIC DEBUG =====")

            print("Writing received:",
                bool(request.writing_sample))

            print("Writing length:",
                len(request.writing_sample or ""))

            print("Consent:",
                request.consent_to_analyze_writing)

            if not request.consent_to_analyze_writing:
                raise HTTPException(
                    status_code=422,
                    detail="Consent is required to analyze a writing sample."
                )

            analyzer = get_semantic_analyzer()

            print("MiniLM analyzer initialized.")

            writing_analysis = analyzer.analyze(
                request.writing_sample
            )

            

        # STEP 5: Generate personalized digital lore.
        lore_profile = lore_generator.generate(
            archetype_result=matched,
            feature_scores=extracted["feature_scores"],
            preference_tags=extracted["preference_tags"],
            writing_analysis=writing_analysis,
        )

        # STEP 6: Return the complete analysis.
        return {
            "questionnaire_version": extracted["questionnaire_version"],
            "feature_scores": extracted["feature_scores"],
            "preference_tags": extracted["preference_tags"],

            "primary_archetype": matched["primary_archetype"],
            "secondary_archetype": matched["secondary_archetype"],
            "matches": matched["matches"],

            "compared_dimensions": matched["metadata"]["compared_dimensions"],
            "matching_method": matched["matching_method"],

            "writing_analysis": writing_analysis,
            "lore_profile": lore_profile,
        }

    except QuestionnaireError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except ArchetypeError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except SemanticAnalysisError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except LoreGenerationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
