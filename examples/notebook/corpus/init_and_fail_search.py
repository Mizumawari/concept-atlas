# -*- coding: utf-8 -*-
import os, glob, re, json

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

phase1_keywords = r'(始める|始まる|気づいたら.*(ている|た)|自然に.*(する|動く)|いつの間にか.*(ている|た)|手が動く)'
phase4_keywords = r'(始められない|動かない|難しい|できない|やりたい.*できない|必要.*できない|着手.*できない)'
# Focus on failure to act despite need/desire, or just difficulty initiating

results = {'Phase1': [], 'Phase4': []}

for f in files:
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except:
        continue
    
    sentences = content.replace('\n', ' ').split('。')
    
    for s in sentences:
        s = s.strip()
        if not s: continue
        
        # Phase 4 (Failure to initiate/difficulty)
        if re.search(r'(行動|作業|執筆|仕事|新しいこと|未知).*' + phase4_keywords, s) or \
           re.search(phase4_keywords + r'.*(行動|作業|執筆|仕事|新しいこと|未知)', s):
            results['Phase4'].append(f'[{fname}] {s}')
            
        # Phase 1 (Initiation) - sample a few explicit ones
        elif re.search(r'(行動|作業|執筆|仕事|会話).*' + phase1_keywords, s):
            if len(results['Phase1']) < 10:  # limit to 10 for brief review
                results['Phase1'].append(f'[{fname}] {s}')

with open('p1_p4_results.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, ensure_ascii=False, indent=2)
