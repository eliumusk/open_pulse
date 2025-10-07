'use client'

import { useState } from 'react'
import { X, ExternalLink, CheckCircle2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface NewsletterNotificationCardProps {
  notificationId: string
  coverImageUrl?: string
  content: string
  onClose: () => void
  onViewFull?: () => void
}

export function NewsletterNotificationCard({
  notificationId,
  coverImageUrl,
  content,
  onClose,
  onViewFull
}: NewsletterNotificationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Fix image URL: replace 0.0.0.0 with localhost
  const fixedImageUrl = coverImageUrl?.replace('0.0.0.0', 'localhost')

  // Extract title from content (first non-empty line)
  const getTitle = () => {
    const lines = content.split('\n').filter((line) => line.trim())
    return lines[0]?.replace(/^#+\s*/, '') || 'Newsletter Generated'
  }

  // Get preview text (first 150 characters)
  const getPreview = () => {
    const cleanContent = content
      .replace(/^#+\s*.+$/gm, '') // Remove headers
      .replace(/\*\*/g, '') // Remove bold markers
      .trim()
    return cleanContent.substring(0, 150) + (cleanContent.length > 150 ? '...' : '')
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.95 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="fixed bottom-6 right-6 z-50 w-96 overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-2xl"
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-gray-200 dark:border-gray-700 bg-green-50 dark:bg-green-900/20 p-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">Newsletter Ready!</h3>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-gray-500 dark:text-gray-400 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
            aria-label="Close notification"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Cover Image */}
        {fixedImageUrl && (
          <div className="relative w-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center" style={{ minHeight: '200px', maxHeight: '300px' }}>
            <img
              src={fixedImageUrl}
              alt="Newsletter cover"
              className="w-full h-auto max-h-[300px] object-contain"
              onError={(e) => {
                console.error('Failed to load image:', fixedImageUrl)
                e.currentTarget.parentElement!.style.display = 'none'
              }}
            />
          </div>
        )}

        {/* Content */}
        <div className="p-4 bg-white dark:bg-gray-900">
          <h4 className="mb-2 font-medium text-gray-900 dark:text-gray-100">{getTitle()}</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">{getPreview()}</p>
        </div>

        {/* Actions */}
        <div className="flex gap-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-3">
          <button
            onClick={() => {
              if (onViewFull) {
                onViewFull()
              }
              setIsExpanded(!isExpanded)
            }}
            className="flex flex-1 items-center justify-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            <ExternalLink className="h-4 w-4" />
            View Full Newsletter
          </button>
          <button
            onClick={onClose}
            className="rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 transition-colors hover:bg-gray-100 dark:hover:bg-gray-600"
          >
            Dismiss
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

// Full content modal (optional)
interface NewsletterModalProps {
  isOpen: boolean
  onClose: () => void
  coverImageUrl?: string
  content: string
}

export function NewsletterModal({
  isOpen,
  onClose,
  coverImageUrl,
  content
}: NewsletterModalProps) {
  if (!isOpen) return null

  // Fix image URL: replace 0.0.0.0 with localhost
  const fixedImageUrl = coverImageUrl?.replace('0.0.0.0', 'localhost')

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="max-h-[90vh] w-full max-w-3xl overflow-hidden rounded-lg border border-border bg-background shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border p-4">
            <h2 className="text-xl font-semibold">Your Newsletter</h2>
            <button
              onClick={onClose}
              className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Content */}
          <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 80px)' }}>
            {fixedImageUrl && (
              <img
                src={fixedImageUrl}
                alt="Newsletter cover"
                className="mb-6 w-full max-w-2xl mx-auto rounded-lg object-contain"
                style={{ maxHeight: '400px' }}
                onError={(e) => {
                  e.currentTarget.style.display = 'none'
                }}
              />
            )}
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <pre className="whitespace-pre-wrap font-sans">{content}</pre>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

