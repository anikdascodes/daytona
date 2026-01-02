import ReactMarkdown from 'react-markdown'
import clsx from 'clsx'
import type { ChatMessage as ChatMessageType } from '../../types'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  const getMessageStyle = () => {
    switch (message.type) {
      case 'thinking':
        return 'bg-purple-50 border-purple-200 text-purple-900'
      case 'action':
        return 'bg-blue-50 border-blue-200 text-blue-900'
      case 'observation':
        return 'bg-gray-50 border-gray-200 text-gray-800'
      case 'terminal':
        return 'bg-gray-900 text-green-400 font-mono text-sm'
      case 'error':
        return 'bg-red-50 border-red-200 text-red-900'
      default:
        if (isUser) return 'bg-blue-600 text-white'
        if (isSystem) return 'bg-yellow-50 border-yellow-200 text-yellow-800'
        return 'bg-white border-gray-200 text-gray-900'
    }
  }

  const getIcon = () => {
    switch (message.type) {
      case 'thinking':
        return (
          <svg className="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        )
      case 'action':
        return (
          <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        )
      case 'terminal':
        return (
          <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        )
      case 'error':
        return (
          <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      default:
        return null
    }
  }

  const getLabel = () => {
    switch (message.type) {
      case 'thinking':
        return 'Thinking'
      case 'action':
        return 'Action'
      case 'observation':
        return 'Observation'
      case 'terminal':
        return 'Terminal'
      case 'error':
        return 'Error'
      default:
        return null
    }
  }

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'max-w-3xl rounded-lg border',
          message.type === 'terminal' ? 'px-4 py-3' : 'px-4 py-3',
          getMessageStyle()
        )}
      >
        {/* Type indicator */}
        {!isUser && message.type && message.type !== 'text' && (
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-current/10">
            {getIcon()}
            <span className="text-xs font-medium uppercase tracking-wider opacity-70">
              {getLabel()}
            </span>
          </div>
        )}

        {/* Content */}
        {message.type === 'terminal' ? (
          <pre className="whitespace-pre-wrap break-all">{message.content}</pre>
        ) : (
          <div className="prose prose-sm max-w-none prose-p:my-1 prose-pre:my-2 prose-code:text-sm">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Timestamp */}
        <div className={clsx(
          'text-xs mt-2 opacity-50',
          isUser ? 'text-right' : 'text-left'
        )}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
