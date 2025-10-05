'use client'

import { FC, useEffect, useMemo, useState } from 'react'
import { useQueryState } from 'nuqs'

import { useStore } from '@/store'
import { getKnowledgeContentAPI, uploadKnowledgeContentAPI } from '@/api/os'

import KnowledgeItem from './KnowledgeItem'
import KnowledgeBlankState from './KnowledgeBlankState'
import AddKnowledgeDialog from './AddKnowledgeDialog'
import UploadFileDialog from './UploadFileDialog'
import UploadTextDialog from './UploadTextDialog'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import Icon from '@/components/ui/icon'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

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

  const [isScrolling, setIsScrolling] = useState(false)
  const [showTypeDialog, setShowTypeDialog] = useState(false)
  const [showFileDialog, setShowFileDialog] = useState(false)
  const [showWebDialog, setShowWebDialog] = useState(false)
  const [showTextDialog, setShowTextDialog] = useState(false)

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

  // Handle file upload
  const handleFileUpload = async (data: {
    file?: File
    url?: string
    name: string
    description: string
  }) => {
    if (!selectedEndpoint || !dbId) {
      toast.error('No endpoint or database selected')
      return
    }

    try {
      await uploadKnowledgeContentAPI(selectedEndpoint, dbId, {
        file: data.file,
        url: data.url,
        name: data.name,
        description: data.description
      })
      await reloadKnowledge()
    } catch (error) {
      // Error already handled in API function
    }
  }

  // Handle text/web upload
  const handleTextUpload = async (data: {
    text: string
    name: string
    description: string
  }, isWeb: boolean) => {
    if (!selectedEndpoint || !dbId) {
      toast.error('No endpoint or database selected')
      return
    }

    try {
      await uploadKnowledgeContentAPI(selectedEndpoint, dbId, {
        [isWeb ? 'url' : 'text_content']: data.text,
        name: data.name,
        description: data.description
      })
      await reloadKnowledge()
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
            onClick={() => setShowTypeDialog(true)}
            className="h-6 px-2 text-xs hover:bg-background-secondary"
          >
            <Icon type="plus-icon" size="xs" />
            <span className="ml-1">Add</span>
          </Button>
        )}
      </div>
      <div
        className={`max-h-[300px] overflow-y-auto font-geist transition-all duration-300 [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar]:transition-opacity [&::-webkit-scrollbar]:duration-300 ${
          isScrolling
            ? '[&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-background [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar]:opacity-0'
            : '[&::-webkit-scrollbar]:opacity-100'
        }`}
        onScroll={() => setIsScrolling(true)}
        onMouseOver={() => setIsScrolling(true)}
        onMouseLeave={() => setIsScrolling(false)}
      >
        {!isEndpointActive ||
        (!isKnowledgeLoading && knowledgeContent.length === 0) ? (
          <KnowledgeBlankState />
        ) : (
          <div className="flex flex-col gap-y-1 pr-1">
            {knowledgeContent.map((content) => (
              <KnowledgeItem key={content.id} content={content} />
            ))}
          </div>
        )}
      </div>

      {/* Dialogs */}
      <AddKnowledgeDialog
        open={showTypeDialog}
        onOpenChange={setShowTypeDialog}
        onSelectType={(type) => {
          if (type === 'file') {
            setShowFileDialog(true)
          } else if (type === 'web') {
            setShowWebDialog(true)
          } else if (type === 'text') {
            setShowTextDialog(true)
          }
        }}
      />

      <UploadFileDialog
        open={showFileDialog}
        onOpenChange={setShowFileDialog}
        onUpload={handleFileUpload}
      />

      <UploadTextDialog
        open={showWebDialog}
        onOpenChange={setShowWebDialog}
        onUpload={(data) => handleTextUpload(data, true)}
        type="web"
      />

      <UploadTextDialog
        open={showTextDialog}
        onOpenChange={setShowTextDialog}
        onUpload={(data) => handleTextUpload(data, false)}
        type="text"
      />
    </div>
  )
}

export default Knowledge

