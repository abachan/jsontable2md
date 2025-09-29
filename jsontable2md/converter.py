"""Compatibility wrappers for legacy imports.

The public API now lives in :mod:`jsontable2md.json_converter`. This module
keeps a very small shim so that existing imports continue to function while
internally delegating to the new implementation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .json_converter import html_table_to_markdown


class TableConverter:
    """Backwards compatible façade over :func:`html_table_to_markdown`."""

    def convert(self, html_content: str, preserve_caption: bool = True) -> str:
        # ``preserve_caption`` is retained for compatibility; the new converter
        # always keeps captions, so the flag is accepted but ignored.
        _ = preserve_caption
        return html_table_to_markdown(html_content)

    def convert_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        html = Path(input_file).read_text(encoding="utf-8")
        markdown = self.convert(html)

        if output_file:
            Path(output_file).write_text(markdown, encoding="utf-8")

        return markdown


def convert_html_table_to_markdown(html_content: str) -> str:
    """Compatibility function mirroring the previous module-level helper."""

    return html_table_to_markdown(html_content)


__all__ = ["TableConverter", "convert_html_table_to_markdown"]