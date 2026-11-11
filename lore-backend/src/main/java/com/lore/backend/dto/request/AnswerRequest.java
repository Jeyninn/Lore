package com.lore.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public class AnswerRequest {

    @NotBlank
    private String questionId;

    @NotEmpty
    private List<String> selectedOptionIds;

    public String getQuestionId() {
        return questionId;
    }

    public void setQuestionId(String questionId) {
        this.questionId = questionId;
    }

    public List<String> getSelectedOptionIds() {
        return selectedOptionIds;
    }

    public void setSelectedOptionIds(List<String> selectedOptionIds) {
        this.selectedOptionIds = selectedOptionIds;
    }
}