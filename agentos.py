"""
Open Pulse AgentOS - Main server application
This file sets up the AgentOS with all agents and serves the API
"""
import asyncio
import json
from typing import Optional
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.tools.mcp import MultiMCPTools
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from agents import create_newsletter_agent, create_digest_agent, create_research_agent
from workflows import create_newsletter_workflow, create_simple_newsletter_workflow
from workflows.notification_manager import get_notification_manager
from config.settings import (
    DATABASE_FILE,
    AGENTOS_PORT,
    AGENTOS_HOST,
    STATIC_DIR,
    validate_settings,
)
from tools import get_mcp_tools


# Validate settings on startup
validate_settings()

# Create custom FastAPI app FIRST (before AgentOS)
custom_app = FastAPI(
    title="Open Pulse API",
    description="Personalized AI Newsletter Service with Notifications",
    version="1.0.0",
)

# Create shared database instance
db = SqliteDb(
    db_file=DATABASE_FILE,
)

# Global MCP tools instance
mcp_tools_instance = None


async def initialize_mcp_tools():
    """Initialize MCP tools asynchronously"""
    global mcp_tools_instance
    if mcp_tools_instance is None:
        try:
            mcp_tools_instance = await get_mcp_tools()
            print("✅ MCP tools initialized successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize MCP tools: {e}")
            print("   Agents will work with limited tools (Arxiv only)")
    return mcp_tools_instance


def add_mcp_tools_to_agent(agent, mcp_tools):
    """Add MCP tools to an agent if available"""
    if mcp_tools:
        # Add MCP tools to existing tools
        if not hasattr(agent, 'tools') or agent.tools is None:
            agent.tools = []
        agent.tools.append(mcp_tools)
    return agent


# Create agents
print("🚀 Creating agents...")
newsletter_agent = create_newsletter_agent(db=db)
digest_agent = create_digest_agent(db=db)
research_agent = create_research_agent(db=db)
print("✅ Agents created successfully")

# Create workflows
print("🔄 Creating workflows...")
newsletter_workflow = create_newsletter_workflow(db=db)
simple_workflow = create_simple_newsletter_workflow(db=db)
print("✅ Workflows created successfully")


# ========================
# Custom API Endpoints (Define BEFORE AgentOS)
# ========================

# We need to define these functions first, then add them to custom_app later
# because they reference agent_os which doesn't exist yet

