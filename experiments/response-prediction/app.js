'use strict';
const questions = [
 ['preferences','What is a small thing that makes a day better?'],
 ['work','When you have a new idea, what do you usually do first?'],
 ['preferences','What makes a conversation interesting to you?'],
 ['decisions','How do you decide what to work on when several things feel important?'],
 ['learning','What do you do first when you don’t understand something?'],
 ['daily life','What do you like doing when you have an unexpected free hour?'],
 ['work','What part of starting a project do you enjoy most?'],
 ['preferences','What makes advice useful to you?'],
 ['decisions','When do you ask someone else for help?'],
 ['learning','What is something you wish school did differently?'],
 ['daily life','What usually helps you get unstuck?'],
 ['work','What makes you lose interest in a project?'],
 ['preferences','What kind of feedback do you prefer?'],
 ['decisions','How do you know when something is good enough to share?'],
 ['daily life','What is one thing you would change about your usual morning?'],
 ['learning','What makes you want to learn a new skill?'],
 ['preferences','What do you notice first when you try a new app?'],
 ['work','What makes working with another person go well?'],
 ['decisions','What do you do when you realize you were wrong?'],
 ['daily life','What would make tomorrow feel like a good day?']
].map(([category,text],i)=>({id:`starter-${String(i+1).padStart(2,'0')}`,category,text}));
const key='radical-agency.response-prediction.v1';
const $=id=>document.getElementById(id);
let records=[], index=0, storageReady=true;
try { const raw=localStorage.getItem(key); if(raw){ const parsed=JSON.parse(raw); if(!Array.isArray(parsed)||!parsed.every(r=>r&&typeof r.answer==='string'&&typeof r.question==='string'&&typeof r.questionId==='string'&&typeof r.savedAt==='string'))throw Error('Invalid saved data'); records=parsed; } } catch { storageReady=false; }
function render(){
 const q=questions[index]; $('question').textContent=q.text; $('category').textContent=q.category; $('position').textContent=`Question ${index+1} of ${questions.length}`;
 $('count').textContent=`${records.length} answers saved`; $('reviewCount').textContent=`(${records.length})`; $('history').replaceChildren();
 for(const r of [...records].reverse()) {const article=document.createElement('article');const heading=document.createElement('h3');heading.textContent=r.question;const answer=document.createElement('p');answer.textContent=r.answer;const meta=document.createElement('small');meta.textContent=`${new Date(r.savedAt).toLocaleString()}${r.context ? ' · '+r.context : ''}`;article.append(heading,answer,meta);$('history').append(article);}
 $('export').disabled=records.length===0; $('save').disabled=!storageReady;
}
function advance(){index=(index+1)%questions.length;$('answerText').value='';$('context').value='';render();$('answerText').focus();}
$('save').addEventListener('click',()=>{
 const answer=$('answerText').value.trim();if(!answer){$('status').textContent='Add an answer before saving.';$('answerText').focus();return;}
 const q=questions[index]; const record={questionId:q.id,question:q.text,category:q.category,answer,context:$('context').value.trim(),savedAt:new Date().toISOString(),purpose:'example',deckVersion:1};
 const next=[...records,record];try{localStorage.setItem(key,JSON.stringify(next));}catch{$('status').textContent='Could not save. Your draft is still here; copy it somewhere safe and export earlier answers.';return;}
 records=next;advance();$('status').textContent='Saved in this browser. Ready for your next thought.';
});
$('skip').addEventListener('click',()=>{if(($('answerText').value.trim()||$('context').value.trim())&&!confirm('Discard this unsaved draft and skip?'))return;advance();$('status').textContent='Skipped. No answer saved.';});
$('export').addEventListener('click',()=>{const payload={schemaVersion:1,experiment:'response-prediction',exportedAt:new Date().toISOString(),records};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download=`radical-agency-answers-${new Date().toISOString().slice(0,10)}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('status').textContent='Export requested. Keep the downloaded file private; it contains your answers.';});
window.addEventListener('beforeunload',event=>{if($('answerText').value.trim()||$('context').value.trim()){event.preventDefault();event.returnValue='';}});
const unanswered=questions.findIndex(q=>!records.some(r=>r.questionId===q.id));index=unanswered<0?0:unanswered;render();
if(!storageReady)$('status').textContent='Browser storage is unavailable or saved data could not be read. Saving is disabled to protect existing data. You can still read the plan and questions.';
