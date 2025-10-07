"""
Notification Manager for Workflow Completion Events
Handles SSE (Server-Sent Events) for real-time notifications to frontend
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from collections import defaultdict
from dataclasses import dataclass, asdict
import uuid


@dataclass
class WorkflowNotification:
    """Data structure for workflow completion notification"""
    notification_id: str
    workflow_id: str
    run_id: str
    user_id: str
    session_id: str
    status: str  # 'completed', 'failed', 'running'
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    error: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class NotificationManager:
    """
    Manages workflow completion notifications using SSE
    
    Features:
    - Track workflow runs that need notifications
    - Store notification data when workflows complete
    - Provide SSE endpoint for frontend to subscribe
    - Auto-cleanup old notifications
    """
    
    def __init__(self, max_notifications: int = 100, ttl_seconds: int = 3600):
        """
        Initialize notification manager
        
        Args:
            max_notifications: Maximum number of notifications to keep in memory
            ttl_seconds: Time-to-live for notifications (default: 1 hour)
        """
        # Track which runs need notifications: {run_id: workflow_metadata}
        self.tracked_runs: Dict[str, Dict[str, Any]] = {}
        
        # Store completed notifications: {notification_id: WorkflowNotification}
        self.notifications: Dict[str, WorkflowNotification] = {}
        
        # SSE subscribers: {client_id: asyncio.Queue}
        self.subscribers: Dict[str, asyncio.Queue] = {}
        
        self.max_notifications = max_notifications
        self.ttl_seconds = ttl_seconds
        
        print("✅ NotificationManager initialized")
    
    def track_workflow_run(
        self,
        run_id: str,
        workflow_id: str,
        user_id: str,
        session_id: str,
        enable_notification: bool = False
    ):
        """
        Register a workflow run for notification tracking
        
        Args:
            run_id: Workflow run ID
            workflow_id: Workflow ID
            user_id: User ID
            session_id: Session ID
            enable_notification: Whether to send notification when complete
        """
        if not enable_notification:
            return
        
        self.tracked_runs[run_id] = {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "session_id": session_id,
            "tracked_at": datetime.now().isoformat(),
        }
        
        print(f"📌 Tracking workflow run: {run_id} for notifications")
    
    async def notify_workflow_completion(
        self,
        run_id: str,
        status: str,
        content: Optional[str] = None,
        cover_image_url: Optional[str] = None,
        error: Optional[str] = None,
        workflow_id: str = "simple-newsletter-workflow",
        user_id: str = "default",
    ):
        """
        Create and broadcast notification for workflow completion

        Args:
            run_id: Workflow run ID
            status: Completion status ('completed' or 'failed')
            content: Generated newsletter content
            cover_image_url: URL to cover image
            error: Error message if failed
            workflow_id: Workflow ID (optional, for non-tracked runs)
            user_id: User ID (optional, for non-tracked runs)
        """
        # Check if this run is being tracked
        if run_id in self.tracked_runs:
            metadata = self.tracked_runs[run_id]
        else:
            # Not tracked, create metadata on the fly
            print(f"ℹ️  Run {run_id} not pre-tracked, creating notification anyway")
            metadata = {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "session_id": f"session_{run_id[:8]}",
                "tracked_at": datetime.now().isoformat(),
            }
        
        # Create notification
        notification = WorkflowNotification(
            notification_id=str(uuid.uuid4()),
            workflow_id=metadata["workflow_id"],
            run_id=run_id,
            user_id=metadata["user_id"],
            session_id=metadata["session_id"],
            status=status,
            content=content,
            cover_image_url=cover_image_url,
            error=error,
        )
        
        # Store notification
        self.notifications[notification.notification_id] = notification
        
        # Cleanup old notifications
        self._cleanup_old_notifications()
        
        # Broadcast to all subscribers
        await self._broadcast_notification(notification)

        # Remove from tracked runs (if it was tracked)
        if run_id in self.tracked_runs:
            del self.tracked_runs[run_id]

        print(f"✅ Notification sent for run {run_id}: {status}")
    
    async def _broadcast_notification(self, notification: WorkflowNotification):
        """Broadcast notification to all SSE subscribers"""
        if not self.subscribers:
            print("⚠️  No active subscribers for notification")
            return
        
        notification_data = notification.to_dict()
        
        # Send to all subscribers
        dead_subscribers = []
        for client_id, queue in self.subscribers.items():
            try:
                await queue.put(notification_data)
                print(f"📤 Sent notification to subscriber {client_id}")
            except Exception as e:
                print(f"❌ Failed to send to subscriber {client_id}: {e}")
                dead_subscribers.append(client_id)
        
        # Cleanup dead subscribers
        for client_id in dead_subscribers:
            del self.subscribers[client_id]
    
    def subscribe(self) -> tuple[str, asyncio.Queue]:
        """
        Subscribe to notifications (for SSE endpoint)
        
        Returns:
            Tuple of (client_id, queue)
        """
        client_id = str(uuid.uuid4())
        queue = asyncio.Queue()
        self.subscribers[client_id] = queue
        
        print(f"🔔 New subscriber: {client_id} (total: {len(self.subscribers)})")
        return client_id, queue
    
    def unsubscribe(self, client_id: str):
        """Unsubscribe from notifications"""
        if client_id in self.subscribers:
            del self.subscribers[client_id]
            print(f"🔕 Unsubscribed: {client_id} (remaining: {len(self.subscribers)})")
    
    def _cleanup_old_notifications(self):
        """Remove old notifications to prevent memory bloat"""
        if len(self.notifications) <= self.max_notifications:
            return
        
        # Sort by creation time and keep only the most recent
        sorted_notifications = sorted(
            self.notifications.items(),
            key=lambda x: x[1].created_at,
            reverse=True
        )
        
        # Keep only max_notifications
        self.notifications = dict(sorted_notifications[:self.max_notifications])
        
        print(f"🧹 Cleaned up old notifications, kept {len(self.notifications)}")
    
    def get_recent_notifications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notifications (for debugging/history)"""
        sorted_notifications = sorted(
            self.notifications.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return [n.to_dict() for n in sorted_notifications[:limit]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification manager statistics"""
        return {
            "tracked_runs": len(self.tracked_runs),
            "stored_notifications": len(self.notifications),
            "active_subscribers": len(self.subscribers),
            "max_notifications": self.max_notifications,
            "ttl_seconds": self.ttl_seconds,
        }


# Global singleton instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get or create the global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager

