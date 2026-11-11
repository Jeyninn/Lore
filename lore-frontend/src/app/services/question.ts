
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface QuestionOption {
  id: string;
  label: string;
  weights?: Record<string, number>;
  tags?: string[];
}

export interface LoreQuestion {
  id: string;
  prompt: string;
  category: string;
  type: 'single_select' | 'multi_select';
  required: boolean;
  minSelections?: number;
  maxSelections?: number;
  options: QuestionOption[];
}
@Injectable({
  providedIn: 'root'
})
export class QuestionService {
  private http = inject(HttpClient);

  private apiUrl = 'http://localhost:8080/api/v1/lore/questions';

  getQuestions(): Observable<LoreQuestion[]> {
    return this.http.get<LoreQuestion[]>(this.apiUrl);
  }
}
