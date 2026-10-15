# -*- coding: utf-8 -*-
import os, glob, re, json

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

# Keywords for failure to start / inability to act / stalling
fail_keywords = r'(始められない|動けない|できない|先延ばし|手がつかない|止まる|実行.*移せない|難しい)'
action_context = r'(行動|作業|執筆|仕事|新しいこと|タスク|やる)'

results = []

for f in files:
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception:
        continue
        
    paragraphs = content.split('\n\n')
    
    for i, p in enumerate(paragraphs):
        p_clean = p.replace('\n', ' ').strip()
        
        if re.search(fail_keywords, p_clean) and re.search(action_context, p_clean):
            match = re.search(fail_keywords, p_clean)
            results.append({
                "src": fname,
                "para_idx": i,
                "keyword": match.group(0),
                "text": p_clean
            })

with open('phase4_data.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, ensure_ascii=False, indent=2)
