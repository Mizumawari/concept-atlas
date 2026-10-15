# -*- coding: utf-8 -*-
import os, glob, re

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

# We need action verbs or onset indicators
onset_keywords = r'(始める|始めた|やり出す|取り組む|着手|向かう|気づいたら|動き出す|開始)'
# We need low drive context
low_drive = r'(欲求.*ない|やりたい.*ない|動機.*ない|理由.*ない|自然に|勝手に|目的.*ない)'

results = []
for f in files:
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except:
        continue
    
    # split into chunks (e.g. paragraphs or sentences)
    chunks = content.split('。')
    for chunk in chunks:
        chunk = chunk.replace('\n', ' ').strip()
        if re.search(onset_keywords, chunk) and re.search(low_drive, chunk):
            results.append(f'[{fname}] {chunk}')

with open('initiation_results.txt', 'w', encoding='utf-8') as out:
    for r in results:
        out.write(r + '\n')
