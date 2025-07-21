#!/usr/bin/env python3
"""
Entry point for running the SRRD-Builder MCP Server as a module
Usage: python3 -m srrd_builder.server
"""

from .launcher import main

if __name__ == "__main__":
    main()
