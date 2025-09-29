"""
JsonTable2Md パッケージ

HTML テーブルを Markdown 拡張記法へ変換するためのコア機能を提供します。
"""

from .jsontable2md import (
    convert_file,
    JsonTable2MdError,
    InputFileError,
    InvalidJsonError,
    ConversionError,
    OutputFileError,
)
from .json_converter import JSONTableConverter, html_table_to_markdown

__all__ = [
    "convert_file",
    "JsonTable2MdError",
    "InputFileError",
    "InvalidJsonError",
    "ConversionError",
    "OutputFileError",
    "JSONTableConverter",
    "html_table_to_markdown",
]

__version__ = "0.1.0"

