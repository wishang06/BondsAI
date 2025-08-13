"""Main entry point for BondsAI."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from bondsai.cli import main

if __name__ == "__main__":
    main()
