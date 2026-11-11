
package com.lore.backend.service;

import com.lore.backend.entity.QuestionnaireSubmission;
import com.lore.backend.repository.QuestionnaireSubmissionRepository;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MlAnalysisService {

    private final QuestionnaireSubmissionRepository submissionRepository;
    private final JsonMapper jsonMapper;
    private final HttpClient httpClient;
    private final String mlBaseUrl;

    public MlAnalysisService(
            QuestionnaireSubmissionRepository submissionRepository,
            @Value("${ml.service.base-url}") String mlBaseUrl) {

        this.submissionRepository = submissionRepository;
        this.mlBaseUrl = mlBaseUrl;
        this.jsonMapper = JsonMapper.builder().build();
        this.httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
    }

    public JsonNode analyzeSubmission(
            Long id,
            String email,
            String writingSample,
            boolean consentToAnalyzeWriting) {

        // 1. Retrieve questionnaire submission.
        QuestionnaireSubmission submission =
                submissionRepository.findWithAnswersById(id)
                        .orElseThrow(() ->
                                new RuntimeException("Submission not found"));

        // 2. Verify ownership.
        if (!submission.getUser().getEmail().equals(email)) {
            throw new RuntimeException(
                    "You cannot access this submission");
        }


        // 3. Convert answers into FastAPI format.
        List<Map<String, Object>> responses = new ArrayList<>();

        submission.getAnswers().forEach(answer -> {

            try {
                JsonNode selectedOptions =
                        jsonMapper.readTree(
                                answer.getSelectedOptionCodes());

                List<String> optionIds = new ArrayList<>();

                selectedOptions.forEach(option ->
                        optionIds.add(option.asString()));

                Map<String, Object> response = new HashMap<>();

                response.put(
                        "question_id",
                        answer.getQuestion().getQuestionCode());

                response.put("option_ids", optionIds);






                responses.add(response);

            } catch (Exception e) {
                throw new RuntimeException(
                        "Could not process submitted answers", e);
            }
        });

        // 4. Build request.
        Map<String, Object> requestBody = new HashMap<>();

        requestBody.put(
                "questionnaire_version",
                submission.getQuestionnaireVersion());

        requestBody.put("responses", responses);






        // Include writing only when the user explicitly consents.
        if (consentToAnalyzeWriting
                && writingSample != null
                && !writingSample.isBlank()) {

            requestBody.put("writing_sample", writingSample);
            requestBody.put("consent_to_analyze_writing", true);
        }

        try {
            // 5. Convert request into JSON.
            String jsonBody =
                    jsonMapper.writeValueAsString(requestBody);

            System.out.println("Sending request to FastAPI:");
            System.out.println(jsonBody);

            // 6. Create HTTP request.
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(mlBaseUrl + "/api/ml/v1/analyze"))
                    .version(HttpClient.Version.HTTP_1_1)
                    .header("Content-Type", "application/json")
                    .header("Accept", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(
                            jsonBody,
                            StandardCharsets.UTF_8
                    ))
                    .build();

            System.out.println("HTTP version: " + request.version());
            System.out.println("Request body length: " + jsonBody.length());

            HttpResponse<String> response = httpClient.send(
                    request,
                    HttpResponse.BodyHandlers.ofString()
            );

            // 7. Send request directly using Java HttpClient.


            System.out.println(
                    "FastAPI HTTP status: " + response.statusCode());

            System.out.println(
                    "FastAPI response: " + response.body());

            // 8. Handle unsuccessful responses.
            if (response.statusCode() < 200 ||
                    response.statusCode() >= 300) {

                throw new RuntimeException(
                        "FastAPI returned HTTP " +
                                response.statusCode() + ": " +
                                response.body());
            }

            // 9. Return ML result.
            return jsonMapper.readTree(response.body());

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException(
                    "ML service request was interrupted", e);

        } catch (Exception e) {
            throw new RuntimeException(
                    "ML service request failed: " +
                            e.getMessage(), e);
        }
    }
}
