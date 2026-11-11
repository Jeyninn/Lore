package com.lore.backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "personality_profiles")
public class PersonalityProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "submission_id", nullable = false, unique = true)
    private QuestionnaireSubmission submission;

    @Column(columnDefinition = "JSON", nullable = false)
    private String generatedResult;

    private LocalDateTime createdAt;

    public PersonalityProfile() {
    }

    public Long getId() {
        return id;
    }

    public QuestionnaireSubmission getSubmission() {
        return submission;
    }

    public void setSubmission(QuestionnaireSubmission submission) {
        this.submission = submission;
    }

    public String getGeneratedResult() {
        return generatedResult;
    }

    public void setGeneratedResult(String generatedResult) {
        this.generatedResult = generatedResult;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}