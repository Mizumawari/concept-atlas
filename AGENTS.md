# AGENTS.md — 概念アトラスを作る手順（AI エージェント向け）

このリポジトリは、**テキストの束（フォルダ／Webサイト）から「概念アトラス」を作るツール**です。
Claude・Codex・Antigravity・ChatGPT などのエージェントは、ユーザーから

- 「このフォルダを概念アトラスにして」
- 「このサイト（URL）をまとめてアトラス化して」

と頼まれたら、以下の手順で進めてください。出力は 1 枚の HTML（3D 概念マップ・一覧・年表・概念索引・全文リーダー）です。

> 実例: `examples/notebook/`（約 440 本の身体・意識・認知の探究記録。概念 82・関係 16・要約 445 件）。
> 迷ったらこの実例の `atlas.toml` と `summaries.tsv` を手本にしてください。

---

## 0. 準備

```bash
pip install -r requirements.txt          # numpy だけ
python -m atlas --help                   # リポジトリのルートで実行
```

Python 3.11 以上（設定ファイル TOML を標準ライブラリで読むため）。

作業用フォルダは `work/<名前>/` に作ってください（`.gitignore` 済み）。

## 1. テキストを集める

| 入力 | やること |
|---|---|
| ローカルのフォルダ | そのまま使う（.md / .txt / .html を読む。サブフォルダが「分類」になる） |
| RSS / Atom / sitemap.xml の URL | `python -m atlas fetch <URL> --out work/<名前>/corpus` |
| 普通の Web ページ | 同上（そのページと同じサイト内のリンク先を 1 階層だけ取得） |
| note.com のクリエイター | `python -m atlas fetch note:<クリエイターID> --out work/<名前>/corpus` |
| URL の一覧 | 1 行 1 URL のテキストを作り `python -m atlas fetch urls.txt --out ...` |

**ネットワークが使えない環境**（サンドボックス）では `fetch` は失敗します。その場合は、エージェント自身のブラウズ機能で本文を取得し、1 記事 1 ファイルの Markdown として保存してください。先頭に次の front matter を付けると日付とリンクが反映されます。

```markdown
---
title: 記事タイトル
date: 2026-10-13
url: https://example.com/post/123
---

# 記事タイトル

本文…
```

## 2. 設定ファイルを作る

```bash
python -m atlas init work/<名前> --title "○○ 概念アトラス"
```

`atlas.toml` の `input` をテキストのフォルダ（例 `"corpus"`）に直します。まずは概念を書かずにビルドして全体を確認します。

```bash
python -m atlas build -c work/<名前>/atlas.toml
```

概念を書かなければ、頻出かつ話題性の高い語を自動で 60 個拾い、共起で 6 領域に分けます。**自動抽出は叩き台です。** 必ず次の手順で手直ししてください。

## 3. 概念辞書を作る（いちばん大事）

1. `python -m atlas suggest -c work/<名前>/atlas.toml` で候補を出す。
2. 代表的な資料を 10〜20 本読み、**その書き手が実際に使っている言葉**で概念を決める。
   - 領域（themes）は 5〜8 個。色は自動で割り当てられる。
   - 概念（concepts）は 40〜90 個。1 つの概念に同義語・表記ゆれ・英語をまとめて `pattern`（正規表現）に書く。
     例: `pattern = "呼吸|breath"`、`pattern = "DMN|デフォルトモード"`
   - 「状態」「問題」「方法」のような一般語は概念にしない。書き手の造語・固有のモデル名は優先して入れる。
3. 概念同士の関係がはっきり書かれている資料（索引・まとめ・理論編など）があれば、`[[relations]]` に書く（任意）。
   `type` は `same`（同じ現象の別の言い方）`dev`（発展・因果）`res`（矛盾と統合）`claim`（中核の主張）`model`（統合モデル）。`nodes` は概念のラベル。
4. 再ビルドし、各概念の資料数（索引タブ）が 0 や全資料になっていないか確認する。

