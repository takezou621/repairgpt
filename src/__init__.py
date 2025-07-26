"""
RepairGPT - AI-powered electronic device repair assistant
"""

import sys
from pathlib import Path

# Add src directory to Python path for consistent imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

__version__ = "0.1.0"
__author__ = "RepairGPT Team"
__email__ = "team@repairgpt.com"
