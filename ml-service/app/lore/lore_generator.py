
from typing import Any


class LoreGenerationError(ValueError):
    """Raised when lore generation receives invalid input."""


class LoreGenerator:
    """Generates a deterministic digital identity from user features."""

    DIMENSION_DESCRIPTIONS = {
        "social_energy": {
            "high": "You draw energy from people, shared experiences, and lively interactions.",
            "low": "You value your own space and prefer meaningful interactions.",
            "balanced": "You balance social interactions with time for yourself.",
        },
        "curiosity": {
            "high": "Your curiosity constantly pulls you toward new ideas and unexplored topics.",
            "low": "You prefer depth and familiarity over constantly chasing something new.",
            "balanced": "You balance familiar interests with new discoveries.",
        },
        "creativity": {
            "high": "Your imagination is one of your strongest defining features.",
            "low": "You tend to approach things practically and prefer clear structures.",
            "balanced": "You combine practical thinking with creative perspectives.",
        },
        "spontaneity": {
            "high": "You enjoy unexpected plans and unpredictable moments.",
            "low": "You prefer having a plan and knowing what comes next.",
            "balanced": "You appreciate a plan but leave room for surprises.",
        },
        "reflection": {
            "high": "You spend time reflecting on experiences, ideas, and their meaning.",
            "low": "You focus on the present and prefer action over overthinking.",
            "balanced": "You know when to reflect and when to move forward.",
        },
        "analytical_style": {
            "high": "You naturally break things down, notice patterns, and look for logical explanations.",
            "low": "You often rely on intuition and the bigger picture.",
            "balanced": "You combine logical reasoning with intuitive thinking.",
        },
        "expressiveness": {
            "high": "You express your thoughts openly and bring personality into conversations.",
            "low": "You prefer expressing yourself selectively.",
            "balanced": "You express yourself when it matters and value both openness and privacy.",
        },
        "exploration": {
            "high": "You enjoy discovering new experiences, interests, and perspectives.",
            "low": "You prefer developing existing interests and keeping things familiar.",
            "balanced": "You enjoy exploring while maintaining your favourite routines.",
        },
    }

    def _level(self, score: int | float | None) -> str | None:
        if score is None:
            return None

        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise LoreGenerationError("Feature scores must be numeric or None.")

        if not 0 <= score <= 100:
            raise LoreGenerationError(
                "Feature scores must be between 0 and 100."
            )

        if score >= 65:
            return "high"
        if score <= 35:
            return "low"
        return "balanced"

    def _describe_features(
        self,
        feature_scores: dict[str, int | None],
    ) -> list[str]:
        descriptions = []

        for dimension, score in feature_scores.items():
            if dimension not in self.DIMENSION_DESCRIPTIONS:
                continue

            level = self._level(score)

            if level is not None:
                descriptions.append(
                    self.DIMENSION_DESCRIPTIONS[dimension][level]
                )

        return descriptions

    def _clean_tags(self, preference_tags: list[str]) -> list[str]:
        cleaned = set()

        for tag in preference_tags:
            if not isinstance(tag, str):
                continue

            normalized = " ".join(
                tag.strip().replace("_", " ").split()
            )

            if normalized:
                cleaned.add(normalized.title())

        return sorted(cleaned)

    def _generate_visual_identity(
        self,
        primary: dict,
        secondary: dict | None,
        preference_tags: list[str],
    ) -> dict:
        primary_visual = primary.get("visual", {})

        secondary_visual = (
            secondary.get("visual", {})
            if isinstance(secondary, dict)
            else {}
        )

        primary_color = primary_visual.get(
            "primary_color", "#A855F7"
        )
        secondary_color = primary_visual.get(
            "secondary_color", "#C4B5FD"
        )
        accent_color = secondary_visual.get(
            "primary_color", secondary_color
        )

        motifs = list(primary_visual.get("motifs", []))

        for motif in secondary_visual.get("motifs", []):
            if motif not in motifs:
                motifs.append(motif)

        return {
            "color_palette": {
                "primary": primary_color,
                "secondary": secondary_color,
                "accent": accent_color,
                "background": "#0B0614",
            },
            "aesthetic": primary_visual.get(
                "aesthetic", "digital_mystery"
            ),
            "motifs": motifs[:6],
            "visual_tags": preference_tags[:6],
            "style": "cyber_identity",
        }

    def generate(
        self,
        archetype_result: dict[str, Any],
        feature_scores: dict[str, int | None],
        preference_tags: list[str] | None = None,
        writing_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        # 1. Validate inputs
        if not isinstance(archetype_result, dict):
            raise LoreGenerationError(
                "Archetype result must be a dictionary."
            )

        primary = archetype_result.get("primary_archetype")
        secondary = archetype_result.get("secondary_archetype")

        if not isinstance(primary, dict) or not primary.get("name"):
            raise LoreGenerationError(
                "A valid primary archetype is required."
            )

        if secondary is not None and not isinstance(secondary, dict):
            raise LoreGenerationError(
                "Secondary archetype must be a dictionary or None."
            )

        if not isinstance(feature_scores, dict):
            raise LoreGenerationError(
                "Feature scores must be a dictionary."
            )

        for dimension, score in feature_scores.items():
            if score is not None:
                if (
                    isinstance(score, bool)
                    or not isinstance(score, (int, float))
                    or not 0 <= score <= 100
                ):
                    raise LoreGenerationError(
                        f"Invalid feature score for {dimension}."
                    )

        if preference_tags is not None and not isinstance(
            preference_tags, list
        ):
            raise LoreGenerationError(
                "Preference tags must be a list."
            )

        if writing_analysis is not None and not isinstance(
            writing_analysis, dict
        ):
            raise LoreGenerationError(
                "Writing analysis must be a dictionary or None."
            )

        # 2. Prepare archetypes and preferences
        primary_name = primary["name"]
        secondary_name = (
            secondary.get("name") if secondary else None
        )

        tags = self._clean_tags(preference_tags or [])
        descriptions = self._describe_features(feature_scores)

        # 3. Extract writing themes.
        # Support both the original "name" field and the newer "theme" field.
        writing_themes = []

        if writing_analysis:
            themes = writing_analysis.get("themes", [])

            if isinstance(themes, list):
                for item in themes:
                    if not isinstance(item, dict):
                        continue

                    theme = item.get("theme") or item.get("name")

                    if isinstance(theme, str) and theme.strip():
                        writing_themes.append(theme.strip())

        # 4. Generate identity title
        if secondary_name:
            identity_title = (
                f"The {primary_name} × {secondary_name}"
                if not primary_name.lower().startswith("the ")
                else f"{primary_name} × {secondary_name}"
            )
        else:
            identity_title = (
                primary_name
                if primary_name.lower().startswith("the ")
                else f"The {primary_name}"
            )

        # 5. Generate visual identity
        visual_identity = self._generate_visual_identity(
            primary=primary,
            secondary=secondary,
            preference_tags=tags,
        )

        # 6. Generate narrative
        narrative_parts = [
            f"You are {identity_title}.",
        ]

        if primary.get("description"):
            narrative_parts.append(primary["description"])

        if secondary_name:
            narrative_parts.append(
                f"Your secondary archetype, {secondary_name}, "
                "adds another layer to your digital identity."
            )

        if descriptions:
            narrative_parts.append(" ".join(descriptions[:3]))

        if writing_themes:
            formatted_themes = ", ".join(
                theme.replace("_", " ")
                for theme in writing_themes[:3]
            )
            narrative_parts.append(
                f"Your writing reflects themes of {formatted_themes}."
            )

        narrative = " ".join(narrative_parts)

        # 7. Generate communication style
        communication_style = []

        for dimension, high_text, low_text, balanced_text in [
            (
                "expressiveness",
                "Expressive and personality-driven",
                "Reserved and selective",
                "Balanced and adaptable",
            ),
            (
                "social_energy",
                "Socially energetic",
                "Thoughtful and independent",
                "Comfortable in different social settings",
            ),
            (
                "analytical_style",
                "Logic-oriented",
                "Intuitive and instinctive",
                "A blend of logic and intuition",
            ),
        ]:
            score = feature_scores.get(dimension)

            if score is None:
                continue

            level = self._level(score)

            if level == "high":
                communication_style.append(high_text)
            elif level == "low":
                communication_style.append(low_text)
            else:
                communication_style.append(balanced_text)

        # 8. Generate creativity identity
        creativity_score = feature_scores.get("creativity")

        if creativity_score is None:
            creativity_identity = (
                "Your creative identity is still an open chapter."
            )
        elif creativity_score >= 65:
            creativity_identity = (
                "An imagination-first mind that enjoys "
                "creating new ideas and possibilities."
            )
        elif creativity_score <= 35:
            creativity_identity = (
                "A practical mind that prefers clarity and structure."
            )
        else:
            creativity_identity = (
                "A balance of imagination and practical thinking."
            )

        # 9. Generate aesthetic identity
        aesthetic_identity = (
            tags if tags else [
                "Your aesthetic is still being discovered"
            ]
        )

        # 10. Generate signature quote
        signature_quote = (
            primary.get("tagline")
            or f"Somewhere between chaos and curiosity — {primary_name}."
        )

        # 11. Generate recommendations
        recommendations = []

        if tags:
            recommendations.append(
                "Explore content connected to your interests: "
                + ", ".join(tags[:4])
                + "."
            )

        if feature_scores.get("curiosity") is not None:
            if feature_scores["curiosity"] >= 65:
                recommendations.append(
                    "Explore an unfamiliar topic or learn a new skill."
                )

        if feature_scores.get("creativity") is not None:
            if feature_scores["creativity"] >= 65:
                recommendations.append(
                    "Try a creative project that lets your imagination lead."
                )

        if feature_scores.get("exploration") is not None:
            if feature_scores["exploration"] >= 65:
                recommendations.append(
                    "Discover a new community, experience, or interest."
                )

        if not recommendations:
            recommendations.append(
                "Keep exploring your interests and discovering "
                "new sides of your digital identity."
            )

        # 12. Return complete lore profile
        return {
            "identity_title": identity_title,
            "primary_archetype": primary,
            "secondary_archetype": secondary,
            "narrative": narrative,
            "feature_descriptions": descriptions,
            "communication_style": communication_style,
            "creativity_identity": creativity_identity,
            "aesthetic_identity": aesthetic_identity,
            "signature_quote": signature_quote,
            "recommendations": recommendations,
            "writing_themes": writing_themes,
            "visual_identity": visual_identity,
            "metadata": {
                "generation_method": "deterministic_rule_based",
                "writing_sample_used": bool(writing_themes),
                "version": 1,
            },
        }
