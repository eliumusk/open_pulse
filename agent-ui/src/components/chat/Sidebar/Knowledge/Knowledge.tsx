'use client'

import { FC, useEffect, useMemo, useState } from 'react'
import { useQueryState } from 'nuqs'

import { useStore } from '@/store'
import {
  getKnowledgeContentAPI,
  uploadKnowledgeContentAPI,
  deleteKnowledgeContentAPI,
  getKnowledgeContentStatusAPI
} from '@/api/os'

import KnowledgeItem from './KnowledgeItem'
import KnowledgeBlankState from './KnowledgeBlankState'
import UploadFileDialog from './UploadFileDialog'
import ViewKnowledgeDialog from './ViewKnowledgeDialog'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import Icon from '@/components/ui/icon'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'
import { KnowledgeContent } from '@/types/os'

interface SkeletonListProps {
  skeletonCount: number
}

const SkeletonList: FC<SkeletonListProps> = ({ skeletonCount }) => {
  const list = useMemo(
    () => Array.from({ length: skeletonCount }, (_, i) => i),
    [skeletonCount]
  )

  return list.map((k, idx) => (
    <Skeleton
      key={k}
      className={cn(
        'mb-1 h-16 rounded-lg px-3 py-2',
        idx > 0 && 'bg-background-secondary'
      )}
    />
  ))
}

const Knowledge = () => {
  const [agentId] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [workflowId] = useQueryState('workflow')
  const [dbId] = useQueryState('db_id')

  const {
    selectedEndpoint,
    mode,
    isEndpointActive,
    isEndpointLoading,
    hydrated,
    knowledgeContent,
    setKnowledgeContent,
    isKnowledgeLoading,
    setIsKnowledgeLoading
  } = useStore()

  const [showUploadDialog, setShowUploadDialog] = useState(false)
  const [showViewDialog, setShowViewDialog] = useState(false)
  const [viewingContent, setViewingContent] = useState<KnowledgeContent | null>(null)

  // Reload knowledge content
  const reloadKnowledge = async () => {
    if (!selectedEndpoint || !dbId) return

    try {
      setIsKnowledgeLoading(true)
      const result = await getKnowledgeContentAPI(selectedEndpoint, dbId, 20, 1)
      setKnowledgeContent(result.data)
    } catch (error) {
      console.error('Error reloading knowledge:', error)
    } finally {
      setIsKnowledgeLoading(false)
    }
  }

  // Poll content status until completed or failed
  const pollContentStatus = async (contentId: string) => {
    if (!selectedEndpoint || !dbId) return

    const maxAttempts = 60 // 60 attempts * 2 seconds = 2 minutes max
    let attempts = 0

    const poll = async (): Promise<void> => {
      try {
        const statusResult = await getKnowledgeContentStatusAPI(
          selectedEndpoint,
          contentId,
          dbId
        )

        if (statusResult.status === 'completed') {
          toast.success('Content processed successfully')
          await reloadKnowledge()
          return
        }

        if (statusResult.status === 'failed') {
          toast.error(
            `Content processing failed: ${statusResult.status_message || 'Unknown error'}`
          )
          await reloadKnowledge()
          return
        }

        // Still processing
        attempts++
        if (attempts < maxAttempts) {
          setTimeout(() => poll(), 2000) // Poll every 2 seconds
        } else {
          toast.warning('Content processing is taking longer than expected')
          await reloadKnowledge()
        }
      } catch (error) {
        console.error('Error polling content status:', error)
        await reloadKnowledge()
      }
    }

    poll()
  }

  // Handle unified upload (file, URL, or text)
  const handleUpload = async (data: {
    file?: File
    url?: string
    text_content?: string
    name: string
    description: string
    reader_id?: string
    chunker?: string
  }) => {
    if (!selectedEndpoint || !dbId) {
      toast.error('No endpoint or database selected')
      return
    }

    try {
      const result = await uploadKnowledgeContentAPI(selectedEndpoint, dbId, {
        file: data.file,
        url: data.url,
        text_content: data.text_content,
        name: data.name,
        description: data.description,
        reader_id: data.reader_id,
        chunker: data.chunker
      })

      // Immediately reload to show the new content with "processing" status
      await reloadKnowledge()

      // Start polling for status updates
      if (result.id) {
        pollContentStatus(result.id)
      }
    } catch (error) {
      // Error already handled in API function
    }
  }

  // Load knowledge content when entity changes
  useEffect(() => {
    const loadKnowledge = async () => {
      // Don't load if endpoint is not ready
      if (!selectedEndpoint || isEndpointLoading || !hydrated) return

      // Don't load if no entity is selected
      if (!(agentId || teamId || workflowId)) {
        setKnowledgeContent([])
        return
      }

      // Don't load if no db_id
      if (!dbId) {
        setKnowledgeContent([])
        return
      }

      try {
        setIsKnowledgeLoading(true)
        const result = await getKnowledgeContentAPI(selectedEndpoint, dbId, 20, 1)
        setKnowledgeContent(result.data)
      } catch (error) {
        console.error('Error loading knowledge:', error)
        setKnowledgeContent([])
      } finally {
        setIsKnowledgeLoading(false)
      }
    }

    loadKnowledge()
  }, [
    selectedEndpoint,
    agentId,
    teamId,
    workflowId,
    dbId,
    mode,
    isEndpointLoading,
    hydrated,
    setKnowledgeContent,
    setIsKnowledgeLoading
  ])

  // Handle delete knowledge
  const handleDeleteKnowledge = async (contentId: string) => {
    if (!selectedEndpoint || !dbId) {
      toast.error('No endpoint or database selected')
      return
    }

    if (window.confirm('Are you sure you want to delete this content? This action cannot be undone.')) {
      try {
        await deleteKnowledgeContentAPI(selectedEndpoint, contentId, dbId)
        await reloadKnowledge()
      } catch (error) {
        // Error already handled in API function
      }
    }
  }

  // Handle view knowledge
  const handleViewKnowledge = (content: KnowledgeContent) => {
    setViewingContent(content)
    setShowViewDialog(true)
  }

  if (isKnowledgeLoading || isEndpointLoading) {
    return (
      <div className="w-full">
        <div className="mb-2 text-xs font-medium uppercase">Knowledge</div>
        <div className="mt-4 w-full">
          <SkeletonList skeletonCount={3} />
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="mb-2 flex w-full items-center justify-between">
        <div className="text-xs font-medium uppercase">Knowledge</div>
        {isEndpointActive && dbId && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowUploadDialog(true)}
            className="h-6 px-2 text-xs hover:bg-background-secondary"
          >
            <Icon type="plus-icon" size="xs" />
            <span className="ml-1">Add</span>
          </Button>
        )}
      </div>
      <div className="font-geist">
        {!isEndpointActive ||
        (!isKnowledgeLoading && knowledgeContent.length === 0) ? (
          <KnowledgeBlankState />
        ) : (
          <div className="flex flex-col gap-y-1">
            {knowledgeContent.map((content) => (
              <KnowledgeItem
                key={content.id}
                content={content}
                onDelete={handleDeleteKnowledge}
                onView={handleViewKnowledge}
              />
            ))}
          </div>
        )}
      </div>

      {/* Dialogs */}
      <ViewKnowledgeDialog
        open={showViewDialog}
        onOpenChange={setShowViewDialog}
        content={viewingContent}
      />

      <UploadFileDialog
        open={showUploadDialog}
        onOpenChange={setShowUploadDialog}
        onUpload={handleUpload}
      />
    </div>
  )
}

export default Knowledge

