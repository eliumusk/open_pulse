'use client'

import * as React from 'react'
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from '@/components/ui/select'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'
import Icon from '@/components/ui/icon'
import { useEffect } from 'react'
import useChatActions from '@/hooks/useChatActions'

export function EntitySelector() {
  const { mode, agents, teams, workflows, setMessages, setSelectedModel } =
    useStore()

  const { focusChatInput } = useChatActions()
  const [agentId, setAgentId] = useQueryState('agent', {
    parse: (value) => value || undefined,
    history: 'push'
  })
  const [teamId, setTeamId] = useQueryState('team', {
    parse: (value) => value || undefined,
    history: 'push'
  })
  const [workflowId, setWorkflowId] = useQueryState('workflow', {
    parse: (value) => value || undefined,
    history: 'push'
  })
  const [, setSessionId] = useQueryState('session')

  const currentEntities =
    mode === 'team' ? teams : mode === 'workflow' ? workflows : agents
  const currentValue =
    mode === 'team' ? teamId : mode === 'workflow' ? workflowId : agentId
  const placeholder =
    mode === 'team'
      ? 'Select Team'
      : mode === 'workflow'
        ? 'Select Workflow'
        : 'Select Agent'

  useEffect(() => {
    if (currentValue && currentEntities.length > 0) {
      const entity = currentEntities.find((item) => item.id === currentValue)
      if (entity) {
        // Workflows don't have model property
        if (mode !== 'workflow' && 'model' in entity) {
          setSelectedModel(entity.model?.model || '')
        } else {
          setSelectedModel('')
        }
        if (mode === 'team') {
          setTeamId(entity.id)
        }
        // Focus input for workflow or when model is available
        if (mode === 'workflow') {
          focusChatInput()
        } else if ('model' in entity && entity.model?.model) {
          focusChatInput()
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentValue, currentEntities, setSelectedModel, mode])

  const handleOnValueChange = (value: string) => {
    const newValue = value === currentValue ? null : value
    const selectedEntity = currentEntities.find((item) => item.id === newValue)

    // Workflows don't have model property
    if (mode !== 'workflow' && selectedEntity && 'model' in selectedEntity) {
      setSelectedModel(selectedEntity.model?.provider || '')
    } else {
      setSelectedModel('')
    }

    if (mode === 'team') {
      setTeamId(newValue)
      setAgentId(null)
      setWorkflowId(null)
    } else if (mode === 'workflow') {
      setWorkflowId(newValue)
      setAgentId(null)
      setTeamId(null)
    } else {
      setAgentId(newValue)
      setTeamId(null)
      setWorkflowId(null)
    }

    setMessages([])
    setSessionId(null)

    if (mode === 'workflow' || (selectedEntity && 'model' in selectedEntity && selectedEntity.model?.provider)) {
      focusChatInput()
    }
  }

  if (currentEntities.length === 0) {
    return (
      <Select disabled>
        <SelectTrigger className="h-9 w-full rounded-xl border border-primary/15 bg-primaryAccent text-xs font-medium uppercase opacity-50">
          <SelectValue placeholder={`No ${mode}s Available`} />
        </SelectTrigger>
      </Select>
    )
  }

  return (
    <Select
      value={currentValue || ''}
      onValueChange={(value) => handleOnValueChange(value)}
    >
      <SelectTrigger className="h-9 w-full rounded-xl border border-primary/15 bg-primaryAccent text-xs font-medium uppercase">
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent className="border-none bg-primaryAccent font-dmmono shadow-lg">
        {currentEntities.map((entity, index) => (
          <SelectItem
            className="cursor-pointer"
            key={`${entity.id}-${index}`}
            value={entity.id}
          >
            <div className="flex items-center gap-3 text-xs font-medium uppercase">
              <Icon type={'user'} size="xs" />
              {entity.name || entity.id}
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
