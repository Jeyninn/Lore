import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SubmissionService } from '../../services/submission';

@Component({
  selector: 'app-processing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './processing.html',
  styleUrl: './processing.css'
})
export class Processing implements OnInit {

  private submissionService = inject(SubmissionService);
  private router = inject(Router);

  loading = true;
  errorMessage = '';

  ngOnInit(): void {
  const state = history.state;

  const submissionId = state?.submissionId;
  const writingSample = state?.writingSample ?? null;
  const writingConsent = state?.writingConsent === true;

  if (!submissionId) {
    this.loading = false;
    this.errorMessage =
      'Submission ID not found. Please complete the questionnaire again.';
    return;
  }

  this.generateProfile(
    submissionId,
    writingSample,
    writingConsent
  );
}

generateProfile(
  submissionId: number,
  writingSample: string | null,
  writingConsent: boolean
): void {

  this.submissionService.analyzeSubmission(
    submissionId,
    writingSample,
    writingConsent
  ).subscribe({
    next: (response) => {
      console.log('ML analysis completed:', response);
      console.log('Writing analysis:', response.writing_analysis);

      this.loading = false;
      this.router.navigate(['/profile']);
    },
    error: (error) => {
      console.error('ML analysis failed:', error);
      this.loading = false;
      this.errorMessage =
        error.error?.message ||
        error.error?.detail ||
        'Something went wrong while generating your lore.';
    }
  });
}

  retry(): void {
    this.router.navigate(['/questionnaire']);
  }
}