"""Utilities for converting HTML tables embedded in JSON values into Markdown."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class _TableCell:
    row: int
    col: int
    rowspan: int
    colspan: int
    text: str


class JSONTableConverter:
    """Convert HTML table strings within JSON-like objects into Markdown."""

    def convert_json_string(self, json_str: str) -> str:
        """Convert HTML tables within a JSON string.

        Args:
            json_str: JSON string containing HTML tables inside values.

        Returns:
            JSON string with HTML tables replaced by Markdown tables.
        """

        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError as exc:  # pragma: no cover - validated via caller tests
            raise ValueError(f"Invalid JSON format: {exc}") from exc

        converted = self.convert_json_data(json_data)
        return json.dumps(converted, ensure_ascii=False, indent=2)

    def convert_json_file(self, input_file: str, output_file: Optional[str] = None) -> str:
        """Convert HTML tables inside a JSON file.

        Args:
            input_file: Path to the source JSON file.
            output_file: Optional path to the file receiving converted JSON.

        Returns:
            Converted JSON content as a string.
        """

        with open(input_file, "r", encoding="utf-8") as file:
            json_str = file.read()

        converted = self.convert_json_string(json_str)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(converted)

        return converted

    def convert_json_data(self, json_data: Any) -> Any:
        """Recursively convert HTML tables within a JSON-like object."""

        if isinstance(json_data, dict):
            return {key: self.convert_json_data(value) for key, value in json_data.items()}
        if isinstance(json_data, list):
            return [self.convert_json_data(item) for item in json_data]
        if isinstance(json_data, str) and "<table" in json_data.lower():
            return _convert_html_table_string(json_data)
        return json_data


def _convert_html_table_string(html_text: str) -> str:
    """Convert the first HTML table in the given string to Markdown."""

    soup = BeautifulSoup(html_text, "html.parser")
    table = soup.find("table")
    if table is None:
        return html_text

    caption = table.find("caption")
    grid = _build_table_grid(table)
    if not grid:
        markdown = ""
    else:
        markdown = _grid_to_markdown(grid)

    if caption and caption.get_text(strip=True):
        caption_text = caption.get_text(strip=True)
        return f"**{caption_text}**\n\n{markdown}" if markdown else f"**{caption_text}**"
    return markdown


def _build_table_grid(table) -> List[List[str]]:
    rows = table.find_all("tr")
    if not rows:
        return []

    cells: List[_TableCell] = []
    occupancy: Dict[tuple[int, int], _TableCell] = {}
    max_cols = 0

    for row_index, row in enumerate(rows):
        col_index = 0
        for cell in row.find_all(["td", "th"]):
            while (row_index, col_index) in occupancy:
                col_index += 1

            colspan = _parse_span(cell.get("colspan"))
            rowspan = _parse_span(cell.get("rowspan"))
            text = cell.get_text(strip=True)

            cell_info = _TableCell(
                row=row_index,
                col=col_index,
                rowspan=rowspan,
                colspan=colspan,
                text=text,
            )
            cells.append(cell_info)

            for row_offset in range(rowspan):
                for col_offset in range(colspan):
                    occupancy[(row_index + row_offset, col_index + col_offset)] = cell_info

            col_index += colspan

        max_cols = max(max_cols, col_index)

    row_count = len(rows)
    grid = [["" for _ in range(max_cols)] for _ in range(row_count)]
    cell_map: Dict[tuple[int, int], _TableCell] = {}

    for cell in cells:
        for r in range(cell.row, cell.row + cell.rowspan):
            for c in range(cell.col, cell.col + cell.colspan):
                cell_map[(r, c)] = cell

        content_col = cell.col + cell.colspan - 1 if cell.colspan > 1 else cell.col
        content_row = cell.row
        grid[content_row][content_col] = cell.text

    for row_index in range(row_count):
        for col_index in range(max_cols):
            if grid[row_index][col_index]:
                continue

            cell = cell_map.get((row_index, col_index))
            if cell is None:
                grid[row_index][col_index] = ""
                continue

            content_col = cell.col + cell.colspan - 1 if cell.colspan > 1 else cell.col

            if row_index > cell.row:
                grid[row_index][col_index] = "^"
            elif col_index < content_col:
                grid[row_index][col_index] = ">"
            else:
                grid[row_index][col_index] = ""

    return grid


def _grid_to_markdown(grid: List[List[str]]) -> str:
    if not grid:
        return ""

    column_count = len(grid[0])
    header = "|" + "|".join(_stringify(grid[0][col]) for col in range(column_count)) + "|"
    separator = "|" + "|".join("-----" for _ in range(column_count)) + "|"
    data_rows = [
        "|" + "|".join(_stringify(grid[row][col]) for col in range(column_count)) + "|"
        for row in range(1, len(grid))
    ]

    return "\n".join([header, separator, *data_rows]) if data_rows else "\n".join([header, separator])


def _parse_span(value: Optional[str]) -> int:
    try:
        return max(int(value), 1) if value else 1
    except (TypeError, ValueError):  # pragma: no cover - defensive branch
        return 1


def _stringify(value: str) -> str:
    return value if value is not None else ""


def html_table_to_markdown(html_text: str) -> str:
    """Public helper for converting a single HTML table string to Markdown."""

    return _convert_html_table_string(html_text)