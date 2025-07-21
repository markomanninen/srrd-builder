#!/usr/bin/env python3
"""
SRRD-Builder CLI Main Entry Point
This file handles execution when called with python -m srrd_builder.cli
"""

import sys
from .main import main

if __name__ == '__main__':
    sys.exit(main())
