package com.lore.backend.controller;

import com.lore.backend.dto.request.QuestionnaireSubmissionRequest;
import com.lore.backend.dto.response.SubmissionDetailsResponse;
import com.lore.backend.service.QuestionnaireSubmissionService;

import jakarta.validation.Valid;

import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/lore/submissions")
public class QuestionnaireSubmissionController {

    private final QuestionnaireSubmissionService submissionService;

    public QuestionnaireSubmissionController(
            QuestionnaireSubmissionService submissionService) {
        this.submissionService = submissionService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> submit(
            @AuthenticationPrincipal String email,
            @Valid @RequestBody QuestionnaireSubmissionRequest request) {

        Long submissionId =
                submissionService.submitQuestionnaire(email, request);

        return Map.of(
                "message", "Questionnaire submitted successfully!",
                "submissionId", submissionId
        );
    }
    @GetMapping("/submissions/{id}")
    public SubmissionDetailsResponse getSubmission(@PathVariable Long id) {
        return submissionService.getSubmissionDetails(id);
    }
}