---
name: concept-atlas
description: テキストのフォルダや Web サイト（URL・RSS・note）から、3D概念マップ・一覧・年表・概念索引・全文リーダーを備えた「概念アトラス」HTML を作る。「概念アトラスにして」「まとめてマップ化して」と頼まれたときに使う。
---

# 概念アトラスを作る

リポジトリのルートにある `AGENTS.md` の手順 1〜7 に従う。要点:

1. 入力を `work/<名前>/corpus/` に用意する（フォルダはそのまま、URL は `python -m atlas fetch <URL> --out work/<名前>/corpus`、取れなければ自分で本文を取得して front matter 付き .md で保存）。
2. `python -m atlas init work/<名前> --title "…"` → `python -m atlas build -c work/<名前>/atlas.toml` で一度全体を見る。
3. `python -m atlas suggest` の候補と代表的な資料を読んで、書き手の言葉で themes（5〜8）と concepts（40〜90、pattern に同義語・英語）を atlas.toml に書く。
4. `python -m atlas digest` の一覧を読み、`summaries.tsv`（パス<TAB>1〜2行の中立な要約）を書く。
5. 再ビルドし、索引タブで概念の偏りとタイトルを確認する。
6. Artifact ツールがあれば `dist/pub/index.html` を公開し、`files` に `data.json` と `texts/t*.json` を渡す。なければ `dist/index.html` を渡す。
