# -*- coding: utf-8 -*-
"""Notebook フォルダを走査して概念マップ用の data.json を生成する。
使い方: Notebook/_concept_map で  python3 build_data.py
"""
import os, re, json, hashlib, collections, math
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')

THEMES = [
  ('body', '身体・生理'), ('sleep', '睡眠・覚醒'), ('cog', '認知・脳・予測'),
  ('con', '意識・自己感覚'), ('psy', '心理・感情'), ('life', '社会・人生・思想'),
  ('prac', '実践・方法'), ('music', '音楽・創作'),
]
CONCEPTS = [
 ('身体感覚','body', r'身体感覚|体感|内受容|interocept'),
 ('緊張・力み','body', r'緊張|力み|張力|tension'),
 ('脱力・緩める','body', r'脱力|リラックス|緩め|緩む|緩み|relax'),
 ('呼吸','body', r'呼吸|breath'),
 ('横隔膜','body', r'横隔膜|diaphragm'),
 ('姿勢・重心','body', r'姿勢|重心|posture'),
 ('腹部・腹圧','body', r'腹圧|腹部|丹田|下腹|abdom'),
 ('体幹','body', r'体幹|torso|胴体'),
 ('深層筋・筋膜','body', r'深層筋|筋膜|fascia|deep muscle'),
 ('骨盤・胸郭','body', r'骨盤|胸郭|pelvi'),
 ('前面／後面モデル','body', r'前面|後面|背面'),
 ('循環・血流','body', r'循環|血流|毛細血管|capillar|circulat'),
 ('スポンジ・拍動モデル','body', r'スポンジ|拍動|sponge|pulse'),
 ('心拍','body', r'心拍|heart rate'),
 ('自律神経','body', r'自律神経|交感神経|副交感|迷走神経|autonomic|vagal'),
 ('収束と拡散','body', r'収束|拡散|converg|diffus'),
 ('寒冷・サウナ','body', r'寒冷|冷水|サウナ|ヴィム|ホフ|cold exposure|sauna'),
 ('周天・内部の熱','body', r'周天|内部の熱'),
 ('CSF（脳脊髄液）','body', r'CSF|脳脊髄液'),
 ('虚圧・充実感','body', r'虚圧|充実感'),
 ('鳩尾・会陰','body', r'鳩尾|みぞおち|会陰'),
 ('頸椎・脊柱','body', r'頚椎|頸椎|脊柱|背骨|胸椎'),
 ('代謝・血糖・食事','body', r'血糖|代謝|1日1食|一日一食|カロリー|LDL|断食|空腹'),
 ('覚醒','sleep', r'覚醒|arousal|wakeful'),
 ('睡眠・短眠','sleep', r'睡眠|短眠|ショートスリープ|short sleep|sleep'),
 ('断眠','sleep', r'断眠|徹夜'),
 ('眠気・睡眠圧','sleep', r'眠気|睡眠圧|sleep pressure'),
 ('あくび','sleep', r'あくび|欠伸|yawn'),
 ('カフェイン・アデノシン','sleep', r'カフェイン|アデノシン|caffeine|adenosine|コーヒー'),
 ('疲労・回復','sleep', r'疲労|回復力|身体回復|疲れ|fatigue|recovery'),
 ('血と神','sleep', r'血と神|血・神|血／神|blood (?:&|and) spirit'),
 ('DMN','cog', r'DMN|デフォルトモード'),
 ('RAS','cog', r'RAS|網様体'),
 ('サリエンス (SN)','cog', r'サリエンス|salience|\bSN\b'),
 ('予測・予測誤差','cog', r'予測誤差|予測|predict'),
 ('反芻・自己参照ループ','cog', r'反芻|自己参照|再帰|ループ|rumina'),
 ('ノイズ','cog', r'ノイズ|noise'),
 ('ゲイン','cog', r'ゲイン|\bgain'),
 ('注意・集中','cog', r'注意資源|注意の|集中力|集中状態|\battention'),
 ('神経可塑性','cog', r'可塑性|plasticity'),
 ('ADHD・薬理','cog', r'ADHD|治療薬|コンサータ|ストラテラ|メチルフェニデート'),
 ('ドーパミン','cog', r'ドーパミン|dopamin'),
 ('脳キャンセル','cog', r'脳キャンセル'),
 ('物語化・意味づけ','cog', r'物語化|意味づけ|意味付け|物語'),
 ('PNSE','con', r'PNSE|持続的非象徴'),
 ('俺フィルター','con', r'俺フィルター'),
 ('自己物語・自己感','con', r'自己物語|自己感|自我|self-narrat|sense of self'),
 ('悟り・覚者','con', r'悟り|覚者|独覚|無為|解脱|涅槃|enlighten'),
 ('瞑想・マインドフルネス','con', r'瞑想|マインドフルネス|坐禅|座禅|meditat|mindful'),
 ('静寂・基底状態','con', r'静寂|基底|常態|凪|baseline'),
 ('フロー・没入','con', r'フロー|没入|flow state|immers'),
 ('明晰・クリア','con', r'明晰|クリアさ|クリアな|clarity'),
 ('修行・阿闍梨','con', r'阿闍梨|修行|作務|行者'),
 ('現実感・リアリティ','con', r'現実感|リアリティ|実在|as real'),
 ('何もしない','con', r'何もしない'),
 ('観察・観照','con', r'観照|観察'),
 ('常駐と即応','con', r'常駐|即応|イベント駆動'),
 ('所有感・主体感','con', r'所有感|主体感|やっている感|自分がやっている'),
 ('不安','psy', r'不安|anxiety'),
 ('感情・情動','psy', r'感情|情動|emotion'),
 ('欲求・快不快','psy', r'欲求|快不快|快楽|快感|不快|desire|pleasure'),
 ('ストレス','psy', r'ストレス|stress'),
 ('苦の構造','psy', r'苦が|苦は|苦を|苦の構造|苦の成立|成立しにくい配置|苦しみ|苦しさ'),
 ('解離・離人感','psy', r'解離|離人'),
 ('他者・社会性','life', r'他者|社会性|対人|社会生活|\bsocial'),
 ('倫理','life', r'倫理|ethic'),
 ('AI','life', r'\bAI\b|ＡＩ|LLM|NotebookLM'),
 ('価値・非対称性','life', r'価値の非対称|非対称|価値観|価値判断|\bvalue'),
 ('人生の運用','life', r'人生の運用|人生|生き方|\blife\b'),
 ('真理・哲学','life', r'真理|永井均|哲学|清水俊史|\btruth|philosoph'),
 ('仏教・東洋思想','life', r'仏教|仏陀|ブッダ|論語|道教|禅|Buddh'),
 ('現れ・枠組み','life', r'立ち現れ|現れ方|枠組み|framework|appearance'),
 ('中央と辺境','life', r'中央と辺境|辺境'),
 ('行動開始・着手','prac', r'行動開始|着手|初動|行動の立ち上が|始動|initiat'),
 ('訓練・トレーニング','prac', r'訓練|トレーニング|練習|筋トレ|training|practice'),
 ('継続・初期投資','prac', r'継続|習慣|初期投資|habit'),
 ('身体操作','prac', r'身体操作|身体の操作|身体を操作|ゼロ誤差|微調整'),
 ('書籍・出版','prac', r'書籍|出版|原稿|manuscript|chapter'),
 ('音楽・音響','music', r'音楽|音響|楽曲|ビート|BPM|music|acoustic'),
 ('Suno・プロンプト','music', r'Suno|SUNO|プロンプト|prompt'),
 ('Neural Mantra','music', r'Neural Mantra|ニューラル|マントラ|mantra'),
 ('リズム・身体同期','music', r'リズム|同期|rhythm|synchron'),
]
CRX = [re.compile(rx, re.I) for _, _, rx in CONCEPTS]

