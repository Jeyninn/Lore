package com.lore.backend.dto.response;

import tools.jackson.databind.JsonNode;

public class QuestionOptionResponse {

    private String id;
    private String label;
    private JsonNode weights;
    private JsonNode tags;

    public QuestionOptionResponse(
            String id,
            String label,
            JsonNode weights,
            JsonNode tags) {

        this.id = id;
        this.label = label;
        this.weights = weights;
        this.tags = tags;
    }

    public String getId() {
        return id;
    }

    public String getLabel() {
        return label;
    }

    public JsonNode getWeights() {
        return weights;
    }

    public JsonNode getTags() {
        return tags;
    }
}