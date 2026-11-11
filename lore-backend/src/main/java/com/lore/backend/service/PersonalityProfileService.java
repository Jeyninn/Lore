package com.lore.backend.service;

import com.lore.backend.entity.PersonalityProfile;
import com.lore.backend.entity.QuestionnaireSubmission;
import com.lore.backend.repository.PersonalityProfileRepository;
import com.lore.backend.repository.QuestionnaireSubmissionRepository;
import tools.jackson.databind.JsonNode;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import java.time.LocalDateTime;

@Service
public class PersonalityProfileService {

    private final PersonalityProfileRepository profileRepository;
    private final QuestionnaireSubmissionRepository submissionRepository;
    private final JsonMapper jsonMapper;

    public PersonalityProfileService(
            PersonalityProfileRepository profileRepository,
            QuestionnaireSubmissionRepository submissionRepository) {

        this.profileRepository = profileRepository;
        this.submissionRepository = submissionRepository;
        this.jsonMapper = JsonMapper.builder().build();
    }


    public JsonNode getLatestProfile(String email) {

        PersonalityProfile profile =
                profileRepository
                        .findFirstBySubmission_User_EmailOrderByCreatedAtDesc(email)
                        .orElseThrow(() ->
                                new RuntimeException("No generated profile found"));

        try {
            return jsonMapper.readTree(profile.getGeneratedResult());
        } catch (Exception e) {
            throw new RuntimeException("Could not read generated profile", e);
        }
    }

    @Transactional
    public PersonalityProfile saveProfile(Long submissionId, JsonNode result) {

        QuestionnaireSubmission submission =
                submissionRepository.findById(submissionId)
                        .orElseThrow(() ->
                                new RuntimeException("Submission not found"));

        try {
            PersonalityProfile profile =
                    profileRepository.findBySubmission_Id(submissionId)
                            .orElseGet(PersonalityProfile::new);

            profile.setSubmission(submission);
            profile.setGeneratedResult(
                    jsonMapper.writeValueAsString(result));

            if (profile.getCreatedAt() == null) {
                profile.setCreatedAt(LocalDateTime.now());
            }

            return profileRepository.save(profile);

        } catch (Exception e) {
            throw new RuntimeException(
                    "Could not save generated profile", e);
        }
    }
}