def cat_of(rel):
  p = rel
  m = [
   ('research_corpus/00_indexes/', '索引'), ('research_corpus/01_original_sources/', '一次資料'),
   ('research_corpus/02_metadata/', 'メタデータ'), ('research_corpus/03_synthesis/', '統合モデル'),
   ('research_corpus/04_experiments/', '監査・実験'), ('research_corpus/05_book_project/', '書籍プロジェクト'),
   ('research_corpus/06_book_manuscript/', '書籍原稿'), ('research_corpus/07_english_medium_articles/', '英語記事 (Medium)'),
   ('research_corpus/08_note_articles/', 'note記事'), ('research_corpus/09_recent_note_corpus/', 'note記事'),
   ('research_corpus/10_note_backfill/', 'note記事'),
  ]
  for pre, c in m:
    if p.startswith(pre): return c
  if p.startswith('research_corpus/'):
    return '一次資料' if re.search(r'/SRC_\d', p) else 'コーパス基盤'
  ext = os.path.splitext(p)[1].lower()
  if 'neural_mantra' in p or 'suno' in p or 'kizu' in p: return '音楽アプリ・Suno'
  return {'.py': '解析スクリプト', '.js': '解析スクリプト', '.json': '解析データ', '.txt': '解析データ',
          '.md': '解析データ', '.zip': 'アーカイブ', '.jpg': '画像', '.png': '画像'}.get(ext, 'その他')

