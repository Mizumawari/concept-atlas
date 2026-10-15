# CLAUDE.md

このリポジトリでの作業手順は **AGENTS.md** にまとめてあります。まずそれを読んでください。

Claude 固有の補足:

- ユーザーとの会話は日本語で。
- 「フォルダ／サイトを概念アトラスにして」と頼まれたら、AGENTS.md の 1〜7 を順に進める。概念辞書（手順 3）と要約（手順 4）は自分で資料を読んで書く。
- Artifact ツールがあるときは、`dist/pub/index.html` をページとして公開し、`files` に `data.json` と `texts/t*.json` をすべて渡す（`{"data.json": ".../dist/pub/data.json", "texts/t0.json": ".../dist/pub/texts/t0.json", ...}`）。同じアトラスの更新は同じ URL に。
- Artifact ツールがないときは `dist/index.html`（単体版）をユーザーに渡す。
- 実例 `examples/notebook/` の設定・要約・概念の粒度を手本にする。`examples/notebook/corpus/` の本文は作者の著作物なので、他の用途に流用しない。
