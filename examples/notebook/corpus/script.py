import codecs
import os
import markdown

src_dir = r'c:\Users\destr\OneDrive\デスクトップ\Notebook\research_corpus\06_book_manuscript'
in_file = os.path.join(src_dir, 'publication_master_v1.0.md')
out_html = os.path.join(src_dir, 'n=1_no_henkyo_Mizumawari.html')

with codecs.open(in_file, 'r', 'utf-8') as f:
    text = f.read()

html_body = markdown.markdown(text)

css = '''
body { font-family: 'Hiragino Mincho ProN', 'Yu Mincho', serif; line-height: 1.8; color: #333; max-width: 800px; margin: 0 auto; padding: 2em; }
h1 { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; page-break-before: always; border-bottom: 1px solid #aaa; padding-bottom: 0.3em; margin-top: 2em; }
h1:first-of-type { page-break-before: auto; text-align: center; border-bottom: none; font-size: 2.5em; margin-top: 15vh; }
h2 { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; margin-top: 1.5em; text-align: center; }
h3 { font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; color: #555; background-color: #f4f4f4; padding: 0.5em; border-left: 5px solid #666; margin-top: 2em; }
hr { border: 0; border-top: 1px solid #ccc; margin: 3em 0; page-break-after: always; }
p { text-align: justify; text-indent: 1em; }
'''

html_full = f'<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n<meta charset=\"UTF-8\">\n<title>n=1の辺境</title>\n<style>\n{css}\n</style>\n</head>\n<body>\n{html_body}\n</body>\n</html>'

with codecs.open(out_html, 'w', 'utf-8') as f:
    f.write(html_full)

print('HTML created.')
