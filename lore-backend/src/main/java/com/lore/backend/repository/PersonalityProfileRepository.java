package com.lore.backend.repository;

import com.lore.backend.entity.PersonalityProfile;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface PersonalityProfileRepository
        extends JpaRepository<PersonalityProfile, Long> {

    // Find profile using questionnaire submission ID
    Optional<PersonalityProfile> findBySubmission_Id(Long submissionId);

    // Find latest profile belonging to a user
    Optional<PersonalityProfile>
    findFirstBySubmission_User_EmailOrderByCreatedAtDesc(String email);
}