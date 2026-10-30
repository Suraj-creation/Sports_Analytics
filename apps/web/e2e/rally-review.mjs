/** Read-only browser QA. Credentials and cookies remain in memory.
 * Set BAI_UI_PASSPHRASE and BAI_UI_SESSION_ID in the environment; never write auth state.
 * API writes are blocked except authentication. This does not run inference.
 */
import { chromium } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const phase = process.argv[2] ?? 'before';
if (!['before', 'final', 'confirm'].includes(phase)) throw new Error('Use before, final, or confirm.');
const baseURL = process.env.BAI_UI_BASE_URL ?? 'http://127.0.0.1:5173';
const sessionId = process.env.BAI_UI_SESSION_ID;
if (!sessionId) throw new Error('Set BAI_UI_SESSION_ID to the saved recording to review.');
const secondarySessionId = process.env.BAI_UI_SECONDARY_SESSION_ID ?? '01M55NQMRAS0ATB73XE3XA6S74';
const output = resolve(process.cwd(), '../../.impeccable/review', phase);
const browser = await chromium.launch({ executablePath: process.env.BAI_UI_CHROME ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ baseURL, reducedMotion: 'reduce' });
const report = { phase, baseURL, capturedAt: new Date().toISOString(), pages: [], interactions: [], blockedWrites: [], consoleErrors: [], httpErrors: [], limitations: ['Chromium native autofill is not seeded: forced CSS pseudo-state is a style probe only.', 'Measurements verify geometry and control colors, not labelled shuttle/event accuracy.'] };

