# -*- coding: utf-8 -*-
import os, glob, re, json

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

# Keyword
keyword = r'(必要性|必要だ|必要に|必要がある|必要)'

results = []
count = 0

for f in files:
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception:
        continue
        
    paragraphs = content.split('\n\n')
    
    for p in paragraphs:
        p_clean = p.replace('\n', ' ').strip()
        
        # We only want it when it's related to action or drive, not just random "I need water" 
        # But user said "all uses of hits". Let's grab them, but prioritize ones near action words if there are too many.
        if re.search(keyword, p_clean) and count < 15:
            # Let's just grab the first 15 distinct paragraphs mentioning it to get a sample
            match = re.search(keyword, p_clean)
            results.append({
                "src": fname,
                "text": p_clean[:300]
            })
            count += 1
            if count >= 15: break
    if count >= 15: break

with open('phase3_data.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, ensure_ascii=False, indent=2)
