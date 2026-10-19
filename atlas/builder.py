# -*- coding: utf-8 -*-
"""Scan a corpus folder and build the atlas data (docs, concepts, similarity, links)."""
import collections, hashlib, json, math, os, re

import numpy as np

from . import text as T
from .htmltext import html_to_text
from .config import resolve

TOK = re.compile(r'[A-Z][A-Za-z0-9]{1,6}|[ァ-ヴー]{3,}|[一-龥]{2,6}|[a-z]{4,}')
STOP = set('''という ところ こと もの それ これ ため よう 場合 状態 意味 結果 必要 重要 自分 実際 可能 問題 理由 存在 説明 以下 今回 一方 自体 程度 部分 全体 以上
  そして しかし また つまり ただ さらに について による として ある いる する なる できる ない 前提 普通 最初 最後 次回 前回 本来 間違 無理 方向 視点 時間 判断 行為 失敗
  変化 関係 過剰 人間 体験 誤解 行動 違和感 本当 自然 特定 一般 一般的 具体的 基本 基本的 非常 単純 簡単 確認 整理 理解 表現 言葉 位置 段階 対象 内容 方法 結論
  現在 以前 今後 同時 一部 一度 一瞬 一つ 二つ 全部 多く 少し 特別 大事 必要性 可能性 重要性 前者 後者 両者 自身 自体 本稿 本書 今日 明日 ここ そこ どこ
  感じ 感覚的 意識的 実感 印象 指摘 主張 提示 記述 報告 観点 立場 事実 現実的 最終的 結果的 根本的 本質的 部分的 全体的 相対的 絶対的 直接 間接'''.split()) | \
  set('this that with from have will would there their which about into more than been were what when your just also only very such'.split())


# ---------------------------------------------------------------- reading
FRONT = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)

def front_matter(text):
  m = FRONT.match(text)
  if not m:
    return {}, text
  meta = {}
  for ln in m[1].splitlines():
    if ':' in ln:
      k, v = ln.split(':', 1)
      meta[k.strip().lower()] = v.strip().strip('"\'')
  return meta, text[m.end():]


