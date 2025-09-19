#!/usr/bin/env python3
"""Main CLI entry point for EPN configuration tools."""

import sys
from pathlib import Path

# Import CLI directly
from epn_core.cli import main

# Set up paths
root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))

if __name__ == "__main__":
    main()
