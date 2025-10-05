'use client'

import { FC, useEffect, useMemo, useState } from 'react'
import { useQueryState } from 'nuqs'

import { useStore } from '@/store'
import {
  getMemoriesAPI,
  createMemoryAPI,
  updateMemoryAPI,
  deleteMemoryAPI
} from '@/api/os'

import MemoryItem from './MemoryItem'
import MemoryBlankState from './MemoryBlankState'
import AddMemoryDialog from './AddMemoryDialog'
import EditMemoryDialog from './EditMemoryDialog'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import Icon from '@/components/ui/icon'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'
import { Memory as MemoryType, MemoryCreateInput, MemoryUpdateInput } from '@/types/os'

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
        'mb-1 h-20 rounded-lg px-3 py-2',
        idx > 0 && 'bg-background-secondary'
      )}
    />
  ))
}

const Memory = () => {
  const [userId] = useQueryState('user_id')

  const {
    selectedEndpoint,
    isEndpointActive,
    isEndpointLoading,
    hydrated,
    memories,
    setMemories,
    isMemoriesLoading,
    setIsMemoriesLoading
  } = useStore()

  const [showAddDialog, setShowAddDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [editingMemory, setEditingMemory] = useState<MemoryType | null>(null)

  // Use user_id from URL or default
  const effectiveUserId = userId || 'default'

  // Reload memories
  const reloadMemories = async () => {
    if (!selectedEndpoint) return

    try {
      setIsMemoriesLoading(true)
      // Memory is user-level, not agent/team-level, so we don't filter by agent_id/team_id
      const result = await getMemoriesAPI(
        selectedEndpoint,
        effectiveUserId,
        undefined, // Don't filter by agent_id
        undefined, // Don't filter by team_id
        20,
        1
      )
      setMemories(result.data)
    } catch (error) {
      console.error('Error reloading memories:', error)
    } finally {
      setIsMemoriesLoading(false)
    }
  }

  // Load memories when user or endpoint changes
  useEffect(() => {
    const loadMemories = async () => {
      // Don't load if endpoint is not ready
      if (!selectedEndpoint || isEndpointLoading || !hydrated) {
        return
      }

      // Memory is user-level, so we load it regardless of entity selection
      // (Unlike Knowledge which is entity-specific)

      try {
        setIsMemoriesLoading(true)
        // Memory is user-level, not agent/team-level, so we don't filter by agent_id/team_id
        const result = await getMemoriesAPI(
          selectedEndpoint,
          effectiveUserId,
          undefined, // Don't filter by agent_id
          undefined, // Don't filter by team_id
          20,
          1
        )
        setMemories(result.data)
      } catch (error) {
        console.error('Error loading memories:', error)
        setMemories([])
      } finally {
        setIsMemoriesLoading(false)
      }
    }

    loadMemories()
  }, [
    selectedEndpoint,
    effectiveUserId,
    isEndpointLoading,
    hydrated,
    setMemories,
    setIsMemoriesLoading
  ])

  // Handle add memory
  const handleAddMemory = async (data: MemoryCreateInput) => {
    if (!selectedEndpoint) {
      toast.error('No endpoint selected')
      return
    }

    try {
      await createMemoryAPI(selectedEndpoint, {
        ...data,
        user_id: effectiveUserId
      })
      await reloadMemories()
    } catch (error) {
      // Error already handled in API function
    }
  }

  // Handle edit memory
  const handleEditMemory = async (memoryId: string, data: MemoryUpdateInput) => {
    if (!selectedEndpoint) {
      toast.error('No endpoint selected')
      return
    }

    try {
      await updateMemoryAPI(selectedEndpoint, memoryId, data, effectiveUserId)
      await reloadMemories()
    } catch (error) {
      // Error already handled in API function
    }
  }

  // Handle delete memory
  const handleDeleteMemory = async (memoryId: string) => {
    if (!selectedEndpoint) {
      toast.error('No endpoint selected')
      return
    }

    // Show confirmation
    if (window.confirm('Are you sure you want to delete this memory?')) {
      try {
        await deleteMemoryAPI(selectedEndpoint, memoryId)
        await reloadMemories()
      } catch (error) {
        // Error already handled in API function
      }
    }
  }

  if (isMemoriesLoading || isEndpointLoading) {
    return (
      <div className="w-full">
        <div className="mb-2 text-xs font-medium uppercase">Memory</div>
        <div className="mt-4 w-full">
          <SkeletonList skeletonCount={3} />
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="mb-2 flex w-full items-center justify-between">
        <div className="text-xs font-medium uppercase">Memory</div>
        {isEndpointActive && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowAddDialog(true)}
            className="h-6 px-2 text-xs hover:bg-background-secondary"
          >
            <Icon type="plus-icon" size="xs" />
            <span className="ml-1">Add</span>
          </Button>
        )}
      </div>
      <div className="font-geist">
        {!isEndpointActive || (!isMemoriesLoading && memories.length === 0) ? (
          <MemoryBlankState />
        ) : (
          <div className="flex flex-col gap-y-1">
            {memories.map((memory) => (
              <MemoryItem
                key={memory.memory_id}
                memory={memory}
                onEdit={(mem) => {
                  setEditingMemory(mem)
                  setShowEditDialog(true)
                }}
                onDelete={handleDeleteMemory}
              />
            ))}
          </div>
        )}
      </div>

      {/* Dialogs */}
      <AddMemoryDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
        onSubmit={handleAddMemory}
      />

      <EditMemoryDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        memory={editingMemory}
        onSubmit={handleEditMemory}
      />
    </div>
  )
}

export default Memory