def date_of(name, text, meta):
  for k in ('date', 'published', 'published_at', 'created'):
    if meta.get(k):
      m = re.search(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', meta[k])
      if m: return f'{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}'
  m = re.search(r'(?:^|[_\-\s])(20\d{2}|19\d{2})[-_]?(\d{2})[-_]?(\d{2})(?:[_\-\s.]|$)', name)
  if m and 1 <= int(m[2]) <= 12 and 1 <= int(m[3]) <= 31: return f'{m[1]}-{m[2]}-{m[3]}'
  m = re.search(r'(?:Published At|Date|公開日|投稿日)\**\s*[:：]\s*(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', text[:3000])
  if m: return f'{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}'
  m = re.search(r'(?:Published At|Date)\**\s*:\s*(\w{3}, \d{1,2} \w{3} \d{4}[^\n]*)', text[:3000])
  if m:
    try:
      from email.utils import parsedate_to_datetime
      return parsedate_to_datetime(m[1].strip()).strftime('%Y-%m-%d')
    except Exception:
      pass
  return None


def category_of(cfg, rel):
  for c in cfg['categories']:
    if rel.startswith(c['prefix']): return c['label']
  parts = rel.split('/')
  if len(parts) > 1: return parts[0]
  ext = os.path.splitext(rel)[1].lower()
  return (cfg.get('ext_categories') or {}).get(ext, cfg.get('root_label', '（直下）'))


def scan(cfg, log=print):
  root = cfg['_root']; out_dir = cfg['_out']
  idrx = re.compile(f"({cfg['id_pattern']})") if cfg['id_pattern'] else None
  inc = {e.lower() for e in cfg['include_ext']}; lst = {e.lower() for e in cfg['list_ext']}
  excl = set(cfg['exclude'])
  docs, texts, full, seen = [], [], {}, {}
  overrides = cfg.get('title_overrides', {})
  for dp, dn, fn in os.walk(root):
    dn[:] = sorted(d for d in dn if not d.startswith('.') and d not in excl
                   and os.path.abspath(os.path.join(dp, d)) != out_dir)
    for f in sorted(fn):
      fp = os.path.join(dp, f); rel = os.path.relpath(fp, root).replace('\\', '/')
      ext = os.path.splitext(f)[1].lower()
      if ext not in inc and ext not in lst: continue
      d = {'id': len(docs), 'path': rel, 'name': f, 'ext': ext, 'size': os.path.getsize(fp), 'cat': category_of(cfg, rel)}
      m = idrx.search(f) if idrx else None
      d['src'] = m[1] if m else None
      text = ''
      if ext in inc:
        raw = open(fp, encoding='utf-8', errors='ignore').read()
        h = hashlib.md5(raw.encode()).hexdigest()
        if h in seen and len(raw) > 200:
          docs[seen[h]].setdefault('copies', []).append(rel); continue
        seen[h] = len(docs)
        if ext in ('.html', '.htm'):
          if cfg.get('html_mode', 'text') == 'app':
            t = re.search(r'<title>(.*?)</title>', raw[:6000], re.S)
            d['title'] = (T.clean(t[1]) + ' — ' + f) if t else f
            d['text'] = 'HTML アプリ（単体で動くページ）'; d['heads'] = []
            docs.append(d); texts.append(re.sub(r'<[^>]+>', ' ', raw[:400000])); continue
          ht, raw = html_to_text(raw)
          if ht and not raw.lstrip().startswith('#'): raw = f'# {ht}\n\n' + raw
        meta, body = front_matter(raw)
        text = body
        lines, chat = T.strip_chat(body.splitlines()) if cfg['strip_chat'] else (body.splitlines(), False)
        d['chat'] = chat
        stem = os.path.splitext(f)[0]
        d['title'], d['tsrc'] = (meta['title'], 'heading') if meta.get('title') else T.title_of(lines, stem)
        ov = overrides.get(rel) or (overrides.get(d['src']) if d['src'] else None)
        if ov: d['title'], d['tsrc'] = ov, 'heading'
        d['date'] = date_of(f, body, meta)
        url = meta.get('url') or meta.get('source')
        if not url:
          m = re.search(r'(?:Original URL|URL|Source)\**\s*[:：]\s*\[?(https?://[^\]\s)]+)', body[:3000])
          url = m[1] if m else None
        if url: d['url'] = url
        if meta.get('summary'): d['sum'] = meta['summary']
        d['heads'] = [T.plain(T.inline(x))[:70] for x in re.findall(r'^#{1,3}\s+(.+)$', body, re.M)][:14]
        d['chars'] = len(body)
        d['compiled'] = any(k in f for k in cfg['compiled_markers'])
        d['blocks'] = T.blocks_of(lines, 600 if d['compiled'] else cfg['preview_chars'], d['title'])
        if not d['compiled']:
          full[d['id']] = T.blocks_of(lines, 10 ** 9, d['title']); d['full'] = 1
        if d['tsrc'] != 'heading' and T.ODD_TITLE.match(d['title']):
          alt = next((b[1] for b in d['blocks'][:10] if b[0] == 'h' and 8 <= len(b[1]) <= 70
                      and not re.match(r'^[\d０-９―—─→↓・]', b[1]) and b[1] not in T.GENERIC_H), None)
          d['raw_title'] = d['title']; d['title'] = alt or re.sub(r'^\d+[\.．]\s*', '', d['title'])
        d['cut'] = T.ends_cut(lines)
        d['ytids'] = sorted(set(T.YT_RE.findall(raw)))
        d['yt'] = len(d['ytids'])
      else:
        d['title'] = f; d['text'] = ''; d['heads'] = []
        if ext in ('.py', '.js'):
          d['text'] = T.clean(open(fp, encoding='utf-8', errors='ignore').read(400))
      docs.append(d); texts.append(text)
  log(f'scanned {len(docs)} files under {root}')
  return docs, texts, full


# ---------------------------------------------------------------- concepts
def auto_concepts(cfg, texts, log=print):
  """Pick frequent, discriminative terms and group them into themes by co-occurrence."""
  N = len(texts); K = cfg['auto_concepts']; k_th = cfg['auto_themes']
  df = collections.Counter()
  for t in texts:
    if t: df.update(set(w for w in TOK.findall(t) if w not in STOP))
  lo, hi = max(2, int(N * 0.01)), max(3, int(N * 0.35))
  tf = collections.Counter()
  for t in texts:
    if t: tf.update(w for w in TOK.findall(t) if w in df)
  # frequent enough to connect documents, bursty enough to be a topic (not a function word)
  cand = [(math.log(1 + n) * math.log(N / n) * math.log(1 + tf[w] / n) * (1.15 if len(w) >= 3 else 1.0), w)
          for w, n in df.items() if lo <= n <= hi and len(w) >= 2]
  cand.sort(reverse=True)
  terms = []
  for _, w in cand:
    if any(w in x or x in w for x in terms): continue
    terms.append(w)
    if len(terms) >= K: break
  if not terms:
    return [{'id': 't0', 'label': '全体'}], []
  X = np.array([[1.0 if w in t else 0.0 for t in texts] for w in terms])
  X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
  k_th = max(1, min(k_th, len(terms)))
  # farthest-first init + a few k-means rounds (deterministic)
  cent = [X[0]]
  for _ in range(1, k_th):
    dist = np.min([1 - X @ c for c in cent], axis=0); cent.append(X[int(np.argmax(dist))])
  C = np.array(cent)
  for _ in range(20):
    lab = np.argmax(X @ C.T, axis=1)
    C = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k_th)])
    C /= np.maximum(np.linalg.norm(C, axis=1, keepdims=True), 1e-9)
  themes, concepts = [], []
  for j in range(k_th):
    members = [terms[i] for i in range(len(terms)) if lab[i] == j]
    if not members: continue
    members.sort(key=lambda w: -df[w])
    tid = f't{len(themes)}'
    themes.append({'id': tid, 'label': '・'.join(members[:2])})
    concepts += [{'label': w, 'theme': tid, 'pattern': re.escape(w)} for w in members]
  log(f'auto concepts: {len(concepts)} terms in {len(themes)} themes (edit atlas.toml to refine)')
  return themes, concepts


