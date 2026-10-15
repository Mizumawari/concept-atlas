# -*- coding: utf-8 -*-
"""Text shaping: title detection, readable blocks, AI-chat preamble removal.

Tuned on Japanese prose (works for English too). Functions take a list of lines.
"""
import re

SKIP_LINE = re.compile(r'^[\s⸻—\-=\*_#>|`]*$')
META_LINE = re.compile(r'\s*\*\s*\*\*(Source ID|Author|Published At|Original URL|Note Key|Title|Date|Original Medium URL|Categories|Hashtags|URL|Tags)\*\*')

def clean(s):
  s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
  s = re.sub(r'[#*`>_]+', ' ', s)
  return re.sub(r'\s+', ' ', s).strip()

def norm(s):
  s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
  return re.sub(r'[\s#*`>_|⸻—―─\-－・「」『』（）()【】\[\]〈〉《》“”"\'、。，．,.:：！？!?…~〜]+', '', s)

# ---- text shaping -------------------------------------------------------
ODD_TITLE = re.compile(r'^(\d+[\.．]|了解|以下|今|これ|ここ|■|はい|本テキスト|本稿|しかし|それでは)')
GENERIC_H = {'全体まとめ', 'まとめ', '結論', '概要', 'はじめに', '前提'}
# Lines an AI chat leaves at the top/bottom of a pasted answer ("了解。以下は…NotebookLM用にまとめた" etc.)
PRE_HEAD = re.compile(r'^(了解|はい[、。]|承知|OK[、。]|以下は|以下に|以下、|以下の|今までの|これまでの|ここまで|今回の|では、|それでは|ご指摘|なるほど)')
PRE_KW = re.compile(r'(まとめ|整理|統合|投入|NotebookLM|構造化|テキスト|版|書き直|再構成|形にし|形で)')
TERM = re.compile(r'[。！？!?」』）\)…》】〉＞>]$')
HEAD_NUM = re.compile(r'^(\d{1,2}(?:[\-\.．]\d{1,2})*[\.．、）\)]?|第[0-9０-９一二三四五六七八九十]+[章節話回部]|[①-⑳]|[IVX]+\.)\s*\S')
LIST_RE = re.compile(r'^([\-\*・•●◦▪]|\d{1,2}[\)）])\s*')

def plain(s): return s.replace('**', '')
def inline(s):
  s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
  s = s.replace('__', '').replace('`', '')
  if s.count('**') % 2: s = s.replace('**', '')
  s = re.sub(r'^\s*>+\s*', '', s)
  return re.sub(r'\s+', ' ', s).strip()

def is_preamble(s):
  if s in ('了解。', '了解', 'はい。', '承知しました。', 'OK。'): return True
  if len(s) <= 160 and PRE_HEAD.match(s) and PRE_KW.search(s): return True
  if len(s) <= 120 and s[:1] in '（(' and PRE_KW.search(s): return True
  if len(s) <= 120 and re.search(r'(NotebookLM|ノートブックLM).{0,30}(投入|用|向け)', s) and not s.startswith('#'): return True
  return False

