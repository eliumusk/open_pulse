'use client'

import { useState, useRef, useCallback } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { TextArea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import Icon from '@/components/ui/icon'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface UploadFileDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUpload: (data: {
    file?: File
    url?: string
    name: string
    description: string
  }) => Promise<void>
}

const UploadFileDialog = ({ open, onOpenChange, onUpload }: UploadFileDialogProps) => {
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile)
    if (!name) {
      setName(selectedFile.name)
    }
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFileSelect(droppedFile)
    }
  }, [name])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleSubmit = async () => {
    if (!file && !url) {
      toast.error('Please select a file or enter a URL')
      return
    }

    if (!name.trim()) {
      toast.error('Please enter a name')
      return
    }

    try {
      setIsUploading(true)
      await onUpload({
        file: file || undefined,
        url: url || undefined,
        name: name.trim(),
        description: description.trim()
      })
      
      // Reset form
      setFile(null)
      setUrl('')
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
    setFile(null)
    setUrl('')
    setName('')
    setDescription('')
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">
            Add file content to the knowledge base
          </DialogTitle>
          <p className="text-sm text-muted">You can add multiple files</p>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-6 py-4">
          {/* Left side - File upload */}
          <div className="space-y-4">
            <div
              className={cn(
                'flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8',
                'transition-colors duration-200',
                isDragging
                  ? 'border-primary bg-primary/5'
                  : 'border-primary/20 bg-background-secondary/30'
              )}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <Icon type="folder" size="lg" className="mb-4 text-muted" />
              <p className="mb-4 text-sm text-muted">Drag & drop files to upload</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                className="uppercase"
              >
                Select File
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={(e) => {
                  const selectedFile = e.target.files?.[0]
                  if (selectedFile) {
                    handleFileSelect(selectedFile)
                  }
                }}
              />
            </div>

            {file && (
              <div className="flex items-center gap-2 rounded-lg bg-background-secondary/50 p-3">
                <Icon type="file" size="sm" />
                <span className="flex-1 truncate text-sm">{file.name}</span>
                <button
                  onClick={() => setFile(null)}
                  className="text-destructive hover:text-destructive/80"
                >
                  <Icon type="trash" size="xs" />
                </button>
              </div>
            )}

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-primary/10" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted">OR</span>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-xs uppercase text-muted">Enter File URL</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="https://example.com/file.pdf"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1"
                  disabled={!!file}
                />
              </div>
            </div>
          </div>

          {/* Right side - Metadata */}
          <div className="space-y-4">
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
            disabled={isUploading || (!file && !url) || !name.trim()}
            className="uppercase"
          >
            {isUploading ? 'Uploading...' : 'Save'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default UploadFileDialog