def analyze(cfg, docs, texts, log=print):
  themes, concepts = cfg['themes'], cfg['concepts']
  if not concepts:
    themes, concepts = auto_concepts(cfg, texts, log)
  elif not themes:
    themes = [{'id': t, 'label': t} for t in dict.fromkeys(c['theme'] for c in concepts)]
  crx = [re.compile(c['pattern'], re.I) for c in concepts]
  N, K = len(docs), len(concepts)
  cnt = np.zeros((N, K))
  for i, t in enumerate(texts):
    if t:
      for k, rx in enumerate(crx): cnt[i, k] = len(rx.findall(t))
  dfc = (cnt > 0).sum(0)
  idf = np.log((N + 1) / (dfc + 1)) + 0.3
  for i, d in enumerate(docs):
    t = texts[i]
    if not t: d['concepts'] = []; continue
    w = np.sqrt(cnt[i] / (max(len(t), 800) / 1000.0)) * idf
    thr = 2 if len(t) > 3000 else 1
    order = [int(k) for k in np.argsort(-w) if cnt[i, k] >= thr]
    d['concepts'] = [[k, round(float(w[k]), 3), int(cnt[i, k])] for k in order[:12]]
  # TF-IDF similarity between documents
  rows = []; dfv = collections.Counter()
  for t in texts:
    c = collections.Counter(TOK.findall(t)) if t else collections.Counter()
    rows.append(c); dfv.update(c.keys())
  keep = sorted(w for w, n in dfv.items() if 2 <= n <= max(2, N * 0.35))
  vk = {w: i for i, w in enumerate(keep)}
  M = np.zeros((N, len(vk)), dtype=np.float32)
  for i, c in enumerate(rows):
    for w, n in c.items():
      j = vk.get(w)
      if j is not None: M[i, j] = (1 + math.log(n)) * math.log(N / dfv[w])
  nrm = np.linalg.norm(M, axis=1, keepdims=True); nrm[nrm == 0] = 1; M /= nrm
  S = M @ M.T; np.fill_diagonal(S, 0)
  thr = cfg['similarity_threshold']
  for i, d in enumerate(docs):
    d['sim'] = []; d['kw'] = []
    if not texts[i] or d.get('text', '').startswith('HTML アプリ'): continue
    top = np.argsort(-M[i])[:10]
    d['kw'] = [keep[j] for j in top if M[i, j] > 0][:8]
    if d.get('compiled'): continue
    d['sim'] = [[int(j), round(float(S[i, j]), 3)] for j in np.argsort(-S[i])[:6]
                if S[i, j] > thr and not docs[j].get('compiled')]
  # cross references by document id ("SRC_012" mentioned in another file)
  byid = collections.defaultdict(list)
  for d in docs:
    if d.get('src'): byid[d['src']].append(d['id'])
  idrx = re.compile(cfg['id_pattern']) if cfg['id_pattern'] else None
  for i, d in enumerate(docs):
    refs = set(idrx.findall(texts[i])) if (idrx and texts[i]) else set()
    refs.discard(d.get('src'))
    d['refs'] = sorted({j for r in refs for j in byid.get(r, []) if j != i})[:40]
  return themes, [{'id': k, 'label': c['label'], 'theme': c['theme'], 'df': int(dfc[k]), 'pattern': c['pattern']} for k, c in enumerate(concepts)]


