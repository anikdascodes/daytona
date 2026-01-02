import { useEffect, useState } from 'react'

interface CodePreviewProps {
  content: string
  path: string
  loading?: boolean
}

export function CodePreview({ content, path, loading }: CodePreviewProps) {
  const [lines, setLines] = useState<string[]>([])

  useEffect(() => {
    setLines(content.split('\n'))
  }, [content])

  const getLanguage = () => {
    const ext = path.split('.').pop()?.toLowerCase()
    const languages: Record<string, string> = {
      ts: 'TypeScript',
      tsx: 'TypeScript React',
      js: 'JavaScript',
      jsx: 'JavaScript React',
      py: 'Python',
      json: 'JSON',
      md: 'Markdown',
      css: 'CSS',
      html: 'HTML',
      sh: 'Shell',
      yaml: 'YAML',
      yml: 'YAML',
    }
    return languages[ext || ''] || 'Plain Text'
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <svg className="w-6 h-6 animate-spin mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Loading...
      </div>
    )
  }

  if (!content) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-500">
        <svg className="w-12 h-12 mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p>Select a file to preview</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <span className="text-sm font-medium text-gray-700 truncate">
            {path.split('/').pop()}
          </span>
        </div>
        <span className="text-xs text-gray-500">{getLanguage()}</span>
      </div>

      {/* Code */}
      <div className="flex-1 overflow-auto">
        <pre className="p-4 text-sm font-mono leading-relaxed">
          <code>
            {lines.map((line, index) => (
              <div key={index} className="flex">
                <span className="w-12 pr-4 text-right text-gray-400 select-none">
                  {index + 1}
                </span>
                <span className="flex-1 whitespace-pre-wrap break-all">
                  {line || ' '}
                </span>
              </div>
            ))}
          </code>
        </pre>
      </div>
    </div>
  )
}
