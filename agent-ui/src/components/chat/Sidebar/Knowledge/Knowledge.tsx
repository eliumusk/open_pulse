'use client'

import { FC, useEffect, useMemo, useState } from 'react'
import { useQueryState } from 'nuqs'

import { useStore } from '@/store'
import { getKnowledgeContentAPI } from '@/api/os'

import KnowledgeItem from './KnowledgeItem'
import KnowledgeBlankState from './KnowledgeBlankState'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

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

  console.log('Knowledge component rendered', {
    isKnowledgeLoading,
    isEndpointLoading,
    knowledgeContentLength: knowledgeContent.length,
    isEndpointActive
  })

  // Load knowledge content when entity changes
  useEffect(() => {
    const loadKnowledge = async () => {
      console.log('Knowledge: Loading...', {
        selectedEndpoint,
        isEndpointLoading,
        hydrated,
        agentId,
        teamId,
        workflowId,
        dbId
      })

      // Don't load if endpoint is not ready
      if (!selectedEndpoint || isEndpointLoading || !hydrated) return

      // Don't load if no entity is selected
      if (!(agentId || teamId || workflowId)) {
        setKnowledgeContent([])
        return
      }

      // Don't load if no db_id
      if (!dbId) {
        console.log('Knowledge: No db_id, showing empty state')
        setKnowledgeContent([])
        return
      }

      try {
        setIsKnowledgeLoading(true)
        console.log('Knowledge: Fetching from API...')
        const result = await getKnowledgeContentAPI(selectedEndpoint, dbId, 20, 1)
        console.log('Knowledge: Received data:', result)
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
      <div className="mb-2 w-full text-xs font-medium uppercase">Knowledge</div>
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
    </div>
  )
}

export default Knowledge

