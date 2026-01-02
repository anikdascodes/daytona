import { useState } from 'react'
import clsx from 'clsx'
import type { FileInfo } from '../../types'

interface FileBrowserProps {
  files: FileInfo[]
  onSelectFile: (path: string) => void
  selectedFile?: string
}

export function FileBrowser({ files, onSelectFile, selectedFile }: FileBrowserProps) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set())

  const toggleDir = (path: string) => {
    setExpandedDirs(prev => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  const getFileIcon = (file: FileInfo) => {
    if (file.is_dir) {
      return expandedDirs.has(file.path) ? (
        <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M2 6a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1H8a3 3 0 00-3 3v1.5a1.5 1.5 0 01-3 0V6z" clipRule="evenodd" />
          <path d="M6 12a2 2 0 012-2h8a2 2 0 012 2v2a2 2 0 01-2 2H2h2a2 2 0 002-2v-2z" />
        </svg>
      ) : (
        <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
        </svg>
      )
    }

    const ext = file.name.split('.').pop()?.toLowerCase()
    const iconColors: Record<string, string> = {
      ts: 'text-blue-500',
      tsx: 'text-blue-500',
      js: 'text-yellow-500',
      jsx: 'text-yellow-500',
      py: 'text-green-500',
      json: 'text-orange-500',
      md: 'text-gray-500',
      css: 'text-pink-500',
      html: 'text-red-500',
    }

    return (
      <svg className={clsx('w-4 h-4', iconColors[ext || ''] || 'text-gray-400')} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    )
  }

  const renderFile = (file: FileInfo, depth: number = 0) => {
    const isExpanded = expandedDirs.has(file.path)
    const isSelected = selectedFile === file.path

    return (
      <div key={file.path}>
        <button
          onClick={() => file.is_dir ? toggleDir(file.path) : onSelectFile(file.path)}
          className={clsx(
            'w-full flex items-center gap-2 px-2 py-1.5 text-left text-sm hover:bg-gray-100 rounded transition-colors',
            isSelected && 'bg-blue-50 text-blue-700'
          )}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
        >
          {file.is_dir && (
            <svg
              className={clsx('w-3 h-3 text-gray-400 transition-transform', isExpanded && 'rotate-90')}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          )}
          {!file.is_dir && <span className="w-3" />}
          {getFileIcon(file)}
          <span className="truncate">{file.name}</span>
        </button>

        {file.is_dir && isExpanded && file.children && (
          <div>
            {file.children.map(child => renderFile(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 text-sm">
        <svg className="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        No files yet
      </div>
    )
  }

  return (
    <div className="py-2">
      {files.map(file => renderFile(file))}
    </div>
  )
}
