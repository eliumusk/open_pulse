"""
Custom readers for Open Pulse

This package provides custom reader implementations and a centralized
registration system for use with Agno Knowledge.

Usage:
    from agno.knowledge import Knowledge
    from readers import register_all_readers

    knowledge = Knowledge(name="My KB", vector_db=vector_db, contents_db=contents_db)
    status = register_all_readers(knowledge)
    print(f"Reader registration status: {status}")
"""
from .jina_reader import JinaWebReader
from .registry import register_all_readers

__all__ = ['JinaWebReader', 'register_all_readers']

