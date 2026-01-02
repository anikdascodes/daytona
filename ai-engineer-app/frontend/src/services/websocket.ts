import type { WSEvent } from '../types'

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface WebSocketCallbacks {
  onMessage: (event: WSEvent) => void
  onStatusChange?: (status: WebSocketStatus) => void
  onError?: (error: Event) => void
}

export class WebSocketService {
  private ws: WebSocket | null = null
  private sessionId: string
  private callbacks: WebSocketCallbacks
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  constructor(sessionId: string, callbacks: WebSocketCallbacks) {
    this.sessionId = sessionId
    this.callbacks = callbacks
  }

  connect(): void {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_WS_HOST || window.location.host
    const url = `${protocol}//${host}/ws/${this.sessionId}`

    this.callbacks.onStatusChange?.('connecting')
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.callbacks.onStatusChange?.('connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const message: WSEvent = JSON.parse(event.data)
        this.callbacks.onMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.callbacks.onStatusChange?.('error')
      this.callbacks.onError?.(error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.callbacks.onStatusChange?.('disconnected')
      this.attemptReconnect()
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
      setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts)
    }
  }

  send(type: string, data: Record<string, any> = {}): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }

  sendChatMessage(content: string): void {
    this.send('chat', { content })
  }

  sendTerminalCommand(command: string): void {
    this.send('terminal', { command })
  }

  requestFileList(path: string = '/workspace'): void {
    this.send('list_files', { path })
  }

  requestFileContent(path: string): void {
    this.send('read_file', { path })
  }

  stopTask(): void {
    this.send('stop')
  }

  ping(): void {
    this.send('ping')
  }

  disconnect(): void {
    this.maxReconnectAttempts = 0 // Prevent reconnection
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}
