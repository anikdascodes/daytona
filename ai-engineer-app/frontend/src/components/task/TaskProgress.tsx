import type { AgentTask } from '../../types'
import { StatusBadge } from '../ui'
import clsx from 'clsx'

interface TaskProgressProps {
  task: AgentTask | null
  isRunning: boolean
}

export function TaskProgress({ task, isRunning }: TaskProgressProps) {
  if (!task) return null

  const getStatusDisplay = () => {
    switch (task.status) {
      case 'planning':
        return { label: 'Planning', status: 'running' as const }
      case 'executing':
        return { label: 'Executing', status: 'running' as const }
      case 'completed':
        return { label: 'Completed', status: 'completed' as const }
      case 'failed':
        return { label: 'Failed', status: 'failed' as const }
      default:
        return { label: 'Pending', status: 'pending' as const }
    }
  }

  const { label, status } = getStatusDisplay()

  return (
    <div className="bg-white border-b px-4 py-3">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isRunning && (
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            )}
            <div>
              <p className="text-sm font-medium text-gray-900 truncate max-w-md">
                {task.description}
              </p>
              <p className="text-xs text-gray-500">
                Task ID: {task.id.slice(0, 8)}...
              </p>
            </div>
          </div>
          <StatusBadge status={status} label={label} pulse={isRunning} />
        </div>

        {/* Progress Steps */}
        {task.plan.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              {task.plan.map((step, index) => (
                <div
                  key={step.id}
                  className={clsx(
                    'flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap',
                    {
                      'bg-green-100 text-green-800': step.status === 'completed',
                      'bg-blue-100 text-blue-800': step.status === 'executing',
                      'bg-gray-100 text-gray-600': step.status === 'pending',
                      'bg-red-100 text-red-800': step.status === 'failed',
                    }
                  )}
                >
                  <span className="w-5 h-5 rounded-full bg-current/10 flex items-center justify-center">
                    {step.status === 'completed' ? (
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : step.status === 'executing' ? (
                      <svg className="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    ) : (
                      <span>{index + 1}</span>
                    )}
                  </span>
                  <span className="truncate max-w-32">{step.description}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
