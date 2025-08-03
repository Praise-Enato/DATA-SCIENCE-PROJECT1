# tests/conftest.py

import sys
from pathlib import Path

# Add the src/ directory (where your modules live) to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SRC_DIR       = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))