## 4. 要約を書く（任意だが強く推奨）

```bash
python -m atlas digest -c work/<名前>/atlas.toml > work/<名前>/digest.tsv
```

`digest.tsv` は「パス／タイトル／見出し／冒頭」の一覧です。これを読み、`summaries.tsv` に

```
パス<TAB>1〜2 行の要約
```

の形で書きます。要約は中立・説明的に（「〜を整理する」「〜を述べる」「〜という観察」）。評価や感想は入れない。
要約は一覧・詳細・マップのツールチップ・年表に表示され、検索対象にもなります。

## 5. 公開記事の一覧と突き合わせる（任意）

ブログや note の記事一覧（`catalog.tsv`）があると、本文と照合して日付・リンク・添付動画を付けられます。

```
key<TAB>date<TAB>title<TAB>url<TAB>head<TAB>media
n687aa5770266	2026-10-13	記事タイトル	https://note.com/...	本文の書き出し40字	YouTubeID,YouTubeID
```

設定に `[catalog] file = "catalog.tsv"  label = "note"` を書きます。

## 6. ビルドと確認

```bash
python -m atlas build -c work/<名前>/atlas.toml
```

- `dist/index.html` … データと全文を埋め込んだ単体版。ダブルクリックで開ける。
- `dist/pub/` … 公開用の軽量版（`index.html` + `data.json` + `texts/t*.json`）。

確認すること: 資料数、日付が付いた数、概念の偏り、タイトルが変なもの（索引タブの「データの状態」）。

## 7. 届ける

- **Claude（claude.ai / Claude Code で Artifact ツールがある場合）**
  `dist/pub/index.html` をページとして公開し、`files` に `data.json` と `texts/t0.json …` をすべて渡す。
  更新時は同じ URL に公開し直す（公開前にその URL の `data.json` を read で読む）。
  単体の HTML ファイルも欲しい場合は `dist/index.html` を添付する。
- **それ以外（Codex / Antigravity / ChatGPT など）**
  `dist/index.html` を渡す（ブラウザでそのまま開ける）。
  Web に置くなら `dist/pub/` をそのまま静的ホスティング（GitHub Pages など）に置く。

外部から読み込むのは three.js（cdn.jsdelivr.net）と Google Fonts だけです。オフラインでは 3D マップが表示されません（一覧・年表・索引は動く）。

---

## 設定項目の一覧（atlas.toml）

| キー | 意味 | 既定 |
|---|---|---|
| `title` | 画面のタイトル | 概念アトラス |
| `input` / `output` | テキストのフォルダ / 出力先（設定ファイルからの相対パス） | `.` / `dist` |
| `id_pattern` | ファイル名中の資料ID。本文で別の ID に触れると「参照」として線で結ぶ | なし |
| `primary_category` | 主な資料の分類名（年表・一覧の並び順に使う） | 最も多い分類 |
| `[[categories]]` | `prefix`（パスの先頭）→ `label`（分類名）。なければ最上位フォルダ名 | |
| `[ext_categories]` | 直下のファイルの拡張子→分類名 | |
| `html_mode` | `"text"`: .html を本文として読む / `"app"`: 単体アプリとして一覧に載せるだけ | text |
| `strip_chat` | AI との対話ログ冒頭の「了解。以下は…」を表示から除く | true |
| `summaries` | 要約ファイル | summaries.tsv |
| `[catalog]` | 公開記事一覧 `file` / `label` / `url`（`{key}` を含む URL の型） | |
| `[[themes]]` | `id` / `label` / `color`（任意） | 自動 |
| `[[concepts]]` | `label` / `theme` / `pattern` | 自動 |
| `[[relations]]` | `type` / `title` / `desc` / `src` / `nodes` | なし |
| `[title_overrides]` | パスまたは ID → タイトル | |
| `auto_concepts` / `auto_themes` | 自動抽出する概念数・領域数 | 60 / 6 |
