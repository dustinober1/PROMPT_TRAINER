/**
 * API Service for Prompt Trainer Backend
 * Handles all HTTP requests to the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ============================================================================
// Paper API
// ============================================================================

export interface Paper {
  id: number;
  title: string;
  content: string;
  rubric_id?: number | null;
  rubric_name?: string | null;
  submission_date: string;
  created_at: string;
}

export interface PaperCreate {
  title: string;
  content: string;
  rubric_id?: number | null;
}

export interface PaperUpdate {
  title?: string;
  content?: string;
  rubric_id?: number | null;
}

export const paperApi = {
  /**
   * Get all papers
   */
  list: (skip = 0, limit = 100) =>
    apiFetch<Paper[]>(`/api/papers/?skip=${skip}&limit=${limit}`),

  /**
   * Get a single paper by ID
   */
  get: (id: number) =>
    apiFetch<Paper>(`/api/papers/${id}`),

  /**
   * Create a new paper
   */
  create: (data: PaperCreate) =>
    apiFetch<Paper>('/api/papers/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /**
   * Update an existing paper
   */
  update: (id: number, data: PaperUpdate) =>
    apiFetch<Paper>(`/api/papers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  /**
   * Delete a paper
   */
  delete: (id: number) =>
    fetch(`${API_BASE_URL}/api/papers/${id}`, { method: 'DELETE' }),
};

// ============================================================================
// Prompt API
// ============================================================================

export interface Prompt {
  id: number;
  version: number;
  template_text: string;
  parent_version_id?: number | null;
  created_at: string;
  is_active: boolean;
}

export interface PromptCreate {
  template_text: string;
  parent_version_id?: number | null;
  is_active?: boolean;
}

export interface PromptUpdate {
  template_text?: string;
  is_active?: boolean;
}

export const promptApi = {
  list: (skip = 0, limit = 100) =>
    apiFetch<Prompt[]>(`/api/prompts/?skip=${skip}&limit=${limit}`),
  get: (id: number) =>
    apiFetch<Prompt>(`/api/prompts/${id}`),
  create: (data: PromptCreate) =>
    apiFetch<Prompt>('/api/prompts/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: PromptUpdate) =>
    apiFetch<Prompt>(`/api/prompts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  activate: (id: number) =>
    apiFetch<Prompt>(`/api/prompts/${id}/activate`, {
      method: 'POST',
    }),
};

// ============================================================================
// Evaluation API (stubbed)
// ============================================================================

export interface EvaluationCriterionResult {
  criterion_id?: number;
  criterion_name?: string;
  score?: string;
  reasoning?: string;
}

export interface ModelResponse {
  evaluations?: EvaluationCriterionResult[];
  [key: string]: unknown;
}

export interface FeedbackEntry {
  id: number;
  evaluation_id: number;
  rubric_id: number;
  criterion_id?: number | null;
  model_score: string;
  user_corrected_score: string;
  user_explanation?: string | null;
  created_at: string;
}

export interface Evaluation {
  id: number;
  paper_id: number;
  paper_title?: string | null;
  rubric_id: number;
  rubric_name?: string | null;
  rubric_scoring_type?: ScoringType | null;
  prompt_id: number;
  model_response: ModelResponse | string | null;
  is_correct?: boolean | null;
  created_at: string;
  feedback?: FeedbackEntry[];
  rubric_criteria?: Criterion[];
}

export interface EvaluationCreate {
  paper_id: number;
  rubric_id: number;
  prompt_id?: number;
}

export const evaluationApi = {
  create: (data: EvaluationCreate) =>
    apiFetch<Evaluation>('/api/evaluations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  get: (id: number) =>
    apiFetch<Evaluation>(`/api/evaluations/${id}`),
  markCorrect: (id: number, isCorrect: boolean) =>
    apiFetch<Evaluation>(`/api/evaluations/${id}/feedback?is_correct=${isCorrect}`, {
      method: 'PATCH',
    }),
  list: (skip = 0, limit = 100) =>
    apiFetch<Evaluation[]>(`/api/evaluations/?skip=${skip}&limit=${limit}`),
  saveFeedback: (evaluationId: number, payload: Omit<FeedbackEntry, 'id' | 'evaluation_id' | 'rubric_id' | 'created_at'>) =>
    apiFetch<FeedbackEntry>(`/api/evaluations/${evaluationId}/feedback`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  listFeedback: (evaluationId: number) =>
    apiFetch<FeedbackEntry[]>(`/api/evaluations/${evaluationId}/feedback`),
};

// ============================================================================
// Rubric API
// ============================================================================

export type ScoringType = 'yes_no' | 'meets' | 'numerical';

export interface Criterion {
  id: number;
  rubric_id: number;
  name: string;
  description?: string;
  order: number;
}

export interface CriterionCreate {
  name: string;
  description?: string;
  order: number;
}

export interface Rubric {
  id: number;
  name: string;
  scoring_type: ScoringType;
  created_at: string;
  criteria: Criterion[];
}

export interface RubricCreate {
  name: string;
  scoring_type: ScoringType;
  criteria: CriterionCreate[];
}

export interface RubricUpdate {
  name?: string;
  scoring_type?: ScoringType;
}

export const rubricApi = {
  /**
   * Get all rubrics
   */
  list: (skip = 0, limit = 100) =>
    apiFetch<Rubric[]>(`/api/rubrics/?skip=${skip}&limit=${limit}`),

  /**
   * Get a single rubric by ID
   */
  get: (id: number) =>
    apiFetch<Rubric>(`/api/rubrics/${id}`),

  /**
   * Create a new rubric with criteria
   */
  create: (data: RubricCreate) =>
    apiFetch<Rubric>('/api/rubrics/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /**
   * Update a rubric (metadata only)
   */
  update: (id: number, data: RubricUpdate) =>
    apiFetch<Rubric>(`/api/rubrics/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  /**
   * Delete a rubric
   */
  delete: (id: number) =>
    fetch(`${API_BASE_URL}/api/rubrics/${id}`, { method: 'DELETE' }),

  /**
   * Update a specific criterion
   */
  updateCriterion: (rubricId: number, criterionId: number, data: Partial<Criterion>) =>
    apiFetch<Criterion>(`/api/rubrics/${rubricId}/criteria/${criterionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  /**
   * Delete a specific criterion
   */
  deleteCriterion: (rubricId: number, criterionId: number) =>
    fetch(`${API_BASE_URL}/api/rubrics/${rubricId}/criteria/${criterionId}`, {
      method: 'DELETE'
    }),
};

// ============================================================================
// Health Check
// ============================================================================

export const healthApi = {
  /**
   * Check if backend is healthy
   */
  check: () => apiFetch<{ status: string; adapter?: string }>('/health'),
};

// ============================================================================
// Metrics API
// ============================================================================

export interface AccuracyMetrics {
  total: number;
  correct: number;
  accuracy_percent: number | null;
  adapter?: string;
  timestamp: string;
}

export const metricsApi = {
  accuracy: () => apiFetch<AccuracyMetrics>('/api/metrics/accuracy'),
};
