"""
Social Agent
"""
import os
from textwrap import dedent
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.gmail import GmailTools
from config.settings import DATABASE_FILE
from config.memory_config import create_wechat_history_memory_manager
from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb,SearchType
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
import os

# Import custom reader registry
from readers import register_all_readers

MODEL_ID = os.getenv("MODEL_ID")

contents_db = SqliteDb(db_file="my_knowledge.db")

vector_db = LanceDb(
    table_name="agno_docs",
    uri="tmp/lancedb",
    search_type=SearchType.hybrid,
    embedder=OpenAIEmbedder(),
)

# Create knowledge base
knowledge = Knowledge(
    name="My Knowledge Base",
    vector_db=vector_db,
    contents_db=contents_db
)

# Register all custom readers
reader_status = register_all_readers(knowledge)
for reader_name, status in reader_status.items():
    if status == "registered":
        print(f"✅ Registered {reader_name}")
    elif status.startswith("skipped"):
        print(f"⚠️  {reader_name}: {status}")
    else:
        print(f"❌ {reader_name}: {status}")


def create_social_agent(db: SqliteDb = None) -> Agent:
    if db is None:
        # Use Agno's default table names
        db = SqliteDb(db_file=DATABASE_FILE)
    
    agent = Agent(
        name="Social Agent",
        model=OpenAIChat(id=MODEL_ID),
        description="A friendly AI assistant that helps users discover and learn about topics they're interested in through social media.",
        instructions=dedent("""
            You are the Social Agent for Open Pulse.
        """),
        db=db,
        knowledge=knowledge,
        memory_manager=create_wechat_history_memory_manager(db),  
        enable_user_memories=True,
        enable_agentic_memory=True,  
        
        add_history_to_context=True,
        num_history_runs=10,  # Keep last 10 conversation turns
        
        enable_session_summaries=True,
        
        add_datetime_to_context=True,
        
        tools=[
            GmailTools()
        ],
        
        markdown=True,
        debug_mode=False,
    )
    
    return agent

