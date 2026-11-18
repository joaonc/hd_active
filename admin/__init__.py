from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
PROJECT_NAME = 'hd_active'
ASSETS_DIR = PROJECT_ROOT / 'assets'
PROJECT_SOURCE_DIR = PROJECT_ROOT / 'src'
"""Source code for the whole project."""
SOURCE_DIR = PROJECT_SOURCE_DIR / PROJECT_NAME
"""Source code for the this project's package."""
