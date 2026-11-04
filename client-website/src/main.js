import { setupDemo } from './demo.js';
import { setupBrief } from './brief.js';
import { siteConfig } from './site-config.js';

document.querySelectorAll('[data-brand]').forEach(node => {
  node.textContent = node.classList.contains('footer-wordmark') || node.closest('.brand') ? siteConfig.wordmark : siteConfig.name;
});
document.title = `${siteConfig.name} — Your game. Seen clearly.`;
document.querySelector('.brand').setAttribute('aria-label', siteConfig.name + ' home');
document.querySelector('.footer-wordmark').setAttribute('aria-label', siteConfig.name);
document.querySelector('#current-year').textContent = String(new Date().getFullYear());
setupDemo();
setupBrief();

const audiences = {
  players: { title: 'A closer look at your game.', body: 'Find an exchange worth revisiting, explore the context around a shot, or follow your matches over time. Choose the depth that feels useful.', status: 'Player experience' },
  coaches: { title: 'A shared starting point for review.', body: 'Relevant clips, event context and defined observations can help frame a useful conversation. Dedicated coach workspaces and athlete permissions are development directions.', status: 'Development direction · coach workflows' },
  venues: { title: 'Make more of the court experience.', body: 'Explore how recorded court video could become a useful service for your players. Venue installations, camera compatibility and commercial workflows need to be assessed together.', status: 'Development direction · venue operations' },
};
document.querySelectorAll('[data-audience]').forEach(button => {
  button.disabled = false;
  button.addEventListener('click', () => {
    const audience = audiences[button.dataset.audience];
    document.querySelector('#audience-subtitle').textContent = audience.title;
    document.querySelector('#audience-body').textContent = audience.body;
    document.querySelector('#audience-status').textContent = audience.status;
    document.querySelectorAll('[data-audience]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  });
});
const domains = {
  badminton: 'Small, fast objects. Continuous movement. Meaningful court geometry. Badminton makes the foundation earn its understanding of the real world.',
  sports: 'Future direction. Other sports may reuse ingestion, event records and evidence infrastructure. Each needs its own models, rules and evaluation before its capabilities can be claimed.',
  workflows: 'Future direction. Visual processes could share the foundation for timelines and inspectable evidence. Industrial or operational use requires independent domain validation, permissions and action policies.',
};
document.querySelectorAll('[data-domain]').forEach(button => {
  button.disabled = false;
  button.addEventListener('click', () => {
    document.querySelector('#domain-description').textContent = domains[button.dataset.domain];
    document.querySelectorAll('[data-domain]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  });
});
let dialogOpener;
document.querySelectorAll('[data-open-dialog]').forEach(button => { button.disabled = false; button.addEventListener('click', () => {
  dialogOpener = button;
  document.getElementById(button.dataset.openDialog).showModal();
}); });
document.querySelectorAll('dialog').forEach(dialog => {
  dialog.querySelectorAll('[data-close-dialog]').forEach(button => button.addEventListener('click', () => dialog.close()));
  dialog.addEventListener('close', () => dialogOpener?.focus({ preventScroll: true }));
  dialog.addEventListener('click', event => { if (event.target === dialog) {
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  } });
});
document.querySelectorAll('.mobile-nav a').forEach(link => link.addEventListener('click', () => { document.querySelector('.mobile-nav').open = false; }));

// Entrances run only on elements already visible in the document. No content is hidden pending JS.
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
if (!reducedMotion.matches && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const element = entry.target;
      element.animate(element.tagName === 'FIGURE' ? [{ opacity: .65 }, { opacity: 1 }] : [{ opacity: .7, transform: 'translateY(14px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 650, easing: 'cubic-bezier(.22,1,.36,1)' });
      observer.unobserve(element);
    });
  }, { threshold: .12 });
  document.querySelectorAll('.story h2,.story-copy,.story-strip figure,.section-intro,.intelligence-heading,.audience-copy,.foundation-principle,.trust-columns article,.conversation-layout>div').forEach(element => observer.observe(element));
}