// Runs inside the browser; it must not depend on Node globals.
function inspectPage() {
  const scope = document.querySelector('main') ?? document;
  const colorCanvas = document.createElement('canvas');
  colorCanvas.width = colorCanvas.height = 1;
  const colorContext = colorCanvas.getContext('2d', { willReadFrequently: true });
  const colors = new Map();
  const rgba = value => {
    if (colors.has(value)) return colors.get(value);
    if (colorContext) {
      colorContext.clearRect(0, 0, 1, 1);
      colorContext.fillStyle = value;
      colorContext.fillRect(0, 0, 1, 1);
      const data = colorContext.getImageData(0, 0, 1, 1).data;
      const color = [data[0], data[1], data[2], data[3] / 255];
      colors.set(value, color);
      return color;
    }
    const parts = value.match(/[\d.]+/g)?.map(Number) ?? [];
    return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0, parts[3] ?? 1];
  };
  const blend = (front, back, alpha = front[3]) => front.slice(0, 3).map((v, i) => v * alpha + back[i] * (1 - alpha));
  const behind = element => {
    if (!element) return [255, 255, 255];
    const style = getComputedStyle(element);
    return blend(rgba(style.backgroundColor), behind(element.parentElement), rgba(style.backgroundColor)[3] * Number(style.opacity));
  };
  const luminance = color => color.map(v => { const n = v / 255; return n <= .04045 ? n / 12.92 : ((n + .055) / 1.055) ** 2.4; }).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
  const contrast = (a, b) => { const x = luminance(a), y = luminance(b); return Math.round((Math.max(x, y) + .05) / (Math.min(x, y) + .05) * 100) / 100; };
  const visible = element => { const rect = element.getBoundingClientRect(); const style = getComputedStyle(element); return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden'; };
  const fields = [...scope.querySelectorAll('input:not([type=file]):not([type=range]):not([type=checkbox]):not([type=radio]), select, textarea')].filter(visible).map(element => {
    const style = getComputedStyle(element);
    const background = behind(element);
    const opacity = Number(style.opacity);
    const foregroundColor = style.webkitTextFillColor || style.color;
    const foreground = blend(rgba(foregroundColor), background, rgba(foregroundColor)[3] * opacity);
    const placeholder = getComputedStyle(element, '::placeholder');
    const placeholderColor = blend(rgba(placeholder.color), background, rgba(placeholder.color)[3] * Number(placeholder.opacity || 1) * opacity);
    return { tag: element.tagName, type: element.getAttribute('type'), label: element.labels?.[0]?.textContent?.trim() ?? element.getAttribute('aria-label') ?? '', disabled: element.disabled, valuePresent: Boolean(element.value), color: style.color, background: style.backgroundColor, effectiveBackground: background, ratio: contrast(foreground, background), placeholderRatio: element.hasAttribute('placeholder') ? contrast(placeholderColor, background) : null, minHeight: element.getBoundingClientRect().height, focused: document.activeElement === element, outline: style.outline, boxShadow: style.boxShadow };
  });
  const overflowing = [...scope.querySelectorAll('*')].filter(element => {
    const rect = element.getBoundingClientRect();
    if (!visible(element) || rect.right <= innerWidth + 2 && rect.left >= -2) return false;
    for (let ancestor = element.parentElement; ancestor; ancestor = ancestor.parentElement) {
      if (['auto', 'scroll', 'hidden', 'clip'].includes(getComputedStyle(ancestor).overflowX)) return false;
    }
    return getComputedStyle(element).position !== 'fixed';
  }).slice(0, 12).map(element => ({ tag: element.tagName, className: String(element.className), text: element.textContent?.slice(0, 80) }));
  const timeline = document.querySelector('.video-timeline');
  const timelineWidth = timeline?.getBoundingClientRect().width;
  const timelineGeometry = [...document.querySelectorAll('.video-timeline, .video-timeline > div, .video-timeline svg, .video-timeline canvas')].filter(visible).map(element => ({ tag: element.tagName, className: String(element.className), clientWidth: element.clientWidth, scrollWidth: element.scrollWidth, width: element.getBoundingClientRect().width, attrWidth: element.getAttribute('width'), fitsTimeline: element.getBoundingClientRect().width <= timelineWidth + 1 }));
  const timelineText = [...document.querySelectorAll('.video-timeline p')].filter(visible).map(element => ({ text: element.textContent, clientWidth: element.clientWidth, scrollWidth: element.scrollWidth }));
  return { title: scope.querySelector('h1')?.textContent, viewport: innerWidth, documentWidth: document.documentElement.scrollWidth, bodyWidth: document.body.scrollWidth, theme: document.documentElement.dataset.theme, overflowing, fields, timelineGeometry, timelineText, unnamedControls: [...scope.querySelectorAll('button, a, select, input:not([type=file])')].filter(visible).filter(element => !element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby') && !element.textContent?.trim() && !element.labels?.length).map(element => ({ tag: element.tagName, className: String(element.className) })).slice(0, 15) };
}

async function visit(page, path) {
  await page.goto(path, { waitUntil: 'domcontentloaded' });
  await page.locator('main h1').first().waitFor({ state: 'visible', timeout: 25000 });
  await page.locator('.rally-loading').waitFor({ state: 'hidden', timeout: 20000 });
  await page.waitForTimeout(path.includes(sessionId) ? 1800 : 650);
}

async function exerciseFields(page, theme, size) {
  const url = page.locator('main input[type=url]').first();
  if (!await url.isVisible().catch(() => false)) {
    report.interactions.push({ theme, size, test: 'URL input', result: 'unavailable', reason: 'YouTube import disabled or URL control absent.' });
    return;
  }
  await url.focus();
  await url.pressSequentially('https://www.youtube.com/watch?v=RallyTyped123', { delay: 5 });
  const typed = await url.inputValue();
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  const pastedValue = 'https://www.youtube.com/watch?v=RallyPasted456';
  await page.evaluate(value => navigator.clipboard.writeText(value), pastedValue);
  await url.press('ControlOrMeta+A');
  await url.press('ControlOrMeta+V');
  const pasted = await url.inputValue();
  await page.keyboard.press('Tab');
  const keyboardTarget = await page.evaluate(() => ({ tag: document.activeElement?.tagName, outline: getComputedStyle(document.activeElement).outline, boxShadow: getComputedStyle(document.activeElement).boxShadow }));
  const select = page.locator('main select').last();
  await select.focus();
  await page.keyboard.press('Home');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Tab');
  const keyboardSelectValue = await select.inputValue();
  await url.focus();
  const fields = (await page.evaluate(inspectPage)).fields;
  await page.screenshot({ path: resolve(output, `${theme}-${size.width}-library-filled-focus.png`), fullPage: true });
  const client = await context.newCDPSession(page);
  let autofillProbe;
  try {
    await client.send('DOM.enable');
    const { root } = await client.send('DOM.getDocument');
    const { nodeId } = await client.send('DOM.querySelector', { nodeId: root.nodeId, selector: 'main input[type=url]' });
    await client.send('CSS.enable');
    await client.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: ['autofill'] });
    autofillProbe = await url.evaluate(element => ({ color: getComputedStyle(element).color, webkitTextFillColor: getComputedStyle(element).webkitTextFillColor, background: getComputedStyle(element).backgroundColor, pseudoMatches: element.matches(':-webkit-autofill') }));
    await client.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: [] });
  } catch (error) { autofillProbe = { unsupported: error.message }; }
  await client.detach();
  report.interactions.push({ theme, size, test: 'URL typing, clipboard paste, keyboard select, focus and autofill style probe', typedPreserved: typed.includes('RallyTyped123'), pastedPreserved: pasted === pastedValue, keyboardTarget, keyboardSelectValue, fields, autofillProbe, submitted: false });
}

