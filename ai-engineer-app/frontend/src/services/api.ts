import axios from 'axios'
import type {
  LLMConfig,
  RuntimeConfig,
  HealthCheckResponse,
  LLMProviderInfo,
  RuntimeProviderInfo,
  SessionInfo,
} from '../types'

const API_BASE = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getLLMProviders = async (): Promise<{ providers: LLMProviderInfo[] }> => {
  const response = await api.get('/api/providers/llm')
  return response.data
}

export const getRuntimeProviders = async (): Promise<{ providers: RuntimeProviderInfo[] }> => {
  const response = await api.get('/api/providers/runtime')
  return response.data
}

export const performHealthCheck = async (
  llmConfig: LLMConfig,
  runtimeConfig: RuntimeConfig
): Promise<HealthCheckResponse> => {
  const response = await api.post('/api/health-check', {
    llm_config: llmConfig,
    runtime_config: runtimeConfig,
  })
  return response.data
}

export const createSession = async (config: {
  llm_config: LLMConfig
  runtime_config: RuntimeConfig
}): Promise<{ session_id: string; created_at: string; status: string }> => {
  const response = await api.post('/api/sessions', config)
  return response.data
}

export const getSession = async (sessionId: string): Promise<SessionInfo> => {
  const response = await api.get(`/api/sessions/${sessionId}`)
  return response.data
}

export const deleteSession = async (sessionId: string): Promise<{ status: string; session_id: string }> => {
  const response = await api.delete(`/api/sessions/${sessionId}`)
  return response.data
}

export const stopSessionTask = async (sessionId: string): Promise<{ status: string; session_id: string }> => {
  const response = await api.post(`/api/sessions/${sessionId}/stop`)
  return response.data
}
