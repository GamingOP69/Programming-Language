"""
Samrat Programming Language — Entry Point

Usage:
    python main.py              # Start REPL
    python main.py <file.sam>   # Run a Samrat file
    python main.py <command>     # Run CLI command
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main as cli_main


def main():
    """Main entry point - delegates to CLI."""
    sys.exit(cli_main())


if __name__ == "__main__":
    main()