STRONG = re.compile(r'(了解|承知|以下は|以下に|以下、|NotebookLM|ノートブックLM|投入|対話内容|これまでの議論|ここまで積み上げ|ここまで全部|テキストです|今回の追加内容|作成しました|読み込ませ)')
ANYMARK = re.compile(r'(了解|承知|以下は|以下に|以下、|NotebookLM|投入|対話内容|束ねる|一つの線|評価も結論も|再構成した|作成しました|読み込ませ|読み込む|コピー|これまでの議論|ここまで積み上げ|テキストです|重視しています|構造にしています|完全版を|統合して、|整理してある|整理しています|まとめ(た|る|ました|ています|たもの)|今回の追加内容|断定を避けつつ|装飾は最小限)')
PAREN_TAG = re.compile(r'[（(][^）)]{0,40}(NotebookLM|統合テキスト|完全版)[^）)]{0,30}[）)]')
def strip_chat(lines):
  """Drop AI-chat preamble at the top and the "※このテキストは…" footer at the bottom."""
  out = list(lines); removed = False
  idx = [i for i, ln in enumerate(out) if ln.strip() and not SKIP_LINE.match(ln) and not META_LINE.match(ln)][:8]
  if any(STRONG.search(out[i]) and len(out[i].strip()) <= 160 for i in idx):
    mark = {}
    for i in idx:
      st = out[i].strip()
      # "…NotebookLMに読み込ませやすい形式でまとめる。不安・緊張と胸郭の閉鎖──…" : keep what follows the preamble
      if STRONG.search(st) and '。' in st[:-1]:
        head, tail = st[:st.rfind('。') + 1], st[st.rfind('。') + 1:].strip()
        if STRONG.search(head) and len(tail) >= 8 and not ANYMARK.search(tail):
          out[i] = tail; removed = True; continue
      core = PAREN_TAG.sub('', st).strip()
      if core != st and len(core) >= 8 and not ANYMARK.search(core):
        out[i] = core; continue            # a title carrying a "(NotebookLM用)" tag: keep the title
      mark[i] = len(st) <= 160 and bool(ANYMARK.search(st) or is_preamble(st) or PAREN_TAG.fullmatch(st))
    # sentence continuations around marked lines ("…を、" + "…まとめた。")
    for _ in range(2):
      for n, i in enumerate(idx):
        if mark.get(i): continue
        st = out[i].strip()
        nxt = idx[n + 1] if n + 1 < len(idx) else None
        prv = idx[n - 1] if n > 0 else None
        if nxt is not None and mark.get(nxt) and re.search(r'[、，,]$', st): mark[i] = True
        if prv is not None and mark.get(prv) and not TERM.search(out[prv].strip()) and not re.search(r'[）)]$', out[prv].strip()) and len(st) <= 80: mark[i] = True
    for i, m in mark.items():
      if m: out[i] = ''; removed = True
  for i in idx[:3]:
    if out[i].strip() and is_preamble(out[i].strip()): out[i] = ''; removed = True
  # footer
  for i in range(len(out) - 1, max(-1, len(out) - 25), -1):
    st = out[i].strip()
    if st.startswith('※') and re.search(r'(NotebookLM|このテキスト|本テキスト|構造化)', st):
      for j in range(i, len(out)): out[j] = ''
      removed = True; break
  return out, removed

def meaningful(lines):
  for ln in lines:
    st = ln.strip()
    if not st or SKIP_LINE.match(ln) or META_LINE.match(ln): continue
    if st.startswith(('[YouTube', 'http', ':::')): continue
    yield st

GEN_HEAD = {'はじめに', '序文', '概要', 'まとめ', '全体まとめ', '結論', '前提', '目次'}
def title_of(lines, fallback):
  ls = list(meaningful(lines))
  # a plain first line that precedes the first heading is the title ("【考察記録】…" then "## はじめに")
  if ls and not ls[0].startswith('#') and any(x.startswith('#') for x in ls[:12]):
    t0 = inline(ls[0]); fh = next(x for x in ls[:12] if x.startswith('#'))
    if 8 <= len(t0) <= 90 and not t0.endswith('。') and inline(fh.lstrip('#')) in GEN_HEAD | {'1. はじめに', '0. はじめに'}:
      return fix_title(t0, ls, ls[0]), 'heading'
  for st in ls[:60]:
    if st.startswith('#'):
      t = inline(st.lstrip('#'))
      if len(t) >= 3 and t not in ('無題', 'タイトル'): return fix_title(t, ls, st), 'heading'
  for k, st in enumerate(ls[:40]):
    t = inline(st)
    if len(t) >= 6:
      return fix_title(t, ls, st), 'body'
  return fallback, 'file'

def fix_title(t, ls, st):
  t = re.sub(r'^(【考察記録】|【考察】|全体まとめ\s*[｜|:：]\s*|まとめ\s*[｜|:：]\s*)', '', t).strip()
  t = t.replace('**', '')
  t = re.sub(r'[（(][^）)]{0,40}(NotebookLM|統合テキスト|用)[^）)]{0,20}[）)]', '', t).strip()
  # attach a continuation line ("…による" + "…プロセス") or a dash subtitle
  try:
    nxt = ls[ls.index(st) + 1]
    if re.search(r'(による|における|についての|をめぐる|から見た|として|[のにでとをはがへ])$', t) and len(nxt) <= 40 and not HEAD_NUM.match(nxt):
      t = t + inline(nxt.lstrip('#').strip())
      nxt = ls[ls.index(st) + 2]
    if nxt[:1] in '―—─〜~-' and len(nxt) < 60 and len(t) < 50: t = t + ' ' + inline(nxt)
  except (ValueError, IndexError): pass
  if len(t) > 80:
    cut = t.find('。')
    t = (t[:cut + 1] if 0 < cut < 80 else t[:78] + '…')
  return t

