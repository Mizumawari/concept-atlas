# -*- coding: utf-8 -*-
"""Load atlas.toml (or atlas.json).

Every key is optional. A config with no [[concepts]] makes the builder derive
concepts automatically from the corpus (see analyze.auto_concepts).
"""
import json, os

try:
  import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
  tomllib = None

DEFAULTS = {
  'title': '概念アトラス',
  'subtitle': '',
  'lang': 'ja',
  'input': '.',                       # corpus root, relative to the config file
  'output': 'dist',                   # output folder, relative to the config file
  'include_ext': ['.md', '.txt', '.markdown', '.html', '.htm'],
  'list_ext': ['.py', '.js', '.json', '.zip', '.pdf', '.png', '.jpg'],   # listed as files without text
  'exclude': ['.git', 'node_modules', '__pycache__', 'dist', '.atlas'],
  'id_pattern': '',                   # regex for document ids found in file names, e.g. "SRC_\\d{3}"
  'primary_category': '',             # the category that holds the main documents (default: largest)
  'strip_chat': True,                 # drop "了解。以下は…まとめた" style AI-chat preambles
  'compiled_markers': ['compiled', 'master', 'MASTER_INDEX'],   # file-name parts of compilations
  'summaries': 'summaries.tsv',       # path<TAB>1-2 line summary
  'preview_chars': 1800,
  'similarity_threshold': 0.12,
  'auto_concepts': 60,                # how many concepts to derive when [[concepts]] is empty
  'auto_themes': 6,
  'categories': [],                   # [{prefix, label}]
  'themes': [],                       # [{id, label, color?}]
  'concepts': [],                     # [{label, theme, pattern}]
  'relations': [],                    # [{type, title, desc, src, nodes:[concept labels]}]
  'relation_types': {},               # {type: {label, color}}
  'catalog': {},                      # {file, label, url} published-article list, see catalog.py
  'title_overrides': {},              # {path or id: title}
  'layout_hint': {},                  # {net, spiral, cat}: text under the layout buttons
}


def load(path=None):
  cfg = json.loads(json.dumps(DEFAULTS))
  base = os.getcwd()
  if path:
    path = os.path.abspath(path)
    base = os.path.dirname(path)
    if path.endswith('.json'):
      user = json.load(open(path, encoding='utf-8'))
    else:
      if tomllib is None:
        raise SystemExit('TOML の読み込みには Python 3.11 以上が必要です（atlas.json も使えます）')
      user = tomllib.load(open(path, 'rb'))
    cfg.update(user)
  cfg['_base'] = base
  cfg['_root'] = os.path.abspath(os.path.join(base, cfg['input']))
  cfg['_out'] = os.path.abspath(os.path.join(base, cfg['output']))
  return cfg


def resolve(cfg, rel):
  """Path given in the config, relative to the config file."""
  if not rel:
    return None
  return rel if os.path.isabs(rel) else os.path.join(cfg['_base'], rel)
