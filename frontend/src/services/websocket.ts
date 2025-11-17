import { WebSocketMessage } from '../types';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private messageHandlers: Set<(message: WebSocketMessage) => void> = new Set();
  private statusHandlers: Set<(status: string) => void> = new Set();

  constructor(private url: string) {}

  connect(): void {
    try {
      console.log(`Connecting to WebSocket: ${this.url}`);
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
        this.notifyStatus('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message:', message);
          this.notifyMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.notifyStatus('error');
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.notifyStatus('disconnected');
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.notifyStatus('error');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
      console.log('📤 Sent message:', message);
    } else {
      console.error('WebSocket is not connected');
    }
  }

  onMessage(handler: (message: WebSocketMessage) => void): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  onStatus(handler: (status: string) => void): () => void {
    this.statusHandlers.add(handler);
    return () => this.statusHandlers.delete(handler);
  }

  private notifyMessage(message: WebSocketMessage): void {
    this.messageHandlers.forEach((handler) => handler(message));
  }

  private notifyStatus(status: string): void {
    this.statusHandlers.forEach((handler) => handler(status));
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
      this.notifyStatus('error');
    }
  }
}