SKIP_LINE = re.compile(r'^[\s⸻—\-=\*_#>|`]*$')
META_LINE = re.compile(r'\s*\*\s*\*\*(Source ID|Author|Published At|Original URL|Note Key|Title|Date|Original Medium URL|Categories)\*\*')

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

TITLE_OVERRIDES = {
  'SRC_150': '夢の記憶は「夢見モード」でないと思い出せないのか（対話）',
}
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

def date_of(name, text):
  m = re.search(r'_(20\d{2})(\d{2})(\d{2})_', name)
  if m: return f'{m[1]}-{m[2]}-{m[3]}'
  m = re.search(r'Published At\*\*:\s*(\d{4}-\d{2}-\d{2})', text)
  if m: return m[1]
  return None

TOK = re.compile(r'[A-Z]{2,6}|[ァ-ヴー]{3,}|[一-龥]{2,6}|[a-z]{4,}')

orig = {}
sm = os.path.join(ROOT, 'research_corpus/02_metadata/source_metadata.md')
if os.path.exists(sm):
  for ln in open(sm, encoding='utf-8', errors='ignore'):
    c = [x.strip() for x in ln.split('|')]
    if len(c) > 4 and c[1].startswith('SRC_'): orig[c[1]] = c[2]

eng = {}
ei = os.path.join(ROOT, 'research_corpus/07_english_medium_articles/INDEX.md')
MON = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
if os.path.exists(ei):
  cur = None
  for ln in open(ei, encoding='utf-8', errors='ignore'):
    m = re.match(r'### \[([^\]]+)\]', ln)
    if m: cur = m[1]; eng[cur] = {}; continue
    if not cur: continue
    m = re.search(r'\*\*Title\*\*:\s*(.*)', ln)
    if m: eng[cur]['title'] = m[1].strip()
    m = re.search(r'\*\*Date\*\*:\s*\w+, (\d+) (\w+) (\d{4})', ln)
    if m: eng[cur]['date'] = f'{m[3]}-{MON[m[2]]:02d}-{int(m[1]):02d}'
    m = re.search(r'Original Medium URL\*\*:\s*\[(https[^\]]+)\]', ln)
    if m: eng[cur]['url'] = m[1].split('?')[0]

