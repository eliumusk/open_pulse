"""Workflows package for Open Pulse"""
from .newsletter_generation import create_newsletter_workflow
from .newsletter_generation_simple import create_simple_newsletter_workflow

__all__ = [
    "create_newsletter_workflow",
    "create_simple_newsletter_workflow",
]

