'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { TextArea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Icon from '@/components/ui/icon'
import { toast } from 'sonner'
import { Memory, MemoryUpdateInput } from '@/types/os'

interface EditMemoryDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  memory: Memory | null
  onSubmit: (memoryId: string, data: MemoryUpdateInput) => Promise<void>
}

const EditMemoryDialog = ({
  open,
  onOpenChange,
  memory,
  onSubmit
}: EditMemoryDialogProps) => {
  const [memoryContent, setMemoryContent] = useState('')
  const [topicsInput, setTopicsInput] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (memory) {
      setMemoryContent(memory.memory)
      setTopicsInput(memory.topics ? memory.topics.join(', ') : '')
    }
  }, [memory])

  const handleSubmit = async () => {
    if (!memory) return

    if (!memoryContent.trim()) {
      toast.error('Please enter memory content')
      return
    }

    try {
      setIsSubmitting(true)
      const topics = topicsInput
        .split(',')
        .map((t) => t.trim())
        .filter((t) => t.length > 0)

      await onSubmit(memory.memory_id, {
        memory: memoryContent.trim(),
        topics: topics.length > 0 ? topics : undefined
      })

      onOpenChange(false)
    } catch (error) {
      console.error('Submit error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    onOpenChange(false)
  }

  if (!memory) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">
            Edit memory
          </DialogTitle>
          <p className="text-sm text-muted">
            Update the memory content or topics
          </p>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label className="text-xs uppercase text-muted">
              <Icon type="text" size="xs" className="mr-1 inline" />
              Memory Content *
            </Label>
            <TextArea
              placeholder="e.g., User likes Tesla cars"
              value={memoryContent}
              onChange={(e) => setMemoryContent(e.target.value)}
              className="min-h-[100px]"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs uppercase text-muted">
              <Icon type="list" size="xs" className="mr-1 inline" />
              Topics (optional)
            </Label>
            <Input
              placeholder="e.g., interests, hobbies (comma-separated)"
              value={topicsInput}
              onChange={(e) => setTopicsInput(e.target.value)}
            />
            <p className="text-xs text-muted/70">
              Separate multiple topics with commas
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-2 border-t border-primary/10 pt-4">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="uppercase"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !memoryContent.trim()}
            className="uppercase"
          >
            {isSubmitting ? 'Updating...' : 'Update Memory'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default EditMemoryDialog

