"""
LangChain Compatibility Shim

This module provides compatibility fixes for LangChain version mismatches.
Specifically, it handles the missing 'debug' attribute in langchain module
that langchain_core.globals expects.
"""

import sys
import langchain


# Fix for: AttributeError: module 'langchain' has no attribute 'debug'
# This occurs when langchain_core.globals tries to access langchain.debug
# which doesn't exist in newer versions of langchain

if not hasattr(langchain, 'debug'):
    # Add debug attribute with default value
    langchain.debug = False
    print("LangChain compatibility: Added missing 'debug' attribute")


if not hasattr(langchain, 'verbose'):
    # Add verbose attribute with default value
    langchain.verbose = False
    print("LangChain compatibility: Added missing 'verbose' attribute")


# Ensure the fix is applied before any langchain_core imports
def ensure_compatibility():
    """
    Ensure LangChain compatibility is applied.
    Call this at the start of your application.
    """
    pass  # Compatibility is applied on import


# Auto-apply on import
ensure_compatibility()
