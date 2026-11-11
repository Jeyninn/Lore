package com.lore.backend.service;

import com.lore.backend.dto.request.AnswerRequest;
import com.lore.backend.dto.request.QuestionnaireSubmissionRequest;
import com.lore.backend.dto.response.SubmissionAnswerResponse;
import com.lore.backend.dto.response.SubmissionDetailsResponse;
import com.lore.backend.entity.*;
import com.lore.backend.repository.*;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

import tools.jackson.databind.json.JsonMapper;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
public class QuestionnaireSubmissionService {

    private final UserRepository userRepository;
    private final QuestionRepository questionRepository;
    private final QuestionnaireSubmissionRepository submissionRepository;
    private final JsonMapper jsonMapper = JsonMapper.builder().build();

    public QuestionnaireSubmissionService(
            UserRepository userRepository,
            QuestionRepository questionRepository,
            QuestionnaireSubmissionRepository submissionRepository) {

        this.userRepository = userRepository;
        this.questionRepository = questionRepository;
        this.submissionRepository = submissionRepository;
    }

    @Transactional
    public Long submitQuestionnaire(
            String email,
            QuestionnaireSubmissionRequest request) {

        if (request.getQuestionnaireVersion() != 1) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST, "Unsupported questionnaire version");
        }

        if (request.getAnswers().size() != 24) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST, "All 24 questions must be answered");
        }

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "User not found"));

        QuestionnaireSubmission submission =
                new QuestionnaireSubmission();

        submission.setUser(user);
        submission.setQuestionnaireVersion(
                request.getQuestionnaireVersion());
        submission.setSubmittedAt(LocalDateTime.now());

        Set<String> answeredQuestions = new HashSet<>();

        for (AnswerRequest answer : request.getAnswers()) {

            String questionId = answer.getQuestionId();
            var selectedIds = answer.getSelectedOptionIds();

            if (!answeredQuestions.add(questionId)) {
                throw new ResponseStatusException(
                        HttpStatus.BAD_REQUEST,
                        "Duplicate question: " + questionId);
            }

            Question question = questionRepository
                    .findByQuestionCode(questionId)
                    .orElseThrow(() -> new ResponseStatusException(
                            HttpStatus.BAD_REQUEST,
                            "Invalid question: " + questionId));

            if (new HashSet<>(selectedIds).size() != selectedIds.size()) {
                throw new ResponseStatusException(
                        HttpStatus.BAD_REQUEST,
                        "Duplicate options selected for " + questionId);
            }

            boolean isMulti =
                    "multi_select".equals(question.getQuestionType());

            int min = isMulti
                    ? question.getMinSelections() : 1;

            int max = isMulti
                    ? question.getMaxSelections() : 1;

            if (selectedIds.size() < min || selectedIds.size() > max) {
                throw new ResponseStatusException(
                        HttpStatus.BAD_REQUEST,
                        "Invalid number of selections for " + questionId);
            }

            Set<String> validOptions = new HashSet<>();

            for (QuestionOption option : question.getOptions()) {
                validOptions.add(option.getOptionCode());
            }

            if (!validOptions.containsAll(selectedIds)) {
                throw new ResponseStatusException(
                        HttpStatus.BAD_REQUEST,
                        "Invalid option for " + questionId);
            }

            QuestionnaireAnswer savedAnswer =
                    new QuestionnaireAnswer();

            savedAnswer.setSubmission(submission);
            savedAnswer.setQuestion(question);

            try {
                savedAnswer.setSelectedOptionCodes(
                        jsonMapper.writeValueAsString(selectedIds));
            } catch (Exception e) {
                throw new RuntimeException(
                        "Could not serialize selected options", e);
            }

            submission.getAnswers().add(savedAnswer);
        }

        if (answeredQuestions.size() != 24) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "All questions must be answered");
        }

        return submissionRepository.save(submission).getId();
    }

    public SubmissionDetailsResponse getSubmissionDetails(Long id) {

        QuestionnaireSubmission submission =
                submissionRepository.findWithAnswersById(id)
                        .orElseThrow(() ->
                                new RuntimeException("Submission not found"));

        List<SubmissionAnswerResponse> answers =
                submission.getAnswers().stream()
                        .map(answer -> new SubmissionAnswerResponse(
                                answer.getQuestion().getQuestionCode(),
                                answer.getSelectedOptionCodes()
                        ))
                        .toList();

        return new SubmissionDetailsResponse(
                submission.getId(),
                submission.getQuestionnaireVersion(),
                answers.size(),
                answers
        );
    }
}