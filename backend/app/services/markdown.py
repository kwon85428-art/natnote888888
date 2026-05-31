"""Markdown → HTML（文章正文展示）。"""

from __future__ import annotations

import markdown


def markdown_to_html(text: str) -> str:
    if not (text or "").strip():
        return ""
    return markdown.markdown(
        text,
        extensions=[
            "markdown.extensions.extra",
            "markdown.extensions.nl2br",
            "markdown.extensions.sane_lists",
        ],
        output_format="html",
    )
