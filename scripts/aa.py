#!/usr/bin/env python3
"""Run directly from any working directory; no installation or packages required."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from agent_architect.cli import main
raise SystemExit(main())
