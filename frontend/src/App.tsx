import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { VSCodePanel } from './components/VSCodePanel';
import { ChatPanel } from './components/ChatPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { Message, AgentStatus, WebSocketMessage } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatus>('idle');

  const { status: connectionStatus, connected, sendMessage } = useWebSocket({
    onMessage: (wsMessage: WebSocketMessage) => {
      handleWebSocketMessage(wsMessage);
    },
  });

  const handleWebSocketMessage = (wsMessage: WebSocketMessage) => {
    console.log('Handling message:', wsMessage);

    // Update agent status based on message type
    if (wsMessage.type === 'task_started' || wsMessage.type === 'task_received') {
      setAgentStatus('working');
    } else if (wsMessage.type === 'agent_thinking') {
      setAgentStatus('thinking');
    } else if (wsMessage.type === 'task_completed' || wsMessage.type === 'task_failed') {
      setAgentStatus('idle');
    } else if (wsMessage.type === 'error' || wsMessage.type === 'agent_error') {
      setAgentStatus('error');
    }

    // Add message to chat
    const messageType = wsMessage.type === 'error' || wsMessage.type === 'agent_error'
      ? 'error'
      : wsMessage.type.startsWith('task_')
        ? 'system'
        : 'agent';

    const newMessage: Message = {
      id: Date.now().toString() + Math.random(),
      type: messageType,
      content: wsMessage.message || JSON.stringify(wsMessage, null, 2),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
  };

  const handleSendTask = (task: string) => {
    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: task,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send task to backend via WebSocket
    sendMessage({
      task_id: Date.now().toString(),
      task: task,
    });

    // Update agent status
    setAgentStatus('working');
  };

  return (
    <Layout connectionStatus={connectionStatus} agentStatus={agentStatus}>
      <div className="flex h-full">
        <VSCodePanel />
        <ChatPanel
          messages={messages}
          onSendTask={handleSendTask}
          agentStatus={agentStatus}
        />
      </div>
    </Layout>
  );
}

export default App;
