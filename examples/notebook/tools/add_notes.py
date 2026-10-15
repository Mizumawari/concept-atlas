# 使い方: python3 tools/add_notes.py new_notes.json   （examples/notebook で実行）
# note_to_md.js の結果(JSON配列)を SRC_xxx として corpus/research_corpus に追加し、catalog.tsv を更新する。
# 追加した資料の一覧を JSON で出力する(要約づくりに使う)。
import json, os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.join(HERE, 'corpus')
SRC_DIR = os.path.join(ROOT, 'research_corpus', '01_original_sources')
REC_DIR = os.path.join(ROOT, 'research_corpus', '09_recent_note_corpus')
CT = os.path.join(HERE, 'catalog.tsv')
items = json.load(open(sys.argv[1], encoding='utf-8'))
known = {l.split('\t')[0] for l in open(CT, encoding='utf-8') if l.strip()}
# 既にコーパスにある記事(例: 08_note_articles)は SRC にせず notes.tsv にだけ足す
def norm(s): return re.sub(r'[\s#*`>_|「」『』（）()【】\[\]、。・…―—\-－:：!！?？]+', '', s)
corpus_titles = set()
for dp, dn, fn in os.walk(os.path.join(ROOT, 'research_corpus')):
  for f in fn:
    if f.endswith('.md'):
      try: first = open(os.path.join(dp, f), encoding='utf-8', errors='ignore').readline()
      except Exception: continue
      if first.startswith('#'): corpus_titles.add(norm(first.lstrip('#')))
nums = [int(m[1]) for f in os.listdir(SRC_DIR) for m in [re.match(r'SRC_(\d{3})', f)] if m]
nxt = max(nums) + 1
added = []
for a in sorted(items, key=lambda x: x['pub']):
  if a['key'] in known: continue
  date = a['pub'][:10]; body = a['body'].strip()
  yt = list(dict.fromkeys(re.findall(r'youtu(?:\.be/|be\.com/watch\?v=)([\w-]{11})', body)))
  plain = re.sub(r'\[YouTube Video:[^\n]*', '', body)
  b40 = norm(re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', plain))[:40]
  url = f"https://note.com/mizumawari_4096/n/{a['key']}"
  open(CT, 'a', encoding='utf-8').write('\t'.join([a['key'], date, a['title'].replace('\t', ' '), url, b40, ','.join(yt)]) + '\n')
  if norm(a['title']) in corpus_titles:
    added.append({'key': a['key'], 'title': a['title'], 'path': None, 'note': '既存の資料と同じ記事のため catalog.tsv にだけ追加'}); continue
  sid = f'SRC_{nxt:03d}'; nxt += 1
  safe = re.sub(r'[\\/:*?"<>|\s　「」『』〈〉“”()（）？！?!、。,.・…―—\-]+', '_', a['title']).strip('_')[:40]
  fn = f"{sid}_{date.replace('-', '')}_{safe}.md"
  pub = a['pub'].replace('.000', '')
  head = [f"# {a['title']}", '', f'* **Source ID**: `{sid}`', '* **Author**: みずまわり (Mizumawari)', f'* **Published At**: {pub}',
          f"* **Original URL**: [https://note.com/mizumawari_4096/n/{a['key']}](https://note.com/mizumawari_4096/n/{a['key']})",
          f"* **Note Key**: `{a['key']}`"]
  if a.get('tags'): head.append('* **Hashtags**: ' + ' '.join(a['tags']))
  text = '\n'.join(head) + '\n\n---\n\n' + body + '\n'
  for d in (SRC_DIR, REC_DIR):
    open(os.path.join(d, fn), 'w', encoding='utf-8').write(text)
  added.append({'key': a['key'], 'src': sid, 'title': a['title'], 'path': 'research_corpus/01_original_sources/' + fn,
                'path2': 'research_corpus/09_recent_note_corpus/' + fn, 'chars': len(body)})
print(json.dumps(added, ensure_ascii=False, indent=1))
