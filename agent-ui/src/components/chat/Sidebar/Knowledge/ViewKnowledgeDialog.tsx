'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { KnowledgeContent } from '@/types/os'
import Icon from '@/components/ui/icon'

interface ViewKnowledgeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  content: KnowledgeContent | null
}

const getStatusBadge = (status: KnowledgeContent['status']) => {
  switch (status) {
    case 'completed':
      return (
        <span className="inline-flex items-center gap-1 rounded-md bg-green-500/10 px-2 py-1 text-xs text-green-600">
          ✓ Completed
        </span>
      )
    case 'processing':
      return (
        <span className="inline-flex items-center gap-1 rounded-md bg-yellow-500/10 px-2 py-1 text-xs text-yellow-600">
          ⏳ Processing
        </span>
      )
    case 'failed':
      return (
        <span className="inline-flex items-center gap-1 rounded-md bg-red-500/10 px-2 py-1 text-xs text-red-600">
          ✗ Failed
        </span>
      )
    default:
      return null
  }
}

const formatSize = (bytes?: number) => {
  if (!bytes) return 'N/A'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

const ViewKnowledgeDialog = ({
  open,
  onOpenChange,
  content
}: ViewKnowledgeDialogProps) => {
  if (!content) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold flex items-center gap-2">
            <Icon type="file" size="sm" />
            Knowledge Content Details
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Name */}
          <div className="space-y-1">
            <label className="text-xs font-medium uppercase text-muted">Name</label>
            <p className="text-sm text-primary">{content.name}</p>
          </div>

          {/* Description */}
          {content.description && (
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Description</label>
              <p className="text-sm text-primary">{content.description}</p>
            </div>
          )}

          {/* Status */}
          <div className="space-y-1">
            <label className="text-xs font-medium uppercase text-muted">Status</label>
            <div>{getStatusBadge(content.status)}</div>
            {content.status === 'failed' && content.status_message && (
              <p className="text-xs text-red-600 mt-1">{content.status_message}</p>
            )}
          </div>

          {/* Type and Size */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Type</label>
              <p className="text-sm text-primary uppercase">{content.type}</p>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Size</label>
              <p className="text-sm text-primary">{formatSize(content.size)}</p>
            </div>
          </div>

          {/* Linked To (URL) */}
          {content.linked_to && (
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Source URL</label>
              <a
                href={content.linked_to}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline break-all"
              >
                {content.linked_to}
              </a>
            </div>
          )}

          {/* Metadata */}
          {content.metadata && Object.keys(content.metadata).length > 0 && (
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Metadata</label>
              <pre className="text-xs bg-background-secondary/50 p-2 rounded overflow-auto max-h-32">
                {JSON.stringify(content.metadata, null, 2)}
              </pre>
            </div>
          )}

          {/* Timestamps */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Created At</label>
              <p className="text-xs text-muted">{formatDate(content.created_at)}</p>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Updated At</label>
              <p className="text-xs text-muted">{formatDate(content.updated_at)}</p>
            </div>
          </div>

          {/* Access Count */}
          {content.access_count !== undefined && (
            <div className="space-y-1">
              <label className="text-xs font-medium uppercase text-muted">Access Count</label>
              <p className="text-sm text-primary">{content.access_count}</p>
            </div>
          )}

          {/* ID */}
          <div className="space-y-1">
            <label className="text-xs font-medium uppercase text-muted">Content ID</label>
            <p className="text-xs font-mono text-muted break-all">{content.id}</p>
          </div>
        </div>

        <div className="flex justify-end border-t border-primary/10 pt-4">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="uppercase"
          >
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default ViewKnowledgeDialog