async function exerciseVideoModes(page, theme, size) {
  const video = page.locator('main video').first();
  await video.waitFor({ state: 'attached', timeout: 15000 });
  let mediaReady = true;
  try { await page.waitForFunction(() => document.querySelector('main video')?.readyState >= 1, null, { timeout: 20000 }); }
  catch { mediaReady = false; }
  await video.evaluate(element => {
    element.pause();
    if (element.readyState >= 1) element.currentTime = Math.min(6, Math.max(0, element.duration - 1));
    window.__rallyQaVideo = element;
  });
  let seekDecoded = false;
  if (mediaReady) {
    try {
      await page.waitForFunction(() => { const element = document.querySelector('main video'); return element && !element.seeking && element.readyState >= 2 && Math.abs(element.currentTime - 6) < .08; }, null, { timeout: 10000 });
      seekDecoded = true;
    } catch { /* Preserve an honest readiness result while still checking mounted media state. */ }
  }
  const initial = await video.evaluate(element => ({ time: element.currentTime, duration: element.duration, readyState: element.readyState, paused: element.paused, src: element.currentSrc, search: location.search, activeAnalysisTab: document.querySelector('.match-tabs [aria-current]')?.textContent }));
  const modes = [];
  for (const [name, label] of [['Focus', 'Focus video'], ['Collapsed', 'Collapse video'], ['Standard', 'Restore video']]) {
    const control = page.getByRole('button', { name: label, exact: true });
    if (!await control.isVisible().catch(() => false)) { modes.push({ name, missing: true }); continue; }
    await control.click();
    await page.waitForTimeout(300);
    const state = await page.evaluate(() => {
      const element = document.querySelector('main video');
      return { sameNode: element === window.__rallyQaVideo, time: element?.currentTime, paused: element?.paused, videoCount: document.querySelectorAll('main video').length, mode: document.querySelector('[data-video-mode]')?.getAttribute('data-video-mode'), scrollY, search: location.search, activeAnalysisTab: document.querySelector('.match-tabs [aria-current]')?.textContent };
    });
    const geometry = await page.evaluate(inspectPage);
    modes.push({ name, ...state, timePreserved: Math.abs((state.time ?? -1) - initial.time) < .08, analysisPreserved: state.search === initial.search && state.activeAnalysisTab === initial.activeAnalysisTab, timelineGeometry: geometry.timelineGeometry, timelineText: geometry.timelineText, shell: await page.evaluate(() => ({ sidebarWidth: document.querySelector('.rally-sidebar')?.getBoundingClientRect().width, mobileNavDisplay: getComputedStyle(document.querySelector('.rally-bottom-nav')).display })) });
    await page.screenshot({ path: resolve(output, `${theme}-${size.width}-match-${name.toLowerCase()}.png`), fullPage: true });
  }
  report.interactions.push({ theme, size, test: 'Video mode node, pause, and currentTime preservation', mediaReady, seekDecoded, initial, modes });
}

