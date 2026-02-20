#!/usr/bin/env python3
"""
NanoStore Bot - Main Entry Point
Run this file to start the bot
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the bot
from core import main

if __name__ == "__main__":
    main()
