// Shared TypeScript types for API communication

export type Language = 'en' | 'hi' | 'mr';
export type InteractionMode = 'text' | 'mcq';
export type EligibilityStatus = 'ELIGIBLE' | 'INELIGIBLE' | 'PARTIAL' | 'UNKNOWN';

// Matches backend UserProfile schema exactly
export interface UserProfile {
  age?: number;
  annual_income?: number;
  state?: string;
  district?: string;
  occupation?: string;
  education_level?: string;
  caste_category?: string;
  gender?: string;
  marital_status?: string;
  is_differently_abled?: boolean;
  landholding_acres?: number;
  preferred_language?: Language;
  interaction_mode?: InteractionMode;
}

export interface MCQOption {
  label: string;
  value: string;
}

// Matches backend ConditionResult (from eligibility engine)
export interface ConditionResult {
  condition_name: string;
  description: string;
  status: 'passed' | 'failed' | 'unknown';
  expected_value?: string;
  actual_value?: unknown;
  reason: string;
}

export interface FinancialBreakoutItem {
  label: string;
  value: string;
  subtext?: string;
  isHighlight?: boolean;
  isSecondary?: boolean;
}

export interface ClarificationPrompt {
  title: string;
  description: string;
  options: Array<{
    label: string;
    icon?: string;
    value?: string;
  }>;
}

// Matches backend EligibilityEvaluation / recommendation shape
export interface SchemeRecommendation {
  scheme_id: string;
  scheme_name: string;
  status: EligibilityStatus;          // backend uses 'status' not 'eligibility_status'
  summary?: string;                   // overall verdict text
  matched_conditions?: ConditionResult[];
  failed_conditions?: ConditionResult[];
  missing_fields?: string[];
  official_url?: string;
  top_evidence_snippet?: string;
  retrieved_sections?: string[];
  retrieval_score?: number;
  // Optional extras matching DESIGN.md & code.html
  department?: string;
  level?: string;
  description?: string;
  match_percentage?: number;
  category_badge?: string;
  effective_benefit?: string;
  financial_breakout?: FinancialBreakoutItem[];
  required_documents?: Array<{ name: string; isVerified?: boolean }>;
  clarification_prompt?: ClarificationPrompt;
  registration_window?: string;
}

export interface ChatRequest {
  message: string;
  session_state?: SessionState;
}

export interface SessionState {
  messages: Array<{ role: string; content: string }>;
  profile: UserProfile;
  detected_language: Language;
  interaction_mode: InteractionMode;
}

export interface ChatResponse {
  response: string;
  detected_language: Language;
  interaction_mode: InteractionMode;
  needs_clarification: boolean;
  mcq_options?: MCQOption[];
  profile: UserProfile;
  recommendations: SchemeRecommendation[];
  source_urls: string[];
  session_state: SessionState;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  userName?: string;
  userAvatar?: string;
  syncNotice?: string;
  mcq_options?: MCQOption[];
  recommendations?: SchemeRecommendation[];
  isLoading?: boolean;
  synthesizingDetails?: string;
}
