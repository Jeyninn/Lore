package com.lore.backend.service;

import com.lore.backend.dto.response.QuestionOptionResponse;
import com.lore.backend.dto.response.QuestionResponse;
import com.lore.backend.entity.Question;
import com.lore.backend.repository.QuestionRepository;

import org.springframework.stereotype.Service;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import java.util.List;

@Service
public class QuestionService {

    private final QuestionRepository questionRepository;
    private final JsonMapper jsonMapper;

    public QuestionService(QuestionRepository questionRepository) {
        this.questionRepository = questionRepository;
        this.jsonMapper = JsonMapper.builder().build();
    }

    public List<QuestionResponse> getAllQuestions() {

        return questionRepository.findAll()
                .stream()
                .map(question -> new QuestionResponse(
                        question.getQuestionCode(),
                        question.getQuestionText(),
                        question.getCategory(),
                        question.getQuestionType(),
                        question.isRequired(),
                        question.getMinSelections(),
                        question.getMaxSelections(),

                        question.getOptions()
                                .stream()
                                .map(option -> new QuestionOptionResponse(
                                        option.getOptionCode(),
                                        option.getOptionText(),
                                        parseJson(option.getWeights()),
                                        parseJson(option.getTags())
                                ))
                                .toList()
                ))
                .toList();
    }

    private JsonNode parseJson(String value) {

        try {
            return value == null
                    ? null
                    : jsonMapper.readTree(value);

        } catch (Exception e) {
            throw new RuntimeException(
                    "Invalid questionnaire JSON data", e);
        }
    }
}