package com.lore.backend.dto.response;

import java.util.List;

public class QuestionResponse {

    private String id;
    private String prompt;
    private String category;
    private String type;
    private boolean required;
    private Integer minSelections;
    private Integer maxSelections;
    private List<QuestionOptionResponse> options;

    public QuestionResponse(
            String id,
            String prompt,
            String category,
            String type,
            boolean required,
            Integer minSelections,
            Integer maxSelections,
            List<QuestionOptionResponse> options) {

        this.id = id;
        this.prompt = prompt;
        this.category = category;
        this.type = type;
        this.required = required;
        this.minSelections = minSelections;
        this.maxSelections = maxSelections;
        this.options = options;
    }

    public String getId() {
        return id;
    }

    public String getPrompt() {
        return prompt;
    }

    public String getCategory() {
        return category;
    }

    public String getType() {
        return type;
    }

    public boolean isRequired() {
        return required;
    }

    public Integer getMinSelections() {
        return minSelections;
    }

    public Integer getMaxSelections() {
        return maxSelections;
    }

    public List<QuestionOptionResponse> getOptions() {
        return options;
    }
}