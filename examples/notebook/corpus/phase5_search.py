# -*- coding: utf-8 -*-
import os, glob, re, json

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

# Keywords
kw_known = r'(習慣|反復|毎日|繰り返|運転|歩行|食事|日常|習熟)'
kw_novel = r'(新し|未知|ゼロから|意図的|初めて|目的を|立ち上)'
kw_success = r'(できる|できた|始める|始めた|発生|進む|動く|自然に)'
kw_fail = r'(できない|難しい|手がつかない|先延ばし|実行.*不可|動かない|困難|停止)'

results = {'Known_Success': [], 'Known_Fail': [], 'Novel_Success': [], 'Novel_Fail': []}

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
        if len(p_clean) < 10: continue
        
        has_known = re.search(kw_known, p_clean)
        has_novel = re.search(kw_novel, p_clean)
        has_success = re.search(kw_success, p_clean)
        has_fail = re.search(kw_fail, p_clean)
        
        # We need specific matches to populate the quadrants accurately
        # If it has known and fail
        if has_known and has_fail:
            results['Known_Fail'].append(f'[{fname}] {p_clean[:200]}')
        # If it has known and success
        elif has_known and has_success:
            if len(results['Known_Success']) < 5:
                results['Known_Success'].append(f'[{fname}] {p_clean[:200]}')
        
        # If it has novel and fail
        if has_novel and has_fail:
            if len(results['Novel_Fail']) < 5:
                results['Novel_Fail'].append(f'[{fname}] {p_clean[:200]}')
        # If it has novel and success
        elif has_novel and has_success:
            if len(results['Novel_Success']) < 5:
                results['Novel_Success'].append(f'[{fname}] {p_clean[:200]}')

with open('phase5_data.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, ensure_ascii=False, indent=2)
