from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import markdown

from markdown_pro.core.front_matter import parse_front_matter
from markdown_pro.core.md_config import MARKDOWN_EXTENSIONS, MARKDOWN_EXTENSION_CONFIGS


DEFAULT_CSS = """
:root { --fg: #111; --muted: #555; --bg: #fff; }
body { font-family: DejaVu Sans, Arial, sans-serif; color: var(--fg); background: var(--bg); line-height: 1.6; }
h1,h2,h3,h4,h5,h6 { margin: 1.2em 0 0.6em; }
p { margin: 0.6em 0; }
a { color: #0b57d0; }
code { background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
pre { background: #f4f4f4; padding: 12px; border-radius: 8px; overflow-x: auto; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
blockquote { border-left: 4px solid #ddd; margin: 1em 0; padding: 0.2em 0.8em; color: var(--muted); }
.admonition { border: 1px solid #ddd; border-left-width: 6px; border-radius: 8px; padding: 10px 12px; margin: 1em 0; }
"""

@dataclass
class RenderResult:
    html_full: str
    html_body: str
    metadata: Dict[str, Any]


class MarkdownProcessor:
    def __init__(self, css: Optional[str] = None) -> None:
        self.css = css or DEFAULT_CSS

    def render(self, text: str) -> RenderResult:
        fm = parse_front_matter(text)
        md = markdown.Markdown(
            extensions=MARKDOWN_EXTENSIONS,
            extension_configs=MARKDOWN_EXTENSION_CONFIGS,
            output_format="html5",
        )

        html_body = md.convert(fm.content)
        # metadata da extensão "meta" vem em md.Meta (valores como lista de strings)
        meta_from_md = getattr(md, "Meta", {}) or {}

        merged_meta: Dict[str, Any] = {}
        merged_meta.update(fm.metadata)
        # normaliza meta do markdown
        for k, v in meta_from_md.items():
            if isinstance(v, list) and len(v) == 1:
                merged_meta[k] = v[0]
            else:
                merged_meta[k] = v

        title = str(merged_meta.get("title") or "Documento")

        html_full = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape_html(title)}</title>
  <style>{self.css}</style>
</head>
<body>
{html_body}
</body>
</html>
"""
        return RenderResult(html_full=html_full, html_body=html_body, metadata=merged_meta)


def _escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )
