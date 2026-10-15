# -*- coding: utf-8 -*-
"""concept-atlas command line.

  python -m atlas init   [folder]            create atlas.toml next to the corpus
  python -m atlas fetch  <url|note:id|urls.txt> --out corpus/
  python -m atlas build  [-c atlas.toml]     build dist/index.html and dist/pub/
  python -m atlas suggest [-c atlas.toml]    print concept candidates as TOML (paste into atlas.toml)
  python -m atlas digest  [-c atlas.toml]    list documents without a summary (for writing summaries.tsv)
"""
import argparse, json, os, re, sys

from . import builder, config, render

INIT = '''# 概念アトラスの設定。すべて省略可能です。
title = "{title}"
subtitle = ""
input = "{input}"          # テキストが入っているフォルダ（この設定ファイルからの相対パス）
output = "dist"            # 出力先
# id_pattern = "SRC_\\\\d{{3}}"   # ファイル名に含まれる資料ID（本文中の相互参照を線で結ぶ）
# html_mode = "text"       # .html を本文として読む（"app" なら単体アプリとして一覧に載せるだけ）
summaries = "summaries.tsv"  # パス<TAB>1〜2行の要約（なくても可）

# 概念を書かなければ、本文から自動で抽出します（python -m atlas suggest で候補を表示）。
# [[themes]]
# id = "body"
# label = "身体・生理"
#
# [[concepts]]
# label = "呼吸"
# theme = "body"
# pattern = "呼吸|breath"     # 正規表現
#
# [catalog]                 # 公開記事の一覧（note・ブログなど）と本文を突き合わせて日付とリンクを付ける
# file = "catalog.tsv"      # 1行目: key<TAB>date<TAB>title<TAB>url<TAB>head<TAB>media
# label = "note"
'''


def main(argv=None):
  ap = argparse.ArgumentParser(prog='python -m atlas', description='テキストの束から概念アトラス（3Dマップ・一覧・年表・索引）を作る')
  sub = ap.add_subparsers(dest='cmd', required=True)
  p = sub.add_parser('init'); p.add_argument('folder', nargs='?', default='.'); p.add_argument('--title', default='概念アトラス')
  p = sub.add_parser('fetch'); p.add_argument('source'); p.add_argument('--out', default='corpus'); p.add_argument('--limit', type=int, default=300)
  for name in ('build', 'suggest', 'digest'):
    p = sub.add_parser(name); p.add_argument('-c', '--config', default=None)
    p.add_argument('--input', default=None, help='設定ファイルなしでフォルダを直接指定')
    p.add_argument('--out', default=None)
  a = ap.parse_args(argv)

  if a.cmd == 'init':
    os.makedirs(a.folder, exist_ok=True)
    path = os.path.join(a.folder, 'atlas.toml')
    if os.path.exists(path): sys.exit(f'{path} は既にあります')
    inp = 'corpus' if os.path.isdir(os.path.join(a.folder, 'corpus')) else '.'
    open(path, 'w', encoding='utf-8').write(INIT.format(title=a.title, input=inp))
    print('created', path); return
  if a.cmd == 'fetch':
    from .fetch import fetch
    fetch(a.source, a.out, a.limit); return

  cfg_path = a.config or (os.path.exists('atlas.toml') and 'atlas.toml') or None
  cfg = config.load(cfg_path)
  if a.input:
    cfg['_root'] = os.path.abspath(a.input)
  if a.out:
    cfg['_out'] = os.path.abspath(a.out)
  log = lambda *x: print(*x, file=sys.stderr)

  if a.cmd == 'build':
    data, full = builder.build(cfg, log)
    html, pub = render.write(cfg, data, full, log)
    print(html)
  elif a.cmd == 'suggest':
    docs, texts, _ = builder.scan(cfg, log)
    c2 = dict(cfg); c2['auto_concepts'] = max(cfg['auto_concepts'], 80)
    themes, concepts = builder.auto_concepts(c2, texts, log)
    print('# 自動抽出した概念の候補。ラベル・領域・パターンを手直しして atlas.toml に貼ってください。')
    for t in themes:
      print(f'\n[[themes]]\nid = "{t["id"]}"\nlabel = "{t["label"]}"')
    for c in concepts:
      print(f'\n[[concepts]]\nlabel = "{c["label"]}"\ntheme = "{c["theme"]}"\npattern = {json.dumps(c["pattern"], ensure_ascii=False)}')
  elif a.cmd == 'digest':
    docs, texts, full = builder.scan(cfg, log)
    builder.load_summaries(cfg, docs, log)
    for d, t in zip(docs, texts):
      if not d.get('full') or d.get('sum'): continue
      heads = ' / '.join(h[:30] for h in d.get('heads', [])[:6])
      body = re.sub(r'\s+', ' ', re.sub(r'^#.*$|\*\*|^[>*-] ', '', t, flags=re.M)).strip()[:200]
      print(f"{d['path']}\t{d['title']}\t{heads}\t{body}")


if __name__ == '__main__':
  main()
