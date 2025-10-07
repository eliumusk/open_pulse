"""
Open Pulse AgentOS - Main server application
This file sets up the AgentOS with all agents and serves the API
"""
from agno.db.sqlite import SqliteDb
from agno.os import AgentOS
from fastapi.staticfiles import StaticFiles
from agents import create_newsletter_agent, create_digest_agent, create_research_agent, create_social_agent
from workflows import create_newsletter_workflow, create_simple_newsletter_workflow
from config.settings import (
    DATABASE_FILE,
    AGENTOS_PORT,
    AGENTOS_HOST,
    STATIC_DIR,
    validate_settings,
)


# Validate settings on startup
validate_settings()

# Create shared database instance
db = SqliteDb(
    db_file=DATABASE_FILE,
)


# Create agents
newsletter_agent = create_newsletter_agent(db=db)
digest_agent = create_digest_agent(db=db)
research_agent = create_research_agent(db=db)
social_agent = create_social_agent(db=db)
print("✅ Agents created successfully")

# Create workflows
newsletter_workflow = create_newsletter_workflow(db=db)
simple_workflow = create_simple_newsletter_workflow(db=db)
print("✅ Workflows created successfully")

# Create AgentOS
agent_os = AgentOS(
    id="open-pulse-os",
    description="Open Pulse - Your personalized AI newsletter service",
    agents=[newsletter_agent, digest_agent, research_agent, social_agent],
    workflows=[newsletter_workflow, simple_workflow],  
)

# Get the FastAPI app
app = agent_os.get_app()

# Mount static files directory for serving images
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    print(f"""
📍 Server starting on: http://{AGENTOS_HOST}:{AGENTOS_PORT}
📚 API Documentation: http://{AGENTOS_HOST}:{AGENTOS_PORT}/docs
""")
    
    agent_os.serve(
        app="agentos:app",
        host=AGENTOS_HOST,
        port=AGENTOS_PORT,
        reload=True,
    )

