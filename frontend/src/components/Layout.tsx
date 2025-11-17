import React from 'react';
import { ConnectionStatus, AgentStatus } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  connectionStatus: ConnectionStatus;
  agentStatus: AgentStatus;
}

export const Layout: React.FC<LayoutProps> = ({ children, connectionStatus, agentStatus }) => {
  const getStatusColor = (status: ConnectionStatus) => {
    switch (status) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'disconnected': return 'bg-red-500';
      case 'error': return 'bg-red-700';
      default: return 'bg-gray-500';
    }
  };

  const getAgentStatusText = (status: AgentStatus) => {
    switch (status) {
      case 'idle': return '🤖 Idle';
      case 'thinking': return '🧠 Thinking...';
      case 'working': return '⚙️ Working...';
      case 'error': return '❌ Error';
      default: return '🤖 Agent';
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold">🤖 Agentic Development System</h1>
          <div className="flex items-center space-x-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${getStatusColor(connectionStatus)}`}></span>
            <span className="text-gray-400">{connectionStatus}</span>
          </div>
        </div>
        <div className="text-sm text-gray-400">
          {getAgentStatusText(agentStatus)}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </div>
  );
};
