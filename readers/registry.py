"""
Reader Registry - Centralized registration system for custom readers

This module provides a unified way to register all custom readers with both
the Knowledge instance and ReaderFactory.
"""
import os
from typing import Optional
from agno.knowledge import Knowledge
from agno.knowledge.reader.reader_factory import ReaderFactory
from .jina_reader import JinaWebReader


def register_all_readers(knowledge: Knowledge) -> dict:
    """
    Register all custom readers with the Knowledge instance.
    
    This function:
    1. Creates instances of all custom readers
    2. Adds them to knowledge.readers dictionary (for AgentOS priority lookup)
    3. Registers them with ReaderFactory (for fallback lookup)
    
    Args:
        knowledge: The Knowledge instance to register readers with
        
    Returns:
        dict: A dictionary of registered reader names and their status
        
    Example:
        >>> knowledge = Knowledge(name="My KB", vector_db=vector_db, contents_db=contents_db)
        >>> status = register_all_readers(knowledge)
        >>> print(status)
        {'JinaWebReader': 'registered', 'CustomReader': 'skipped: missing API key'}
    """
    status = {}
    
    # Initialize knowledge.readers if it doesn't exist
    if not knowledge.readers:
        knowledge.readers = {}
    
    # Register JinaWebReader
    jina_status = _register_jina_reader(knowledge)
    status['JinaWebReader'] = jina_status
    
    # Add more custom readers here in the future
    # Example:
    # custom_status = _register_custom_reader(knowledge)
    # status['CustomReader'] = custom_status
    
    return status


def _register_jina_reader(knowledge: Knowledge) -> str:
    """
    Register JinaWebReader with the Knowledge instance.
    
    Args:
        knowledge: The Knowledge instance to register with
        
    Returns:
        str: Registration status message
    """
    jina_api_key = os.getenv("JINA_API_KEY")
    
    if not jina_api_key:
        return "skipped: JINA_API_KEY not found"
    
    try:
        # Create JinaWebReader instance
        jina_reader = JinaWebReader(
            api_key=jina_api_key,
            name="Jina Web Reader",
            description="A reader for web content using Jina API"
        )
        
        # Add to knowledge.readers dictionary (AgentOS checks this first!)
        knowledge.readers["JinaWebReader"] = jina_reader
        
        # Also register with ReaderFactory (for fallback lookup)
        def create_jina_reader(**kwargs):
            """Factory method to create JinaWebReader instance."""
            return JinaWebReader(api_key=jina_api_key, **kwargs)
        
        ReaderFactory.register_reader(
            key="JinaWebReader",
            reader_method=create_jina_reader,
            name="Jina Web Reader",
            description="A reader for web content using Jina API",
            extensions=None
        )
        
        return "registered"
        
    except Exception as e:
        return f"failed: {str(e)}"


# Template for adding new custom readers:
"""
def _register_custom_reader(knowledge: Knowledge) -> str:
    '''
    Register CustomReader with the Knowledge instance.
    
    Args:
        knowledge: The Knowledge instance to register with
        
    Returns:
        str: Registration status message
    '''
    # Check for required API keys or configuration
    api_key = os.getenv("CUSTOM_API_KEY")
    if not api_key:
        return "skipped: CUSTOM_API_KEY not found"
    
    try:
        # Create reader instance
        custom_reader = CustomReader(
            api_key=api_key,
            name="Custom Reader",
            description="Description of what this reader does"
        )
        
        # Add to knowledge.readers
        knowledge.readers["CustomReader"] = custom_reader
        
        # Register with ReaderFactory
        def create_custom_reader(**kwargs):
            return CustomReader(api_key=api_key, **kwargs)
        
        ReaderFactory.register_reader(
            key="CustomReader",
            reader_method=create_custom_reader,
            name="Custom Reader",
            description="Description of what this reader does",
            extensions=None  # or [".ext1", ".ext2"] for file-based readers
        )
        
        return "registered"
        
    except Exception as e:
        return f"failed: {str(e)}"
"""

