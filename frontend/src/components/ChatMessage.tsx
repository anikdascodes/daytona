import React from 'react';
import { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';
  const isSystem = message.type === 'system';

  const getBgColor = () => {
    if (isUser) return 'bg-blue-600';
    if (isError) return 'bg-red-600';
    if (isSystem) return 'bg-gray-700';
    return 'bg-gray-600';
  };

  const getIcon = () => {
    if (isUser) return '👤';
    if (isError) return '❌';
    if (isSystem) return 'ℹ️';
    return '🤖';
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3xl rounded-lg p-3 ${getBgColor()}`}>
        <div className="flex items-start space-x-2">
          <span className="text-lg">{getIcon()}</span>
          <div className="flex-1">
            <pre className="whitespace-pre-wrap font-sans text-sm">{message.content}</pre>
            <div className="text-xs text-gray-300 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
