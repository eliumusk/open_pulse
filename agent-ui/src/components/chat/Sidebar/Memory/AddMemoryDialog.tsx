'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { TextArea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Icon from '@/components/ui/icon'
import { toast } from 'sonner'
import { MemoryCreateInput } from '@/types/os'

interface AddMemoryDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: MemoryCreateInput) => Promise<void>
}

const AddMemoryDialog = ({ open, onOpenChange, onSubmit }: AddMemoryDialogProps) => {
  const [memory, setMemory] = useState('')
  const [topicsInput, setTopicsInput] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!memory.trim()) {
      toast.error('Please enter memory content')
      return
    }

    try {
      setIsSubmitting(true)
      const topics = topicsInput
        .split(',')
        .map((t) => t.trim())
        .filter((t) => t.length > 0)

      await onSubmit({
        memory: memory.trim(),
        topics: topics.length > 0 ? topics : undefined
      })

      // Reset form
      setMemory('')
      setTopicsInput('')
      onOpenChange(false)
    } catch (error) {
      console.error('Submit error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setMemory('')
    setTopicsInput('')
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">
            Add new memory
          </DialogTitle>
          <p className="text-sm text-muted">
            Store information about the user for future reference
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
              value={memory}
              onChange={(e) => setMemory(e.target.value)}
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
            disabled={isSubmitting || !memory.trim()}
            className="uppercase"
          >
            {isSubmitting ? 'Adding...' : 'Add Memory'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default AddMemoryDialog

