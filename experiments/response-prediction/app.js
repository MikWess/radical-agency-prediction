'use strict';
const $ = id => document.getElementById(id);
const legacyKey = 'radical-agency.response-prediction.v1';
const draftKey = 'radical-agency.response-prediction.draft.v2';
let token, state, current, busy = false;
const scoreButtons = [...document.querySelectorAll('[data-score]')];
function status(message) { $('status').textContent = message; }
async function api(path, body) {
  const response = await fetch(`/api/${path}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: {'Content-Type': 'application/json', ...(token ? {'X-Lab-Token': token} : {})},
    ...(body === undefined ? {} : {body: JSON.stringify(body)})
  });
  let data;
  try { data = await response.json(); } catch { throw Error('The prediction server is not connected. Start the local server, then reconnect.'); }
  if (!response.ok) throw Error(data.error || 'Request failed. Please retry.');
  return data;
}
function setBusy(value) {
  busy = value;
  $('start').disabled = value || !token;
  $('reveal').disabled = value;
  $('retry').disabled = value;
  $('answerText').disabled = value;
  $('context').disabled = value;
  scoreButtons.forEach(button => { button.disabled = value; });
}
function saveDraft() {
  if (!current || current.answer !== null) return;
  try { localStorage.setItem(draftKey, JSON.stringify({id: current.id, answer: $('answerText').value, context: $('context').value})); }
  catch { status('Draft backup is unavailable. Keep this page open until you save your answer.'); }
}
function clearDraft() { try { localStorage.removeItem(draftKey); } catch {} }
function showRun(run) {
  current = run;
  const revealed = run.answer !== null;
  $('question').textContent = run.question.text;
  $('examples').textContent = `${run.exampleCount} earlier examples used`;
  $('phase').textContent = revealed ? 'Prediction revealed' : 'Prediction locked · Your turn';
  $('explanation').textContent = `${revealed ? 'Your answer is now an example for future predictions.' : 'Its prediction is already saved. Answer without seeing it, then reveal.'}${run.repeatedQuestion ? ' Repeated question: earlier answers to this exact question were excluded.' : ''}`;
  $('answerForm').hidden = revealed;
  $('comparison').hidden = !revealed;
  $('start').hidden = !revealed;
  if (revealed) {
    $('actual').textContent = run.answer;
    $('predicted').textContent = run.prediction;
    $('timing').textContent = `Predicted at ${new Date(run.predictedAt).toLocaleTimeString()} · Answer saved at ${new Date(run.answeredAt).toLocaleTimeString()} · ${run.generationSeconds}s to predict`;
    $('start').textContent = 'Try the next question';
    scoreButtons.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.score) === run.score)));
  } else {
    $('answerText').value = ''; $('context').value = '';
    try { const draft = JSON.parse(localStorage.getItem(draftKey) || 'null'); if (draft?.id === run.id) { $('answerText').value = draft.answer; $('context').value = draft.context; } } catch {}
  }
}
function renderHistory() {
  $('count').textContent = `${state.exampleCount} answers in your notebook`;
  $('reviewCount').textContent = `(${state.history.length})`;
  $('export').disabled = state.exampleCount === 0 && state.history.length === 0;
  $('history').replaceChildren();
  const rated = state.history.filter(r => r.score !== null);
  $('progress').textContent = rated.length ? `${rated.length} predictions rated · Average main-point score ${(rated.reduce((sum, r) => sum + r.score, 0) / rated.length).toFixed(2)} / 2. This is your rating, not an objective accuracy percentage.` : 'Your completed predictions will appear here. Rate their main point to track the experiment.';
  for (const run of [...state.history].reverse()) {
    const article = document.createElement('article');
    const heading = document.createElement('h3'); heading.textContent = run.question.text;
    const meta = document.createElement('small'); meta.textContent = `${new Date(run.answeredAt).toLocaleString()} · ${run.exampleCount} examples · ${run.score === null ? 'Not rated' : `Score ${run.score}/2`}${run.repeatedQuestion ? ' · Repeated question' : ''}`;
    const actual = document.createElement('p'); actual.textContent = `You: ${run.answer}`;
    const predicted = document.createElement('p'); predicted.textContent = `Model: ${run.prediction}`;
    article.append(heading, meta, actual, predicted); $('history').append(article);
  }
}
async function refresh() { state = await api('state'); token = state.token; renderHistory(); }
async function connect() {
  setBusy(true); $('retry').hidden = true; status('Connecting to the local model server…');
  try {
    await refresh();
    let warning = '';
    try {
      const raw = localStorage.getItem(legacyKey);
      if (raw) { await api('import', {records: JSON.parse(raw)}); await refresh(); }
    } catch { warning = ' Earlier browser answers could not be imported; their original copy is untouched.'; }
    if (state.active) showRun(state.active);
    else if (state.history.length) showRun(state.history[state.history.length - 1]);
    else { $('phase').textContent = 'Ready · Local Qwen3 4B'; $('examples').textContent = `${state.exampleCount} earlier answers available`; }
    status(`Connected. ${state.active ? 'Your hidden prediction is ready.' : 'Start whenever you’re ready. The first prediction may take longer while the model loads.'}${warning}`);
  } catch (error) { status(error.message); $('retry').hidden = false; }
  finally { setBusy(false); }
}
$('start').addEventListener('click', async () => {
  if (busy) return;
  setBusy(true); $('phase').textContent = 'Preparing a hidden prediction';
  status('The model is making its guess using only earlier answers. First use loads the model; keep this page open.');
  try { const run = await api('start', {}); showRun(run); status('Prediction saved and hidden. Your turn.'); }
  catch (error) { status(error.message); $('phase').textContent = 'Prediction not ready · Retry'; }
  finally { setBusy(false); if (current?.answer === null) $('answerText').focus(); }
});
$('reveal').addEventListener('click', async () => {
  if (busy || !current) return;
  const answer = $('answerText').value.trim();
  if (!answer) { status('Add your answer before revealing its prediction.'); $('answerText').focus(); return; }
  saveDraft(); setBusy(true);
  try {
    const run = await api('answer', {id: current.id, answer, context: $('context').value.trim()});
    clearDraft(); showRun(run); status('Your answer is saved. Here is the prediction made before you answered.');
    try { await refresh(); } catch { status('Answer saved and revealed. History refresh failed; reconnect to update it.'); }
  } catch (error) { status(error.message); }
  finally { setBusy(false); }
});
scoreButtons.forEach(button => button.addEventListener('click', async () => {
  if (busy || !current) return;
  setBusy(true);
  try { const run = await api('score', {id: current.id, score: Number(button.dataset.score)}); showRun(run); await refresh(); status('Rating saved. Try another question to give it one more example.'); }
  catch (error) { status(error.message); }
  finally { setBusy(false); }
}));
$('export').addEventListener('click', async () => {
  try {
    const data = await api('export');
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));
    const link = document.createElement('a'); link.href = url; link.download = `radical-agency-experiment-${new Date().toISOString().slice(0, 10)}.json`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000); status('Export requested. It includes your personal answers and completed predictions; keep it private.');
  } catch (error) { status(error.message); }
});
$('retry').addEventListener('click', connect);
$('answerText').addEventListener('input', saveDraft);
$('context').addEventListener('input', saveDraft);
window.addEventListener('beforeunload', event => { if (current?.answer === null && ($('answerText').value.trim() || $('context').value.trim())) { event.preventDefault(); event.returnValue = ''; } });
connect();
