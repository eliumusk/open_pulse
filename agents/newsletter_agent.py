"""
Newsletter Agent - The main conversational agent for Open Pulse
This agent interacts with users to understand their interests and preferences
"""
import os
from textwrap import dedent
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.arxiv import ArxivTools
from config.settings import DATABASE_FILE
from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb,SearchType
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.google import GeminiEmbedder
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


def create_newsletter_agent(db: SqliteDb = None) -> Agent:
    """
    Create the Newsletter Agent for conversational interactions.
    
    This agent:
    - Chats with users about their interests
    - Remembers user preferences using Memory
    - Can search for information using MCP tools
    - Maintains conversation history
    
    Args:
        db: Database instance (optional, will create if not provided)
    
    Returns:
        Agent: Configured Newsletter Agent
    """
    if db is None:
        # Use Agno's default table names
        db = SqliteDb(db_file=DATABASE_FILE)
    
    agent = Agent(
        name="Newsletter Agent",
        model=OpenAIChat(id=MODEL_ID),
        description="A friendly AI assistant that helps users discover and learn about topics they're interested in.",
        instructions=dedent("""
            You are the Newsletter Agent for Open Pulse, a personalized newsletter service.
            
            Your role is to:
            1. Have friendly conversations with users about their interests
            2. Learn about what topics they care about (technology, science, business, etc.)
            3. Remember their preferences and interests
            4. Help them discover new information using your search tools
            5. Be curious and ask follow-up questions to better understand their interests
            
            Guidelines:
            - Be warm, friendly, and conversational
            - Ask open-ended questions to learn more about the user
            - When the user mentions an interest, explore it deeper
            - Use your search tools to find relevant, current information
            - Remember what users tell you - their interests will be used to generate personalized newsletters
            - If asked about newsletters, explain that based on your conversations, 
              the system will automatically generate personalized content for them
            
            Example conversation starters:
            - "What topics have been catching your attention lately?"
            - "Tell me about your professional interests or hobbies"
            - "What kind of news or information do you wish you had more time to explore?"
        """),
        # Enable memory to remember user preferences
        db=db,
        knowledge=knowledge,
        enable_user_memories=True,
        enable_agentic_memory=True,  # Let the agent manage its own memories
        
        # Add conversation history to context
        add_history_to_context=True,
        num_history_runs=10,  # Keep last 10 conversation turns
        
        # Enable session summaries for long conversations
        enable_session_summaries=True,
        
        # Add current date/time to context
        add_datetime_to_context=True,
        
        # Tools - will be added dynamically with MCP tools
        tools=[
            #ArxivTools(enable_search_arxiv=True, enable_read_arxiv_papers=False)
        ],
        
        # Enable markdown formatting
        markdown=True,

        # Enable debug mode for detailed logs
        debug_mode=False,
    )
    
    return agent

