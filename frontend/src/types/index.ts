export interface EvidenceItem {
  evidence_id: string;
  source_type: 'database' | 'document' | 'web';
  source_id: string;
  content: string;
  relevance_score: number;
  source_quality: number;
  timestamp: string;
  citation: string;
  agent: string;
  metadata: Record<string, any>;
}

export interface TraceEvent {
  event_id: string;
  step: string;
  agent: string;
  status: 'started' | 'completed' | 'retrying' | 'warning' | 'error';
  message: string;
  timestamp: string;
  details?: Record<string, any>;
}

export interface CitationItem {
  source_type: string;
  source_id: string;
  raw_tag: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  run_id?: string;
  confidence?: number;
  citations?: CitationItem[];
  evidence?: EvidenceItem[];
  trace_events?: TraceEvent[];
  execution_time_ms?: number;
  user_rating?: number;
  loading?: boolean;
}

export interface StrategyEpisode {
  episode_id: string;
  timestamp: string;
  domain: string;
  question_type: string;
  original_query: string;
  rewritten_query?: string;
  agent: string;
  strategy: {
    retriever: string;
    top_k: number;
    reranker: string;
  };
  critic_score: number;
  user_feedback?: number;
  latency_ms: number;
  success: boolean;
  retries_needed: number;
}

export interface StrategySummary {
  total_episodes: number;
  avg_critic_score: number;
  success_rate: number;
  avg_latency_ms: number;
  retriever_distribution: Record<string, number>;
  recent_episodes: StrategyEpisode[];
}

export interface SystemMetricSummary {
  system: string;
  recall: number;
  hit_rate: number;
  mrr: number;
  groundedness: number;
  citation_coverage: number;
  avg_latency_ms: number;
  avg_retries: number;
}

export interface EvaluationResults {
  benchmark_size: number;
  summary: SystemMetricSummary[];
  detailed_results: any[];
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
  title: string;
  chunks: number;
  char_count: number;
  content_hash?: string;
}
