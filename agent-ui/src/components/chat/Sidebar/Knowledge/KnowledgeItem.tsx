import { memo, useState } from 'react'
import { KnowledgeContent } from '@/types/os'
import { cn } from '@/lib/utils'
import Icon from '@/components/ui/icon'

interface KnowledgeItemProps {
  content: KnowledgeContent
  onDelete: (contentId: string) => void
  onView: (content: KnowledgeContent) => void
}

const getStatusIcon = (status: KnowledgeContent['status']) => {
  switch (status) {
    case 'completed':
      return <span className="text-green-500">✓</span>
    case 'processing':
      return <span className="text-yellow-500">⏳</span>
    case 'failed':
      return <span className="text-red-500">✗</span>
    default:
      return null
  }
}

const getTypeIcon = (type: string) => {
  const lowerType = type.toLowerCase()
  if (lowerType.includes('pdf')) return '📄'
  if (lowerType.includes('url') || lowerType.includes('web')) return '🌐'
  if (lowerType.includes('text') || lowerType.includes('txt')) return '📝'
  if (lowerType.includes('doc')) return '📃'
  if (lowerType.includes('image') || lowerType.includes('img')) return '🖼️'
  return '📄'
}

const formatSize = (bytes?: number) => {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const KnowledgeItem = ({ content, onDelete, onView }: KnowledgeItemProps) => {
  const typeIcon = getTypeIcon(content.type)
  const statusIcon = getStatusIcon(content.status)
  const sizeStr = formatSize(content.size)
  const [showDescription, setShowDescription] = useState(false)

  return (
    <div
      className={cn(
        'group relative mb-1 flex flex-col gap-1 rounded-lg px-3 py-2',
        'bg-background-secondary/50 hover:bg-background-secondary',
        'transition-colors duration-200'
      )}
    >
      {/* Name row */}
      <div className="flex items-center gap-2">
        <span className="text-sm">{typeIcon}</span>
        <span className="flex-1 truncate text-sm font-medium text-primary">
          {content.name}
        </span>
        {statusIcon && <span className="text-xs">{statusIcon}</span>}

        {/* Action buttons */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onView(content)}
            className="rounded p-1 hover:bg-background-secondary/80 transition-colors"
            title="View details"
          >
            <Icon type="eye" size="xs" className="text-muted hover:text-primary" />
          </button>
          <button
            onClick={() => onDelete(content.id)}
            className="rounded p-1 hover:bg-background-secondary/80 transition-colors"
            title="Delete content"
          >
            <Icon type="trash" size="xs" className="text-muted hover:text-destructive" />
          </button>
        </div>
      </div>

      {/* Description (if exists and expanded) */}
      {content.description && (
        <div className="pl-6">
          {showDescription ? (
            <p className="text-xs text-muted/80">{content.description}</p>
          ) : (
            <button
              onClick={() => setShowDescription(true)}
              className="text-xs text-muted/60 hover:text-primary transition-colors"
            >
              Show description
            </button>
          )}
        </div>
      )}

      {/* Info row */}
      <div className="flex items-center gap-2 text-xs text-muted pl-6">
        <span className="uppercase">{content.type}</span>
        {sizeStr && (
          <>
            <span>•</span>
            <span>{sizeStr}</span>
          </>
        )}
        {content.status === 'processing' && (
          <>
            <span>•</span>
            <span className="text-yellow-600">Processing...</span>
          </>
        )}
        {content.status === 'failed' && content.status_message && (
          <>
            <span>•</span>
            <span className="text-red-600 truncate" title={content.status_message}>
              {content.status_message}
            </span>
          </>
        )}
      </div>
    </div>
  )
}

export default memo(KnowledgeItem)

KnowledgeItem.displayName = 'KnowledgeItem'

