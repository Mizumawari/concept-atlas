# -*- coding: utf-8 -*-
"""Minimal HTML -> markdown-ish text (headings, paragraphs, lists, quotes, tables, YouTube embeds).

Only the standard library is used so the tool runs anywhere.
"""
import re
from html.parser import HTMLParser

BLOCK = {'p', 'div', 'section', 'article', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote',
         'pre', 'tr', 'br', 'hr', 'figure', 'figcaption', 'header', 'footer', 'main', 'ul', 'ol', 'table'}
SKIP = {'script', 'style', 'noscript', 'svg', 'nav', 'form', 'button', 'iframe', 'template'}
YT = re.compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/|live/))([A-Za-z0-9_-]{11})')


class _P(HTMLParser):
  def __init__(self):
    super().__init__(convert_charrefs=True)
    self.out = []; self.buf = []; self.skip = 0; self.prefix = ''; self.title = ''; self._in_title = False
    self.cells = None; self.bold = 0

  def flush(self):
    s = re.sub(r'[ \t\r\f\v]+', ' ', ''.join(self.buf)).strip()
    if s:
      self.out.append(self.prefix + s)
    self.buf = []; self.prefix = ''

  def handle_starttag(self, tag, attrs):
    a = dict(attrs)
    if tag in SKIP:
      if tag == 'iframe':
        m = YT.search(a.get('src', '') or '')
        if m: self.flush(); self.out.append(f'[YouTube Video: https://youtu.be/{m[1]}](https://youtu.be/{m[1]})')
      self.skip += 1; return
    if self.skip: return
    if tag == 'title': self._in_title = True; return
    if tag == 'figure':
      m = YT.search(a.get('data-src', '') or '')
      if m: self.flush(); self.out.append(f'[YouTube Video: https://youtu.be/{m[1]}](https://youtu.be/{m[1]})')
    if tag == 'tr': self.flush(); self.cells = []; return
    if tag in ('td', 'th') and self.cells is not None: self.buf = []; return
    if tag in BLOCK:
      self.flush()
      if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'): self.prefix = '#' * min(int(tag[1]), 4) + ' '
      elif tag == 'li': self.prefix = '* '
      elif tag == 'blockquote': self.prefix = '> '
      elif tag == 'hr': self.out.append('---')
    if tag in ('b', 'strong'): self.buf.append('**'); self.bold += 1
    if tag == 'a':
      m = YT.search(a.get('href', '') or '')
      if m: self.flush(); self.out.append(f'[YouTube Video: https://youtu.be/{m[1]}](https://youtu.be/{m[1]})')

  def handle_endtag(self, tag):
    if tag in SKIP:
      self.skip = max(0, self.skip - 1); return
    if self.skip: return
    if tag == 'title': self._in_title = False; return
    if tag in ('td', 'th') and self.cells is not None:
      self.cells.append(re.sub(r'\s+', ' ', ''.join(self.buf)).strip().replace('|', '／')); self.buf = []; return
    if tag == 'tr' and self.cells is not None:
      if any(self.cells): self.out.append('| ' + ' | '.join(self.cells) + ' |')
      self.cells = None; return
    if tag in ('b', 'strong') and self.bold: self.buf.append('**'); self.bold -= 1
    if tag in BLOCK: self.flush()

  def handle_data(self, data):
    if self._in_title: self.title += data; return
    if not self.skip: self.buf.append(data)


def html_to_text(html):
  """Return (title, markdown_text)."""
  p = _P()
  # prefer the main article when the page has one
  m = re.search(r'<(article|main)\b.*?</\1>', html, re.S | re.I)
  body = m[0] if m and len(m[0]) > 800 else html
  p.feed(body); p.flush()
  if not p.title:
    t = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    p.title = re.sub(r'\s+', ' ', t[1]).strip() if t else ''
  return p.title.strip(), '\n\n'.join(p.out)
