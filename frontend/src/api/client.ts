import axios from 'axios';
import type { ChatRequest, ChatResponse } from '../types/api';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
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

export default api;
