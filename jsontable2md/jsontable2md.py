#!/usr/bin/env python3
"""Core conversion helpers for jsontable2md.

Public API:
    - :func:`convert_file`
    - Exception classes (``InputFileError`` etc.)

Design:
    * Fail-fast with typed exceptions (no status code return anymore)
    * Keep JSON structure – only HTML table string values are replaced
    * Write output atomically (best‑effort) & avoid silent overwrites unless explicitly allowed
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Union, Any, Dict, Callable

from .json_converter import JSONTableConverter


logger = logging.getLogger(__name__)


class JsonTable2MdError(RuntimeError):
    """Base exception for the package (kept for type grouping)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InputFileError(JsonTable2MdError):
    """Raised when the input file cannot be read."""


class InvalidJsonError(JsonTable2MdError):
    """Raised when the input file content is not valid JSON."""


class ConversionError(JsonTable2MdError):
    """Raised when HTML table conversion fails."""


class OutputFileError(JsonTable2MdError):
    """Raised when writing the output file fails or is blocked."""


TableJson = Dict[str, Any]


def _read_raw_json(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputFileError(f"Input file not found: {path}") from exc
    except OSError as exc:
        raise InputFileError(f"Failed to read input file: {path}") from exc


def _parse_json(raw: str, origin: Path) -> TableJson:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InvalidJsonError(f"Invalid JSON format in {origin}: {exc.msg}") from exc


def _convert_json_tables(json_obj: TableJson) -> TableJson:
    converter = JSONTableConverter()
    try:
        return converter.convert_json_data(json_obj)
    except Exception as exc:  # pragma: no cover
        raise ConversionError(f"Table conversion failed: {exc}") from exc


def _write_output(data: TableJson, path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise OutputFileError(f"Output file already exists (overwrite disabled): {path}")
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        raise OutputFileError(f"Failed to write output file: {path}") from exc


def convert_file(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    overwrite: bool = False,
) -> TableJson:
    """Convert HTML tables embedded in a JSON file to Markdown syntax and return converted JSON.

    Parameters
    ----------
    input_path : str | Path
        Input JSON file path.
    output_path : str | Path
        Output JSON file path.
    overwrite : bool, default False
        If False and output exists an :class:`OutputFileError` is raised.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    raw = _read_raw_json(input_path)
    parsed = _parse_json(raw, input_path)
    converted = _convert_json_tables(parsed)
    _write_output(converted, output_path, overwrite)
    return converted
