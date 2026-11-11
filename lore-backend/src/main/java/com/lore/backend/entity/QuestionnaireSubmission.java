package com.lore.backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "questionnaire_submissions")
public class QuestionnaireSubmission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private Integer questionnaireVersion;

    @Column(nullable = false)
    private LocalDateTime submittedAt;

    @OneToMany(
            mappedBy = "submission",
            cascade = CascadeType.ALL,
            orphanRemoval = true
    )
    private List<QuestionnaireAnswer> answers = new ArrayList<>();

    public QuestionnaireSubmission() {}

    public Long getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public Integer getQuestionnaireVersion() {
        return questionnaireVersion;
    }

    public void setQuestionnaireVersion(Integer questionnaireVersion) {
        this.questionnaireVersion = questionnaireVersion;
    }

    public LocalDateTime getSubmittedAt() {
        return submittedAt;
    }

    public void setSubmittedAt(LocalDateTime submittedAt) {
        this.submittedAt = submittedAt;
    }

    public List<QuestionnaireAnswer> getAnswers() {
        return answers;
    }

    public void setAnswers(List<QuestionnaireAnswer> answers) {
        this.answers = answers;
    }
}