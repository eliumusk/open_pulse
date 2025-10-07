'use client'

import { useEffect, useRef, useState } from 'react'
import { useStore } from '@/store'

export interface WorkflowNotification {
  notification_id: string
  workflow_id: string
  run_id: string
  user_id: string
  session_id: string
  status: 'completed' | 'failed' | 'running'
  content?: string
  cover_image_url?: string
  error?: string
  created_at: string
}

interface UseNotificationStreamReturn {
  notifications: WorkflowNotification[]
  isConnected: boolean
  error: string | null
  clearNotifications: () => void
}

export function useNotificationStream(): UseNotificationStreamReturn {
  const [notifications, setNotifications] = useState<WorkflowNotification[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const { selectedEndpoint } = useStore()

  useEffect(() => {
    // Don't connect if no endpoint
    if (!selectedEndpoint) {
      return
    }

    // Construct SSE URL
    const sseUrl = `${selectedEndpoint}/api/notifications/stream`

    console.log('🔔 Connecting to notification stream:', sseUrl)

    // Create EventSource
    const eventSource = new EventSource(sseUrl)
    eventSourceRef.current = eventSource

    // Connection opened
    eventSource.addEventListener('open', () => {
      console.log('✅ Notification stream connected')
      setIsConnected(true)
      setError(null)
    })

    // Connected event
    eventSource.addEventListener('connected', (event) => {
      const data = JSON.parse(event.data)
      console.log('🔌 Connected to notification stream:', data)
    })

    // Workflow completed event
    eventSource.addEventListener('workflow_completed', (event) => {
      const notification: WorkflowNotification = JSON.parse(event.data)
      console.log('📬 Received workflow notification:', notification)

      // Add to notifications list
      setNotifications((prev) => [notification, ...prev])

      // Optional: Show browser notification
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Newsletter Ready!', {
          body: 'Your personalized newsletter has been generated.',
          icon: notification.cover_image_url,
        })
      }
    })

    // Heartbeat event (keep-alive)
    eventSource.addEventListener('heartbeat', () => {
      // Just keep connection alive, no action needed
    })

    // Error handling
    eventSource.addEventListener('error', (event) => {
      console.error('❌ Notification stream error:', event)
      setIsConnected(false)
      setError('Connection to notification stream lost')

      // EventSource will automatically try to reconnect
    })

    // Cleanup on unmount
    return () => {
      console.log('🔌 Closing notification stream')
      eventSource.close()
      eventSourceRef.current = null
      setIsConnected(false)
    }
  }, [selectedEndpoint])

  // Request browser notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        console.log('🔔 Notification permission:', permission)
      })
    }
  }, [])

  const clearNotifications = () => {
    setNotifications([])
  }

  return {
    notifications,
    isConnected,
    error,
    clearNotifications
  }
}

