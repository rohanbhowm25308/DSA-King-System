/* DSA King System — account-based Progress / Rankings extension. */
let hunterProgress=null,hunterLeaderboard=null,hunterFilter='All';
async function refreshHunterStats(){
  try{const r=await fetch('/api/progress',{credentials:'same-origin'});if(r.ok){hunterProgress=await r.json();if(tab==='Progress')renderHunterStats('Progress');}}
  catch(e){console.warn('Progress unavailable',e)}
}
const hpEscape=v=>escapeHTML(v);
function hunterBar(label,done,total,css){
  const percent=total?Math.min(100,Math.round(done/total*100)):0;
  return `<div class="hunter-diff"><div class="hunter-diff-title"><b class="${css}">${label}</b><span>${done} / ${total} solved · ${percent}%</span></div><div class="hunter-track"><i class="${css}" style="width:${percent}%"></i></div></div>`;
}
function hunterHeatmap(activity){
  const counts=new Map((activity||[]).map(x=>[x.day,x.submissions]));
  const cells=[];const now=new Date();now.setHours(12,0,0,0);
  for(let n=119;n>=0;n--){const d=new Date(now);d.setDate(d.getDate()-n);const date=[d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-');const count=counts.get(date)||0;const strength=count>=6?4:count>=3?3:count>=2?2:count?1:0;cells.push(`<span class="hunter-day heat-${strength}" title="${date}: ${count} submissions"></span>`)}
  return `<div class="hunter-heat">${cells.join('')}</div><small>Last 120 days · darker cells mean more submissions</small>`;
}
function hunterProblemRows(p){
 const solved=new Set(p.solved_ids),bookmarks=new Set(p.bookmarks||[]);
 const rows=PROBLEMS.filter(x=>x.id<=4||x.id===100005||x.id===100006||(x.id>=2001&&x.id<=2206));
 const filtered=rows.filter(x=>hunterFilter==='All'||(hunterFilter==='Solved'?solved.has(x.id):hunterFilter==='Unsolved'?!solved.has(x.id):hunterFilter==='Saved'?bookmarks.has(x.id):x.difficulty===hunterFilter));
 return `<div class="hunter-filters">${['All','Easy','Medium','Hard','Solved','Unsolved','Saved'].map(k=>`<button class="${hunterFilter===k?'primary':'secondary'}" onclick="hunterFilter='${k}';renderHunterStats('Progress')">${k}</button>`).join('')}</div><div class="hunter-problems">${filtered.map(x=>`<div class="hunter-problem"><span class="hunter-check">${solved.has(x.id)?'✓':'○'}</span><button class="hunter-problem-name" onclick="selectProblem(${x.id})">${hpEscape(x.title)}</button><small class="${x.difficulty.toLowerCase()}">${x.difficulty}</small><button class="hunter-bookmark" onclick="toggleHunterBookmark(${x.id})" title="Save problem">${bookmarks.has(x.id)?'★':'☆'}</button></div>`).join('')||'<p>No problems match this filter.</p>'}</div>`;
}
async function toggleHunterBookmark(id){
 try{const r=await fetch('/api/bookmarks/'+id,{method:'POST',credentials:'same-origin'});if(!r.ok)throw Error('Log in to save problems');await refreshHunterStats();}
 catch(e){alert(e.message)}
}
function hunterShare(){
 if(!hunterProgress)return;
 const p=hunterProgress;const msg=`♛ DSA KING SYSTEM — My Hunter Progress\n${p.solved}/${p.total} curated DSA problems solved\nEasy ${p.by_difficulty.Easy}/${p.totals.Easy} · Medium ${p.by_difficulty.Medium}/${p.totals.Medium} · Hard ${p.by_difficulty.Hard}/${p.totals.Hard}\n${p.xp} verified XP · ${p.streak}-day activity streak`;
 if(navigator.clipboard?.writeText)navigator.clipboard.writeText(msg).then(()=>alert('Progress summary copied!')).catch(()=>prompt('Copy your progress:',msg));else prompt('Copy your progress:',msg);
}
async function renderHunterStats(section){
 const el=document.getElementById('page');if(!el)return;
 if(section==='Progress'){
  if(!hunterProgress){el.innerHTML='<div class="panel"><h3>HUNTER PROGRESS</h3><p>Loading account progress…</p></div>';try{const r=await fetch('/api/progress');if(!r.ok)throw Error('Please sign in to see your saved progress.');hunterProgress=await r.json();}catch(e){el.innerHTML=`<div class="panel"><h3>HUNTER PROGRESS</h3><p>${hpEscape(e.message)}</p></div>`;return;}}
  if(tab!=='Progress')return;
  const p=hunterProgress;const percentage=p.total?Math.round(p.solved/p.total*100):0;
  el.innerHTML=`<div class="hunter-hero"><div><small>◈ VERIFIED HUNTER RECORD</small><h2>YOUR ASCENSION<br><em>IN NUMBERS.</em></h2><p>Accepted submissions are saved to your account. Repeated practice variants do not inflate ranked totals.</p><button class="primary" onclick="hunterShare()">↗ SHARE PROGRESS</button></div><div class="hunter-ring" style="--pct:${percentage}"><div><strong>${p.solved}<small> / ${p.total}</small></strong><span>CURATED SOLVED</span><small>${percentage}% COMPLETE</small></div></div></div>
   <div class="hunter-metrics"><div><small>VERIFIED XP</small><strong>${p.xp}</strong></div><div><small>SUBMISSIONS</small><strong>${p.submissions}</strong></div><div><small>ACTIVE STREAK</small><strong>${p.streak} <span>days</span></strong></div><div><small>COMPLETION</small><strong>${percentage}%</strong></div></div>
   <div class="hunter-two"><div class="panel"><h3>DIFFICULTY BREAKDOWN</h3>${hunterBar('Easy',p.by_difficulty.Easy,p.totals.Easy,'easy')}${hunterBar('Medium',p.by_difficulty.Medium,p.totals.Medium,'medium')}${hunterBar('Hard',p.by_difficulty.Hard,p.totals.Hard,'hard')}</div><div class="panel"><h3>ACTIVITY MATRIX</h3>${hunterHeatmap(p.activity)}<p class="hunter-note">Activity streak counts consecutive calendar days with at least one submission (UTC dates).</p></div></div>
   <div class="panel"><h3>HUNTER ACHIEVEMENTS</h3><div class="hunter-achievements">${[[1,'FIRST BLOOD','Solve your first problem'],[5,'CODE HUNTER','Solve 5 distinct problems'],[10,'ALGORITHM SLAYER','Solve 10 distinct problems']].map(([threshold,name,desc])=>`<div class="hunter-achievement ${p.solved>=threshold?'unlocked':'locked'}"><b>${p.solved>=threshold?'◆':'◇'} ${name}</b><small>${desc}</small></div>`).join('')}<div class="hunter-achievement ${p.by_difficulty.Hard>=1?'unlocked':'locked'}"><b>${p.by_difficulty.Hard>=1?'◆':'◇'} HARD CONQUEROR</b><small>Complete one Hard problem</small></div></div></div><div class="panel"><h3>PROBLEM TRACKER · ${p.total} CURATED CHALLENGES</h3><p>Filter by difficulty or completion. Save problems for later with ☆.</p>${hunterProblemRows(p)}</div>`;
 }else if(section==='Leaderboard'){
  el.innerHTML='<div class="panel"><h3>♛ GLOBAL HUNTER LEADERBOARD</h3><p>Loading rankings…</p></div>';
  try{const r=await fetch('/api/leaderboard');if(!r.ok)throw Error('Please sign in to view rankings.');hunterLeaderboard=await r.json();}catch(e){el.innerHTML=`<div class="panel"><h3>LEADERBOARD</h3><p>${hpEscape(e.message)}</p></div>`;return;}
  if(tab!=='Leaderboard')return;
  const l=hunterLeaderboard;
  el.innerHTML=`<div class="hunter-hero"><div><small>♛ HUNTER RANKINGS</small><h2>CLIMB THE<br><em>LEADERBOARD.</em></h2><p>Ranks are based on verified XP: Easy +50 · Medium +100 · Hard +200, counted once per curated problem.</p></div><div class="hunter-podium"><small>YOUR POSITION</small><strong>${l.your_rank?'#'+l.your_rank:'—'}</strong><span>${l.ranked_total} participating hunters</span></div></div><div class="panel"><h3>TOP 100 HUNTERS</h3><div class="hunter-table-wrap"><table class="hunter-table"><thead><tr><th>RANK</th><th>HUNTER</th><th>SOLVED</th><th>EASY</th><th>MEDIUM</th><th>HARD</th><th>XP</th></tr></thead><tbody>${l.leaderboard.map(x=>`<tr class="${x.is_you?'hunter-you':''}"><td>#${x.rank}</td><td>${hpEscape(x.name)}${x.is_you?' <small>(YOU)</small>':''}</td><td>${x.solved}</td><td class="easy">${x.easy}</td><td class="medium">${x.medium}</td><td class="hard">${x.hard}</td><td><b>${x.xp}</b></td></tr>`).join('')||'<tr><td colspan="7">No accepted submissions yet. Solve a problem to appear here.</td></tr>'}</tbody></table></div><p class="hunter-note">Rankings are shared only among accounts registered on this same server/database. No fabricated users or scores.</p></div>`;
 }
}
