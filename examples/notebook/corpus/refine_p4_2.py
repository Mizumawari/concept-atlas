# -*- coding: utf-8 -*-
import glob, json

files = glob.glob(r'research_corpus\01_original_sources\SRC_*.md')
results = []
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except: continue
    
    for p in content.split('\n\n'):
        p_clean = p.replace('\n', ' ')
        if ('始められない' in p_clean or '動けない' in p_clean or '行動を起こすのが' in p_clean or '手がつかない' in p_clean) and '難' in p_clean:
            results.append(f'[{f}] {p_clean[:300]}')

with open('refine_out2.txt', 'w', encoding='utf-8') as out:
    for r in results:
        out.write(r + '\n\n')
