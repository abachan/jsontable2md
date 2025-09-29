# jsontable2md

jsontable2mdは、JSON内に埋め込まれたHTMLテーブルをMarkdown拡張記法（`>` / `^` によるセル結合表現）へ変換するPythonライブラリです。`rowspan` / `colspan` を解析し、元のJSON構造を保持したままテーブル部分のみMarkdownへ置換します。

## 特徴

- JSON内の複雑な `rowspan` / `colspan` を含むHTMLテーブルをMarkdown化
- `<caption>` は太字行として取り込み
- クロスプラットフォーム対応（Windows/Linux/Mac）

## インストール

```bash
pip install jsontable2md
```

## 使用方法

```python
from jsontable2md import convert_file

# 基本的な使用方法
converted = convert_file(
    input_path="input.json",
    output_path="output.json"
)

# 上書きを許可する場合
converted = convert_file(
    input_path="input.json",
    output_path="output.json",
    overwrite=True
)
```

## パラメータ（convert_file）

- `input_path` (str | Path): 入力JSONファイルパス
- `output_path` (str | Path): 出力先ファイルパス
- `overwrite` (bool): 既存出力を上書きするか（デフォルト: False）

## 戻り値（convert_file）

戻り値は変換後の JSON オブジェクト（dict）。

## エラーハンドリング

```python
from jsontable2md import convert_file
import logging

# ログレベルの設定
logging.basicConfig(level=logging.INFO)

try:
    converted = convert_file(input_path="input.json",output_path="output.json")
    print("JSON内に埋め込まれたHTMLテーブルをMarkdown拡張記法に変換完了しました")
except Exception as e:
    print(f"エラーが発生しました: {e}")
```

## ライセンス

本プロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。