'use client'
import Sidebar from '@/components/chat/Sidebar/Sidebar'
import { ChatArea } from '@/components/chat/ChatArea'
import { Suspense, useState } from 'react'
import { useNotificationStream } from '@/hooks/useNotificationStream'
import {
  NewsletterNotificationCard,
  NewsletterModal
} from '@/components/notifications/NewsletterNotificationCard'

export default function Home() {
  const { notifications, clearNotifications } = useNotificationStream()
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set())
  const [modalContent, setModalContent] = useState<{
    coverImageUrl?: string
    content: string
  } | null>(null)

  // Get the latest undismissed notification
  const activeNotification = notifications.find(
    (n) => !dismissedIds.has(n.notification_id) && n.status === 'completed'
  )

  const handleDismiss = (notificationId: string) => {
    setDismissedIds((prev) => new Set(prev).add(notificationId))
  }

  const handleViewFull = (notification: typeof activeNotification) => {
    if (notification) {
      setModalContent({
        coverImageUrl: notification.cover_image_url,
        content: notification.content || ''
      })
    }
  }

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="flex h-screen bg-background/80">
        <Sidebar />
        <ChatArea />

        {/* Notification Card */}
        {activeNotification && (
          <NewsletterNotificationCard
            notificationId={activeNotification.notification_id}
            coverImageUrl={activeNotification.cover_image_url}
            content={activeNotification.content || ''}
            onClose={() => handleDismiss(activeNotification.notification_id)}
            onViewFull={() => handleViewFull(activeNotification)}
          />
        )}

        {/* Full Content Modal */}
        <NewsletterModal
          isOpen={modalContent !== null}
          onClose={() => setModalContent(null)}
          coverImageUrl={modalContent?.coverImageUrl}
          content={modalContent?.content || ''}
        />
      </div>
    </Suspense>
  )
}

