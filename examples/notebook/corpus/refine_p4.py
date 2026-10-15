# -*- coding: utf-8 -*-
import json
with open('phase4_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = []
for item in data:
    text = item['text']
    if '行動を起こす' in text or '始められない' in text or '動けない' in text or '先延ばし' in text or '手がつかない' in text:
        results.append(f"[{item['src']}] {text[:300]}")

with open('refine_out.txt', 'w', encoding='utf-8') as out:
    for r in results:
        out.write(r + '\n\n')
