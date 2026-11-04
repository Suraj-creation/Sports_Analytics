import { buildBrief } from './brief-model.js';
import { siteConfig } from './site-config.js';

export function setupBrief() {
  const form = document.querySelector('#brief-form');
  const result = document.querySelector('#brief-result');
  const output = document.querySelector('#brief-output');
  const feedback = document.querySelector('#brief-feedback');
  const error = document.querySelector('#brief-error');
  const emailLink = document.querySelector('#email-brief');
  form.addEventListener('submit', event => {
    event.preventDefault(); error.hidden = true; feedback.textContent = '';
    try {
      const data = new FormData(form);
      output.value = buildBrief({ role: data.get('role'), source: data.get('source'), goal: data.get('goal') }, siteConfig.name);
      form.hidden = true; result.hidden = false;
      if (/^[^\s@?]+@[^\s@?]+\.[^\s@?]+$/.test(siteConfig.contactEmail)) {
        emailLink.href = `mailto:${siteConfig.contactEmail}?subject=${encodeURIComponent(siteConfig.name + ' demo discussion')}&body=${encodeURIComponent(output.value)}`;
        emailLink.hidden = false;
      }
      document.querySelector('#copy-brief').focus({ preventScroll: true });
    } catch (failure) { error.textContent = failure.message; error.hidden = false; }
  });
  document.querySelector('#copy-brief').addEventListener('click', async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(output.value);
      feedback.textContent = 'Copied. Your brief has not been sent.';
    } catch {
      output.focus(); output.select(); feedback.textContent = 'The text is selected. Use your device’s Copy command to copy it.';
    }
  });
  document.querySelector('#download-brief').addEventListener('click', () => {
    const blob = new Blob([output.value], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a'); link.href = url; link.download = 'rally-demo-brief.txt';
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    feedback.textContent = 'Download requested. Your brief has not been sent.';
  });
  document.querySelector('#edit-brief').addEventListener('click', () => {
    result.hidden = true; form.hidden = false; document.querySelector('#brief-goal').focus();
  });
  document.querySelector('#prepare-brief').disabled = false;
}
