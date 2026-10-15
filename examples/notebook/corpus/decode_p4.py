import json
with open('p4_novel_safe.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('p4_novel_out.txt', 'w', encoding='utf-8') as out:
    for item in data:
        out.write(f"[{item['file']}] {item['text'][:300]}\n")
