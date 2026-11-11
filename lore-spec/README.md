
# LORE.exe Questionnaire Specification

## Current version

- Specification ID: `lore-questionnaire`
- Version: `1`
- File: `questionnaire.v1.json`
- Locale: English
- Status: Active

## Purpose

This specification defines the questions, answer options, validation rules,
metadata tags and deterministic feature-scoring rules used by LORE.exe.

It is the canonical questionnaire contract for the application.

## Question categories

| Category | Questions | Purpose |
|---|---|---|
| Social energy | q01–q04 | Social preferences |
| Thinking style | q05–q08 | Information and decision preferences |
| Chaos and spontaneity | q09–q12 | Planning and adaptability preferences |
| Creative identity | q13–q16 | Creative and fictional preferences |
| Communication style | q17–q20 | Communication preferences |
| Digital culture | q21–q24 | Online, aesthetic and interest preferences |

## Question types

### single_select

The user must select exactly one option.

### multi_select

The user must select between the question's `min_selections`
and `max_selections` values.

## Feature dimensions

The questionnaire uses eight dimensions:

- `social_energy`
- `curiosity`
- `creativity`
- `spontaneity`
- `reflection`
- `analytical_style`
- `expressiveness`
- `exploration`

Each option can contribute a score from 0 to 4 to one or more dimensions.

An option without a `weights` field does not contribute to numerical
feature scoring. Its tags are retained as preference metadata.

## Scoring algorithm

For each dimension:

1. Collect the scores assigned by the selected answers.
2. Ignore questions that do not contribute to that dimension.
3. Calculate the arithmetic mean.
4. Convert the result to a 0–100 scale.

Formula:

score = round((mean / 4) * 100)

A dimension with no contributing answers is `null`, not zero.

The score is a product-specific response-pattern indicator.
It is not a validated personality measurement.

## Stable identifiers

Question IDs and option IDs are permanent identifiers.

Examples:

- `q01`
- `q01_a`
- `q22_g`

Never use question text or option labels as database identifiers.

If wording changes, preserve the IDs if the underlying meaning
and scoring remain the same.

If meaning or scoring changes, create a new questionnaire version.

## Writing samples

Writing samples are optional and require explicit user consent.

- Minimum length: 100 characters
- Maximum length: 2,000 characters
- Do not retain raw writing by default.
- Process samples transiently unless the user explicitly opts into storage.
- Never use writing samples to infer sensitive personal attributes.

## Versioning policy

Never silently edit an active questionnaire version after users
have submitted responses.

For a scoring or structural change:

1. Create `questionnaire.v2.json`.
2. Increment the version.
3. Preserve the previous specification.
4. Associate every submission and generated profile with its version.
5. Ensure old submissions can still be interpreted.

## Architecture

Angular obtains the questionnaire through Spring Boot APIs.

Spring Boot owns authentication, submission validation and persistence.

FastAPI performs feature extraction and archetype matching using
the same versioned specification.

The Angular application must not independently define scoring weights.
