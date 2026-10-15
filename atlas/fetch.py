# -*- coding: utf-8 -*-
"""Collect a corpus from the web into a folder of markdown files.

  python -m atlas fetch <url> --out corpus/        # RSS/Atom feed, sitemap.xml, or a page (+ same-site links)
  python -m atlas fetch note:<creator> --out corpus/   # every public article of a note.com creator
  python -m atlas fetch urls.txt --out corpus/     # one URL per line

Each page becomes `YYYYMMDD_<slug>.md` with a small front matter (title, date, url) so the
builder picks up dates and links. Only the standard library is used.
If your environment cannot reach the site (sandboxed agents), save the pages or texts into a
folder by other means and build from that folder instead.
"""
import json, os, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

from .htmltext import html_to_text

UA = 'Mozilla/5.0 (concept-atlas fetcher)'


def get(url, timeout=30):
  req = urllib.request.Request(url, headers={'User-Agent': UA})
  with urllib.request.urlopen(req, timeout=timeout) as r:
    raw = r.read(); enc = r.headers.get_content_charset() or 'utf-8'
  return raw.decode(enc, errors='ignore')


def slug(s, n=40):
  s = re.sub(r'[\\/:*?"<>|\s　「」『』〈〉“”()（）？！?!、。,.・…―—\-#]+', '_', s).strip('_')
  return s[:n] or 'page'


def save(out, title, body, date=None, url=None, tags=None, extra=None):
  os.makedirs(out, exist_ok=True)
  d = (date or '')[:10]
  fn = f"{d.replace('-', '')}_{slug(title)}.md" if d else f"{slug(title)}.md"
  fm = ['---', f'title: {title}']
  if d: fm.append(f'date: {d}')
  if url: fm.append(f'url: {url}')
  if tags: fm.append('tags: ' + ' '.join(tags))
  for k, v in (extra or {}).items(): fm.append(f'{k}: {v}')
  fm.append('---')
  path = os.path.join(out, fn)
  open(path, 'w', encoding='utf-8').write('\n'.join(fm) + f'\n\n# {title}\n\n' + body.strip() + '\n')
  return path


def iso(s):
  if not s: return None
  m = re.search(r'(\d{4})-(\d{2})-(\d{2})', s)
  if m: return m[0]
  try:
    from email.utils import parsedate_to_datetime
    return parsedate_to_datetime(s).strftime('%Y-%m-%d')
  except Exception:
    return None


def from_feed(xml, out, limit, log):
  root = ET.fromstring(xml); n = 0
  items = root.findall('.//item') or root.findall('{http://www.w3.org/2005/Atom}entry')
  for it in items[:limit]:
    g = lambda *tags: next((it.findtext(t) for t in tags if it.findtext(t)), '')
    title = g('title', '{http://www.w3.org/2005/Atom}title').strip()
    link = g('link') or (it.find('{http://www.w3.org/2005/Atom}link').get('href') if it.find('{http://www.w3.org/2005/Atom}link') is not None else '')
    date = iso(g('pubDate', '{http://www.w3.org/2005/Atom}published', '{http://www.w3.org/2005/Atom}updated'))
    html = g('{http://purl.org/rss/1.0/modules/content/}encoded', '{http://www.w3.org/2005/Atom}content')
    if len(re.sub(r'<[^>]+>', '', html)) < 600 and link:   # feed has only an excerpt: fetch the page
      try: html = get(link); time.sleep(0.5)
      except Exception as e: log(f'  skip {link}: {e}')
    _, body = html_to_text(html)
    save(out, title or link, body, date, link); n += 1
  return n


def from_sitemap(xml, out, limit, log):
  locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', xml)
  if locs and all(l.endswith('.xml') for l in locs[:3]):        # sitemap index
    sub = []
    for l in locs[:10]:
      try: sub += re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', get(l))
      except Exception: pass
    locs = sub
  return from_urls(locs[:limit], out, log)


def from_urls(urls, out, log):
  n = 0
  for u in urls:
    try:
      html = get(u)
    except Exception as e:
      log(f'  skip {u}: {e}'); continue
    title, body = html_to_text(html)
    m = re.search(r'(?:article:published_time|datePublished)["\']?\s*(?:content=|:)\s*["\']([^"\']+)', html)
    save(out, title or u, body, iso(m[1]) if m else None, u); n += 1
    time.sleep(0.5)
  return n


def from_page(url, html, out, limit, log):
  """A page and the same-site article links on it (one level)."""
  host = urllib.parse.urlparse(url).netloc
  links = []
  for h in re.findall(r'href=["\']([^"\'#]+)["\']', html):
    u = urllib.parse.urljoin(url, h)
    p = urllib.parse.urlparse(u)
    if p.netloc == host and p.path not in ('', '/') and not re.search(r'\.(png|jpe?g|gif|css|js|svg|pdf|zip)$', p.path, re.I):
      links.append(u.split('?')[0])
  links = list(dict.fromkeys([url] + links))[:limit]
  return from_urls(links, out, log)


def from_note(creator, out, limit, log):
  """note.com creator via its public JSON API."""
  n, page = 0, 1
  while n < limit:
    j = json.loads(get(f'https://note.com/api/v2/creators/{creator}/contents?kind=note&page={page}'))
    for c in j['data']['contents']:
      d = json.loads(get(f"https://note.com/api/v3/notes/{c['key']}"))['data']
      _, body = html_to_text('<article>' + (d.get('body') or '') + '</article>')
      tags = [h['hashtag']['name'] for h in d.get('hashtag_notes') or [] if h.get('hashtag')]
      save(out, d['name'], body, iso(d.get('publish_at')), f"https://note.com/{creator}/n/{c['key']}", tags, {'key': c['key']})
      n += 1; time.sleep(0.4)
      if n >= limit: break
    if j['data'].get('isLastPage'): break
    page += 1
  return n


def fetch(src, out, limit=300, log=print):
  if src.startswith('note:'):
    n = from_note(src[5:], out, limit, log)
  elif os.path.exists(src):
    urls = [l.strip() for l in open(src, encoding='utf-8') if l.strip().startswith('http')]
    n = from_urls(urls[:limit], out, log)
  else:
    body = get(src)
    head = body[:600].lower()
    if '<rss' in head or '<feed' in head:
      n = from_feed(body, out, limit, log)
    elif '<urlset' in head or '<sitemapindex' in head:
      n = from_sitemap(body, out, limit, log)
    else:
      n = from_page(src, body, out, limit, log)
  log(f'saved {n} pages to {out}')
  return n
