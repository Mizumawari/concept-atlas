# -*- coding: utf-8 -*-
import os, glob, re

corpus_dir = r'research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))

print("=== PHASE 1: 行動開始の記述 ===")
p1_count = 0
for f in files:
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except:
        continue
    for line in content.split('。'):
        line = line.replace('\n', ' ').strip()
        if re.search(r'(自然に|いつの間にか|勝手に|気づいたら)', line) and re.search(r'(行動|動く|向かう|始める|やっている|している)', line):
            if len(line) < 200:
                print(f"[{fname}] {line}")
                p1_count += 1
        if p1_count > 10: break
    if p1_count > 10: break

print("\n=== PHASE 4: 始まらない・できない記述 ===")
p4_count = 0
for f in files:
    fname = os.path.basename(f)
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except:
        continue
    for line in content.split('。'):
        line = line.replace('\n', ' ').strip()
        if re.search(r'(始められない|動かない|行動.*難しい|行動.*できない|できない|未知.*難しい|新規.*難しい)', line):
            if len(line) < 200:
                print(f"[{fname}] {line}")
                p4_count += 1
        if p4_count > 10: break
    if p4_count > 10: break
