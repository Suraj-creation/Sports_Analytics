import { getAnswer, getPhase, phaseCount } from './demo-data.js';

export function setupDemo() {
  const image = document.querySelector('#phase-image');
  const overlay = document.querySelector('#movement-overlay');
  const lineGroup = document.querySelector('#pose-lines');
  const pointGroup = document.querySelector('#pose-points');
  const phaseButtons = [...document.querySelectorAll('[data-phase]')];
  const layerButtons = [...document.querySelectorAll('[data-layer]')];
  const questionButtons = [...document.querySelectorAll('[data-question]')];
  const citation = document.querySelector('#evidence-citation');
  const svgNamespace = 'http://www.w3.org/2000/svg';
  let selectedPhase = 0;
  let layer = 'source';

  function drawPose(phase) {
    lineGroup.replaceChildren(...phase.chains.map(chain => {
      const line = document.createElementNS(svgNamespace, 'polyline');
      line.setAttribute('points', chain.map(index => phase.points[index].join(',')).join(' '));
      return line;
    }));
    pointGroup.replaceChildren(...phase.points.map(([x, y]) => {
      const point = document.createElementNS(svgNamespace, 'circle');
      point.setAttribute('cx', x); point.setAttribute('cy', y); point.setAttribute('r', '6');
      return point;
    }));
    document.querySelector('#movement-trail').setAttribute('d', phase.trail);
    const marker = document.querySelector('#court-marker');
    marker.setAttribute('cx', phase.marker[0]); marker.setAttribute('cy', phase.marker[1]);
  }
  function showAnswer(id) {
    const answer = getAnswer(id);
    document.querySelector('#answer-status').textContent = answer.status;
    document.querySelector('#answer-title').textContent = answer.title;
    document.querySelector('#answer-body').textContent = answer.body;
    citation.hidden = answer.phase === null;
    citation.dataset.citation = answer.phase === null ? '' : String(answer.phase);
    citation.replaceChildren(document.createTextNode(answer.citation + ' '));
    if (answer.phase !== null) {
      const arrow = document.createElement('span'); arrow.setAttribute('aria-hidden', 'true'); arrow.textContent = '↗'; citation.append(arrow);
    }
    questionButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.question === id)));
  }
  function showPhase(index, updateAnswer = true) {
    const phase = getPhase(index);
    selectedPhase = index;
    image.src = phase.image; image.alt = phase.alt;
    document.querySelector('#phase-label').textContent = phase.title;
    phaseButtons.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.phase) === index)));
    drawPose(phase);
    if (updateAnswer) showAnswer(phase.question);
  }
  function showLayer(nextLayer) {
    layer = nextLayer;
    overlay.toggleAttribute('hidden', layer !== 'movement');
    layerButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.layer === layer)));
    document.querySelector('#layer-description').textContent = layer === 'movement' ? 'Illustrated pose and path, not inferred measurements' : 'Original illustration, without annotations';
  }
  phaseButtons.forEach(button => button.addEventListener('click', () => showPhase(Number(button.dataset.phase))));
  layerButtons.forEach(button => button.addEventListener('click', () => showLayer(button.dataset.layer)));
  questionButtons.forEach(button => button.addEventListener('click', () => {
    const id = button.dataset.question;
    const answer = getAnswer(id);
    if (answer.phase !== null) showPhase(answer.phase, false);
    showAnswer(id);
  }));
  citation.addEventListener('click', () => {
    if (citation.hidden || citation.dataset.citation === '') return;
    showPhase(Number(citation.dataset.citation)); showLayer('source');
    document.querySelector('.demo-view').scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    phaseButtons[selectedPhase].focus({ preventScroll: true });
  });
  document.querySelector('.phase-selector').addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const index = event.key === 'Home' ? 0 : event.key === 'End' ? phaseCount - 1 : (selectedPhase + (event.key === 'ArrowRight' ? 1 : -1) + phaseCount) % phaseCount;
    showPhase(index); phaseButtons[index].focus();
  });
  [...phaseButtons, ...layerButtons, ...questionButtons, citation].forEach(button => { button.disabled = false; });
  showPhase(0);
}