# ---------------------------------------------------------------- catalog (published articles) & summaries
def load_catalog(cfg):
  cat = cfg.get('catalog') or {}
  p = resolve(cfg, cat.get('file'))
  if not p or not os.path.exists(p): return []
  rows = []
  lines = open(p, encoding='utf-8').read().splitlines()
  head = lines[0].split('\t') if lines else []
  for ln in lines[1:]:
    if not ln.strip(): continue
    r = dict(zip(head, ln.split('\t')))
    if not r.get('url') and cat.get('url'):
      r['url'] = cat['url'].format(**r)
    r['media'] = [x for x in (r.get('media') or '').split(',') if x]
    rows.append(r)
  return rows


def link_catalog(cfg, docs, texts, log=print):
  rows = load_catalog(cfg)
  if not rows: return [], 0
  heads = {i: (T.norm(d['title']), T.norm(texts[i][:6000])) for i, d in enumerate(docs)
           if texts[i] and d['ext'] in ('.md', '.txt', '.markdown', '.html', '.htm') and not d.get('compiled') and d.get('full')}
  def attach(d, r, fuzzy=None):
    rec = {'key': r['key'], 'date': r.get('date', ''), 'title': r.get('title', ''), 'url': r.get('url', '')}
    if fuzzy: rec['fuzzy'] = fuzzy
    if 'note' in d and d['note']['key'] != r['key']:
      d.setdefault('notes_more', []).append(rec); return
    d['note'] = rec
    d['url'] = d.get('url') or rec['url']
    if not d.get('date') and rec['date']: d['date'] = rec['date']; d['date_src'] = 'catalog'
    if d.get('tsrc') != 'heading' or len(T.norm(d['title'])) < 6:
      d['raw_title'] = d['title']; d['title'] = rec['title']
  for r in rows:
    nt = T.norm(r.get('title', '')); nb = T.norm(r.get('head', ''))
    pt = nt[:14]; pb = nb[-16:] if len(nb) >= 22 else ''
    hits = []
    for i, (dt, dx) in heads.items():
      sc = 0
      if pt and (pt in dx[:900] or (len(dt) >= 10 and dt[:14] == pt)): sc += 2
      if pb and pb in dx: sc += 2
      if sc: hits.append((sc, i))
    if hits:
      best = max(h[0] for h in hits)
      for sc, i in hits:
        if sc == best: attach(docs[i], r)
  bigr = lambda s: {s[i:i + 2] for i in range(len(s) - 1)}
  got = {d['note']['key'] for d in docs if 'note' in d}
  cands = []
  for r in rows:
    if r['key'] in got: continue
    nb = bigr(T.norm(r.get('title', '')))
    if len(nb) < 4: continue
    for i, (dt, dx) in heads.items():
      if 'note' in docs[i]: continue
      j = len(nb & (bigr(dt) | bigr(dx[:160]))) / len(nb)
      if j >= 0.6: cands.append((j, r['key'], i))
  cands.sort(reverse=True); un, ud = set(), set()
  byk = {r['key']: r for r in rows}
  for j, k, i in cands:
    if k in un or i in ud: continue
    attach(docs[i], byk[k], round(j, 2)); un.add(k); ud.add(i)
  # media (e.g. YouTube ids) listed in the catalog
  for d in docs:
    own = set(d.pop('ytids', []) or [])
    ks = ([d['note']['key']] if 'note' in d else []) + [m['key'] for m in d.get('notes_more', [])]
    extra = [v for k in ks for v in byk.get(k, {}).get('media', []) if v not in own]
    if extra: d['nyt'] = list(dict.fromkeys(extra)); d['yt'] = len(own) + len(d['nyt'])
  used = {d['note']['key'] for d in docs if 'note' in d} | {m['key'] for d in docs for m in d.get('notes_more', [])}
  unmatched = [{'key': r['key'], 'date': r.get('date', ''), 'title': r.get('title', ''), 'url': r.get('url', ''), 'yt': r['media']}
               for r in rows if r['key'] not in used]
  log(f"catalog: {len(rows)} entries, {len(rows) - len(unmatched)} linked")
  return unmatched, len(rows)


