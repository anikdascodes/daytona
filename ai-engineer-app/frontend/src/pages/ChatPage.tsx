import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useConfigStore } from '../store/configStore'
import { deleteSession, stopSessionTask } from '../services/api'
import { WebSocketService, WebSocketStatus } from '../services/websocket'
import { Button, StatusBadge, LoadingOverlay } from '../components/ui'
import { ChatMessage, ChatInput } from '../components/chat'
import { TaskProgress } from '../components/task'
import { Terminal } from '../components/terminal'
import { FileBrowser, CodePreview } from '../components/files'
import type { ChatMessage as ChatMessageType, WSEvent, AgentTask, FileInfo } from '../types'

type TabType = 'chat' | 'terminal' | 'files'

export default function ChatPage() {
  const { sessionId, reset } = useConfigStore()
  const navigate = useNavigate()

  // WebSocket state
  const [wsStatus, setWsStatus] = useState<WebSocketStatus>('connecting')
  const wsRef = useRef<WebSocketService | null>(null)

  // Chat state
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [currentTask, setCurrentTask] = useState<AgentTask | null>(null)
  const [isRunning, setIsRunning] = useState(false)

  // Terminal state
  const [terminalOutput, setTerminalOutput] = useState<string[]>([])

  // Files state
  const [files, setFiles] = useState<FileInfo[]>([])
  const [selectedFile, setSelectedFile] = useState<string | undefined>()
  const [fileContent, setFileContent] = useState('')
  const [loadingFile, setLoadingFile] = useState(false)

  // UI state
  const [activeTab, setActiveTab] = useState<TabType>('chat')
  const [showSidebar, setShowSidebar] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize WebSocket
  useEffect(() => {
    if (!sessionId) {
      navigate('/')
      return
    }

    const ws = new WebSocketService(sessionId, {
      onMessage: handleWebSocketMessage,
      onStatusChange: setWsStatus,
      onError: (error) => {
        console.error('WebSocket error:', error)
        addSystemMessage('Connection error. Please refresh the page.')
      },
    })

    ws.connect()
    wsRef.current = ws

    return () => {
      ws.disconnect()
    }
  }, [sessionId])

  // Auto scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = useCallback((message: Omit<ChatMessageType, 'id' | 'timestamp'>) => {
    setMessages(prev => [
      ...prev,
      {
        ...message,
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
      },
    ])
  }, [])

  const addSystemMessage = useCallback((content: string) => {
    addMessage({ role: 'system', content, type: 'text' })
  }, [addMessage])

  const handleWebSocketMessage = useCallback((event: WSEvent) => {
    console.log('WS Event:', event.type, event.data)

    switch (event.type) {
      case 'connected':
        addSystemMessage('Connected to AI Engineer')
        break

      case 'runtime_starting':
        addSystemMessage(event.data.message || 'Starting runtime...')
        break

      case 'runtime_ready':
        addSystemMessage(event.data.message || 'Runtime ready!')
        // Request initial file list
        wsRef.current?.requestFileList()
        break

      case 'status':
        if (event.data.message) {
          addSystemMessage(event.data.message)
        }
        break

      case 'task_started':
        setCurrentTask(event.data.task)
        setIsRunning(true)
        break

      case 'task_planning':
        addMessage({
          role: 'assistant',
          content: event.data.message || 'Analyzing your request...',
          type: 'thinking',
        })
        break

      case 'task_plan_ready':
        if (event.data.task) {
          setCurrentTask(event.data.task)
        }
        break

      case 'task_step_started':
        if (event.data.step) {
          addMessage({
            role: 'assistant',
            content: `Starting: ${event.data.step.description}`,
            type: 'action',
          })
        }
        break

      case 'task_step_completed':
        if (event.data.step) {
          addMessage({
            role: 'assistant',
            content: `Completed: ${event.data.step.description}`,
            type: 'observation',
          })
        }
        break

      case 'task_completed':
        setCurrentTask(event.data.task || null)
        setIsRunning(false)
        addSystemMessage('Task completed successfully!')
        wsRef.current?.requestFileList()
        break

      case 'task_failed':
        setCurrentTask(event.data.task || null)
        setIsRunning(false)
        addMessage({
          role: 'assistant',
          content: `Task failed: ${event.data.error || 'Unknown error'}`,
          type: 'error',
        })
        break

      case 'agent_thinking':
        if (event.data.thought) {
          addMessage({
            role: 'assistant',
            content: event.data.thought,
            type: 'thinking',
          })
        }
        break

      case 'agent_action':
        const actionContent = event.data.action_type === 'command'
          ? `Running command: \`${event.data.command}\``
          : event.data.action_type === 'file_write'
          ? `Writing file: \`${event.data.path}\``
          : event.data.action_type === 'file_read'
          ? `Reading file: \`${event.data.path}\``
          : `Action: ${event.data.action_type}`

        addMessage({
          role: 'assistant',
          content: actionContent,
          type: 'action',
          metadata: event.data,
        })
        break

      case 'agent_observation':
        if (event.data.content) {
          addMessage({
            role: 'assistant',
            content: event.data.content,
            type: 'observation',
          })
        }
        break

      case 'agent_message':
        if (event.data.content) {
          addMessage({
            role: 'assistant',
            content: event.data.content,
            type: 'text',
          })
        }
        break

      case 'terminal_output':
        setTerminalOutput(prev => [
          ...prev,
          event.data.output || '',
        ])
        addMessage({
          role: 'assistant',
          content: event.data.output || '',
          type: 'terminal',
        })
        break

      case 'terminal_error':
        setTerminalOutput(prev => [
          ...prev,
          `Error: ${event.data.error || 'Command failed'}`,
        ])
        break

      case 'file_created':
      case 'file_modified':
        wsRef.current?.requestFileList()
        break

      case 'files_list':
        if (event.data.files) {
          setFiles(buildFileTree(event.data.files))
        }
        break

      case 'file_content':
        setFileContent(event.data.content || '')
        setLoadingFile(false)
        break

      case 'error':
        addMessage({
          role: 'system',
          content: event.data.message || 'An error occurred',
          type: 'error',
        })
        break
    }
  }, [addMessage, addSystemMessage])

  const buildFileTree = (flatFiles: FileInfo[]): FileInfo[] => {
    // Simple tree builder - for now just return flat list
    // TODO: Build proper tree structure
    return flatFiles.filter(f => f.path && f.name)
  }

  const handleSendMessage = (content: string) => {
    addMessage({
      role: 'user',
      content,
      type: 'text',
    })
    wsRef.current?.sendChatMessage(content)
  }

  const handleStopTask = async () => {
    if (sessionId) {
      try {
        await stopSessionTask(sessionId)
        wsRef.current?.stopTask()
      } catch (error) {
        console.error('Failed to stop task:', error)
      }
    }
  }

  const handleTerminalCommand = (command: string) => {
    wsRef.current?.sendTerminalCommand(command)
    setTerminalOutput(prev => [...prev, `$ ${command}`])
  }

  const handleSelectFile = (path: string) => {
    setSelectedFile(path)
    setLoadingFile(true)
    wsRef.current?.requestFileContent(path)
  }

  const handleEndSession = async () => {
    if (confirm('Are you sure you want to end this session?')) {
      if (sessionId) {
        try {
          await deleteSession(sessionId)
        } catch (error) {
          console.error('Failed to delete session:', error)
        }
      }
      wsRef.current?.disconnect()
      reset()
      navigate('/')
    }
  }

  const getStatusIndicator = () => {
    switch (wsStatus) {
      case 'connected':
        return <StatusBadge status="healthy" label="Connected" size="sm" />
      case 'connecting':
        return <StatusBadge status="pending" label="Connecting..." size="sm" pulse />
      case 'disconnected':
        return <StatusBadge status="unhealthy" label="Disconnected" size="sm" />
      case 'error':
        return <StatusBadge status="failed" label="Error" size="sm" />
    }
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-gray-900">AI Engineer</h1>
            </div>
            <div className="h-6 w-px bg-gray-300" />
            {getStatusIndicator()}
            {sessionId && (
              <span className="text-sm text-gray-500">
                Session: {sessionId.slice(0, 8)}...
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
              </svg>
            </Button>
            <Button variant="danger" size="sm" onClick={handleEndSession}>
              End Session
            </Button>
          </div>
        </div>
      </header>

      {/* Task Progress Bar */}
      <TaskProgress task={currentTask} isRunning={isRunning} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Main Panel */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Tabs */}
          <div className="bg-white border-b">
            <div className="flex">
              {(['chat', 'terminal'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {tab === 'chat' ? 'Chat' : 'Terminal'}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'chat' ? (
              <div className="h-full flex flex-col">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {wsStatus === 'connecting' && (
                    <LoadingOverlay message="Connecting to session..." />
                  )}

                  {messages.length === 0 && wsStatus === 'connected' && (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Build</h3>
                      <p className="text-gray-600 max-w-md mx-auto">
                        Describe what you want to build, fix, or modify. The AI will plan and execute the task automatically.
                      </p>
                      <div className="mt-6 space-y-2 text-sm text-gray-500">
                        <p>Try something like:</p>
                        <ul className="space-y-1">
                          <li>"Create a React todo app with TypeScript"</li>
                          <li>"Fix the bug in server.py where users can't login"</li>
                          <li>"Add unit tests for the authentication module"</li>
                        </ul>
                      </div>
                    </div>
                  )}

                  {messages.map(msg => (
                    <ChatMessage key={msg.id} message={msg} />
                  ))}

                  <div ref={messagesEndRef} />
                </div>

                {/* Chat Input */}
                <ChatInput
                  onSend={handleSendMessage}
                  onStop={handleStopTask}
                  disabled={wsStatus !== 'connected'}
                  isRunning={isRunning}
                />
              </div>
            ) : (
              <div className="h-full p-4">
                <Terminal output={terminalOutput} onCommand={handleTerminalCommand} />
              </div>
            )}
          </div>
        </div>

        {/* Sidebar - Files */}
        {showSidebar && (
          <div className="w-80 border-l bg-white flex flex-col">
            {/* Sidebar Header */}
            <div className="px-4 py-3 border-b flex items-center justify-between">
              <h3 className="font-medium text-gray-900">Files</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => wsRef.current?.requestFileList()}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </Button>
            </div>

            {/* File Browser */}
            <div className="flex-1 overflow-y-auto border-b">
              <FileBrowser
                files={files}
                onSelectFile={handleSelectFile}
                selectedFile={selectedFile}
              />
            </div>

            {/* Code Preview */}
            <div className="h-64 overflow-hidden">
              <CodePreview
                content={fileContent}
                path={selectedFile || ''}
                loading={loadingFile}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
