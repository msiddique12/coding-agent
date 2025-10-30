"""
LLM Providers Module

Simple interface for LLM providers.
Currently using NVIDIA NIM for free inference.

Quick Start:
    from llm_providers import NVIDIAProvider
    
    # Create a provider
    provider = NVIDIAProvider(model='llama-8b')
    
    # Use it
    response = provider.query('Write a hello world function')
    print(response)
"""

from .base import LLMProvider
from .nvidia_nim import NVIDIAProvider

# Define what gets imported with "from llm_providers import *"
__all__ = [
    'LLMProvider',
    'NVIDIAProvider',
]