YT_RE = re.compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/|live/))([A-Za-z0-9_-]{11})')
SOFT_HEAD_BAD = re.compile(r'([、，,：:]|[はがをにでとのやもりてしけど]|による|における|として)$')
def blocks_of(lines, limit=1800, title=''):
  """Rebuild readable blocks: headings, paragraphs (lines joined until a sentence ends), list items."""
  blocks = []; cur = None; total = 0; pend = False; nt = norm(title); early = 0
  for raw in lines:
    st0 = raw.strip()
    if st0 and not SKIP_LINE.match(raw) and early < 3:
      early += 1
      if nt and len(norm(st0)) >= 4 and norm(st0) in nt: continue
    st = raw.strip()
    if not st or SKIP_LINE.match(raw):
      cur = None; continue
    ym = YT_RE.search(st)
    if ym and (st.startswith(('[YouTube', 'http', '<')) or len(st) < 120):
      if not blocks or blocks[-1] != ['yt', ym[1]]: blocks.append(['yt', ym[1]])
      cur = None; continue
    if META_LINE.match(raw) or st.startswith(('[YouTube', 'http', ':::')): continue
    if st.startswith('|') and st.count('|') >= 2:
      cells = [inline(c) for c in st.strip('|').split('|')]
      if all(re.fullmatch(r':?-{2,}:?', c.strip()) or not c.strip() for c in cells): continue
      blocks.append(['tr', cells]); total += sum(len(c) for c in cells); cur = None; pend = False
      if total > limit: break
      continue
    if re.match(r'^(→|↓|⇒|⇩|↑|=>|->|[│├└┌┐┘┤┬┴┼])', st):
      txt = inline(st)
      blocks.append(['flow', txt]); total += len(txt); cur = None; pend = False
      if total > limit: break
      continue
    m = re.match(r'^#{1,6}\s*(.+)', st)
    soft = (not m and not LIST_RE.match(st) and len(st) <= 32 and '。' not in st and not TERM.search(st) and not SOFT_HEAD_BAD.search(st)
            and not re.search(r'[→↓⇒]', st) and not (re.match(r'[ぁ-ゖ]', st) and not re.match(r'(なぜ|どう|なに|いま|これから)', st)) and (cur is None or TERM.search(blocks[cur][1])))
    if m or soft or (HEAD_NUM.match(st) and len(st) <= 46 and not re.search(r'[。、，]$', st) and not LIST_RE.match(st)):
      txt = inline(m[1] if m else st)
      txt = plain(txt)
      if txt and len(txt) > 64:          # heading glued to its body text: show as a paragraph
        blocks.append(['p', txt]); total += len(txt); cur = None; pend = False
      elif txt:
        blocks.append(['h', txt]); total += len(txt); cur = None; pend = False
      else:
        cur = None; pend = False
    elif LIST_RE.match(st):
      txt = inline(LIST_RE.sub('', st, count=1))
      if not txt: pend = True; continue
      blocks.append(['li', txt]); total += len(txt); cur = None; pend = False
    else:
      txt = inline(st)
      if not txt: continue
      if pend: blocks.append(['li', txt]); pend = False; cur = None
      elif cur is not None and not TERM.search(blocks[cur][1]) and not blocks[cur][1].endswith(('：', ':')):
        blocks[cur][1] += txt
      else:
        blocks.append(['p', txt]); cur = len(blocks) - 1
      total += len(txt)
    if total > limit: break
  # trim the overflow at a sentence end
  over = total - limit
  if over > 0 and blocks and isinstance(blocks[-1][1], str):
    b = blocks[-1]; keep = max(0, len(b[1]) - over)
    cut = b[1].rfind('。', 0, keep)
    b[1] = b[1][:cut + 1] if cut > 20 else b[1][:keep] + '…'
    blocks.append(['more', ''])
  elif over > 0:
    blocks.append(['more', ''])
  while blocks and blocks[-1][0] == 'h': blocks.pop()
  if len(blocks) >= 2 and blocks[-1][0] == 'more' and blocks[-2][0] == 'h': blocks.pop(-2)
  return blocks

def ends_cut(lines):
  """True when the last meaningful line stops mid-sentence (e.g. ends with 、 or a particle)."""
  ls = [st for st in meaningful(lines) if not re.fullmatch(r'\*\*\[.*\]\*\*', st)]
  if not ls: return False
  last = re.sub(r'[:：]{2,}$', '', inline(ls[-1])).strip()
  if LIST_RE.match(ls[-1]) or ls[-1].startswith(('#', '|')): return False
  if TERM.search(last): return False
  return bool(re.search(r'[、，,：:（(「『]$', last) or re.search(r'[はがをにでとのへやもりてし]$', last) and len(last) > 4)

