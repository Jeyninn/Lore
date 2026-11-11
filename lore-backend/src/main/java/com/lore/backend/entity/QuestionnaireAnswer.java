package com.lore.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(
        name = "questionnaire_answers",
        uniqueConstraints = {
                @UniqueConstraint(
                        columnNames = {"submission_id", "question_id"}
                )
        }
)
public class QuestionnaireAnswer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "submission_id", nullable = false)
    private QuestionnaireSubmission submission;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "question_id", nullable = false)
    private Question question;

    @Column(nullable = false, columnDefinition = "JSON")
    private String selectedOptionCodes;

    public QuestionnaireAnswer() {}

    public Long getId() {
        return id;
    }

    public QuestionnaireSubmission getSubmission() {
        return submission;
    }

    public void setSubmission(QuestionnaireSubmission submission) {
        this.submission = submission;
    }

    public Question getQuestion() {
        return question;
    }

    public void setQuestion(Question question) {
        this.question = question;
    }

    public String getSelectedOptionCodes() {
        return selectedOptionCodes;
    }

    public void setSelectedOptionCodes(String selectedOptionCodes) {
        this.selectedOptionCodes = selectedOptionCodes;
    }
}