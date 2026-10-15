# -*- coding: utf-8 -*-
import os, glob, re

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

low_drive = r'(欲求.*(ない|消え|薄)|動機.*(ない|消え|薄)|(やりたい|したい).*(ない|薄)|モチベーション.*(ない|消)|何もしない|勝手に|自然に)'
actions = r'(行動|執筆|仕事|運転|会話|生活|作業|集中|没入|書く)'

with open('action_results.txt', 'w', encoding='utf-8') as out:
    found = 0
    for f in files:
        if found >= 20: break
        fname = os.path.basename(f)
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
        except:
            continue
            
        paragraphs = content.split('\n\n')
        for p in paragraphs:
            p_clean = p.replace('\n', ' ')
            if re.search(low_drive, p_clean) and re.search(actions, p_clean):
                out.write(f'--- {fname} ---\n')
                out.write(p_clean[:400] + '\n\n')
                found += 1
                break
