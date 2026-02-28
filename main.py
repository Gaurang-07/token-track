"""
main.py - Entry point for TokenTrack.

Usage:
    python main.py
    python main.py --port 8080
    python main.py --no-open
"""

import argparse
import sys
import os

# Ensure the project directory is always on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(
        description="TokenTrack — Multi-AI token analytics & chat dashboard."
    )
    parser.add_argument("--port",    type=int, default=3456)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    try:
        from server import run
        run(port=args.port, open_browser=not args.no_open)
    except ImportError as e:
        print(f"Import error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()