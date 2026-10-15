# 実例: Notebook 概念アトラス

みずまわり（Mizumawari）の身体・意識・認知の探究記録（note・Medium・研究ノート・書籍原稿・解析データ）を概念アトラスにしたものです。

- 開く: `dist/index.html`（単体版。ダウンロードしてブラウザで開ける）
- 作り直す: リポジトリのルートで `python -m atlas build -c examples/notebook/atlas.toml`
- 公開版: https://claude.ai/artifact/HDoFQpr6qtVpR5BaLrL2oh

| ファイル | 中身 |
|---|---|
| `atlas.toml` | 分類 13・領域 8・概念 82・整理済みの関係 16 |
| `summaries.tsv` | 資料ごとの 1〜2 行の要約（445 件） |
| `catalog.tsv` | note の公開記事 196 本（本文と照合して日付・リンク・YouTube を付ける） |
| `corpus/research_corpus/` | 一次資料 SRC_001〜、統合モデル、書籍原稿、英語記事、note 記事 |
| `corpus/*.py, *.json, *.txt` | 行動開始コーパスなどの解析スクリプトと結果 |
| `tools/note_to_md.js`, `tools/add_notes.py` | note の新着を取り込む（ブラウザで JS を実行 → JSON → SRC として追加・catalog 更新） |
| `legacy/` | 汎用化する前の Notebook 専用ビルドスクリプトと自動取り込み手順 |

## note の新着を取り込む

1. note.com を開いたブラウザで `tools/note_to_md.js` を実行（`__KNOWN__` を catalog.tsv の key の配列に置き換える）。結果の `NEWNOTES[...]` の JSON を `new_notes.json` に保存。
2. `python tools/add_notes.py new_notes.json`（examples/notebook で実行）
3. 追加された資料の要約を `summaries.tsv` に追記して、ビルドし直す。

本文の著作権は作者に帰属します。
