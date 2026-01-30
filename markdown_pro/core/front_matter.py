from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import yaml


@dataclass
class FrontMatterResult:
    metadata: Dict[str, Any]
    content: str


def parse_front_matter(text: str) -> FrontMatterResult:
    """
    Suporta YAML front matter no estilo:

    ---
    title: Meu doc
    author: Fulano
    tags:
      - a
      - b
    ---

    Conteúdo...
    """
    lines = text.splitlines()
    if len(lines) < 3:
        return FrontMatterResult(metadata={}, content=text)

    if lines[0].strip() != "---":
        return FrontMatterResult(metadata={}, content=text)

    # encontra o segundo --- (fim)
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return FrontMatterResult(metadata={}, content=text)

    yaml_block = "\n".join(lines[1:end_idx]).strip()
    rest = "\n".join(lines[end_idx + 1 :]).lstrip("\n")

    if not yaml_block:
        return FrontMatterResult(metadata={}, content=rest)

    try:
        data = yaml.safe_load(yaml_block) or {}
        if not isinstance(data, dict):
            data = {"_front_matter": data}
        return FrontMatterResult(metadata=data, content=rest)
    except Exception:
        # se YAML estiver quebrado, não destrói o documento
        return FrontMatterResult(metadata={"_front_matter_error": True}, content=text)
