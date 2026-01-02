// Types matching backend models

export type TaskStatus = 'pending' | 'planning' | 'executing' | 'completed' | 'failed' | 'awaiting_input'

export type LLMProvider = 'openai' | 'anthropic' | 'google' | 'custom'

export type RuntimeProvider = 'docker' | 'daytona' | 'modal' | 'e2b'

export interface LLMConfig {
  provider: LLMProvider
  model: string
  api_key: string
  base_url?: string
  temperature: number
  max_tokens?: number
}

export interface RuntimeConfig {
  provider: RuntimeProvider
  api_key?: string
  api_url?: string
  target?: string
  timeout: number
}

export interface SessionConfig {
  llm_config: LLMConfig
  runtime_config: RuntimeConfig
}

export interface HealthCheckResponse {
  llm_status: 'healthy' | 'unhealthy'
  llm_message: string
  llm_latency_ms?: number
  runtime_status: 'healthy' | 'unhealthy'
  runtime_message: string
  overall_healthy: boolean
  timestamp: string
}

export interface TaskStep {
  id: string
  description: string
  status: TaskStatus
  started_at?: string
  completed_at?: string
  output?: string
  error?: string
}

export interface AgentTask {
  id: string
  description: string
  status: TaskStatus
  plan: TaskStep[]
  current_step: number
  started_at: string
  completed_at?: string
  final_output?: string
  error?: string
}

// WebSocket Event Types matching backend
export type WSEventType =
  | 'connected'
  | 'disconnected'
  | 'error'
  | 'status'
  | 'runtime_starting'
  | 'runtime_ready'
  | 'task_started'
  | 'task_planning'
  | 'task_plan_ready'
  | 'task_step_started'
  | 'task_step_completed'
  | 'task_completed'
  | 'task_failed'
  | 'agent_thinking'
  | 'agent_action'
  | 'agent_observation'
  | 'agent_message'
  | 'terminal_output'
  | 'terminal_error'
  | 'file_created'
  | 'file_modified'
  | 'file_deleted'
  | 'files_list'
  | 'file_content'

export interface WSEvent {
  type: WSEventType
  data: Record<string, any>
  timestamp: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  type?: 'text' | 'thinking' | 'action' | 'observation' | 'error' | 'terminal'
  metadata?: Record<string, any>
}

export interface FileInfo {
  path: string
  name: string
  is_dir: boolean
  children?: FileInfo[]
}

export interface LLMProviderInfo {
  id: LLMProvider
  name: string
  models: string[]
  requires_base_url: boolean
  placeholder_url?: string
}

export interface RuntimeProviderInfo {
  id: RuntimeProvider
  name: string
  description: string
  requires_api_key: boolean
  requires_api_url: boolean
  default_api_url?: string
  signup_url?: string
}

export interface SessionInfo {
  session_id: string
  created_at: string
  is_initialized: boolean
  is_running: boolean
  current_task?: AgentTask
  task_count: number
}
