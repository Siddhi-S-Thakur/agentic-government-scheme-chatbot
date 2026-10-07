import axios from 'axios';
import type { ChatRequest, ChatResponse, UserProfile, SchemeRecommendation } from '../types/api';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 45000,
  headers: { 'Content-Type': 'application/json' },
});

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
