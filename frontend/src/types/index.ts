export interface Message {
  id: string;
  type: 'user' | 'agent' | 'system' | 'error';
  content: string;
  timestamp: Date;
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export type AgentStatus = 'idle' | 'thinking' | 'working' | 'error';

export interface WebSocketMessage {
  type: string;
  task_id?: string;
  message?: string;
  action?: string;
  result?: any;
  error?: string;
}
