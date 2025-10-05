import { memo, useState } from 'react'
import { Memory } from '@/types/os'
import { cn } from '@/lib/utils'
import Icon from '@/components/ui/icon'

interface MemoryItemProps {
  memory: Memory
  onEdit: (memory: Memory) => void
  onDelete: (memoryId: string) => void
}

// Simple time ago formatter
const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  const weeks = Math.floor(days / 7)
  if (weeks < 4) return `${weeks}w ago`
  const months = Math.floor(days / 30)
  if (months < 12) return `${months}mo ago`
  const years = Math.floor(days / 365)
  return `${years}y ago`
}

const MemoryItem = ({ memory, onEdit, onDelete }: MemoryItemProps) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const maxLength = 100
  const needsTruncation = memory.memory.length > maxLength

  const displayText = needsTruncation && !isExpanded
    ? memory.memory.slice(0, maxLength) + '...'
    : memory.memory

  const formattedDate = memory.updated_at ? formatTimeAgo(memory.updated_at) : ''

  return (
    <div
      className={cn(
        'group relative mb-1 flex flex-col gap-2 rounded-lg px-3 py-2',
        'bg-background-secondary/50 hover:bg-background-secondary',
        'transition-colors duration-200'
      )}
    >
      {/* Memory content */}
      <div className="flex items-start gap-2">
        <span className="text-sm">💭</span>
        <div className="flex-1">
          <p className="text-sm text-primary leading-relaxed">
            {displayText}
          </p>
          {needsTruncation && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-1 text-xs text-muted hover:text-primary transition-colors"
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      </div>

      {/* Topics */}
      {memory.topics && memory.topics.length > 0 && (
        <div className="flex flex-wrap gap-1 pl-6">
          {memory.topics.map((topic, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1 rounded-md bg-primary/10 px-2 py-0.5 text-xs text-primary"
            >
              🏷️ {topic}
            </span>
          ))}
        </div>
      )}

      {/* Footer with date and actions */}
      <div className="flex items-center justify-between pl-6">
        <span className="text-xs text-muted">
          📅 {formattedDate}
        </span>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onEdit(memory)}
            className="rounded p-1 hover:bg-background-secondary/80 transition-colors"
            title="Edit memory"
          >
            <Icon type="edit" size="xs" className="text-muted hover:text-primary" />
          </button>
          <button
            onClick={() => onDelete(memory.memory_id)}
            className="rounded p-1 hover:bg-background-secondary/80 transition-colors"
            title="Delete memory"
          >
            <Icon type="trash" size="xs" className="text-muted hover:text-destructive" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default memo(MemoryItem)

MemoryItem.displayName = 'MemoryItem'

