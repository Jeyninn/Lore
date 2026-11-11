
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
export interface AnswerPayload {
  questionId: string;
  selectedOptionIds: string[];
}

export interface SubmissionPayload {
  questionnaireVersion: number;
  answers: AnswerPayload[];
}
@Injectable({
  providedIn: 'root'
})
export class SubmissionService {
  private http = inject(HttpClient);

  private baseUrl = 'http://localhost:8080/api/v1/lore';

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');

    return new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
  }

  submitQuestionnaire(data: SubmissionPayload): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/submissions`,
      data,
      { headers: this.getHeaders() }
    );
  }

 analyzeSubmission(
  submissionId: number,
  writingSample: string | null,
  writingConsent: boolean
): Observable<any> {

  const body = writingConsent
    ? {
        writingSample,
        consentToAnalyzeWriting: true
      }
    : {};

  return this.http.post(
    `${this.baseUrl}/submissions/${submissionId}/analyze`,
    body,
    { headers: this.getHeaders() }
  );
}
}
