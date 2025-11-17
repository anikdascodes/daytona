import React, { useRef, useEffect } from 'react';
import { Message, AgentStatus } from '../types';
import { ChatMessage } from './ChatMessage';
import { TaskInput } from './TaskInput';

interface ChatPanelProps {
  messages: Message[];
  onSendTask: (task: string) => void;
  agentStatus: AgentStatus;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, onSendTask, agentStatus }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="w-2/5 h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 px-4 py-3 border-b border-gray-700">
        <h2 className="text-lg font-semibold">💬 AI Agent Chat</h2>
        <p className="text-sm text-gray-400">Describe any development task</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8 space-y-4">
            <p className="text-xl">👋 Welcome!</p>
            <p className="text-sm">Describe any development task you want me to complete.</p>
            <div className="text-left max-w-md mx-auto mt-4">
              <p className="text-sm font-semibold mb-2">Example tasks:</p>
              <ul className="text-sm space-y-1">
                <li>• Create a FastAPI REST API with user authentication</li>
                <li>• Write a Python script to process CSV files</li>
                <li>• Build a React component for a todo list</li>
                <li>• Add unit tests for the authentication module</li>
                <li>• Fix the bug in the user registration form</li>
              </ul>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <TaskInput
        onSend={onSendTask}
        disabled={agentStatus === 'working' || agentStatus === 'thinking'}
      />
    </div>
  );
};
