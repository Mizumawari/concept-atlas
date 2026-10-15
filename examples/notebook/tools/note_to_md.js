// 使い方: note.com を開いたタブで実行する。__KNOWN__ を notes.tsv のキー配列(JSON)に置き換える。
// 戻り値: 'NEWNOTES' + JSON配列 [{key,title,pub,tags,body(markdown)}]
const KNOWN=new Set(__KNOWN__);
function md(html){
  const doc=new DOMParser().parseFromString('<div>'+html+'</div>','text/html'); const out=[];
  const inl=n=>{ if(n.nodeType===3) return n.textContent; if(n.nodeType!==1) return ''; const t=n.tagName; const c=[...n.childNodes].map(inl).join('');
    if(t==='BR') return '\n'; if(t==='P'||t==='DIV') return c+'\n'; if(t==='B'||t==='STRONG') return c.trim()?'**'+c+'**':c; if(t==='A'){const h=n.getAttribute('href')||''; return h&&!h.startsWith('#')?`[${c}](${h})`:c;} return c; };
  const quote=e=>inl(e).replace(/\n+$/,'').split('\n').map(l=>'> '+l).join('\n');
  const blk=(n,depth)=>{ for(const e of n.children){ const t=e.tagName;
    if(/^H[1-6]$/.test(t)) out.push('#'.repeat(Math.min(+t[1],4))+' '+inl(e).trim());
    else if(t==='P'){ const s=inl(e).trim(); if(s) out.push(s); }
    else if(t==='UL'||t==='OL'){ let i=1; for(const li of e.children){ const own=[...li.childNodes].filter(x=>!(x.nodeType===1&&/^(UL|OL)$/.test(x.tagName))).map(inl).join('').trim(); out.push('  '.repeat(depth)+(t==='OL'?(i++)+'. ':'* ')+own); const sub=[...li.children].filter(x=>/^(UL|OL)$/.test(x.tagName)); if(sub.length){ const w=document.createElement('div'); sub.forEach(s=>w.appendChild(s.cloneNode(true))); blk(w,depth+1);} } }
    else if(t==='BLOCKQUOTE'){ out.push(quote(e)); }
    else if(t==='PRE'){ out.push('```\n'+e.textContent.replace(/\n$/,'')+'\n```'); }
    else if(t==='HR') out.push('---');
    else if(t==='TABLE'){ const rows=[...e.querySelectorAll('tr')].map(r=>'| '+[...r.children].map(c=>inl(c).trim().replace(/\n/g,' ').replace(/\|/g,'／')).join(' | ')+' |'); if(rows.length){ const n=(rows[0].match(/ \| /g)||[]).length+1; rows.splice(1,0,'|'+' --- |'.repeat(n)); out.push(rows.join('\n')); } }
    else if(t==='FIGURE'){ const src=e.getAttribute('data-src')||''; if(/youtu/.test(src)){ out.push(`[YouTube Video: ${src}](${src})`); continue; }
      const bq=e.querySelector('blockquote'); const cap=e.querySelector('figcaption'); const capT=cap?cap.textContent.trim():'';
      if(bq){ out.push(quote(bq)+(capT?'\n> — '+capT:'')); }
      else if(e.querySelector('table')){ blk(e,depth); }
      else if(capT) out.push('（図）'+capT); }
    else if(t==='DIV'||t==='SECTION') blk(e,depth);
    else { const s=inl(e).trim(); if(s) out.push(s); } } };
  blk(doc.body.firstChild,0); return out.join('\n\n').replace(/\n{3,}/g,'\n\n');
}
const list=[];
for(let p=1;p<=3;p++){ const j=await fetch(`/api/v2/creators/mizumawari_4096/contents?kind=note&page=${p}`).then(r=>r.json()); list.push(...j.data.contents); if(j.data.isLastPage) break; }
const fresh=list.filter(c=>!KNOWN.has(c.key));
const res=[];
for(const c of fresh){ const d=(await fetch('/api/v3/notes/'+c.key).then(r=>r.json())).data;
  const tags=(d.hashtag_notes||[]).map(h=>h.hashtag&&h.hashtag.name).filter(Boolean).map(x=>x.startsWith('#')?x:'#'+x);
  res.push({key:c.key,title:d.name,pub:d.publish_at,tags,body:md(d.body||'')}); }
'NEWNOTES'+JSON.stringify(res)
