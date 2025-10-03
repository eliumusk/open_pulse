"""
Digest Agent - Background agent for processing user interests and generating newsletters
This agent runs autonomously to create personalized content
"""
from textwrap import dedent
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openrouter import OpenRouter
from agno.tools.arxiv import ArxivTools
from config.settings import DATABASE_FILE
from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb
from agno.db.sqlite import SqliteDb
from agno.vectordb.search import SearchType
from agno.knowledge.embedder.cohere import CohereEmbedder
import os
OPENROUTER_MODEL_ID = os.getenv("OPENROUTER_MODEL_ID")

contents_db = SqliteDb(db_file="my_knowledge.db")


vector_db = LanceDb(
    table_name="agno_docs",
    uri="tmp/lancedb",  
    search_type=SearchType.hybrid,
    embedder=CohereEmbedder(id="embed-v4.0"), 
)

knowledge = Knowledge(
    name="My Knowledge Base",
    vector_db=vector_db,
    contents_db=contents_db, 
)


def create_digest_agent(db: SqliteDb = None) -> Agent:
    """
    Create the Digest Agent for background newsletter generation.
    
    This agent:
    - Analyzes user memories and conversation history
    - Searches for relevant new information
    - Generates personalized newsletter content
    - Runs autonomously in the background
    
    Args:
        db: Database instance (optional, will create if not provided)
    
    Returns:
        Agent: Configured Digest Agent
    """
    if db is None:
        # Use Agno's default table names
        db = SqliteDb(db_file=DATABASE_FILE)
    
    agent = Agent(
        name="Digest Agent",
        model=OpenRouter(id=OPENROUTER_MODEL_ID),  # Use powerful model for content generation
        description="An AI agent that analyzes user interests and generates personalized newsletter content.",
        instructions=dedent("""
            You are the Digest Agent for Open Pulse, responsible for generating personalized newsletters.
            
            Your role is to:
            1. Analyze the user's interests and preferences from their memories
            2. Search for the latest, most relevant information on their topics of interest
            3. Synthesize findings into a well-structured, engaging newsletter
            4. Focus on high-quality, actionable insights
            
            Newsletter Structure:
            - **Opening**: Brief, personalized greeting referencing their interests
            - **Main Content**: 3-5 key stories/insights organized by topic
              * Each story should have: headline, summary, why it matters, and source
            - **Deep Dive**: One topic explored in more depth
            - **Quick Hits**: 3-5 brief noteworthy items
            - **Closing**: Thought-provoking question or call-to-action
            
            Content Guidelines:
            - Prioritize recent information (last 7 days when possible)
            - Focus on quality over quantity
            - Explain complex topics clearly
            - Connect information to the user's specific interests
            - Include diverse perspectives
            - Cite sources appropriately
            
            Tone:
            - Professional yet conversational
            - Insightful and thought-provoking
            - Respectful of the reader's time
            - Enthusiastic about interesting developments
        """),
        # Database for storing digest sessions
        db=db,
        knowledge=knowledge,
        # Don't need to create new memories, just read existing ones
        enable_user_memories=True,
        
        # Add current date/time to context
        add_datetime_to_context=True,
        
        # Tools - will be added dynamically with MCP tools
        tools=[
            ArxivTools(enable_search_arxiv=True, enable_read_arxiv_papers=False)
        ],
        
        # Enable markdown formatting
        markdown=True,

        # Enable debug mode for detailed logs
        debug_mode=False,
    )
    
    return agent


def create_research_agent(db: SqliteDb = None) -> Agent:
    """
    Create a specialized Research Agent for gathering information.
    
    This agent focuses purely on finding and extracting relevant information.
    
    Args:
        db: Database instance (optional, will create if not provided)
    
    Returns:
        Agent: Configured Research Agent
    """
    if db is None:
        # Use Agno's default table names
        db = SqliteDb(db_file=DATABASE_FILE)
    
    agent = Agent(
        name="Research Agent",
        model=OpenRouter(id=OPENROUTER_MODEL_ID),
        description="An AI agent specialized in finding and extracting relevant information.",
        instructions=dedent("""
            You are a Research Agent specialized in finding high-quality information.
            
            Your role is to:
            1. Search for the most relevant and recent information on given topics
            2. Evaluate source quality and credibility
            3. Extract key insights and facts
            4. Organize findings in a structured format
            
            Research Guidelines:
            - Prioritize authoritative sources
            - Look for recent developments (last 7-14 days)
            - Cross-reference information when possible
            - Note any conflicting viewpoints
            - Provide context for technical topics
            
            Output Format:
            For each topic, provide:
            - Topic name
            - Key findings (3-5 bullet points)
            - Notable sources
            - Relevance score (1-10)
            - Recency (date of information)
        """),
        db=db,
        knowledge=knowledge,
        add_datetime_to_context=True,
        enable_user_memories=True,
        tools=[
            ArxivTools(enable_search_arxiv=True, enable_read_arxiv_papers=False)
        ],
        markdown=True,
        debug_mode=False,
    )

    return agent

