import { lstat, readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import path from 'node:path';
import { isMain, mimeTypes, packageRoot, parseArgs, publicFiles } from './build.mjs';

function basePath(value) {
  const base = value.endsWith('/') ? value : `${value}/`;
  if (!/^\/(?:[a-z\d_-]+\/)*$/i.test(base)) throw new Error('Base must be a path such as / or /rally/.');
  return base;
}

function byteRange(value, size) {
  const match = /^bytes=(\d*)-(\d*)$/i.exec(value.trim());
  if (!match || (!match[1] && !match[2]) || size === 0) return null;
  // Parse decimal offsets exactly before bounding them to the in-memory file.
  const length = BigInt(size);
  let start;
  let end = length - 1n;
  if (match[1]) {
    start = BigInt(match[1]);
    const requestedEnd = match[2] ? BigInt(match[2]) : end;
    if (start >= length || requestedEnd < start) return null;
    if (requestedEnd < end) end = requestedEnd;
  } else {
    const suffix = BigInt(match[2]);
    if (suffix === 0n) return null;
    start = suffix >= length ? 0n : length - suffix;
  }
  return { start: Number(start), end: Number(end) };
}

export async function createPreviewServer({ directory = packageRoot, base = '/' } = {}) {
  const root = path.resolve(directory);
  const mount = basePath(base);
  const files = new Set(await publicFiles(root));
  return createServer(async (request, response) => {
    response.setHeader('X-Content-Type-Options', 'nosniff');
    response.setHeader('Referrer-Policy', 'no-referrer');
    response.setHeader('Cache-Control', 'no-store');
    const reply = (status, text) => {
      response.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end(request.method === 'HEAD' ? undefined : text);
    };
    if (!['GET', 'HEAD'].includes(request.method)) {
      response.setHeader('Allow', 'GET, HEAD');
      return reply(405, 'Method not allowed.');
    }
    const raw = (request.url ?? '').split('?')[0];
    let pathname;
    try {
      if (!raw.startsWith('/') || /%2f|%5c/i.test(raw)) throw new Error('Invalid path');
      pathname = decodeURIComponent(raw);
      if (/[\\\0]/.test(pathname) || /(?:^|\/)\.{1,2}(?:\/|$)/.test(pathname)) throw new Error('Invalid path');
    } catch { return reply(400, 'Invalid request path.'); }
    if (mount !== '/' && pathname === mount.slice(0, -1)) {
      response.writeHead(308, { Location: mount });
      return response.end();
    }
    if (!pathname.startsWith(mount)) return reply(404, 'Not found.');
    const relative = pathname.slice(mount.length) || 'index.html';
    if (!files.has(relative)) return reply(404, 'Not found.');
    try {
      let absolute = root;
      for (const segment of ['', ...relative.split('/')]) {
        absolute = path.join(absolute, segment);
        const info = await lstat(absolute);
        if (info.isSymbolicLink()) return reply(403, 'Symbolic links are not served.');
      }
      const body = await readFile(absolute);
      response.setHeader('Accept-Ranges', 'bytes');
      response.setHeader('Content-Type', mimeTypes[path.extname(relative).toLowerCase()]);
      let content = body;
      let status = 200;
      if (request.headers.range !== undefined) {
        const range = byteRange(request.headers.range, body.length);
        if (!range) {
          response.writeHead(416, { 'Content-Range': `bytes */${body.length}`, 'Content-Length': 0 });
          return response.end();
        }
        content = body.subarray(range.start, range.end + 1);
        status = 206;
        response.setHeader('Content-Range', `bytes ${range.start}-${range.end}/${body.length}`);
      }
      response.writeHead(status, { 'Content-Length': content.length });
      response.end(request.method === 'HEAD' ? undefined : content);
    } catch (error) {
      reply(error.code === 'ENOENT' || error.code === 'ENOTDIR' ? 404 : 500, 'File unavailable.');
    }
  });
}

if (isMain(import.meta.url)) {
  try {
    const options = parseArgs(process.argv.slice(2), { host: '127.0.0.1', port: '4178', dir: packageRoot, base: '/' });
    if (!/^\d+$/.test(options.port) || Number(options.port) > 65535) throw new Error('Port must be an integer from 0 to 65535.');
    const server = await createPreviewServer({ directory: options.dir, base: options.base });
    server.once('error', (error) => { console.error(error.message); process.exitCode = 1; });
    server.listen(Number(options.port), options.host, () => {
      const host = options.host.includes(':') ? `[${options.host}]` : options.host;
      console.log(`Static preview: http://${host}:${server.address().port}${basePath(options.base)}`);
    });
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
