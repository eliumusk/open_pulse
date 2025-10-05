'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { TextArea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import Icon from '@/components/ui/icon'
import { toast } from 'sonner'

interface UploadTextDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUpload: (data: {
    text: string
    name: string
    description: string
  }) => Promise<void>
  type: 'web' | 'text'
}

const UploadTextDialog = ({ open, onOpenChange, onUpload, type }: UploadTextDialogProps) => {
  const [text, setText] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isUploading, setIsUploading] = useState(false)

  const isWeb = type === 'web'
  const title = isWeb ? 'Add web content to the knowledge base' : 'Add text content to the knowledge base'
  const placeholder = isWeb ? 'https://example.com' : 'Enter your text content here...'
  const label = isWeb ? 'URL' : 'Text Content'

  const handleSubmit = async () => {
    if (!text.trim()) {
      toast.error(`Please enter ${isWeb ? 'a URL' : 'text content'}`)
      return
    }

    if (!name.trim()) {
      toast.error('Please enter a name')
      return
    }

    try {
      setIsUploading(true)
      await onUpload({
        text: text.trim(),
        name: name.trim(),
        description: description.trim()
      })
      
      // Reset form
      setText('')
      setName('')
      setDescription('')
      onOpenChange(false)
    } catch (error) {
      console.error('Upload error:', error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleCancel = () => {
    setText('')
    setName('')
    setDescription('')
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">{title}</DialogTitle>
          <p className="text-sm text-muted">
            {isWeb ? 'Add content from a web URL' : 'Add raw text content'}
          </p>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label className="text-xs uppercase text-muted">
              <Icon type={isWeb ? 'globe' : 'text'} size="xs" className="mr-1 inline" />
              {label}
            </Label>
            {isWeb ? (
              <Input
                placeholder={placeholder}
                value={text}
                onChange={(e) => setText(e.target.value)}
                type="url"
              />
            ) : (
              <TextArea
                placeholder={placeholder}
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="font-mono text-sm"
              />
            )}
          </div>

          <div className="space-y-2">
            <Label className="text-xs uppercase text-muted">
              <Icon type="text" size="xs" className="mr-1 inline" />
              Name
            </Label>
            <Input
              placeholder="Enter name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs uppercase text-muted">
              <Icon type="list" size="xs" className="mr-1 inline" />
              Description
            </Label>
            <TextArea
              placeholder="Enter description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="resize-none"
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 border-t border-primary/10 pt-4">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isUploading}
            className="uppercase"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isUploading || !text.trim() || !name.trim()}
            className="uppercase"
          >
            {isUploading ? 'Uploading...' : 'Save'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default UploadTextDialog

