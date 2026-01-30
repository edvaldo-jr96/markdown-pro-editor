from __future__ import annotations
from pathlib import Path


APP_DIR_NAME = ".markdown-pro"


def get_app_home() -> Path:
    """Diretório do app em HOME: ~/.markdown-pro"""
    home = Path.home()
    app_home = home / APP_DIR_NAME
    app_home.mkdir(parents=True, exist_ok=True)
    return app_home


def recent_files_path() -> Path:
    return get_app_home() / "recent-files.json"
