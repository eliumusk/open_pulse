'use client'

import { useState, useRef, useCallback } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { TextArea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import Icon from '@/components/ui/icon'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface UploadFileDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onUpload: (data: {
    file?: File
    url?: string
    text_content?: string
    name: string
    description: string
    reader_id?: string
    chunker?: string
  }) => Promise<void>
}

const UploadFileDialog = ({ open, onOpenChange, onUpload }: UploadFileDialogProps) => {
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState('')
  const [textContent, setTextContent] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [readerId, setReaderId] = useState<string>('auto')
  const [chunker, setChunker] = useState<string>('default')
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
    if (!file && !url && !textContent) {
      toast.error('Please select a file, enter a URL, or provide text content')
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
        text_content: textContent || undefined,
        name: name.trim(),
        description: description.trim(),
        reader_id: readerId === 'auto' ? undefined : readerId,
        chunker: chunker === 'default' ? undefined : chunker
      })

      // Reset form
      setFile(null)
      setUrl('')
      setTextContent('')
      setName('')
      setDescription('')
      setReaderId('auto')
      setChunker('default')
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
    setTextContent('')
    setName('')
    setDescription('')
    setReaderId('auto')
    setChunker('default')
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">
            Add Content to Knowledge Base
          </DialogTitle>
          <p className="text-sm text-muted">
            Upload files, enter URLs, or paste text content. The system will automatically detect and optimize processing.
          </p>
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
              <p className="mb-2 text-sm text-muted">Drag & drop files to upload</p>
              <p className="mb-4 text-xs text-muted/70">
                Supports: PDF, DOCX, JSON, CSV, MD, TXT, etc.
              </p>
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
                accept=".pdf,.docx,.doc,.json,.csv,.md,.txt"
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
              <Label className="text-xs uppercase text-muted">Enter URL</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="https://example.com/file.pdf or https://youtube.com/..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1"
                  disabled={!!file || !!textContent}
                />
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-primary/10" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted">OR</span>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-xs uppercase text-muted">Paste Text Content</Label>
              <TextArea
                placeholder="Paste your text content here..."
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                className="resize-none min-h-[100px]"
                disabled={!!file || !!url}
              />
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

            {/* Advanced Options */}
            <div className="space-y-3 rounded-lg border border-primary/10 bg-background-secondary/30 p-4">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex w-full items-center justify-between text-sm font-medium text-muted hover:text-secondary transition-colors"
              >
                <span className="flex items-center gap-2">
                  <Icon type="hammer" size="xs" />
                  Advanced Options
                </span>
                <Icon
                  type="chevron-down"
                  size="xs"
                  className={cn(
                    'transition-transform duration-200',
                    showAdvanced && 'rotate-180'
                  )}
                />
              </button>

              {showAdvanced && (
                <div className="space-y-3 pt-2">
                  <div className="space-y-2">
                    <Label className="text-xs text-muted">
                      Reader Type
                    </Label>
                    <Select value={readerId} onValueChange={setReaderId}>
                      <SelectTrigger>
                        <SelectValue placeholder="Auto-detect (recommended)" />
                      </SelectTrigger>
                      <SelectContent
                        className="
                          backdrop-blur-md
                          bg-zinc-800/80 dark:bg-zinc-950/70
                          text-popover-foreground
                          border border-border/40
                          shadow-lg rounded-xl
                        "
                      >
                        <SelectItem value="auto">Auto-detect</SelectItem>
                        <SelectItem value="PDFReader">PDF Reader</SelectItem>
                        <SelectItem value="CSVReader">CSV Reader</SelectItem>
                        <SelectItem value="JSONReader">JSON Reader</SelectItem>
                        <SelectItem value="MarkdownReader">Markdown Reader</SelectItem>
                        <SelectItem value="TextReader">Text Reader</SelectItem>
                        <SelectItem value="WebsiteReader">Website Reader</SelectItem>
                        <SelectItem value="YouTubeReader">YouTube Reader</SelectItem>
                        <SelectItem value="ArxivReader">arXiv Reader</SelectItem>
                        <SelectItem value="WikipediaReader">Wikipedia Reader</SelectItem>
                        <SelectItem value="WebSearchReader">Web Search Reader</SelectItem>
                        <SelectItem value="FirecrawlReader">Firecrawl Reader</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted/70">
                      Leave as auto-detect for automatic format detection
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs text-muted">
                      Chunking Strategy
                    </Label>
                    <Select value={chunker} onValueChange={setChunker}>
                      <SelectTrigger>
                        <SelectValue placeholder="Default chunking" />
                      </SelectTrigger>
                      <SelectContent
                        className="
                          backdrop-blur-md
                          bg-zinc-800/80 dark:bg-zinc-950/70
                          text-popover-foreground
                          border border-border/40
                          shadow-lg rounded-xl
                        "
                      >                        <SelectItem value="default">Default</SelectItem>
                        <SelectItem value="FixedSizeChunker">Fixed Size Chunker</SelectItem>
                        <SelectItem value="SemanticChunker">Semantic Chunker</SelectItem>
                        <SelectItem value="RecursiveChunker">Recursive Chunker</SelectItem>
                        <SelectItem value="DocumentChunker">Document Chunker</SelectItem>
                        <SelectItem value="RowChunker">CSV Row Chunker</SelectItem>
                        <SelectItem value="MarkdownChunker">Markdown Chunker</SelectItem>
                        <SelectItem value="AgenticChunker">Agentic Chunker</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted/70">
                      Controls how content is split for processing
                    </p>
                  </div>
                </div>
              )}
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
            variant="outline"
            onClick={handleSubmit}
            disabled={isUploading || (!file && !url && !textContent) || !name.trim()}
            className="uppercase"
          >
            {isUploading ? 'Processing...' : 'Add to Knowledge Base'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default UploadFileDialog

