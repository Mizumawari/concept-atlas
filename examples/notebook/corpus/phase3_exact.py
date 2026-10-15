# -*- coding: utf-8 -*-
import os, glob, re, json

files = glob.glob(r'research_corpus\01_original_sources\SRC_*.md')
files.sort()

keyword = r'(必要性|必要だ|必要に|必要がある|必要)'
results = []
count = 0

for f in files:
    if count >= 12: break
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception:
        continue
        
    paragraphs = content.split('\n\n')
    for p in paragraphs:
        p_clean = p.replace('\n', ' ').strip()
        # Find explicit necessity mentions
        if re.search(r'[^不]必要', p_clean) and len(p_clean) < 300:
            if not any(r['text'] == p_clean for r in results):
                results.append({
                    "src": fname,
                    "text": p_clean
                })
                count += 1
                break

with open('phase3_final.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, ensure_ascii=False, indent=2)
