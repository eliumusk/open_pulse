'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

type ContentType = 'file' | 'web' | 'text'

interface AddKnowledgeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSelectType: (type: ContentType) => void
}

const contentTypes: Array<{
  type: ContentType
  label: string
  icon: string
  description: string
}> = [
  {
    type: 'file',
    label: 'FILE',
    icon: '📄',
    description: 'Upload files from your computer'
  },
  {
    type: 'web',
    label: 'WEB',
    icon: '🌐',
    description: 'Add content from a URL'
  },
  {
    type: 'text',
    label: 'TEXT',
    icon: '📝',
    description: 'Add raw text content'
  }
]

const AddKnowledgeDialog = ({
  open,
  onOpenChange,
  onSelectType
}: AddKnowledgeDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">
            Select content type to add to the knowledge base
          </DialogTitle>
          <p className="text-sm text-muted">
            You can add different types of content
          </p>
        </DialogHeader>
        <div className="grid grid-cols-3 gap-3 py-4">
          {contentTypes.map((item) => (
            <button
              key={item.type}
              onClick={() => {
                onSelectType(item.type)
                onOpenChange(false)
              }}
              className={cn(
                'flex flex-col items-center gap-2 rounded-lg border border-primary/15',
                'bg-background-secondary/30 p-4 transition-all duration-200',
                'hover:bg-background-secondary hover:border-primary/30',
                'focus:outline-none focus:ring-2 focus:ring-primary/50'
              )}
            >
              <span className="text-2xl">{item.icon}</span>
              <span className="text-xs font-medium uppercase">{item.label}</span>
            </button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default AddKnowledgeDialog