docs = []; seen = {}; texts = []; FULL = {}
for dp, dn, fn in os.walk(ROOT):
  dn[:] = sorted(d for d in dn if not d.startswith(('.', '_concept_map')))
  for f in sorted(fn):
    full = os.path.join(dp, f); rel = os.path.relpath(full, ROOT).replace('\\', '/')
    ext = os.path.splitext(f)[1].lower()
    if f.endswith('.bak_before_rewrite') or '.bak_' in f: ext = '.bak'
    size = os.path.getsize(full)
    d = {'id': len(docs), 'path': rel, 'name': f, 'ext': ext, 'size': size, 'cat': cat_of(rel)}
    text = ''
    if ext in ('.md', '.txt'):
      text = open(full, encoding='utf-8', errors='ignore').read()
      h = hashlib.md5(text.encode()).hexdigest()
      if h in seen and len(text) > 200:
        docs[seen[h]].setdefault('copies', []).append(rel); continue
      seen[h] = len(docs)
    stem = os.path.splitext(f)[0]
    m = re.match(r'(SRC_\d{3})', f); d['src'] = m[1] if m else None
    if d['src'] and d['src'] in orig and not re.search(r'_20\d{6}_', f): d['orig'] = orig[d['src']]
    if ext in ('.md', '.txt'):
      lines, d['chat'] = strip_chat(text.splitlines())
      d['title'], d['tsrc'] = title_of(lines, stem)
      if d.get('src') in TITLE_OVERRIDES and d['cat'] == '一次資料': d['title'], d['tsrc'] = TITLE_OVERRIDES[d['src']], 'heading' 
      if rel.startswith('research_corpus/10_note_backfill/'):
        m0 = re.match(r'#\s+(.+)', text)
        if m0: d['title'], d['tsrc'] = m0[1].strip(), 'heading'
      if f in eng:
        d['title'] = eng[f].get('title', d['title']); d['date'] = eng[f].get('date'); d['url'] = eng[f].get('url')
      else:
        d['date'] = date_of(f, text)
      m = re.search(r'Original URL\*\*:\s*\[(https[^\]]+)\]', text)
      if m: d['url'] = m[1]
      d['heads'] = [plain(inline(x))[:70] for x in re.findall(r'^#{1,3}\s+(.+)$', text, re.M)][:14]
      d['chars'] = len(text)
      compiled = ('compiled' in f) or ('master' in f) or f in ('MASTER_INDEX.md', 'source_metadata.md')
      d['compiled'] = compiled
      d['blocks'] = blocks_of(lines, 600 if compiled else 1800, d['title'])
      if not compiled:
        FULL[d['id']] = blocks_of(lines, 10 ** 9, d['title']); d['full'] = 1
      if d['tsrc'] != 'heading' and ODD_TITLE.match(d['title']):
        alt = next((b[1] for b in d['blocks'][:10] if b[0] == 'h' and 8 <= len(b[1]) <= 70 and not re.match(r'^[\d０-９―—─→↓・]', b[1]) and not re.search(r'[→↓]', b[1]) and b[1] not in GENERIC_H), None)
        d['raw_title'] = d['title']
        d['title'] = alt or re.sub(r'^\d+[\.．]\s*', '', d['title'])
      d['cut'] = ends_cut(lines) if ext == '.md' else False
      d['ytids'] = sorted(set(YT_RE.findall(text))); d['yt'] = len(d['ytids'])
    elif ext in ('.py', '.js'):
      t = open(full, encoding='utf-8', errors='ignore').read(1500)
      d['title'] = f; d['text'] = clean(t[:400]); d['heads'] = []
    elif ext == '.html':
      head = open(full, encoding='utf-8', errors='ignore').read(6000)
      m = re.search(r'<title>(.*?)</title>', head, re.S)
      d['title'] = (clean(m[1]) + ' — ' + f) if m else f; d['text'] = 'HTML アプリ（単体で動くページ）'; d['heads'] = []
      if ext == '.html':
        raw = open(full, encoding='utf-8', errors='ignore').read(400000)
        text = re.sub(r'<[^>]+>', ' ', raw)
    else:
      d['title'] = f; d['text'] = ''; d['heads'] = []
    if ext == '.bak': d['cat'] = 'バックアップ'
    docs.append(d); texts.append(text)

N = len(docs); K = len(CONCEPTS)
cnt = np.zeros((N, K))
for i, t in enumerate(texts):
  if t:
    for k, rx in enumerate(CRX): cnt[i, k] = len(rx.findall(t))
dfc = (cnt > 0).sum(0)
idf = np.log((N + 1) / (dfc + 1)) + 0.3
for i, d in enumerate(docs):
  t = texts[i]
  if not t: d['concepts'] = []; continue
  L = max(len(t), 800)
  w = np.sqrt(cnt[i] / (L / 1000.0)) * idf
  thr = 2 if len(t) > 3000 else 1
  order = [int(k) for k in np.argsort(-w) if cnt[i, k] >= thr]
  d['concepts'] = [[k, round(float(w[k]), 3), int(cnt[i, k])] for k in order[:12]]

rows = []
dfv = collections.Counter()
for t in texts:
  c = collections.Counter(TOK.findall(t)) if t else collections.Counter()
  rows.append(c); dfv.update(c.keys())
keep = sorted(w for w, n in dfv.items() if 2 <= n <= N * 0.35)
vk = {w: i for i, w in enumerate(keep)}
inv = keep
M = np.zeros((N, len(vk)), dtype=np.float32)
for i, c in enumerate(rows):
  for w, n in c.items():
    j = vk.get(w)
    if j is not None: M[i, j] = (1 + math.log(n)) * math.log(N / dfv[w])
