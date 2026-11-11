package com.lore.backend.repository;

import com.lore.backend.entity.QuestionnaireSubmission;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface QuestionnaireSubmissionRepository
        extends JpaRepository<QuestionnaireSubmission, Long> {

    @EntityGraph(attributePaths = {"answers", "answers.question"})
    Optional<QuestionnaireSubmission> findWithAnswersById(Long id);
}