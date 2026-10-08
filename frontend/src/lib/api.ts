/**
 * Centralized API client with timeouts, typed responses, and friendly error handling.
 */

const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (
    typeof window !== 'undefined' &&
    window.location.hostname &&
    window.location.hostname !== 'localhost' &&
    window.location.hostname !== '127.0.0.1'
  ) {
    if (!envUrl || envUrl.includes('localhost') || envUrl.includes('127.0.0.1')) {
      return `http://${window.location.hostname}:8000/api/v1`;
    }
  }
  return envUrl || 'http://localhost:8000/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

export interface ApiError {
  code: string;
  message: string;
  fields?: Record<string, string[]>;
  status?: number;
}

export class ApiException extends Error {
  code: string;
  fields?: Record<string, string[]>;
  status?: number;

  constructor(error: ApiError) {
    super(error.message);
    this.name = 'ApiException';
    this.code = error.code;
    this.fields = error.fields;
    this.status = error.status;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs: number = 25000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const signal = options.signal
    ? (options.signal as any)
    : controller.signal;

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(options.headers || {}),
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errData: any;
      try {
        errData = await response.json();
      } catch {
        errData = {
          code: 'server_error',
          message: `Server returned HTTP ${response.status}`,
        };
      }
      throw new ApiException({
        code: errData.code || 'request_failed',
        message: errData.message || 'Request failed. Please try again.',
        fields: errData.fields || {},
        status: response.status,
      });
    }

    return (await response.json()) as T;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error instanceof ApiException) {
      throw error;
    }
    if (error.name === 'AbortError') {
      throw new ApiException({
        code: 'timeout',
        message: 'The request timed out. Please check your connection and try again.',
      });
    }
    throw new ApiException({
      code: 'network_error',
      message: error.message || 'Network error. Please verify the backend server is running.',
    });
  }
}

// ----------------- Type Definitions -----------------

export interface SymptomItem {
  id: string;
  label: string;
  query_name: string;
}

export interface DiseaseConfidence {
  disease: string;
  confidence: number;
}

export interface DiseasePredictionResult {
  success: boolean;
  disease: string;
  predicted_disease: string;
  matched_symptoms: string[];
  confidence_scores: DiseaseConfidence[];
  description: string;
  precautions: string[];
  medications: string[];
  diet: string[];
  workout: string[];
}

export interface DrugRecommendationItem {
  name: string;
  similarity_percent: number;
  description: string;
  buy_link: string;
}

export interface DrugRecommendationResult {
  success: boolean;
  medicine: string;
  description: string;
  recommendations: DrugRecommendationItem[];
}

export interface DrugPaginatedResult {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: string[];
}

export interface HeartFieldOption {
  value: string;
  label: string;
}

export interface HeartFieldSchema {
  name: string;
  label: string;
  help: string;
  default: string;
  options: HeartFieldOption[];
}

export interface HeartOptionsSchema {
  demographics: HeartFieldSchema[];
  medical_history: HeartFieldSchema[];
  lifestyle: HeartFieldSchema[];
}

export interface HeartPieChartItem {
  feature: string;
  raw_feature?: string;
  importance: number;
}

export interface HeartFactorImportance {
  feature: string;
  label: string;
  importance: number;
}

export interface HeartAssessmentResult {
  success: boolean;
  risk_score: number;
  risk_level: 'Low' | 'Moderate' | 'High' | 'Very High';
  risk_summary: string;
  recommendations: string[];
  pie_chart_data: HeartPieChartItem[];
  factor_importances: HeartFactorImportance[];
  disclaimer: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatResponse {
  role: 'assistant';
  content: string;
  sources: string[];
}

// ----------------- API Methods -----------------

export const api = {
  getHealth: () => request<{ status: string; service: string }>('/health/'),

  getSymptoms: () =>
    request<{ count: number; results: SymptomItem[] }>('/disease/symptoms/'),

  predictDisease: (symptoms: string[], signal?: AbortSignal) =>
    request<DiseasePredictionResult>(
      '/disease/predict/',
      {
        method: 'POST',
        body: JSON.stringify({ symptoms }),
        signal,
      },
      30000
    ),

  searchDisease: (query: string, signal?: AbortSignal) =>
    request<{ query: string; count: number; results: DiseasePredictionResult[] }>(
      `/disease/search/?q=${encodeURIComponent(query)}`,
      { signal }
    ),

  searchDrugs: (q: string = '', page: number = 1, pageSize: number = 20, signal?: AbortSignal) =>
    request<DrugPaginatedResult>(
      `/drugs/?q=${encodeURIComponent(q)}&page=${page}&page_size=${pageSize}`,
      { signal }
    ),

  recommendDrug: (medicine: string, signal?: AbortSignal) =>
    request<DrugRecommendationResult>(
      '/drugs/recommend/',
      {
        method: 'POST',
        body: JSON.stringify({ medicine }),
        signal,
      },
      30000
    ),

  getHeartOptions: (signal?: AbortSignal) =>
    request<HeartOptionsSchema>('/heart/options/', { signal }),

  assessHeartRisk: (data: Record<string, string>, signal?: AbortSignal) =>
    request<HeartAssessmentResult>(
      '/heart/assess/',
      {
        method: 'POST',
        body: JSON.stringify(data),
        signal,
      },
      30000
    ),

  sendChat: (query: string, messages?: ChatMessage[], signal?: AbortSignal) =>
    request<ChatResponse>(
      '/chat/',
      {
        method: 'POST',
        body: JSON.stringify({ query, messages, stream: false }),
        signal,
      },
      45000
    ),

  streamChat: async (
    query: string,
    onToken: (token: string) => void,
    onMeta?: (meta: { sources: string[] }) => void,
    onError?: (err: Error) => void,
    signal?: AbortSignal
  ) => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({ query, stream: true }),
        signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No readable stream available in response.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          const blockLines = block.split('\n');
          let event = 'message';
          let data = '';

          for (const line of blockLines) {
            if (line.startsWith('event: ')) {
              event = line.replace('event: ', '').trim();
            } else if (line.startsWith('data: ')) {
              data = line.replace('data: ', '').trim();
            }
          }

          if (data) {
            try {
              const parsed = JSON.parse(data);
              if (event === 'meta' && onMeta) {
                onMeta(parsed);
              } else if (event === 'token' && parsed.token) {
                onToken(parsed.token);
              }
            } catch {
              // ignore malformed SSE
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        if (onError) {
          onError(err);
        }
        throw err;
      }
    }
  },
};
