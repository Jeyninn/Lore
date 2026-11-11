package com.lore.backend.repository;

import com.lore.backend.entity.Question;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface QuestionRepository extends JpaRepository<Question, Long> {

    boolean existsByQuestionCode(String questionCode);

    Optional<Question> findByQuestionCode(String questionCode);
}