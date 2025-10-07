"""
Memory Configuration for Open Pulse

This module provides centralized memory management configuration for all agents.
It allows customization of how memories are created, stored, and retrieved.
"""
import os
from agno.memory import MemoryManager
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb


# Memory extraction rules and instructions
MEMORY_EXTRACTION_RULES = """
## Memory Extraction Rules

### What to Store:
1. **User Interests**: Topics, domains, industries the user cares about
2. **Content Preferences**: Preferred content types (articles, videos, papers, etc.)
3. **Reading Habits**: Frequency, time preferences, content length preferences
4. **Professional Context**: Job role, industry, expertise level
5. **Learning Goals**: Skills to develop, knowledge areas to explore
6. **Communication Style**: Preferred tone, detail level, language preferences

### What NOT to Store:
1. **Sensitive Personal Information**: Real names, addresses, phone numbers
2. **Temporary Context**: One-time requests, transient information
3. **System Instructions**: Technical commands, debugging information
4. **Redundant Information**: Information already captured in existing memories

### Memory Quality Guidelines:
1. **Be Specific**: "User is interested in AI safety research" > "User likes AI"
2. **Be Actionable**: Store information that helps personalize future content
3. **Be Concise**: One clear fact per memory entry
4. **Be Persistent**: Only store information that's likely to remain relevant
5. **Be Contextual**: Include enough context to understand the memory later

### Examples:

✅ Good Memories:
- "User is a software engineer interested in distributed systems and database internals"
- "User prefers technical deep-dives over high-level overviews"
- "User wants to receive newsletters on Monday mornings"
- "User is learning Rust and interested in systems programming"

❌ Bad Memories:
- "User said hello" (temporary, not useful)
- "User's name is John Smith" (sensitive personal info)
- "User asked about the weather" (not relevant to newsletter service)
- "User likes technology" (too vague, not actionable)
"""


# Additional instructions for chat history processing
WECHAT_HISTORY_EXTRACTION_RULES = """
## Chat History Processing Rules

When processing uploaded chat histories:

1. **Aggregate Patterns**: Look for recurring themes across multiple messages
2. **Identify Evolution**: Track how user interests change over time
3. **Extract Implicit Preferences**: Infer preferences from user behavior and reactions
4. **Consolidate Information**: Merge similar memories to avoid redundancy
5. **Prioritize Recent Information**: Weight recent conversations more heavily

### Processing Strategy:
- First pass: Extract explicit statements of interest
- Second pass: Identify implicit preferences from questions and reactions
- Third pass: Consolidate and deduplicate memories
- Final pass: Validate memories against extraction rules
"""


def create_memory_manager(
    db: SqliteDb,
    model_id: str = None,
    additional_instructions: str = None,
    enable_wechat_history_processing: bool = False
) -> MemoryManager:
    """
    Create a customized MemoryManager for Open Pulse agents.

    Args:
        db: Database connection for storing memories
        model_id: Model to use for memory creation (default: gpt-4o-mini)
        additional_instructions: Extra instructions to append to base rules
        enable_wechat_history_processing: Whether to include chat history processing rules

    Returns:
        MemoryManager: Configured memory manager instance

    Example:
        >>> db = SqliteDb(db_file="open_pulse.db")
        >>> memory_manager = create_memory_manager(
        ...     db=db,
        ...     model_id="gpt-4o-mini",
        ...     enable_wechat_history_processing=True
        ... )
        >>> agent = Agent(
        ...     db=db,
        ...     memory_manager=memory_manager,
        ...     enable_user_memories=True
        ... )
    """
    # Use environment variable or default model
    if model_id is None:
        model_id = os.getenv("MODEL_ID", "gpt-4o-mini")

    # Build instructions
    instructions = MEMORY_EXTRACTION_RULES

    if enable_wechat_history_processing:
        instructions += "\n\n" + WECHAT_HISTORY_EXTRACTION_RULES

    if additional_instructions:
        instructions += "\n\n## Additional Instructions\n\n" + additional_instructions

    # Create memory manager
    memory_manager = MemoryManager(
        db=db,
        model=OpenAIChat(id=model_id),
        additional_instructions=instructions
    )

    return memory_manager


def create_newsletter_memory_manager(db: SqliteDb) -> MemoryManager:
    """
    Create a memory manager optimized for the Newsletter Agent.

    This configuration focuses on:
    - User interests and content preferences
    - Communication style and frequency
    - Professional context and learning goals

    Args:
        db: Database connection

    Returns:
        MemoryManager: Configured for newsletter personalization
    """
    additional_instructions = """
    ### Newsletter-Specific Rules:

    - Focus on content preferences: topics, formats, sources
    - Track engagement patterns: what content gets positive feedback
    - Remember delivery preferences: frequency, timing, length
    - Store professional context for content relevance
    - Capture learning goals to suggest educational content
    """

    return create_memory_manager(
        db=db,
        additional_instructions=additional_instructions,
        enable_wechat_history_processing=False
    )


def create_digest_memory_manager(db: SqliteDb) -> MemoryManager:
    """
    Create a memory manager optimized for the Digest Agent.

    This configuration focuses on:
    - Reading existing memories (not creating new ones)
    - Understanding user context for content generation
    - Tracking content performance over time

    Args:
        db: Database connection

    Returns:
        MemoryManager: Configured for digest generation
    """
    additional_instructions = """
    ### Digest-Specific Rules:

    - Prioritize reading existing memories over creating new ones
    - Focus on actionable preferences for content curation
    - Track which topics generate the most engagement
    - Remember content sources that user finds valuable
    - Note any content types or topics to avoid
    """

    return create_memory_manager(
        db=db,
        additional_instructions=additional_instructions,
        enable_wechat_history_processing=False
    )


def create_chat_history_memory_manager(db: SqliteDb) -> MemoryManager:
    """
    Create a memory manager optimized for processing uploaded chat histories.

    This configuration focuses on:
    - Batch processing of conversation history
    - Pattern recognition across multiple messages
    - Consolidation and deduplication
    - Evolution tracking over time

    Args:
        db: Database connection

    Returns:
        MemoryManager: Configured for chat history processing
    """
    additional_instructions = """
    ### Chat History Processing:

    - Process conversations in batches to identify patterns
    - Look for recurring themes and evolving interests
    - Consolidate similar memories to avoid redundancy
    - Weight recent conversations more heavily
    - Extract both explicit and implicit preferences
    - Create high-quality, actionable memories from conversation context
    """

    return create_memory_manager(
        db=db,
        model_id="gpt-4o",  # Use more powerful model for batch processing
        additional_instructions=additional_instructions,
        enable_wechat_history_processing=True
    )


# Export configuration
__all__ = [
    'create_memory_manager',
    'create_newsletter_memory_manager',
    'create_digest_memory_manager',
    'create_chat_history_memory_manager',
    'MEMORY_EXTRACTION_RULES',
    'WECHAT_HISTORY_EXTRACTION_RULES',
]

