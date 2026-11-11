
package com.lore.backend.config;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import com.lore.backend.entity.Question;
import com.lore.backend.entity.QuestionOption;
import com.lore.backend.repository.QuestionRepository;

import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

@Component
public class QuestionnaireSeeder implements CommandLineRunner {

    private final QuestionRepository questionRepository;
    private final JsonMapper jsonMapper;

    public QuestionnaireSeeder(
            QuestionRepository questionRepository,
            JsonMapper jsonMapper) {

        this.questionRepository = questionRepository;
        this.jsonMapper = jsonMapper;
    }

    @Override
    public void run(String... args) throws Exception {

        try (InputStream inputStream =
                     new ClassPathResource("questionnaire.v1.json")
                             .getInputStream()) {

            JsonNode root = jsonMapper.readTree(inputStream);

            JsonNode questions = root.get("questions");

            for (JsonNode questionNode : questions) {

                String code = questionNode.get("id").asText();

                if (questionRepository.existsByQuestionCode(code)) {
                    continue;
                }

                Question question = new Question();

                question.setQuestionCode(code);
                question.setQuestionText(
                        questionNode.get("prompt").asText());
                question.setCategory(
                        questionNode.get("category").asText());
                question.setQuestionType(
                        questionNode.get("type").asText());
                question.setRequired(
                        questionNode.get("required").asBoolean());

                if (questionNode.has("min_selections")) {
                    question.setMinSelections(
                            questionNode.get("min_selections").asInt());
                }

                if (questionNode.has("max_selections")) {
                    question.setMaxSelections(
                            questionNode.get("max_selections").asInt());
                }

                List<QuestionOption> options = new ArrayList<>();

                for (JsonNode optionNode : questionNode.get("options")) {

                    QuestionOption option = new QuestionOption();

                    option.setOptionCode(
                            optionNode.get("id").asText());

                    option.setOptionText(
                            optionNode.get("label").asText());

                    if (optionNode.has("weights")) {
                        option.setWeights(
                                jsonMapper.writeValueAsString(
                                        optionNode.get("weights")));
                    }

                    if (optionNode.has("tags")) {
                        option.setTags(
                                jsonMapper.writeValueAsString(
                                        optionNode.get("tags")));
                    }

                    option.setQuestion(question);
                    options.add(option);
                }

                question.setOptions(options);
                questionRepository.save(question);
            }
        }

        System.out.println(
                "LORE.exe questionnaire seeding completed!");
    }
}
