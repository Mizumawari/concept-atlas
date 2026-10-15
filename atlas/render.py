# -*- coding: utf-8 -*-
"""Write the atlas pages.

dist/index.html        single file: data and full text inlined (open it directly, e.g. file://)
dist/pub/index.html    light page that loads pub/data.json and pub/texts/t*.json (for hosting / Claude artifacts)
"""
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = 40


def write(cfg, data, full, log=print):
  out = cfg['_out']; pub = os.path.join(out, 'pub'); tx = os.path.join(pub, 'texts')
  os.makedirs(tx, exist_ok=True)
  for f in os.listdir(tx):
    if f.startswith('t') and f.endswith('.json'): os.remove(os.path.join(tx, f))
  tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
  tpl = tpl.replace('<title>概念アトラス</title>', f"<title>{_esc(data['meta']['title'])}</title>")
  dj = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
  tj = json.dumps({str(k): v for k, v in full.items()}, ensure_ascii=False, separators=(',', ':'))
  single = tpl.replace('/*__DATA__*/', dj.replace('</', '<\\/')).replace('/*__TEXTS__*/', tj.replace('</', '<\\/'))
  open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(single)
  open(os.path.join(pub, 'index.html'), 'w', encoding='utf-8').write(tpl.replace('/*__DATA__*/', '').replace('/*__TEXTS__*/', ''))
  open(os.path.join(pub, 'data.json'), 'w', encoding='utf-8').write(dj)
  groups = collections.defaultdict(dict)
  for k, v in full.items(): groups[k // BUNDLE][str(k)] = v
  for g, m in groups.items():
    open(os.path.join(tx, f't{g}.json'), 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, separators=(',', ':')))
  log(f"wrote {os.path.join(out, 'index.html')} ({os.path.getsize(os.path.join(out, 'index.html')) // 1024} KB)")
  log(f"wrote {pub}/ (index.html + data.json + {len(groups)} text bundles)")
  return os.path.join(out, 'index.html'), pub


def _esc(s):
  return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
