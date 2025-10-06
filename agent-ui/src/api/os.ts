import { toast } from 'sonner'

import { APIRoutes } from './routes'

import {
  AgentDetails,
  KnowledgeContent,
  Memory,
  MemoryCreateInput,
  MemoryListResponse,
  MemoryUpdateInput,
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
    // Return empty array for 404 (new session with no runs yet)
    if (response.status === 404) {
      return []
    }
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

export const uploadKnowledgeContentAPI = async (
  endpoint: string,
  dbId: string,
  data: {
    file?: File
    url?: string
    text_content?: string
    name: string
    description?: string
    reader_id?: string
    chunker?: string
  }
): Promise<KnowledgeContent> => {
  const apiUrl = new URL(APIRoutes.GetKnowledgeContent(endpoint))
  apiUrl.searchParams.set('db_id', dbId)

  const formData = new FormData()
  formData.append('name', data.name)
  if (data.description) {
    formData.append('description', data.description)
  }

  if (data.file) {
    formData.append('file', data.file)
  } else if (data.url) {
    formData.append('url', data.url)
  } else if (data.text_content) {
    formData.append('text_content', data.text_content)
  }

  // Add advanced options if provided
  if (data.reader_id) {
    formData.append('reader_id', data.reader_id)
  }
  if (data.chunker) {
    formData.append('chunker', data.chunker)
  }

  try {
    const response = await fetch(apiUrl.toString(), {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage =
        errorData.detail || errorData.message || response.statusText
      toast.error(`Failed to upload content: ${errorMessage}`)
      throw new Error(errorMessage)
    }

    const result = await response.json()
    toast.success('Content upload started')
    return result
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    toast.error('Error uploading content')
    throw new Error('Upload failed')
  }
}

export const getKnowledgeContentStatusAPI = async (
  endpoint: string,
  contentId: string,
  dbId: string
): Promise<{ status: 'processing' | 'completed' | 'failed'; status_message?: string }> => {
  const apiUrl = new URL(APIRoutes.GetKnowledgeContentStatus(endpoint, contentId))
  apiUrl.searchParams.set('db_id', dbId)

  try {
    const response = await fetch(apiUrl.toString(), {
      method: 'GET'
    })

    if (!response.ok) {
      throw new Error('Failed to get content status')
    }

    return await response.json()
  } catch (error) {
    console.error('Error getting content status:', error)
    throw error
  }
}

export const deleteKnowledgeContentAPI = async (
  endpoint: string,
  contentId: string,
  dbId: string
): Promise<void> => {
  const url = new URL(APIRoutes.DeleteKnowledgeContent(endpoint, contentId))
  url.searchParams.set('db_id', dbId)

  try {
    const response = await fetch(url.toString(), { method: 'DELETE' })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage =
        errorData.detail || errorData.message || response.statusText
      toast.error(`Failed to delete content: ${errorMessage}`)
      throw new Error(errorMessage)
    }

    toast.success('Content deleted successfully')
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    toast.error('Error deleting content')
    throw new Error('Delete failed')
  }
}

// Memory APIs
export const getMemoriesAPI = async (
  endpoint: string,
  userId?: string,
  agentId?: string,
  teamId?: string,
  limit: number = 20,
  page: number = 1
): Promise<MemoryListResponse> => {
  const url = new URL(APIRoutes.GetMemories(endpoint))
  if (userId) url.searchParams.set('user_id', userId)
  if (agentId) url.searchParams.set('agent_id', agentId)
  if (teamId) url.searchParams.set('team_id', teamId)
  url.searchParams.set('limit', limit.toString())
  url.searchParams.set('page', page.toString())

  try {
    const response = await fetch(url.toString(), { method: 'GET' })
    if (!response.ok) {
      if (response.status !== 404) {
        toast.error(`Failed to fetch memories: ${response.statusText}`)
      }
      return { data: [], meta: { page: 1, limit, total_pages: 0, total_count: 0 } }
    }
    return await response.json()
  } catch {
    return { data: [], meta: { page: 1, limit, total_pages: 0, total_count: 0 } }
  }
}

export const createMemoryAPI = async (
  endpoint: string,
  data: MemoryCreateInput
): Promise<Memory> => {
  const url = APIRoutes.CreateMemory(endpoint)

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage =
        errorData.detail || errorData.message || response.statusText
      toast.error(`Failed to create memory: ${errorMessage}`)
      throw new Error(errorMessage)
    }

    const result = await response.json()
    toast.success('Memory created successfully')
    return result
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    toast.error('Error creating memory')
    throw new Error('Create failed')
  }
}

export const updateMemoryAPI = async (
  endpoint: string,
  memoryId: string,
  data: MemoryUpdateInput,
  userId?: string
): Promise<Memory> => {
  const url = APIRoutes.UpdateMemory(endpoint, memoryId)

  // PATCH requires user_id in the body
  const requestBody = {
    ...data,
    user_id: userId
  }

  try {
    const response = await fetch(url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage =
        errorData.detail || errorData.message || response.statusText
      toast.error(`Failed to update memory: ${errorMessage}`)
      throw new Error(errorMessage)
    }

    const result = await response.json()
    toast.success('Memory updated successfully')
    return result
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    toast.error('Error updating memory')
    throw new Error('Update failed')
  }
}

export const deleteMemoryAPI = async (
  endpoint: string,
  memoryId: string
): Promise<void> => {
  const url = APIRoutes.DeleteMemory(endpoint, memoryId)

  try {
    const response = await fetch(url, { method: 'DELETE' })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage =
        errorData.detail || errorData.message || response.statusText
      toast.error(`Failed to delete memory: ${errorMessage}`)
      throw new Error(errorMessage)
    }

    toast.success('Memory deleted successfully')
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    toast.error('Error deleting memory')
    throw new Error('Delete failed')
  }
}
