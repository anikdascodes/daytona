import React, { useState } from 'react';

interface TaskInputProps {
  onSend: (task: string) => void;
  disabled?: boolean;
}

export const TaskInput: React.FC<TaskInputProps> = ({ onSend, disabled = false }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-gray-800 border-t border-gray-700">
      <div className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={disabled ? 'Agent is working...' : 'Describe a development task...'}
          disabled={disabled}
          className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
        >
          Send
        </button>
      </div>
      <div className="mt-2 text-xs text-gray-400">
        Press Enter to send • The AI agent has full control of the workspace
      </div>
    </form>
  );
};
