# 新着 note の自動取り込み手順（定期タスク用）

対象: https://note.com/mizumawari_4096 の新着記事 → Notebook 概念アトラスへ反映
アトラス: https://claude.ai/artifact/HDoFQpr6qtVpR5BaLrL2oh
作業フォルダ: Notebook/_concept_map（デバイスのシェルでは $HOME/mnt/Notebook/_concept_map）

1. 既知キーを取得: `cd $HOME/mnt/Notebook/_concept_map && python3 -c "import json;print(json.dumps([l.split('|')[0] for l in open('notes.tsv',encoding='utf-8') if l.strip()]))"`
2. 内蔵ブラウザで https://note.com/mizumawari_4096 を開き、`note_to_md.js` の中身の `__KNOWN__` を手順1の配列に置き換えて javascript_tool で実行する。
   - 結果が `NEWNOTES[]` なら新着なし。ここで終了（何も公開しない）。
   - 結果が大きいとファイルに保存される。そのファイルから python で 'NEWNOTES' 以降の JSON 配列を取り出す。
3. JSON 配列を /mnt/user-data/outputs/new_notes_<日付>.json に保存し、device_commit_files で `_concept_map/inbox/new_notes.json` に書き込む。
4. `python3 add_notes.py inbox/new_notes.json` を実行。SRC_xxx として 01_original_sources と 09_recent_note_corpus に保存され、notes.tsv / note_youtube.tsv が更新される。出力に追加資料の path が出る。
5. 追加された各資料（path が null でないもの）を読み、1〜2行の日本語の要約（中立・説明的、「〜を述べる」「〜を整理する」調）を書き、`summaries.tsv` に `path<TAB>要約` で追記する（path は research_corpus/01_original_sources/... の方）。
6. `python3 build_data.py` を実行。
7. `pub/notebook_atlas.html`, `pub/data.json`, `pub/texts/*.json`（ある分すべて）を device_stage_files でステージ。
8. Artifact を action "read"（url=アトラス、path="data.json"）で読んでから、action "publish"（url=アトラス、file_path=ステージした notebook_atlas.html、files={"data.json":..., "texts/tN.json":...}）で更新する。
9. 追加した記事タイトルを短く報告する。エラー時は何をしたか・どこで止まったかを報告する。
