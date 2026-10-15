import os, glob, re

corpus_dir = r'c:\Users\destr\OneDrive\デスクトップ\Notebook\research_corpus\01_original_sources'
files = glob.glob(os.path.join(corpus_dir, 'SRC_*.md'))
files.sort()

low_drive = r'(欲求.*ない|動機.*ない|やりたい.*ない|したい.*ない|モチベーション.*ない|何もしない|勝手に|自然に)'
actions = r'(執筆|仕事|運転|会話|生活|作業|集中|没入|食べる|話す|歩く)'

with open('action_table.md', 'w', encoding='utf-8') as out:
    count = 0
    for f in files:
        if count >= 15: break
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
                out.write(f'### {fname}\n')
                out.write(f'{p_clean[:300]}...\n\n')
                count += 1
                break
