#!/usr/bin/env python3
"""
AI Code Critic Entry Point.
Allows running the CLI directly using python.
"""

import sys
import warnings

# Suppress all library-level warnings to ensure clean, focused CLI output
warnings.filterwarnings("ignore")

from ai_reviewer.cli import main

if __name__ == "__main__":
    sys.exit(main())
