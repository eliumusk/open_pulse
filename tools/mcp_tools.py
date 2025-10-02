"""
MCP Tools configuration for Open Pulse
Provides search and research capabilities through MCP servers
"""
import os
from agno.tools.mcp import MultiMCPTools


async def get_mcp_tools() -> MultiMCPTools:
    """
    Initialize and return MCP tools for the agents.
    
    This includes:
    - Brave Search: Web search capabilities
    - Arxiv: Academic paper search
    
    Returns:
        MultiMCPTools: Configured MCP tools instance
    """
    # Get API keys from environment
    brave_api_key = os.getenv("BRAVE_API_KEY")
    
    # Build environment variables for MCP servers
    env = {
        **os.environ,
    }
    
    if brave_api_key:
        env["BRAVE_API_KEY"] = brave_api_key
    
    # Configure MCP server commands
    commands = []
    
    # Add Brave Search if API key is available
    if brave_api_key:
        commands.append("npx -y @modelcontextprotocol/server-brave-search")
    
    # Add Arxiv (no API key required)
    # Note: We'll use Agno's built-in ArxivTools instead for simplicity
    
    if not commands:
        raise ValueError(
            "No MCP servers configured. Please set BRAVE_API_KEY environment variable."
        )
    
    # Initialize MCP tools
    mcp_tools = MultiMCPTools(
        commands=commands,
        env=env,
        timeout_seconds=30,
        allow_partial_failure=True,  # Continue even if one server fails
    )
    
    # Connect to MCP servers
    await mcp_tools.connect()
    
    return mcp_tools


async def close_mcp_tools(mcp_tools: MultiMCPTools):
    """Close MCP tools connections"""
    await mcp_tools.close()

