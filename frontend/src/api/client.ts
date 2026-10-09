import axios from 'axios';
import type { ChatRequest, ChatResponse, UserProfile, SchemeRecommendation, RegisterPayload } from '../types/api';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 45000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Auth API ────────────────────────────────────────────────
export interface AuthUserResponse {
  id: number;
  username: string;
  full_name: string;
  email: string | null;
  session_id: string;
  profile?: UserProfile;
}

export async function registerUser(payload: RegisterPayload): Promise<AuthUserResponse> {
  try {
    const { data } = await api.post<AuthUserResponse>('/api/auth/register', {
      username: payload.username,
      full_name: payload.fullName,
      password: payload.password,
      email: payload.email || null,
      age: payload.age || null,
      gender: payload.gender || null,
      occupation: payload.occupation || null,
      state: payload.state || null,
      district: payload.district || null,
      annual_income: payload.annual_income || null,
      caste_category: payload.caste_category || null,
      landholding_acres: payload.landholding_acres || null,
      preferred_language: payload.preferred_language || 'en',
    });
    return data;
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response?.data?.detail) {
      throw new Error(err.response.data.detail);
    }
    throw new Error('Registration failed. Please try again.');
  }
}

export async function loginUser(
  usernameOrEmail: string,
  password: string
): Promise<AuthUserResponse> {
  try {
    const { data } = await api.post<AuthUserResponse>('/api/auth/login', {
      username_or_email: usernameOrEmail,
      password,
    });
    return data;
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response?.data?.detail) {
      throw new Error(err.response.data.detail);
    }
    throw new Error('Invalid credentials. Please try again.');
  }
}

export async function fetchCurrentUser(sessionId: string): Promise<AuthUserResponse> {
  const { data } = await api.get<AuthUserResponse>(`/api/auth/me?session_id=${sessionId}`);
  return data;
}

// ── Citizen Profile API ─────────────────────────────────────
export async function fetchUserProfile(sessionId: string): Promise<UserProfile> {
  try {
    const { data } = await api.get<UserProfile>(`/api/profile/${sessionId}`);
    return data;
  } catch (err) {
    console.warn('Failed to fetch user profile:', err);
    return {};
  }
}

export async function updateUserProfile(
  sessionId: string,
  profile: UserProfile
): Promise<UserProfile> {
  const { data } = await api.put<UserProfile>(`/api/profile/${sessionId}`, profile);
  return data;
}

// ── Conversation History API ────────────────────────────────
export interface ConversationMessage {
  role: string;
  content: string;
  metadata: Record<string, unknown> | null;
}

export async function fetchChatHistory(sessionId: string): Promise<ConversationMessage[]> {
  try {
    const { data } = await api.get<ConversationMessage[]>(`/api/conversations/${sessionId}`);
    return data;
  } catch {
    return [];
  }
}

export async function clearChatHistory(sessionId: string): Promise<void> {
  try {
    await api.delete(`/api/conversations/${sessionId}`);
  } catch (err) {
    console.warn('Failed to clear conversation history on backend:', err);
  }
}

export async function syncChatHistory(
  sessionId: string,
  messages: Array<{ role: string; content: string }>
): Promise<{ status: string; count: number }> {
  try {
    const { data } = await api.post<{ status: string; count: number }>('/api/conversations/sync', {
      session_id: sessionId,
      messages,
    });
    return data;
  } catch (err) {
    console.warn('Failed to sync conversation messages to backend:', err);
    return { status: 'failed', count: 0 };
  }
}

// ── Chat API ────────────────────────────────────────────────
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>('/api/chat', request);
  return data;
}

export async function checkHealth(): Promise<{ status: string; indexed_schemes: number }> {
  const { data } = await api.get('/health');
  return data;
}

export interface SchemeCatalogItem {
  scheme_id: string;
  scheme_name: string;
  department: string;
  level: string;
  state: string | null;
  scheme_category: string;
}

export async function fetchSchemesCatalog(): Promise<SchemeCatalogItem[]> {
  try {
    const { data } = await api.get<SchemeCatalogItem[]>('/api/schemes');
    return data;
  } catch (err) {
    console.warn('Failed to fetch schemes catalog from backend, using cached list:', err);
    return [];
  }
}

export async function checkDirectEligibility(
  profile: UserProfile,
  schemeId?: string
): Promise<SchemeRecommendation[]> {
  try {
    const { data } = await api.post<SchemeRecommendation[]>('/api/eligibility', {
      profile,
      scheme_id: schemeId || null,
    });
    return data;
  } catch (err) {
    console.warn('Failed to check direct eligibility:', err);
    return [];
  }
}

export default api;
