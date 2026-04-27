"""项目路径常量，避免依赖运行时 cwd。"""
from pathlib import Path

# src/agent_system/paths.py -> 项目根 = parents[2]
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
CONFIG_DIR: Path = PROJECT_ROOT / "configs"
SKILLS_JSON: Path = CONFIG_DIR / "skills.json"
API_CATALOG_JSON: Path = CONFIG_DIR / "api_catalog.json"
