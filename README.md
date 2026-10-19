# concept-atlas — テキストの束を「概念アトラス」にする

フォルダに溜まった文章や、Web サイト・ブログ・note の記事をまとめて読み込み、
**3D 概念マップ・一覧・年表・概念索引・全文リーダー**を 1 枚の HTML にするツールです。

AI エージェント（Claude / Codex / Antigravity / ChatGPT など）にこのリポジトリを読ませて
「このフォルダ（またはこの URL）を概念アトラスにして」と頼むと、`AGENTS.md` の手順に沿って
テキストの収集 → 概念辞書づくり → 要約 → HTML 生成まで進めます。Claude ならアーティファクトとして公開もできます。

実例: **Notebook 概念アトラス**（`examples/notebook/`）— 身体・意識・認知をめぐる約 440 本の探究記録、
概念 82・領域 8・整理済みの関係 16・要約 445 件・note 記事 196 本と照合済み。

---

## 画面でできること

| タブ | 内容 |
|---|---|
| マップ | 資料（点）と概念（光点）を 3D 空間に配置。「概念網」「番号・日付順の螺旋」「分類別の星団」を切り替え。点を選ぶと詳細と関連資料・概念が開く |
| 一覧 | 分類・概念・状態で絞り込み、日付・タイトル・分量で並べ替え。各行に 1〜2 行の要約 |
| 年表 | 月ごとの資料数を領域別に積み上げ、よく出る概念 × 月のヒートマップ、月ごとの資料一覧 |
| 概念索引 | 領域ごとの概念と資料数、よく一緒に出る概念、データの状態、整理済みの関係 |
| 全文リーダー | 見出し・段落・箇条書き・表を整形して全文を表示。検索語のハイライト |

全文検索、`#list` `#time` `#index` や `#資料ID` でのリンク、スマホ表示に対応しています。

同じフォルダに `jev_overlay.json`（配信ツール JEV の Atlas Bridge が書き出す）があれば、資料・概念ごとに「配信（JEV）で」欄（質問数・検証の判定と出典・配信で答えた時刻）、マップ上の検証の光、「この星について JEV に聞く」ボタンが出ます。無ければ何も出ません。

## すぐ使う

```bash
git clone https://github.com/Mizumawari/concept-atlas
cd concept-atlas
pip install -r requirements.txt            # numpy のみ（Python 3.11+）

# 1) 手元のフォルダをそのままアトラスに（概念は自動抽出）
python -m atlas build --input ~/Documents/my-notes --out work/my-notes/dist
#    → work/my-notes/dist/index.html をブラウザで開く

# 2) Web から集めてアトラスに
python -m atlas fetch https://example.com/feed.xml --out work/blog/corpus     # RSS / Atom / sitemap / ページ
python -m atlas fetch note:mizumawari_4096 --out work/note/corpus            # note のクリエイター
python -m atlas init work/blog --title "ブログ 概念アトラス"
python -m atlas build -c work/blog/atlas.toml

# 3) 実例を作り直す
python -m atlas build -c examples/notebook/atlas.toml
```

## 仕組み

```
テキスト（.md / .txt / .html）──┐
  └ fetch: RSS・sitemap・ページ・note ┘
        │
        ▼  atlas/builder.py
  ・タイトル・日付・URL の抽出（front matter / ファイル名 / 本文）
  ・AI 対話ログの前置きの除去、段落・見出し・表の整形
  ・概念辞書（正規表現）での出現数 → 資料ごとの主要概念
     （辞書がなければ、話題性の高い語を自動抽出して共起で領域に分ける）
  ・TF-IDF による資料間の類似、資料 ID の相互参照
  ・公開記事一覧（catalog.tsv）との照合 → 日付・リンク・動画
  ・要約（summaries.tsv）
        │
        ▼  atlas/render.py + atlas/template.html（three.js）
  dist/index.html        単体版（データと全文を埋め込み）
  dist/pub/              公開用（index.html + data.json + texts/*.json）
```

概念辞書と要約は、エージェント（または人）が資料を読んで書く前提です。
自動抽出だけでも動きますが、書き手の言葉で辞書を作ると地図の質が大きく上がります。手順は `AGENTS.md`。

## ファイル構成

```
atlas/                 エンジン（Python。依存は numpy のみ）
  cli.py               python -m atlas {init,fetch,build,suggest,digest}
  builder.py           走査・概念・類似度・照合・要約
  text.py              タイトル判定・整形・AI 対話の前置き除去
  fetch.py             Web からの収集（RSS / sitemap / ページ / note）
  htmltext.py          HTML → テキスト
  render.py            HTML の書き出し
  template.html        画面（three.js 0.128 / 単一ファイル）
AGENTS.md              AI エージェント向けの手順（Claude / Codex / ChatGPT など共通）
CLAUDE.md              Claude 向けの補足
.claude/skills/        Claude Code 用スキル
examples/notebook/     実例：Notebook 概念アトラス
  atlas.toml           概念 82・領域 8・関係 16・分類の設定
  summaries.tsv        要約 445 件
  catalog.tsv          note 記事 196 本の一覧（照合用）
  corpus/              本文（research_corpus と解析スクリプト・データ）
  dist/                生成済みのアトラス
  tools/               note の新着を取り込むスクリプト
  legacy/              Notebook 専用だった旧ビルドスクリプト
```

## ライセンス

- `atlas/` などのコード: MIT License（`LICENSE`）
- `examples/notebook/corpus/`・`summaries.tsv`・`catalog.tsv` の文章: 著作権は作者（みずまわり / Mizumawari）に帰属します。閲覧・引用の範囲を超える再利用はご遠慮ください。

---

## English (short)

**concept-atlas** turns a folder of texts (or a website / RSS feed / sitemap / note.com creator) into a single
interactive HTML "concept atlas": a 3D concept map, a filterable list, a timeline, a concept index and a full-text reader.

```bash
pip install -r requirements.txt
python -m atlas build --input path/to/texts --out dist      # auto-derived concepts
python -m atlas fetch https://example.com/feed.xml --out corpus
python -m atlas build -c examples/notebook/atlas.toml       # the bundled example
```

Point an AI agent at this repository and ask it to "make a concept atlas of this folder / site";
the workflow (collect → concept dictionary → summaries → build → deliver) is in `AGENTS.md`.
