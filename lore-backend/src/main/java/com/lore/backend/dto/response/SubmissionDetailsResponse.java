package com.lore.backend.dto.response;

import java.util.List;

public record SubmissionDetailsResponse(
        Long submissionId,
        Integer questionnaireVersion,
        int answerCount,
        List<SubmissionAnswerResponse> answers
) {}