import clsx from 'clsx'

type Status = 'healthy' | 'unhealthy' | 'pending' | 'running' | 'completed' | 'failed'

interface StatusBadgeProps {
  status: Status
  label?: string
  size?: 'sm' | 'md'
  pulse?: boolean
}

const statusConfig: Record<Status, { bg: string; text: string; dot: string }> = {
  healthy: { bg: 'bg-green-100', text: 'text-green-800', dot: 'bg-green-500' },
  unhealthy: { bg: 'bg-red-100', text: 'text-red-800', dot: 'bg-red-500' },
  pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', dot: 'bg-yellow-500' },
  running: { bg: 'bg-blue-100', text: 'text-blue-800', dot: 'bg-blue-500' },
  completed: { bg: 'bg-green-100', text: 'text-green-800', dot: 'bg-green-500' },
  failed: { bg: 'bg-red-100', text: 'text-red-800', dot: 'bg-red-500' },
}

const statusLabels: Record<Status, string> = {
  healthy: 'Healthy',
  unhealthy: 'Unhealthy',
  pending: 'Pending',
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
}

export function StatusBadge({ status, label, size = 'md', pulse = false }: StatusBadgeProps) {
  const config = statusConfig[status]
  const displayLabel = label || statusLabels[status]

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full font-medium',
        config.bg,
        config.text,
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
      )}
    >
      <span
        className={clsx(
          'rounded-full',
          config.dot,
          size === 'sm' ? 'w-1.5 h-1.5 mr-1.5' : 'w-2 h-2 mr-2',
          pulse && 'animate-pulse'
        )}
      />
      {displayLabel}
    </span>
  )
}
