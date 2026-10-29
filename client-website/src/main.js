import { setupVision } from './vision.js';
import { setupCatalogue } from './catalogue.js';
import { setupInvestigation } from './investigation.js';
import { setupBrief } from './brief.js';

setupVision();
setupCatalogue();
setupInvestigation();
setupBrief();
document.querySelector('#current-year').textContent=new Date().getFullYear();

const intents={
  relive:'Find the exchange worth watching again, with the surrounding play still in view.',
  discover:'Explore candidate strokes and rally patterns. Follow a question back to the moments that support it.',
  improve:'Bring a clearer question into your next session. Review context with a coach before drawing a conclusion.',
};
document.querySelectorAll('[data-intent]').forEach(button=>{
  button.disabled=false;
  button.addEventListener('click',()=>{
    document.querySelectorAll('[data-intent]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    document.querySelector('#intent-description').textContent=intents[button.dataset.intent];
  });
});
const domains={
  badminton:['Badminton provides the first concrete language: courts, exchanges, candidate strokes, rally boundaries and match context.','Each observation still needs suitable footage, explicit scope and reviewable evidence.'],
  sports:['Other sports could build on a shared video-to-evidence foundation, with their own language for players, space, actions and events.','Future domain packs require sport-specific definitions, tracking, rules, tools and evaluation. They are not currently promised capabilities.'],
  workflows:['The broader architectural direction is reasoning over recorded activity: connect observations, temporal events, explicit calculations and inspectable answers.','Beyond-sport uses require dedicated domain design, permissions, validation and appropriate human review. This is a direction for future work.'],
};
document.querySelectorAll('[data-domain]').forEach(button=>{
  button.disabled=false;button.addEventListener('click',()=>{
    document.querySelectorAll('[data-domain]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
    const [text,note]=domains[button.dataset.domain], target=document.querySelector('#domain-description'), span=document.createElement('span');
    target.textContent=text;span.textContent=note;target.append(span);
  });
});
document.querySelectorAll('[data-toggle-notes]').forEach(button=>{
  button.disabled=false;button.addEventListener('click',()=>{const target=document.getElementById(button.dataset.toggleNotes);target.hidden=!target.hidden;button.setAttribute('aria-expanded',String(!target.hidden));});
});
document.querySelectorAll('.mobile-nav a').forEach(link=>link.addEventListener('click',()=>document.querySelector('.mobile-nav').open=false));

const film=document.querySelector('#tracking-film'), status=document.querySelector('#film-status');
film.muted=true;
const calmMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
if(calmMotion.matches){film.removeAttribute('autoplay');film.removeAttribute('loop');film.controls=true;film.pause();status.textContent='17-second supplied reference · Use the player controls to play.';}
else if('IntersectionObserver' in window)new IntersectionObserver(([entry])=>{if(entry.isIntersecting)film.play().catch(()=>{});else film.pause();},{threshold:.15}).observe(film);
else film.play().catch(()=>{});
document.querySelectorAll('[data-film-time]').forEach(button=>{
  button.disabled=false;button.addEventListener('click',()=>{
    const t=Number(button.dataset.filmTime);
    film.currentTime=Math.min(t,Math.max(0,(film.duration||t+1)-0.1));
    if(!calmMotion.matches)film.play().catch(()=>{});
  });
});
film.addEventListener('error',()=>{status.textContent='The reference video could not be loaded. The poster and context remain available.';document.querySelectorAll('[data-film-time]').forEach(button=>button.disabled=true);});

// One brief, nonessential entrance per large heading; content is visible by default.
const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
if(!reduceMotion.matches&&'IntersectionObserver' in window) {
  const observer=new IntersectionObserver(entries=>{
    for(const entry of entries)if(entry.isIntersecting){
      if(!reduceMotion.matches)entry.target.animate([{opacity:0.65,transform:'translateY(12px)'},{opacity:1,transform:'translateY(0)'}],{duration:360,easing:'cubic-bezier(.22,1,.36,1)'});
      observer.unobserve(entry.target);
    }
  },{threshold:0.25});
  document.querySelectorAll('.section-heading h2,.human-copy h2,.principles h2').forEach(heading=>observer.observe(heading));
  reduceMotion.addEventListener('change',event=>{if(event.matches){observer.disconnect();document.getAnimations().forEach(animation=>animation.cancel());}},{once:true});
}
