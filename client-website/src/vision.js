import { poseData } from './pose-data.js';

export const poseThreshold = 0.35;
export const poseEdges = [[0,1],[0,2],[1,3],[2,4],[5,6],[5,7],[7,9],[6,8],[8,10],[5,11],[6,12],[11,12],[11,13],[13,15],[12,14],[14,16]];
export function visiblePose(scene) {
  const record = poseData[scene];
  if (!record) return { points: [], edges: [] };
  const points = record.keypoints.map(([x,y,confidence],id) => ({x,y,confidence,id})).filter(point => point.confidence >= poseThreshold);
  const ids = new Set(points.map(point => point.id));
  return { points, edges: poseEdges.filter(([a,b]) => ids.has(a) && ids.has(b)) };
}

const descriptions = {
  source: ['Source scene', 'Start with what is visible.', 'A generated scene provides a controlled visual study. It is separate from the synthetic rally record.', 'No derived layer. Watch the body position, racket and surroundings in their original image context.'],
  pose: ['Estimated observation', 'A position. With context.', 'Look beyond the contact. An estimated shoulder, hip or ankle position is a starting point for review.', 'Estimated landmarks locate joints in this image. They do not measure physical speed or technique quality.'],
  movement: ['Illustrative concept', 'Follow the recovery.', 'A movement trail can reveal changes in position. This example is hand-authored to explain the idea.', 'The dotted path is illustrative. It is not tracked movement, calibrated distance or a physical speed measurement.'],
  events: ['Illustrative concept', 'A moment becomes an event.', 'Contact candidates need temporal evidence, context and review before they become reliable match events.', 'A still image cannot validate a contact. This label demonstrates how a candidate event could stay tied to its source.'],
};
const scenes = {
  net: { src:'./assets/net-recovery.webp', alt:'A player stretches low toward the net, seen from beside the court.', title:'Net recovery', path:'M1260 920Q1180 820 1050 840T790 865', end:[790,865] },
  overhead: { src:'./assets/contact.webp', alt:'A badminton player prepares an overhead shot.', title:'Overhead preparation', path:'M1310 850Q1170 840 1120 780T1200 730', end:[1200,730] },
};
const namespace = 'http://www.w3.org/2000/svg';
function drawPose(svg, scene) {
  const record=poseData[scene], visible=visiblePose(scene);
  svg.replaceChildren();
  svg.setAttribute('viewBox', '0 0 '+record.width+' '+record.height);
  for (const [a,b] of visible.edges) {
    const line=document.createElementNS(namespace,'line');
    const [x1,y1]=record.keypoints[a], [x2,y2]=record.keypoints[b];
    for (const [key,value] of Object.entries({x1,y1,x2,y2})) line.setAttribute(key,value);
    svg.append(line);
  }
  for (const {x,y} of visible.points) {
    const point=document.createElementNS(namespace,'circle');
    point.setAttribute('cx',x); point.setAttribute('cy',y); point.setAttribute('r',5.5);
    svg.append(point);
  }
  return visible.points.length;
}
export function setupVision() {
  const hero=document.querySelector('.hero-stage');
  const heroSvg=hero.querySelector('.pose-svg');
  document.querySelector('#hero-landmark-count').textContent=drawPose(heroSvg,'net');
  const heroToggle=document.querySelector('#hero-pose-toggle');
  heroToggle.disabled=false;
  heroToggle.addEventListener('click',()=>{
    const enabled=heroToggle.getAttribute('aria-pressed')!=='true';
    heroToggle.setAttribute('aria-pressed',String(enabled));
    heroSvg.toggleAttribute('hidden',!enabled);
    heroToggle.lastElementChild.textContent='Pose layer '+(enabled?'on':'off');
  });
  const stage=document.querySelector('.explorer-stage'), image=document.querySelector('#explorer-image');
  const svg=stage.querySelector('.pose-svg'), movement=document.querySelector('#movement-layer'), event=document.querySelector('#event-layer');
  let scene='overhead', layer='pose';
  function render() {
    const record=poseData[scene], current=scenes[scene], description=descriptions[layer];
    image.src=current.src; image.alt=current.alt; image.width=record.width; image.height=record.height;
    stage.dataset.scene=scene;
    const count=drawPose(svg,scene);
    svg.toggleAttribute('hidden',layer!=='pose');
    movement.toggleAttribute('hidden',layer!=='movement');
    movement.setAttribute('viewBox','0 0 '+record.width+' '+record.height);
    movement.querySelector('path').setAttribute('d',current.path);
    movement.querySelector('circle').setAttribute('cx',current.end[0]);
    movement.querySelector('circle').setAttribute('cy',current.end[1]);
    event.hidden=layer!=='events';
    document.querySelector('#landmark-readout').textContent=layer==='pose'?count+' / 17 landmarks visible':layer==='source'?'Original generated image':'Illustrative '+layer+' layer';
    document.querySelector('#observation-status').textContent=description[0];
    document.querySelector('#observation-heading').textContent=description[1];
    document.querySelector('#observation-body').textContent=description[2];
    document.querySelector('#layer-explanation').textContent=description[3];
    document.querySelector('#observation-source').textContent=current.title;
    document.querySelectorAll('[data-scene-select]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.sceneSelect===scene)));
    document.querySelectorAll('[data-evidence-layer]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.evidenceLayer===layer)));
  }
  document.querySelectorAll('[data-scene-select]').forEach(button=>{
    button.disabled=false; button.addEventListener('click',()=>{scene=button.dataset.sceneSelect;render();});
  });
  document.querySelectorAll('[data-evidence-layer]').forEach(button=>{
    button.disabled=false; button.addEventListener('click',()=>{layer=button.dataset.evidenceLayer;render();});
  });
  const inspect=document.querySelector('#inspect-source');
  inspect.disabled=false;inspect.addEventListener('click',()=>{layer='source';render();});
  render();
}
