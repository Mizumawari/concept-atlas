# -*- coding: utf-8 -*-
import os, glob, re, json

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

# User requested keywords
keywords = r'(始める|始まる|開始|やる|やろう|やった|気づいたら|いつの間にか|自然に|勝手に|そのまま|手が動く|身体が動く|決める|意思|選択|必要|行動|動く|取り掛かる)'

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
        
        # We need a keyword AND an action context (to filter out random noise)
        if re.search(keywords, p_clean) and re.search(r'(仕事|執筆|運転|作業|食べる|話す|歩く)', p_clean):
            # Context around the match
            match = re.search(keywords, p_clean)
            if match:
                results.append({
                    "src": fname,
                    "para_idx": i,
                    "keyword": match.group(0),
                    "text": p_clean
                })

# Output top 10 as JSON for safe reading
with open('phase12_data.json', 'w', encoding='utf-8') as out:
    json.dump(results[:15], out, ensure_ascii=False, indent=2)
