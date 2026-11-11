
import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import {
  QuestionService,
  LoreQuestion
} from '../../services/question';

import { SubmissionService } from '../../services/submission';

@Component({
  selector: 'app-questionnaire',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './questionnaire.html',
  styleUrl: './questionnaire.css'
})
export class Questionnaire implements OnInit {
  private cdr = inject(ChangeDetectorRef);
  private questionService = inject(QuestionService);
  private submissionService = inject(SubmissionService);
  private router = inject(Router);
  showWritingStep = false;

  writingSample = '';
  writingConsent = false;
  writingError = '';

  questions: LoreQuestion[] = [];
  answers: Record<string, string[]> = {};

  currentIndex = 0;
  loading = true;
  submitting = false;
  errorMessage = '';

 ngOnInit() {
  console.log('Questionnaire component initialized');
  this.loadQuestions();
}

loadQuestions(): void {
  this.loading = true;
  this.errorMessage = '';

  this.questionService.getQuestions().subscribe({
    next: (data) => {
      this.questions = data;
      this.loading = false;

      console.log('Questions:', this.questions.length);
      console.log('Loading:', this.loading);

      this.cdr.detectChanges();
    },

    error: (error) => {
      console.error('Question API error:', error);

      this.errorMessage = 'Unable to load questions. Please try again.';
      this.loading = false;

      this.cdr.detectChanges();
    }
  });
}

  get currentQuestion(): LoreQuestion | undefined {
    return this.questions[this.currentIndex];
  }

  get progress(): number {
    return this.questions.length
      ? ((this.currentIndex + 1) / this.questions.length) * 100
      : 0;
  }

  get isLastQuestion(): boolean {
    return this.currentIndex === this.questions.length - 1;
  }

  isSelected(optionId: string): boolean {
  const questionId = this.currentQuestion?.id;

  return questionId !== undefined &&
    (this.answers[questionId] || []).includes(optionId);
}

selectOption(optionId: string): void {
  const question = this.currentQuestion;
  if (!question) return;

  const questionId = question.id;
  const selected: string[] = this.answers[questionId] || [];

  if (question.type === 'single_select') {
    this.answers[questionId] = [optionId];
    return;
  }

  if (selected.includes(optionId)) {
    this.answers[questionId] = selected.filter(
      (id: string) => id !== optionId
    );
    return;
  }

  const max = question.maxSelections ?? 3;

  if (selected.length < max) {
    this.answers[questionId] = [...selected, optionId];
  }
}

  canContinue(): boolean {
    const question = this.currentQuestion;
    if (!question) return false;

    const selected = this.answers[question.id] || [];
    const minimum = question.minSelections ?? 1;

    return !question.required || selected.length >= minimum;
  }

  nextQuestion(): void {
    if (!this.canContinue()) return;

    if (this.isLastQuestion) {
      this.showWritingStep = true;
    } else {
      this.currentIndex++;
    }
  }

  previousQuestion(): void {
    if (this.currentIndex > 0) {
      this.currentIndex--;
    }
  }
  backToQuestions(): void {
  this.showWritingStep = false;
  this.currentIndex = this.questions.length - 1;
  }

  validateWriting(): boolean {
  this.writingError = '';

  if (!this.writingConsent) {
    return true;
  }

  const length = this.writingSample.trim().length;

  if (length < 100 || length > 2000) {
    this.writingError =
      'With consent, your writing must contain 100–2000 characters.';
    return false;
  }

  return true;
}

  submitAnswers(): void {
  if (this.submitting || !this.questions.length) return;

  if (!this.validateWriting()) return;

    const payload = {
      questionnaireVersion: 1,
      answers: this.questions.map(question => ({
        questionId: question.id,
        selectedOptionIds: this.answers[question.id] || []
      }))
    };

    this.submitting = true;
    this.errorMessage = '';

    this.submissionService.submitQuestionnaire(payload).subscribe({
      next: (response) => {
        const submissionId = response.id ?? response.submissionId;

        if (!submissionId) {
          this.submitting = false;
          this.errorMessage =
            'Submission saved, but the response did not contain a submission ID.';
          return;
        }
        if (!this.validateWriting()) {
          this.submitting = false;
          return;
        }

        this.router.navigate(['/processing'], {
          state: {
            submissionId,
            writingSample: this.writingConsent
              ? this.writingSample.trim()
              : null,
            writingConsent: this.writingConsent
          }
        });
      },
      error: (error) => {
        console.error('Submission failed:', error);
        this.submitting = false;
        this.errorMessage =
          error.error?.message || 'Could not submit your answers.';
      }
    });
  }
}