nrm = np.linalg.norm(M, axis=1, keepdims=True); nrm[nrm == 0] = 1; M /= nrm
S = M @ M.T; np.fill_diagonal(S, 0)
for i, d in enumerate(docs):
  d['sim'] = []; d['kw'] = []
  if not texts[i] or d['ext'] == '.html': continue
  row = M[i]; top = np.argsort(-row)[:10]
  d['kw'] = [inv[j] for j in top if row[j] > 0][:8]
  if d.get('compiled'): continue
  cand = [int(j) for j in np.argsort(-S[i])[:6] if S[i, j] > 0.12 and not docs[j].get('compiled') and docs[j]['ext'] != '.html']
  d['sim'] = [[j, round(float(S[i, j]), 3)] for j in cand]

bysrc = collections.defaultdict(list)
for d in docs:
  if d.get('src') and d['cat'] == '一次資料': bysrc[d['src']].append(d['id'])
for i, d in enumerate(docs):
  refs = set(re.findall(r'SRC_\d{3}', texts[i])) if texts[i] else set()
  refs.discard(d.get('src'))
  d['refs'] = sorted({j for r in refs for j in bysrc.get(r, []) if j != i})[:40]

# ---- link documents to published note articles (notes.tsv: key|date|title|body-start)
NT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.tsv')
def norm(s):
  s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
  return re.sub(r'[\s#*`>_|⸻—―─\-－・「」『』（）()【】\[\]〈〉《》“”"\'、。，．,.:：！？!?…~〜]+', '', s)
notes = []
if os.path.exists(NT_PATH):
  for ln in open(NT_PATH, encoding='utf-8'):
    c = ln.rstrip('\n').split('|')
    if len(c) >= 3: notes.append({'key': c[0], 'date': c[1], 'title': c[2], 'body': c[3] if len(c) > 3 else ''})
heads_n = {}
for i, d in enumerate(docs):
  if texts[i] and d['ext'] == '.md' and not d.get('compiled'):
    heads_n[i] = (norm(d['title']), norm(texts[i][:6000]))
linked = 0
for n in notes:
  nt = norm(n['title']); nb = norm(n['body'])
  probe_t = nt[:14]
  probe_b = nb[-16:] if len(nb) >= 22 else ''
  hits = []
  for i, (dt, dx) in heads_n.items():
    sc = 0
    if probe_t and (probe_t in dx[:900] or (len(dt) >= 10 and (dt[:14] == probe_t))): sc += 2
    if probe_b and probe_b in dx: sc += 2
    if sc: hits.append((sc, i))
  if not hits: continue
  best = max(h[0] for h in hits)
  for sc, i in hits:
    if sc < best: continue
    d = docs[i]
    if 'note' in d and d['note']['key'] != n['key']:
      d.setdefault('notes_more', []).append({'key': n['key'], 'date': n['date'], 'title': n['title']}); continue
    d['note'] = {'key': n['key'], 'date': n['date'], 'title': n['title']}
    d['url'] = d.get('url') or f"https://note.com/mizumawari_4096/n/{n['key']}"
    if not d.get('date'): d['date'] = n['date']; d['date_src'] = 'note'
    if d.get('tsrc') != 'heading' or len(norm(d['title'])) < 6:
      d['raw_title'] = d['title']; d['title'] = n['title']
  linked += 1
def bigr(s): return {s[i:i+2] for i in range(len(s) - 1)}
matched_keys = {d['note']['key'] for d in docs if 'note' in d}
cands = []
for n in notes:
  if n['key'] in matched_keys: continue
  nb = bigr(norm(n['title']))
  if len(nb) < 4: continue
  for i, (dt, dx) in heads_n.items():
    if 'note' in docs[i]: continue
    db = bigr(dt) | bigr(dx[:160])
    j = len(nb & db) / len(nb)
    if j >= 0.6: cands.append((j, n['key'], i))
cands.sort(reverse=True); used_n = set(); used_d = set(); fuzzy = []
for j, k, i in cands:
  if k in used_n or i in used_d: continue
  n = next(x for x in notes if x['key'] == k); d = docs[i]
  d['note'] = {'key': k, 'date': n['date'], 'title': n['title'], 'fuzzy': round(j, 2)}
  d['url'] = d.get('url') or f"https://note.com/mizumawari_4096/n/{k}"
  if not d.get('date'): d['date'] = n['date']; d['date_src'] = 'note'
  used_n.add(k); used_d.add(i); linked += 1; fuzzy.append((d.get('src'), d['title'][:30], n['title'][:30], round(j, 2)))
