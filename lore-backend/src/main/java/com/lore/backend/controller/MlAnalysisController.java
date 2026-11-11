package com.lore.backend.controller;

import com.lore.backend.service.MlAnalysisService;
import com.lore.backend.service.PersonalityProfileService;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import com.lore.backend.dto.request.WritingAnalysisRequest;
import tools.jackson.databind.JsonNode;

@RestController
@RequestMapping("/api/v1/lore")
public class MlAnalysisController {

    private final MlAnalysisService mlAnalysisService;
    private final PersonalityProfileService profileService;

    public MlAnalysisController(
            MlAnalysisService mlAnalysisService,
            PersonalityProfileService profileService) {

        this.mlAnalysisService = mlAnalysisService;
        this.profileService = profileService;
    }
    @GetMapping("/profile")
    public JsonNode getMyProfile(
            @AuthenticationPrincipal String email) {

        return profileService.getLatestProfile(email);
    }


    @PostMapping("/submissions/{id}/analyze")
    public JsonNode analyzeSubmission(
            @PathVariable Long id,
            @AuthenticationPrincipal String email,
            @RequestBody(required = false) WritingAnalysisRequest writingRequest) {

        String writingSample = null;
        boolean consent = false;

        if (writingRequest != null) {
            writingSample = writingRequest.getWritingSample();
            consent = writingRequest.isConsentToAnalyzeWriting();
        }

        JsonNode result = mlAnalysisService.analyzeSubmission(
                id, email, writingSample, consent
        );



        profileService.saveProfile(id, result);

        return result;
    }

}