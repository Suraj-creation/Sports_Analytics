import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { isMain, packageRoot, parseArgs, publicFiles } from './build.mjs';

const decodeEntities = (value) => value.replace(/&amp;/gi, '&').replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code))).replace(/&#x([\da-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)));

function cssReferences(source) {
  const references = [];
  for (const match of source.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/url\(\s*(?:"([^"]*)"|'([^']*)'|([^\s)]+))\s*\)|@import\s+["']([^"']+)["']/gi)) {
    references.push(match[1] ?? match[2] ?? match[3] ?? match[4]);
  }
  return references;
}

function moduleReferences(source) {
  const text = source.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
  const references = [];
  for (const pattern of [
    /\bimport\s*(?:\(\s*)?(['"`])([^'"`\r\n]+)\1/g,
    /\b(?:import|export)\s+[\w$*{},\s]+\s+from\s*(['"])([^'"\r\n]+)\1/g,
    /\b(?:fetch|Worker|SharedWorker|WebSocket|EventSource|URL)\s*\(\s*(['"`])([^'"`\r\n]+)\1/g,
  ]) {
    for (const match of text.matchAll(pattern)) references.push(match[2]);
  }
  if (/\bimport\s*\(\s*(?!['"`])\S/.test(text)) throw new Error('Computed imports cannot be checked; use a literal local module path.');
  if (references.some((value) => value.includes('${'))) throw new Error('Computed runtime paths cannot be checked; use literal local paths.');
  return references;
}

export async function check(directory = packageRoot) {
  const root = path.resolve(directory);
  const files = await publicFiles(root);
  const published = new Set(files);
  const errors = [];
  const texts = new Map();
  for (const file of files) {
    if (/\.(?:html|css|m?js)$/.test(file)) texts.set(file, await readFile(path.join(root, file), 'utf8'));
  }
  function reference(from, raw, navigation = false) {
    const value = decodeEntities(raw).trim();
    if (!value) return;
    const fail = (reason) => errors.push(`${from}: ${reason}: ${value}`);
    if (/^(?:https?:|mailto:|tel:)/i.test(value) && navigation) return;
    if (/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(value)) return fail('External runtime dependency is forbidden');
    if (value.startsWith('/')) return fail('Use a relative path for subpath deployment');
    let decoded;
    try { decoded = decodeURIComponent(value); } catch { return fail('Malformed URL'); }
    if (/[\\\0]/.test(decoded)) return fail('Invalid local path');
    const [pathname] = decoded.split(/[?#]/);
    const target = pathname ? path.posix.normalize(path.posix.join(path.posix.dirname(from), pathname)) : from;
    if (target === '..' || target.startsWith('../')) return fail('Reference resolves outside the package');
    const normalized = target === '.' || pathname.endsWith('/') ? path.posix.join(target, 'index.html') : target;
    if (!published.has(normalized)) return fail(`Missing or not public file ${normalized}`);
    const fragment = decoded.includes('#') ? decoded.slice(decoded.indexOf('#') + 1) : '';
    if (fragment && normalized.endsWith('.html')) {
      const ids = [...texts.get(normalized).matchAll(/\bid\s*=\s*(?:"([^"]+)"|'([^']+)')/gi)].map((match) => match[1] ?? match[2]);
      if (!ids.includes(fragment)) fail(`Missing fragment ${fragment}`);
    }
  }
  for (const [file, source] of texts) {
    try {
      if (file.endsWith('.css')) {
        for (const value of cssReferences(source)) reference(file, value);
      } else if (/\.m?js$/.test(file)) {
        for (const value of moduleReferences(source)) {
          if (!value.startsWith('.') && !value.startsWith('/') && !/^[a-z][a-z\d+.-]*:/i.test(value)) errors.push(`${file}: Bare runtime imports are forbidden: ${value}`);
          else reference(file, value);
        }
      } else {
        for (const tag of source.replace(/<!--[\s\S]*?-->/g, '').matchAll(/<([a-z][\w:-]*)\b([^>]*?)>/gi)) {
          const name = tag[1].toLowerCase();
          if (name === 'base') errors.push(`${file}: A base element would break portable relative URLs.`);
          for (const attribute of tag[2].matchAll(/([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/g)) {
            const key = attribute[1].toLowerCase();
            const value = attribute[2] ?? attribute[3] ?? attribute[4];
            if (['src', 'href', 'poster', 'action', 'data'].includes(key)) reference(file, value, name === 'a' && key === 'href');
            if (key === 'srcset') for (const item of value.split(',')) reference(file, item.trim().split(/\s+/)[0]);
            if (key === 'style') for (const item of cssReferences(value)) reference(file, item);
          }
        }
        for (const match of source.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)) for (const value of cssReferences(match[1])) reference(file, value);
        for (const match of source.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)) for (const value of moduleReferences(match[1])) reference(file, value);
      }
    } catch (error) { errors.push(`${file}: ${error.message}`); }
  }
  if (errors.length) throw new Error([...new Set(errors)].join('\n'));
  return files.length;
}

if (isMain(import.meta.url)) {
  try {
    const options = parseArgs(process.argv.slice(2), { dir: packageRoot });
    const count = await check(options.dir);
    console.log(`Checked local references in ${count} public files.`);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