def create_custom_endpoints(app: FastAPI, agent_os_instance: AgentOS):
    """Add custom endpoints to the FastAPI app"""

    @app.post("/api/workflows/{workflow_id}/run-with-notification")
    async def create_workflow_run_with_notification(
        workflow_id: str,
        request: Request,
    ):
        """
        Custom endpoint to run workflow and track for notifications
        This is separate from the default AgentOS workflow endpoint
        """
        # Parse form data
        form_data = await request.form()

        # Get workflow from AgentOS
        workflow = None
        for wf in agent_os_instance.workflows:
            if wf.name.lower().replace(" ", "-") == workflow_id:
                workflow = wf
                break

        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}, 404

        # Prepare workflow input
        message = form_data.get("message", "")
        user_id = form_data.get("user_id", "default")
        session_id = form_data.get("session_id", "")

        # Run workflow
        try:
            # Start workflow execution in background task
            async def run_and_track_workflow():
                try:
                    # Run workflow (this will block until complete)
                    result = await workflow.arun(
                        input=message,
                        additional_data={
                            "user_id": user_id,
                            "session_id": session_id,
                        },
                    )

                    run_id = result.run_id
                    print(f"✅ Workflow {run_id} completed, sending notification...")

                    # Extract content and cover image
                    content = result.content if hasattr(result, 'content') else None
                    cover_image_url = None

                    # Try to extract cover image
                    if hasattr(result, 'step_results') and result.step_results:
                        for step_result in result.step_results:
                            if hasattr(step_result, 'images') and step_result.images:
                                img = step_result.images[0]
                                if hasattr(img, 'url'):
                                    cover_image_url = img.url
                                    break

                    # Send notification
                    notification_manager = get_notification_manager()
                    await notification_manager.notify_workflow_completion(
                        run_id=run_id,
                        status="completed",
                        content=content,
                        cover_image_url=cover_image_url,
                        workflow_id=workflow_id,
                        user_id=user_id,
                    )

                except Exception as e:
                    print(f"❌ Workflow execution error: {e}")
                    import traceback
                    traceback.print_exc()

            # Start workflow in background
            asyncio.create_task(run_and_track_workflow())

            return {
                "workflow_id": workflow_id,
                "status": "started",
                "notification_enabled": True,
                "message": "Workflow started in background"
            }

        except Exception as e:
            print(f"❌ Error starting workflow: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}, 500


    async def monitor_workflow_completion(workflow, run_id: str, enable_notification: bool = True):
        """
        Background task to monitor workflow completion and send notification
        """
        if not enable_notification:
            return

        max_wait = 600  # 10 minutes max
        check_interval = 3  # Check every 3 seconds
        elapsed = 0

        notification_manager = get_notification_manager()

        while elapsed < max_wait:
            await asyncio.sleep(check_interval)
            elapsed += check_interval

            try:
                # Get workflow run status
                run = workflow.get_run(run_id)

                if run and run.has_completed():
                    print(f"✅ Workflow {run_id} completed, extracting results...")

                    # Extract content and cover image
                    content = run.content if hasattr(run, 'content') else None
                    cover_image_url = None

                    # Try to extract cover image from run step results
                    if hasattr(run, 'step_results') and run.step_results:
                        for step_result in run.step_results:
                            # Check if this step has images
                            if hasattr(step_result, 'images') and step_result.images:
                                img = step_result.images[0]
                                if hasattr(img, 'url'):
                                    cover_image_url = img.url
                                    print(f"🖼️  Found cover image: {cover_image_url}")
                                    break

                    # Also try events
                    if not cover_image_url and hasattr(run, 'events') and run.events:
                        for event in run.events:
                            if hasattr(event, 'images') and event.images:
                                img = event.images[0]
                                if hasattr(img, 'url'):
                                    cover_image_url = img.url
                                    print(f"🖼️  Found cover image in events: {cover_image_url}")
                                    break

                    # Send notification
                    await notification_manager.notify_workflow_completion(
                        run_id=run_id,
                        status="completed",
                        content=content,
                        cover_image_url=cover_image_url,
                    )

                    return

                elif run and hasattr(run, 'status') and run.status == 'failed':
                    print(f"❌ Workflow {run_id} failed")
                    await notification_manager.notify_workflow_completion(
                        run_id=run_id,
                        status="failed",
                        error="Workflow execution failed",
                    )
                    return

            except Exception as e:
                print(f"⚠️  Error checking workflow status: {e}")
                import traceback
                traceback.print_exc()

        # Timeout
        print(f"⏰ Workflow {run_id} monitoring timed out")
        await notification_manager.notify_workflow_completion(
            run_id=run_id,
            status="failed",
            error="Workflow monitoring timeout",
        )


    @app.get("/api/notifications/stream")
    async def notification_stream(request: Request):
        """
        SSE endpoint for real-time workflow completion notifications
        Frontend subscribes to this endpoint to receive notifications
        """
        notification_manager = get_notification_manager()
        client_id, queue = notification_manager.subscribe()

        async def event_generator():
            try:
                # Send initial connection message
                yield {
                    "event": "connected",
                    "data": json.dumps({
                        "message": "Connected to notification stream",
                        "client_id": client_id,
                    })
                }

                print(f"✅ SSE client {client_id} connected")

                # Stream notifications
                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        print(f"🔌 Client {client_id} disconnected")
                        break

                    try:
                        # Wait for notification with timeout
                        notification = await asyncio.wait_for(queue.get(), timeout=30.0)

                        print(f"📤 Sending notification to client {client_id}")

                        yield {
                            "event": "workflow_completed",
                            "data": json.dumps(notification)
                        }

                    except asyncio.TimeoutError:
                        # Send heartbeat to keep connection alive
                        yield {
                            "event": "heartbeat",
                            "data": json.dumps({"timestamp": asyncio.get_event_loop().time()})
                        }

            except Exception as e:
                print(f"❌ Error in notification stream for client {client_id}: {e}")
                import traceback
                traceback.print_exc()

            finally:
                # Cleanup
                notification_manager.unsubscribe(client_id)
                print(f"🔕 Client {client_id} unsubscribed")

        return EventSourceResponse(event_generator())


    @app.get("/api/notifications/stats")
    async def notification_stats():
        """Get notification manager statistics (for debugging)"""
        notification_manager = get_notification_manager()
        return notification_manager.get_stats()


# Create AgentOS with custom FastAPI app
agent_os = AgentOS(
    id="open-pulse-os",
    description="Open Pulse - Your personalized AI newsletter service",
    agents=[newsletter_agent, digest_agent, research_agent],
    workflows=[newsletter_workflow, simple_workflow],
    base_app=custom_app,  # Pass our custom app
    enable_mcp_server=True,
)

# Get the combined app (custom_app + AgentOS routes)
app = agent_os.get_app()

# Mount static files directory for serving images
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Add custom endpoints to the app
create_custom_endpoints(app, agent_os)


@app.on_event("startup")
async def startup_event():
    """Initialize MCP tools on startup"""
    print("🔧 Initializing MCP tools...")
    mcp_tools = await initialize_mcp_tools()
    
    if mcp_tools:
        # Add MCP tools to all agents
        add_mcp_tools_to_agent(newsletter_agent, mcp_tools)
        add_mcp_tools_to_agent(digest_agent, mcp_tools)
        add_mcp_tools_to_agent(research_agent, mcp_tools)
        print("✅ MCP tools added to all agents")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up MCP tools on shutdown"""
    global mcp_tools_instance
    if mcp_tools_instance:
        from tools import close_mcp_tools
        await close_mcp_tools(mcp_tools_instance)
        print("✅ MCP tools closed")


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    🌟 Open Pulse AgentOS 🌟                  ║
║                                                              ║
║  Your personalized AI newsletter service                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📍 Server starting on: http://{AGENTOS_HOST}:{AGENTOS_PORT}
📚 API Documentation: http://{AGENTOS_HOST}:{AGENTOS_PORT}/docs
🔌 MCP Server: http://{AGENTOS_HOST}:{AGENTOS_PORT}/mcp

""")
    
    agent_os.serve(
        app="agentos:app",
        host=AGENTOS_HOST,
        port=AGENTOS_PORT,
        reload=True,
    )

