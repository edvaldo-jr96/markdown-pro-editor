from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from markdown_pro.utils.paths import recent_files_path
from markdown_pro.utils.config_store import read_json, write_json


MAX_RECENTS = 10


@dataclass
class DocumentState:
    path: Optional[Path] = None
    content: str = ""
    dirty: bool = False


class DocumentManager:
    def __init__(self) -> None:
        self.state = DocumentState()

    # ---------- Document lifecycle ----------
    def new_document(self) -> None:
        self.state = DocumentState(path=None, content="", dirty=False)

    def open_document(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        self.state = DocumentState(path=path, content=text, dirty=False)
        self._add_recent(path)
        return text

    def save(self, content: str) -> Path:
        if self.state.path is None:
            raise ValueError("Documento sem caminho. Use save_as().")
        self.state.path.write_text(content, encoding="utf-8")
        self.state.content = content
        self.state.dirty = False
        self._add_recent(self.state.path)
        return self.state.path

    def save_as(self, path: Path, content: str) -> Path:
        path.write_text(content, encoding="utf-8")
        self.state.path = path
        self.state.content = content
        self.state.dirty = False
        self._add_recent(path)
        return path

    def set_dirty(self, dirty: bool) -> None:
        self.state.dirty = dirty

    # ---------- Recents ----------
    def get_recents(self) -> list[str]:
        data = read_json(recent_files_path(), default={"recents": []})
        recents = data.get("recents", [])
        # garantir tipo
        return [r for r in recents if isinstance(r, str)]

    def _add_recent(self, path: Path) -> None:
        recents = self.get_recents()
        s = str(path)
        if s in recents:
            recents.remove(s)
        recents.insert(0, s)
        recents = recents[:MAX_RECENTS]
        write_json(recent_files_path(), {"recents": recents})
