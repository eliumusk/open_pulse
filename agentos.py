"""
Open Pulse AgentOS - Main server application
This file sets up the AgentOS with all agents and serves the API
"""
import asyncio
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from agno.tools.mcp import MultiMCPTools

from agents import create_newsletter_agent, create_digest_agent, create_research_agent
from workflows import create_newsletter_workflow, create_simple_newsletter_workflow
from config.settings import (
    DATABASE_FILE,
    AGENTOS_PORT,
    AGENTOS_HOST,
    validate_settings,
)
from tools import get_mcp_tools


# Validate settings on startup
validate_settings()

# Create shared database instance
# ✅ Use Agno's default table names for consistency
db = SqliteDb(
    db_file=DATABASE_FILE,
    # Don't specify session_table - use default 'sessions'
    # Don't specify memory_table - use default 'memories'
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

# Create AgentOS
agent_os = AgentOS(
    id="open-pulse-os",
    description="Open Pulse - Your personalized AI newsletter service",
    agents=[newsletter_agent, digest_agent, research_agent],
    workflows=[newsletter_workflow, simple_workflow],  # Add both workflows!
    # Enable MCP server so other agents can interact with this AgentOS
    enable_mcp_server=True,
)

# Get the FastAPI app
app = agent_os.get_app()


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

Available Agents:
  • Newsletter Agent - Chat about your interests
  • Digest Agent - Generate personalized newsletters
  • Research Agent - Find relevant information

Available Workflows:
  • Newsletter Generation Workflow - Full workflow with LLM and search
  • Simple Newsletter Workflow - Simplified workflow for testing (no API calls)

Press Ctrl+C to stop the server
""")
    
    agent_os.serve(
        app="agentos:app",
        host=AGENTOS_HOST,
        port=AGENTOS_PORT,
        reload=True,
    )

