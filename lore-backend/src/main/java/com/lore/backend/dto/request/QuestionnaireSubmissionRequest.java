package com.lore.backend.dto.request;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.util.List;

public class QuestionnaireSubmissionRequest {

    @NotNull
    private Integer questionnaireVersion;

    @NotEmpty
    @Valid
    private List<AnswerRequest> answers;

    public Integer getQuestionnaireVersion() {
        return questionnaireVersion;
    }

    public void setQuestionnaireVersion(Integer questionnaireVersion) {
        this.questionnaireVersion = questionnaireVersion;
    }

    public List<AnswerRequest> getAnswers() {
        return answers;
    }

    public void setAnswers(List<AnswerRequest> answers) {
        this.answers = answers;
    }
}