def load_summaries(cfg, docs, log=print):
  p = resolve(cfg, cfg.get('summaries'))
  if not p or not os.path.exists(p): return
  sm = {}
  for ln in open(p, encoding='utf-8'):
    c = ln.rstrip('\n').split('\t', 1)
    if len(c) == 2 and c[1].strip(): sm[c[0].replace('\\', '/')] = c[1].strip()
  for d in docs:
    v = sm.get(d['path'])
    if v: d['sum'] = v
  log(f"summaries: {sum(1 for d in docs if d.get('sum'))} docs")


# ---------------------------------------------------------------- main entry
def build(cfg, log=print):
  docs, texts, full = scan(cfg, log)
  themes, concepts = analyze(cfg, docs, texts, log)
  unmatched, total = link_catalog(cfg, docs, texts, log)
  for d in docs: d.pop('ytids', None)
  load_summaries(cfg, docs, log)
  cats = collections.Counter(d['cat'] for d in docs if d.get('full'))
  primary = cfg['primary_category'] or (cats.most_common(1)[0][0] if cats else '')
  cat_cfg = cfg.get('catalog') or {}
  data = {
    'meta': {'title': cfg['title'], 'subtitle': cfg['subtitle'], 'primary': primary,
             'catalogLabel': cat_cfg.get('label', ''), 'idPattern': cfg['id_pattern'],
             'layoutHint': cfg.get('layout_hint', {}), 'relationTypes': cfg.get('relation_types', {}),
             'rootLabel': cfg.get('root_label', '（直下）')},
    'notes_unmatched': unmatched, 'notes_total': total,
    'themes': themes, 'concepts': concepts, 'relations': cfg.get('relations', []), 'docs': docs,
  }
  log(f"docs {len(docs)}, with text {sum(1 for d in docs if d.get('full'))}, concepts {len(concepts)}, themes {len(themes)}")
  return data, full
