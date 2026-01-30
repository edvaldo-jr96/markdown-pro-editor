from __future__ import annotations

MARKDOWN_EXTENSIONS = [
    "extra",
    "tables",
    "toc",
    "footnotes",
    "attr_list",
    "admonition",
    "codehilite",
    "meta",
]

MARKDOWN_EXTENSION_CONFIGS = {
    "toc": {"permalink": True},
    "codehilite": {
        "guess_lang": False,
        "use_pygments": True,
        "noclasses": True,  # inline styles (bom pro PDF/HTML standalone)
    },
}
