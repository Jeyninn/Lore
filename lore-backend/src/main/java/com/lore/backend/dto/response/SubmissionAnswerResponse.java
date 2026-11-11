package com.lore.backend.dto.response;

public record SubmissionAnswerResponse(
        String questionCode,
        String selectedOptionCodes
) {}