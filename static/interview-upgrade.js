/* AI Mock Interview: dynamically varied questions, real Groq evaluation, no fake scores. */
let hunterInterviewQuestion=null;
let hunterInterviewDifficulty='Any';
let hunterInterviewBusy=false;
const interviewOldRender=render;
render=function(){interviewOldRender();if(tab==='Interviews')hunterInterviewUpgrade();};
function hunterInterviewUpgrade(){
 const root=document.querySelector('#interview');if(!root)return;
 root.innerHTML=`<div class="hunter-interview-panel"><div class="hunter-interview-toolbar"><label>Difficulty <select id="hunter-interview-difficulty"><option>Any</option><option>Easy</option><option>Medium</option><option>Hard</option></select></label><button class="primary" onclick="startInterview()">NEW RANDOM QUESTION ↻</button></div><p class="hunter-interview-note">Question-bank variations across algorithms and difficulty levels. AI feedback requires Groq. Questions can repeat; this is not an infinite set of unique curated questions.</p><div id="hunter-interview-workspace"><p>Choose a difficulty and start a mock interview.</p></div></div>`;
 document.querySelector('#hunter-interview-difficulty').value=hunterInterviewDifficulty;
}
async function startInterview(){
 if(hunterInterviewBusy)return;
 const sel=document.querySelector('#hunter-interview-difficulty');
 if(sel)hunterInterviewDifficulty=sel.value;
 const workspace=document.querySelector('#hunter-interview-workspace');if(!workspace)return;
 workspace.innerHTML='<p>Preparing a new interview question…</p>';
 try{
  const res=await fetch('/api/interview/question?difficulty='+encodeURIComponent(hunterInterviewDifficulty)+'&seed='+String(Math.floor(Math.random()*Number.MAX_SAFE_INTEGER)));
  const data=await res.json();if(!res.ok)throw new Error(data.error||'Could not load question');
  hunterInterviewQuestion=data;
  workspace.innerHTML=`<div class="hunter-interview-question"><small>${escapeHTML(data.difficulty)} · ${escapeHTML(data.topic)} · ${escapeHTML(data.title)}</small><h3>${escapeHTML(data.question)}</h3><p>${escapeHTML(data.context)}</p></div><label for="hunter-interview-answer">Your explanation</label><textarea id="hunter-interview-answer" class="textarea" placeholder="Explain your approach, edge cases, correctness and complexity…" rows="7"></textarea><div class="hunter-interview-actions"><button class="primary" id="hunter-interview-evaluate" onclick="finishInterview()">EVALUATE WITH AI →</button><button class="hunter-skip-btn" onclick="startInterview()">SKIP / NEXT QUESTION ↻</button></div><div id="hunter-interview-feedback" aria-live="polite"></div>`;
 }catch(e){workspace.innerHTML='<p class="innovation-error">'+escapeHTML(e.message)+'</p>';}
}
async function finishInterview(){
 if(hunterInterviewBusy||!hunterInterviewQuestion)return;
 const answer=document.querySelector('#hunter-interview-answer')?.value.trim();
 if(!answer){alert('Please explain your approach first.');return;}
 const button=document.querySelector('#hunter-interview-evaluate');
 const box=document.querySelector('#hunter-interview-feedback');
 hunterInterviewBusy=true;button.disabled=true;button.textContent='AI IS EVALUATING…';box.innerHTML='<p>Evaluating your reasoning…</p>';
 try{
  const res=await fetch('/api/interview/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:hunterInterviewQuestion.id,difficulty:hunterInterviewQuestion.difficulty,answer})});
  const data=await res.json();if(!res.ok)throw new Error(data.error||'AI evaluation failed');
  const score=Number(data.score)||0;
  const percentage=Math.max(0,Math.min(100,score*10));
  const verdict=percentage<25?'INCORRECT — NEEDS IMPROVEMENT':percentage<30?'ALMOST THERE — KEEP IMPROVING':percentage<70?'CORRECT — KEEP IMPROVING':'CORRECT — STRONG ANSWER';
  const verdictClass=percentage<25?'incorrect':percentage<30?'partial':'correct';
  const items=(xs)=>'<ul>'+(xs||[]).map(x=>'<li>'+escapeHTML(x)+'</li>').join('')+'</ul>';
  box.innerHTML=`<div class="hunter-interview-result"><div class="hunter-interview-verdict ${verdictClass}">${verdict} · ${percentage}% (${score}/10)</div><p>${percentage<25?"Your answer needs substantial improvement. Study the areas below and try again.":percentage<30?"You are close to the 30% passing threshold. Improve the missing concepts below.":"Green signal: your answer meets the 30% threshold. This is a minimum pass, not a perfect answer—review the improvements below."}</p><h4>Strengths</h4>${items(data.strengths)}<h4>Improvements</h4>${items(data.improvements)}<h4>Model explanation</h4><p>${escapeHTML(data.model_answer)}</p><h4>Follow-up question</h4><p>${escapeHTML(data.follow_up)}</p><small>AI feedback can be imperfect. Check important technical claims.</small></div>`;
  state.interviews=state.interviews||[];
  state.interviews.unshift({verdict,question:hunterInterviewQuestion.question,answer,score:data.score,percentage,at:new Date().toLocaleString(),feedback:(data.improvements||[]).join(' | ')});
  state.interviews=state.interviews.slice(0,100);save();
  button.textContent='EVALUATED ✓';
 }catch(e){box.innerHTML='<p class="innovation-error">'+escapeHTML(e.message)+'</p>';button.disabled=false;button.textContent='RETRY AI EVALUATION';}
 finally{hunterInterviewBusy=false;}
}