print('fuzzy', len(fuzzy)); [print('  ~', f) for f in fuzzy[:40]]
print('notes', len(notes), 'linked notes', linked, 'docs with note', sum(1 for d in docs if 'note' in d))
print('chat-stripped', sum(1 for d in docs if d.get('chat')), 'cut', sum(1 for d in docs if d.get('cut')))

# ---- YouTube links attached to the note articles (note_youtube.tsv: key|id,id)
NY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'note_youtube.tsv')
note_yt = {}
if os.path.exists(NY_PATH):
  for ln in open(NY_PATH, encoding='utf-8'):
    c = ln.strip().split('|')
    if len(c) == 2: note_yt[c[0]] = [x for x in c[1].split(',') if x]
for d in docs:
  own = set(d.pop('ytids', []) or [])
  ks = ([d['note']['key']] if 'note' in d else []) + [m['key'] for m in d.get('notes_more', [])]
  extra = [v for k in ks for v in note_yt.get(k, []) if v not in own]
  if extra: d['nyt'] = list(dict.fromkeys(extra)); d['yt'] = len(own) + len(d['nyt'])
print('docs with note videos', sum(1 for d in docs if d.get('nyt')))
unmatched = [n for n in notes if n['key'] not in {d['note']['key'] for d in docs if 'note' in d} | {m['key'] for d in docs for m in d.get('notes_more', [])}]
# ---- 1〜2行の要約 (summaries.tsv: path<TAB>summary)
SM_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summaries.tsv')
if os.path.exists(SM_PATH):
  sm = {}
  for ln in open(SM_PATH, encoding='utf-8'):
    c = ln.rstrip('\n').split('\t', 1)
    if len(c) == 2 and c[1].strip(): sm[c[0].replace('\\', '/')] = c[1].strip()
  for d in docs:
    v = sm.get(d['path'].replace('\\', '/'))
    if v: d['sum'] = v
print('docs with summary', sum(1 for d in docs if d.get('sum')))
out_notes = [{'key': n['key'], 'date': n['date'], 'title': n['title'], 'yt': note_yt.get(n['key'], [])} for n in unmatched]
out = {'notes_unmatched': out_notes, 'notes_total': len(notes), 'themes': [{'id': a, 'label': b} for a, b in THEMES],
       'concepts': [{'id': k, 'label': l, 'theme': t, 'df': int(dfc[k])} for k, (l, t, _) in enumerate(CONCEPTS)],
       'docs': docs}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('docs', N, 'bytes', os.path.getsize(OUT))
print(collections.Counter(d['cat'] for d in docs))

# ---- template.html があれば、ページを書き出す
#   notebook_atlas.html      : データと全文を埋め込んだ単体版（PC でそのまま開ける）
#   pub/notebook_atlas.html  : 公開用（data.json と texts/*.json を別ファイルで読み込む軽量版）
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'template.html')
BUNDLE = 40
if os.path.exists(TPL):
  dj = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
  tj = json.dumps({str(k): v for k, v in FULL.items()}, ensure_ascii=False, separators=(',', ':'))
  tpl = open(TPL, encoding='utf-8').read()
  local = tpl.replace('/*__DATA__*/', dj.replace('</', '<\\/')).replace('/*__TEXTS__*/', tj.replace('</', '<\\/'))
  open(os.path.join(HERE, 'notebook_atlas.html'), 'w', encoding='utf-8').write(local)
  pub = os.path.join(HERE, 'pub'); os.makedirs(os.path.join(pub, 'texts'), exist_ok=True)
  open(os.path.join(pub, 'notebook_atlas.html'), 'w', encoding='utf-8').write(tpl.replace('/*__DATA__*/', '').replace('/*__TEXTS__*/', ''))
  open(os.path.join(pub, 'data.json'), 'w', encoding='utf-8').write(dj)
  groups = collections.defaultdict(dict)
  for k, v in FULL.items(): groups[k // BUNDLE][str(k)] = v
  for g, m in groups.items():
    open(os.path.join(pub, 'texts', f't{g}.json'), 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, separators=(',', ':')))
  print('wrote local + pub;', len(groups), 'text bundles;', sum(os.path.getsize(os.path.join(pub, 'texts', f)) for f in os.listdir(os.path.join(pub, 'texts'))) // 1024, 'KB of full text')
