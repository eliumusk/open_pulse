import { toast } from 'sonner'

import { APIRoutes } from './routes'

import {
  AgentDetails,
  KnowledgeContent,
  Sessions,
  TeamDetails,
  WorkflowDetails
} from '@/types/os'

export const getAgentsAPI = async (
  endpoint: string
): Promise<AgentDetails[]> => {
  const url = APIRoutes.GetAgents(endpoint)
  try {
    const response = await fetch(url, { method: 'GET' })
    if (!response.ok) {
      toast.error(`Failed to fetch  agents: ${response.statusText}`)
      return []
    }
    const data = await response.json()
    return data
  } catch {
    toast.error('Error fetching  agents')
    return []
  }
}

export const getStatusAPI = async (base: string): Promise<number> => {
  const response = await fetch(APIRoutes.Status(base), {
    method: 'GET'
  })
  return response.status
}

export const getAllSessionsAPI = async (
  base: string,
  type: 'agent' | 'team' | 'workflow',
  componentId: string,
  dbId: string
): Promise<Sessions | { data: [] }> => {
  try {
    const url = new URL(APIRoutes.GetSessions(base))
    url.searchParams.set('type', type)
    url.searchParams.set('component_id', componentId)
    url.searchParams.set('db_id', dbId)

    const response = await fetch(url.toString(), {
      method: 'GET'
    })

    if (!response.ok) {
      if (response.status === 404) {
        return { data: [] }
      }
      throw new Error(`Failed to fetch sessions: ${response.statusText}`)
    }
    return response.json()
  } catch {
    return { data: [] }
  }
}

export const getSessionAPI = async (
  base: string,
  type: 'agent' | 'team' | 'workflow',
  sessionId: string,
  dbId?: string
) => {
  // build query string
  const queryParams = new URLSearchParams({ type })
  if (dbId) queryParams.append('db_id', dbId)

  const response = await fetch(
    `${APIRoutes.GetSession(base, sessionId)}?${queryParams.toString()}`,
    {
      method: 'GET'
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch session: ${response.statusText}`)
  }

  return response.json()
}

export const deleteSessionAPI = async (
  base: string,
  dbId: string,
  sessionId: string
) => {
  const queryParams = new URLSearchParams()
  if (dbId) queryParams.append('db_id', dbId)
  const response = await fetch(
    `${APIRoutes.DeleteSession(base, sessionId)}?${queryParams.toString()}`,
    {
      method: 'DELETE'
    }
  )
  return response
}

export const getTeamsAPI = async (endpoint: string): Promise<TeamDetails[]> => {
  const url = APIRoutes.GetTeams(endpoint)
  try {
    const response = await fetch(url, { method: 'GET' })
    if (!response.ok) {
      toast.error(`Failed to fetch  teams: ${response.statusText}`)
      return []
    }
    const data = await response.json()

    return data
  } catch {
    toast.error('Error fetching  teams')
    return []
  }
}

export const deleteTeamSessionAPI = async (
  base: string,
  teamId: string,
  sessionId: string
) => {
  const response = await fetch(
    APIRoutes.DeleteTeamSession(base, teamId, sessionId),
    {
      method: 'DELETE'
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to delete team session: ${response.statusText}`)
  }
  return response
}

export const getWorkflowsAPI = async (
  endpoint: string
): Promise<WorkflowDetails[]> => {
  const url = APIRoutes.GetWorkflows(endpoint)
  try {
    const response = await fetch(url, { method: 'GET' })
    if (!response.ok) {
      toast.error(`Failed to fetch workflows: ${response.statusText}`)
      return []
    }
    const data = await response.json()
    return data
  } catch {
    toast.error('Error fetching workflows')
    return []
  }
}

export const getKnowledgeContentAPI = async (
  endpoint: string,
  dbId: string,
  limit: number = 20,
  page: number = 1
): Promise<{ data: KnowledgeContent[]; total: number }> => {
  const url = new URL(APIRoutes.GetKnowledgeContent(endpoint))
  url.searchParams.set('db_id', dbId)
  url.searchParams.set('limit', limit.toString())
  url.searchParams.set('page', page.toString())

  try {
    const response = await fetch(url.toString(), { method: 'GET' })
    if (!response.ok) {
      // Don't show error toast for 404 or knowledge not found
      if (response.status !== 404) {
        toast.error(`Failed to fetch knowledge: ${response.statusText}`)
      }
      return { data: [], total: 0 }
    }
    const data = await response.json()
    // Handle different response formats
    if (Array.isArray(data)) {
      return { data, total: data.length }
    }
    return { data: data.data || [], total: data.total || 0 }
  } catch {
    // Silent fail for knowledge - it's optional
    return { data: [], total: 0 }
  }
}
