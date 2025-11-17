import { useEffect, useRef, useState } from 'react';
import { WebSocketService } from '../services/websocket';
import { WebSocketMessage, ConnectionStatus } from '../types';

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: any) => void;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [status, setStatus] = useState<ConnectionStatus>('connecting');
  const wsRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    // Determine WebSocket URL based on current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = window.location.port || '80';
    const wsUrl = `${protocol}//${host}:${port}/ws/agent`;

    console.log('Initializing WebSocket connection to:', wsUrl);

    // Create WebSocket service
    const ws = new WebSocketService(wsUrl);
    wsRef.current = ws;

    // Set up status handler
    const unsubscribeStatus = ws.onStatus((newStatus) => {
      setStatus(newStatus as ConnectionStatus);
    });

    // Set up message handler
    const unsubscribeMessage = ws.onMessage((message) => {
      if (options.onMessage) {
        options.onMessage(message);
      }
    });

    // Connect
    ws.connect();

    // Cleanup on unmount
    return () => {
      unsubscribeStatus();
      unsubscribeMessage();
      ws.disconnect();
    };
  }, []);

  const sendMessage = (message: any) => {
    if (wsRef.current) {
      wsRef.current.send(message);
    }
  };

  return {
    status,
    connected: status === 'connected',
    sendMessage,
  };
}
