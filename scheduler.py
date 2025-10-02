"""
Newsletter Scheduler
Handles scheduled and on-demand newsletter generation
"""
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from agno.db.sqlite import SqliteDb
from workflows import create_newsletter_workflow
from config.settings import (
    DATABASE_FILE,
    NEWSLETTER_GENERATION_HOUR,
    NEWSLETTER_GENERATION_MINUTE,
)


class NewsletterScheduler:
    """
    Manages scheduled newsletter generation
    
    Supports multiple modes:
    - Development: Fast intervals (seconds/minutes) for testing
    - Production: Daily at specific time
    - On-demand: Manual trigger via API
    """
    
    def __init__(self, db: SqliteDb = None):
        """
        Initialize the scheduler
        
        Args:
            db: Database instance (optional)
        """
        self.scheduler = AsyncIOScheduler()
        self.workflow = create_newsletter_workflow(db=db)
        self.job_id = "newsletter_generation_job"
        
        # Track running jobs
        self.running_jobs: Dict[str, Any] = {}
        
    async def generate_newsletter_for_user(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        interests: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate newsletter for a single user
        
        Args:
            user_id: User ID
            session_id: Session ID (optional)
            interests: User interests (optional, will be extracted from memories)
        
        Returns:
            Dict with generation result
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting newsletter generation for user: {user_id}")
        print(f"{'='*60}\n")
        
        try:
            # Run workflow in background
            result = await self.workflow.arun(
                input=interests or "Generate a personalized newsletter based on my interests",
                additional_data={
                    "user_id": user_id,
                    "session_id": session_id,
                },
                background=True,  # Non-blocking execution
            )
            
            # Store the run_id for tracking
            self.running_jobs[user_id] = {
                "run_id": result.run_id,
                "started_at": datetime.now().isoformat(),
                "status": "running",
            }
            
            print(f"✅ Newsletter generation started for {user_id}")
            print(f"   Run ID: {result.run_id}")
            
            # Poll for completion (in production, this would be done separately)
            max_wait = 300  # 5 minutes max
            elapsed = 0
            while not result.has_completed() and elapsed < max_wait:
                await asyncio.sleep(5)
                elapsed += 5
                result = self.workflow.get_run(result.run_id)
                print(f"   ⏳ Waiting for completion... ({elapsed}s)")
            
            if result.has_completed():
                self.running_jobs[user_id]["status"] = "completed"
                self.running_jobs[user_id]["completed_at"] = datetime.now().isoformat()
                print(f"\n✅ Newsletter generation completed for {user_id}")
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "run_id": result.run_id,
                    "content": result.content,
                }
            else:
                print(f"\n⚠️  Newsletter generation timed out for {user_id}")
                return {
                    "success": False,
                    "user_id": user_id,
                    "error": "Timeout",
                }
                
        except Exception as e:
            print(f"\n❌ Error generating newsletter for {user_id}: {e}")
            self.running_jobs[user_id] = {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat(),
            }
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
            }
    
    async def generate_newsletters_for_all_users(self):
        """
        Generate newsletters for all active users
        This is the function called by the scheduler
        """
        print(f"\n{'='*60}")
        print(f"📰 Daily Newsletter Generation Started")
        print(f"   Time: {datetime.now().isoformat()}")
        print(f"{'='*60}\n")
        
        # TODO: In production, fetch active users from database
        # For MVP, we'll use a test user
        test_users = [
            {
                "user_id": "test_user_1",
                "session_id": None,
                "interests": "AI, machine learning, and technology trends",
            },
        ]
        
        results = []
        for user in test_users:
            result = await self.generate_newsletter_for_user(
                user_id=user["user_id"],
                session_id=user.get("session_id"),
                interests=user.get("interests"),
            )
            results.append(result)
            
            # Small delay between users to avoid rate limiting
            await asyncio.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"✅ Daily Newsletter Generation Completed")
        print(f"   Total users: {len(results)}")
        print(f"   Successful: {sum(1 for r in results if r['success'])}")
        print(f"   Failed: {sum(1 for r in results if not r['success'])}")
        print(f"{'='*60}\n")
        
        return results
    
    def start_development_mode(self, interval_minutes: int = 2):
        """
        Start scheduler in development mode with short intervals
        
        Args:
            interval_minutes: Interval in minutes (default: 2)
        """
        print(f"\n🔧 Starting scheduler in DEVELOPMENT mode")
        print(f"   Interval: Every {interval_minutes} minute(s)")
        print(f"   First run: {datetime.now() + timedelta(minutes=interval_minutes)}")
        
        self.scheduler.add_job(
            self.generate_newsletters_for_all_users,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id=self.job_id,
            replace_existing=True,
        )
        
        self.scheduler.start()
        print(f"✅ Scheduler started in development mode\n")
    
    def start_production_mode(
        self,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
    ):
        """
        Start scheduler in production mode with daily cron schedule
        
        Args:
            hour: Hour of day (0-23, default from config)
            minute: Minute of hour (0-59, default from config)
        """
        hour = hour or NEWSLETTER_GENERATION_HOUR
        minute = minute or NEWSLETTER_GENERATION_MINUTE
        
        print(f"\n🚀 Starting scheduler in PRODUCTION mode")
        print(f"   Schedule: Daily at {hour:02d}:{minute:02d}")
        
        self.scheduler.add_job(
            self.generate_newsletters_for_all_users,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=self.job_id,
            replace_existing=True,
        )
        
        self.scheduler.start()
        print(f"✅ Scheduler started in production mode\n")
    
    def start_once_after_delay(self, delay_minutes: int = 2):
        """
        Run the job once after a delay (useful for testing)
        
        Args:
            delay_minutes: Delay in minutes before execution
        """
        run_time = datetime.now() + timedelta(minutes=delay_minutes)
        
        print(f"\n⏰ Scheduling one-time execution")
        print(f"   Will run at: {run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   (in {delay_minutes} minute(s))")
        
        self.scheduler.add_job(
            self.generate_newsletters_for_all_users,
            trigger=DateTrigger(run_date=run_time),
            id=f"{self.job_id}_once",
            replace_existing=True,
        )
        
        self.scheduler.start()
        print(f"✅ One-time job scheduled\n")
    
    def modify_schedule(self, interval_minutes: Optional[int] = None, hour: Optional[int] = None):
        """
        Modify the existing schedule
        
        Args:
            interval_minutes: New interval in minutes (for development mode)
            hour: New hour (for production mode)
        """
        if interval_minutes:
            print(f"🔄 Modifying schedule to every {interval_minutes} minute(s)")
            self.scheduler.reschedule_job(
                self.job_id,
                trigger=IntervalTrigger(minutes=interval_minutes),
            )
        elif hour is not None:
            print(f"🔄 Modifying schedule to daily at {hour:02d}:00")
            self.scheduler.reschedule_job(
                self.job_id,
                trigger=CronTrigger(hour=hour, minute=0),
            )
        
        print(f"✅ Schedule modified\n")
    
    def stop(self):
        """Stop the scheduler"""
        print(f"\n🛑 Stopping scheduler...")
        self.scheduler.shutdown()
        print(f"✅ Scheduler stopped\n")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        jobs = self.scheduler.get_jobs()
        return {
            "running": self.scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
                for job in jobs
            ],
            "running_workflows": self.running_jobs,
        }


# For testing
if __name__ == "__main__":
    print("🧪 Testing Newsletter Scheduler")
    print("=" * 60)
    
    scheduler = NewsletterScheduler()
    
    # Get mode from environment variable
    mode = os.getenv("SCHEDULER_MODE", "development")
    
    if mode == "development":
        # Run every 2 minutes for testing
        scheduler.start_development_mode(interval_minutes=2)
    elif mode == "once":
        # Run once after 2 minutes
        scheduler.start_once_after_delay(delay_minutes=2)
    else:
        # Production mode
        scheduler.start_production_mode()
    
    try:
        # Keep the script running
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()