async function exerciseKeyboard(page, theme, size) {
  await page.evaluate(() => { document.body.tabIndex = -1; document.body.focus(); });
  const stops = [];
  for (let index = 0; index < 8; index += 1) {
    await page.keyboard.press('Tab');
    stops.push(await page.evaluate(() => {
      const element = document.activeElement;
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return { tag: element.tagName, label: element.getAttribute('aria-label') || element.textContent?.trim().slice(0, 90), outline: style.outline, boxShadow: style.boxShadow, visible: rect.width > 0 && rect.height > 0 && rect.right > 0 && rect.left < innerWidth, focusVisible: element.matches(':focus-visible') };
    }));
  }
  await page.evaluate(() => document.body.removeAttribute('tabindex'));
  report.interactions.push({ theme, size, test: 'Keyboard navigation', stops });
}

async function captureLogin() {
  for (const theme of ['light', 'dark']) {
    const loginContext = await browser.newContext({ baseURL, reducedMotion: 'reduce' });
    try {
      await loginContext.route('**/api/**', route => ['GET', 'HEAD', 'OPTIONS'].includes(route.request().method()) ? route.continue() : route.abort('blockedbyclient'));
      const page = await loginContext.newPage();
      await page.goto('/', { waitUntil: 'domcontentloaded' });
      await page.getByRole('heading', { name: 'Sign in to Rally' }).waitFor();
      await page.evaluate(value => { localStorage.setItem('rally-display-v1', JSON.stringify({ theme: value, reducedMotion: true })); document.documentElement.dataset.theme = value; }, theme);
      for (const size of [{ width: 1440, height: 960 }, { width: 390, height: 844 }]) {
        await page.setViewportSize(size);
        const capture = `${theme}-${size.width}-login.png`;
        await page.screenshot({ path: resolve(output, capture), fullPage: true });
        report.pages.push({ path: '/ [unauthenticated]', theme, size, capture, ...await page.evaluate(inspectPage) });
      }
    } finally { await loginContext.close(); }
  }
}
try {
  await mkdir(output, { recursive: true });
  if (phase === 'confirm') await captureLogin();
  await context.route('**/api/**', async route => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    if (!['GET', 'HEAD', 'OPTIONS'].includes(request.method()) && !['/api/auth/login', '/api/auth/logout'].includes(pathname)) {
      report.blockedWrites.push({ method: request.method(), pathname });
      await route.abort('blockedbyclient');
    } else await route.continue();
  });
  if (!process.env.BAI_UI_PASSPHRASE) throw new Error('Set BAI_UI_PASSPHRASE in the environment.');
  const login = await context.request.post('/api/auth/login', { data: { passphrase: process.env.BAI_UI_PASSPHRASE } });
  if (!login.ok()) throw new Error(`Authentication returned HTTP ${login.status()}.`);
  const page = await context.newPage();
  page.on('pageerror', error => report.consoleErrors.push({ route: new URL(page.url()).pathname, message: error.message }));
  page.on('console', message => { if (message.type() === 'error') report.consoleErrors.push({ route: new URL(page.url()).pathname, message: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.httpErrors.push({ route: new URL(page.url()).pathname, pathname: new URL(response.url()).pathname, status: response.status() }); });
  const routes = phase === 'before' ? ['/', '/matches', '/library', `/matches/${sessionId}`] : phase === 'confirm' ? ['/library', '/people', '/progress', `/sessions/${sessionId}/calibrate`, `/matches/${sessionId}`, `/matches/${secondarySessionId}`] : ['/', '/matches', '/library', '/moments', '/progress', '/people', '/settings', '/help', '/system', `/sessions/${sessionId}/calibrate`, `/matches/${sessionId}`];
  const sizes = phase === 'before' ? [{ width: 1440, height: 960 }, { width: 390, height: 844 }] : [{ width: 1440, height: 960 }, { width: 1280, height: 960 }, { width: 768, height: 1024 }, { width: 390, height: 844 }];
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  for (const theme of ['light', 'dark']) {
    await page.evaluate(value => {
      localStorage.setItem('rally-display-v1', JSON.stringify({ theme: value, reducedMotion: true }));
      document.documentElement.dataset.theme = value;
      document.documentElement.dataset.reducedMotion = 'true';
    }, theme);
    for (const size of sizes) {
      await page.setViewportSize(size);
      for (const path of routes) {
        if (phase === 'confirm' && [1280, 768].includes(size.width) && path !== `/matches/${sessionId}`) continue;
        try {
        await visit(page, path);
        const name = path === '/' ? 'home' : path.includes('calibrate') ? 'calibrate' : path.includes(sessionId) ? 'match' : path.includes(secondarySessionId) ? 'match-secondary' : path.slice(1);
        const capture = `${theme}-${size.width}-${name}.png`;
        await page.screenshot({ path: resolve(output, capture), fullPage: true });
        const viewportCapture = phase !== 'before' && [1440, 390].includes(size.width) ? `${theme}-${size.width}-${name}-viewport.png` : undefined;
        if (viewportCapture) await page.screenshot({ path: resolve(output, viewportCapture), fullPage: false });
        const metrics = await page.evaluate(inspectPage);
        report.pages.push({ path, theme, size, capture, viewportCapture, ...metrics });
        process.stdout.write(`Captured ${capture}\n`);
        if (phase !== 'before' && [1440, 390].includes(size.width)) {
          try {
            if (path === '/') await exerciseKeyboard(page, theme, size);
            if (path === '/library') await exerciseFields(page, theme, size);
            if (path === `/matches/${sessionId}`) await exerciseVideoModes(page, theme, size);
          } catch (error) {
            report.interactions.push({ path, theme, size, test: 'interaction', error: error.message });
          }
        }
        } catch (error) {
          report.pages.push({ path, theme, size, error: error.message });
          process.stdout.write(`Route check failed: ${theme} ${size.width} ${path}: ${error.message.split('\n')[0]}\n`);
        }
        await writeFile(resolve(output, 'report.json'), JSON.stringify(report, null, 2));
      }
    }
  }
  report.summary = {
    routeChecks: report.pages.length,
    failedRoutes: report.pages.filter(page => page.error).length,
    horizontalOverflow: report.pages.filter(page => page.documentWidth > page.viewport + 1).map(page => ({ path: page.path, theme: page.theme, width: page.size.width, documentWidth: page.documentWidth })),
    lowContrastFields: report.pages.flatMap(page => (page.fields ?? []).filter(field => field.ratio < 4.5 || field.placeholderRatio !== null && field.placeholderRatio < 4.5).map(field => ({ path: page.path, theme: page.theme, width: page.size.width, ...field }))),
    interactionErrors: report.interactions.filter(interaction => interaction.error),
  };
  await writeFile(resolve(output, 'report.json'), JSON.stringify(report, null, 2));
  process.stdout.write(JSON.stringify({ output, pages: report.pages.length, consoleErrors: report.consoleErrors.length, httpErrors: report.httpErrors.length, blockedWrites: report.blockedWrites.length }) + '\n');
} finally { await context.close(); await browser.close(); }
