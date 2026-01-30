from __future__ import annotations


def wrap(text: str, left: str, right: str) -> str:
    return f"{left}{text}{right}"


def make_link(text: str, url: str) -> str:
    return f"[{text}]({url})"
