#!/usr/bin/env python3
"""Main CLI entry point for Dark Data Platform."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dark_data.cli.simple_viewer import main as simple_viewer_main


def main():
    """Main CLI entry point."""
    simple_viewer_main()


if __name__ == "__main__":
    main()