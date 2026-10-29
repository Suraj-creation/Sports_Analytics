import { sample, getSummary, getShotMix, getPatterns, getHighlights, metricDefinitions } from './catalogue-data.js';

// Only fixed, authored fixture values enter the HTML templates in this module.
const titleCase=value=>value.charAt(0).toUpperCase()+value.slice(1);
const tableRows=()=>sample.rallies.map(rally=>'<tr><th scope="row">'+rally.id+'</th><td>'+rally.shots.length+'</td><td>'+rally.duration+'s</td><td>'+rally.shots.filter(shot=>shot.type==='unknown').length+'</td></tr>').join('');
export function inspectRally(id) {
  if (!sample.rallies.some(rally=>rally.id===id)) return;
  document.dispatchEvent(new CustomEvent('rally-select',{detail:{id}}));
  const target=document.querySelector('#record-title');
  target.setAttribute('tabindex','-1');target.focus({preventScroll:true});
  document.querySelector('#rally-record').scrollIntoView({behavior:'instant',block:'start'});
}
export function setupCatalogue() {
  const summary=getSummary(), chart=document.querySelector('#catalogue-chart');
  const definition=document.querySelector('#metric-definition'), definitionToggle=document.querySelector('#metric-definition-toggle');
  let category='rallies', selected='R4', currentDefinition='meanShots';
  const recordPanel=document.querySelector('#rally-record');
  function renderRecord(id) {
    const rally=sample.rallies.find(item=>item.id===id);
    if(!rally)return;
    recordPanel.hidden=false;
    recordPanel.innerHTML='<div class="record-heading"><div><span class="data-state">Synthetic source record / '+rally.id+'</span><h4 id="record-title">Rally '+id.slice(1)+' / '+rally.shots.length+' candidate strokes / '+rally.duration+' seconds</h4></div><button class="definition-button" id="close-record" aria-label="Close rally record">Close</button></div><p>This hand-authored event sequence is the evidence behind the sample calculations. It has no associated match footage. The generated scenes above are separate visual studies.</p><ol class="stroke-sequence">'+rally.shots.map((shot,index)=>'<li class="'+(shot.type==='unknown'?'unknown':'')+'"><small>'+String(index+1).padStart(2,'0')+' / '+shot.id+'</small><strong>'+titleCase(shot.type)+'</strong><span>Sample '+shot.player+'</span></li>').join('')+'</ol><p class="record-footer">Scope: official sample rally. Unknown labels retained. Event IDs identify synthetic observations; they are not verified contacts.</p>';
    recordPanel.querySelector('#close-record').addEventListener('click',()=>{
      recordPanel.hidden=true;
      const target=document.querySelector('[data-catalogue="'+category+'"]');target.focus({preventScroll:true});
    });
  }
  document.querySelector('#summary-active').innerHTML=summary.activePlaySeconds+'<span>s</span>';
  document.querySelector('#summary-mean').textContent=summary.meanShots;
  document.querySelector('#summary-classified').innerHTML=summary.classifiedStrokes+'<span>/'+summary.strokeCount+'</span>';
  document.querySelector('#sample-table').innerHTML='<table><caption class="sr-only">Synthetic official rally records. Two warm-up exchanges excluded.</caption><thead><tr><th>Rally</th><th>Candidate strokes</th><th>Duration</th><th>Unknown labels</th></tr></thead><tbody>'+tableRows()+'</tbody></table>';
  function showDefinition(key) {
    currentDefinition=key;
    const extraDefinitions={
      patterns:{title:'Within-rally adjacent pairs',question:'Which candidate label follows another in the sample?',formula:'Sum of (candidate strokes in each rally − 1) = 48 eligible pairs',scope:'Adjacent observations within each of the six official synthetic rallies.',exclusions:'No warm-up exchange or cross-rally pair. Unknown labels remain eligible.',limitation:'The table shows the six most frequent pairs. Labels are candidates; sequence does not establish intent, causality or stroke accuracy.',evidence:sample.rallies.map(rally=>rally.id)},
      highlights:{title:'Sample highlight selection',question:'Which exchanges rank highest under an explicit selection rule?',formula:'Sort by candidate stroke count descending, then duration descending; take the first three',scope:'The six official synthetic rallies. Selected: R4, R6, R2.',exclusions:'The two warm-up exchanges are excluded.',limitation:'This rule selects longer candidate exchanges. It is not a validated excitement, skill or performance score.',evidence:getHighlights().map(rally=>rally.id)},
    };
    const data=metricDefinitions[key]??extraDefinitions[key];
    definition.innerHTML='<div><h4>'+data.title+'</h4><p>'+data.question+'</p><code>'+data.formula+'</code><p><strong>Evidence:</strong> '+data.evidence.join(', ')+'</p></div><div><p><strong>Scope:</strong> '+data.scope+'</p><p><strong>Exclusions:</strong> '+data.exclusions+'</p><p><strong>Limit:</strong> '+data.limitation+'</p></div>';
    definition.hidden=false;definitionToggle.setAttribute('aria-expanded','true');
  }
  function setCopy(state,question,caption) {
    document.querySelector('#catalogue-state').textContent=state;
    document.querySelector('#catalogue-question').textContent=question;
    document.querySelector('#catalogue-caption').textContent=caption;
  }
  function renderRallies() {
    const rally=sample.rallies.find(item=>item.id===selected);
    setCopy('Calculated from sample events','Which exchanges kept going?','Select a rally to inspect its record. Two warm-up exchanges are excluded.');
    chart.innerHTML='<div class="rally-bars" aria-label="Candidate strokes per official rally">'+sample.rallies.map(item=>'<button class="rally-bar" data-rally="'+item.id+'" aria-pressed="'+(item.id===selected)+'" aria-label="'+item.id+': '+item.shots.length+' candidate strokes, '+item.duration+' seconds"><span class="bar-count">'+item.shots.length+'</span><span class="bar-fill" style="height:'+Math.round(item.shots.length/14*160)+'px"></span><span class="bar-label">'+item.id+'</span></button>').join('')+'</div><div class="rally-detail"><div><strong>Rally '+selected.slice(1)+' / '+rally.shots.length+' candidate strokes</strong><p>'+rally.duration+' seconds · '+rally.shots.filter(shot=>shot.type==='unknown').length+' unknown label'+(rally.shots.filter(shot=>shot.type==='unknown').length===1?'':'s')+' retained</p></div><button class="text-link" data-inspect="'+selected+'">Open rally record ↗</button></div>';
    currentDefinition='meanShots';
  }
  function render() {
    definition.hidden=true;definitionToggle.setAttribute('aria-expanded','false');
    definitionToggle.hidden=category==='movement'||category==='progress';
    if(category==='rallies') renderRallies();
    if(category==='shots') {
      setCopy('Candidate classifications','What shapes the exchange?','All 54 candidates stay in the denominator. Names are illustrative labels; unknown does not mean no stroke occurred.');
      chart.innerHTML='<div class="shot-bars">'+getShotMix().map(shot=>'<div class="shot-row '+shot.type+'"><span>'+shot.label+'</span><span class="shot-track"><span style="width:'+shot.share*100+'%"></span></span><strong>'+shot.count+'</strong><small>'+Math.round(shot.share*100)+'%</small></div>').join('')+'</div>';
      currentDefinition='classificationCoverage';
    }
    if(category==='movement') {
      setCopy('Illustrative concept / not measured','Where does the play take you?','A qualitative movement study. No distance, speed, balance score or technique grade is inferred from this diagram.');
      chart.innerHTML='<div class="movement-study"><svg viewBox="0 0 180 330" role="img" aria-label="Illustrative badminton court movement with a visible gap"><g class="court-lines"><path d="M24 15h132v290H24zM34 15v290M146 15v290M24 160h132M24 117h132M24 203h132M24 31h132M24 289h132M90 15v102M90 203v102"/></g><path class="court-trail" d="M120 267Q144 233 108 215T65 240M85 251Q108 248 102 210T121 196"/><circle class="court-point" cx="121" cy="196" r="5"/></svg><div><h4>Position. Recovery.<br>Gaps in the view.</h4><p>A future movement view should preserve tracking gaps and distinguish image positions from calibrated court coordinates.</p><ul><li>Suitable court view and calibration</li><li>Temporal player tracking</li><li>Occlusion and identity review</li></ul></div></div>';
    }
    if(category==='patterns') {
      setCopy('Calculated within each sample rally','What tends to come next?','48 adjacent pairs across six rallies. No pair crosses a rally boundary. Associations do not establish tactics, intent or causality.');
      chart.innerHTML='<table class="pattern-table"><thead><tr><th>Observed sequence</th><th>Count / 48</th><th>Evidence</th></tr></thead><tbody>'+getPatterns().slice(0,6).map(pair=>'<tr><td>'+titleCase(pair.from)+' → '+titleCase(pair.to)+'</td><td>'+pair.count+'</td><td>'+pair.evidence.map(id=>'<button data-inspect="'+id+'">'+id+'</button>').join(' · ')+'</td></tr>').join('')+'</tbody></table>';
      currentDefinition='patterns';
    }
    if(category==='highlights') {
      setCopy('Transparent selection rule','What is worth another look?','Ranked by candidate stroke count, then duration. These are sample selections, not a skill or match-quality score.');
      chart.innerHTML='<div class="highlight-list">'+getHighlights().map((item,index)=>'<article class="highlight-item"><span>0'+(index+1)+'</span><div><strong>Rally '+item.id.slice(1)+'</strong><p>'+item.shots+' candidate strokes · '+item.duration+' seconds</p></div><button class="text-link" data-inspect="'+item.id+'">Inspect ↗</button></article>').join('')+'</div>';
      currentDefinition='highlights';
    }
    if(category==='progress') {
      setCopy('Planned / requires comparable sessions','What changes over time?','There is one synthetic record here. A trend would require multiple eligible sessions and a stable definition of what is being compared.');
      chart.innerHTML='<div class="planned-state"><div class="planned-symbol" aria-hidden="true">↗</div><h4>A meaningful comparison starts<br>before the chart.</h4><p>Progress needs more than a rising line. The same player, suitable footage and comparable definitions must come first.</p><ul><li>Consistent identity across eligible sessions</li><li>Comparable calibration and recording conditions</li><li>Versioned metrics and uncertainty</li></ul></div>';
    }
    bindChart();
  }
  function bindChart() {
    chart.querySelectorAll('[data-inspect]').forEach(button=>button.onclick=()=>inspectRally(button.dataset.inspect));
    chart.querySelectorAll('[data-rally]').forEach(button=>button.onclick=()=>{selected=button.dataset.rally;renderRallies();bindChart();chart.querySelector('[data-rally="'+selected+'"]').focus({preventScroll:true});});
  }
  document.querySelectorAll('[data-catalogue]').forEach(button=>{
    button.disabled=false;
    button.addEventListener('click',()=>{category=button.dataset.catalogue;document.querySelectorAll('[data-catalogue]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));render();});
  });
  document.querySelectorAll('[data-definition]').forEach(button=>{button.disabled=false;button.addEventListener('click',()=>showDefinition(button.dataset.definition));});
  definitionToggle.disabled=false;
  definitionToggle.addEventListener('click',()=>{if(definition.hidden)showDefinition(currentDefinition);else{definition.hidden=true;definitionToggle.setAttribute('aria-expanded','false');}});
  document.addEventListener('rally-select',event=>{selected=event.detail.id;if(category==='rallies'){renderRallies();bindChart();}renderRecord(selected);});
  render();
}
