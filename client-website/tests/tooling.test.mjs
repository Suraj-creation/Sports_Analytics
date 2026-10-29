import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { request } from 'node:http';
import { copyFile, mkdtemp, mkdir, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const packageRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const script = (name) => path.join(packageRoot, 'scripts', `${name}.mjs`);
const run = (name, root) => spawnSync(process.execPath, [script(name), '--dir', root], { encoding: 'utf8' });

async function fixture(t) {
  const root = await mkdtemp(path.join(tmpdir(), 'rally-tooling-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  await Promise.all(['src', 'assets', 'docs'].map((name) => mkdir(path.join(root, name))));
  await Promise.all([
    writeFile(path.join(root, 'index.html'), '<!doctype html><html><head><link rel="stylesheet" href="./src/site.css"></head><body id="top"><img src="./assets/court.svg" alt="Court"><a href="#top">Top</a><script type="module" src="./src/main.js"></script></body></html>'),
    writeFile(path.join(root, 'src', 'site.css'), 'body { background-image: url("../assets/court.svg"); }'),
    writeFile(path.join(root, 'src', 'main.js'), 'export const working = true;'),
    writeFile(path.join(root, 'assets', 'court.svg'), '<svg xmlns="http://www.w3.org/2000/svg"/>'),
    writeFile(path.join(root, 'docs', 'private.txt'), 'private methodology draft'),
    writeFile(path.join(root, '.env'), 'PASSWORD=do-not-publish'),
    writeFile(path.join(root, 'package.json'), '{"type":"module","private":true}'),
  ]);
  return root;
}

test('build extracts only the public website and replaces its own previous output', async (t) => {
  const root = await fixture(t);
  let result = run('build', root);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual((await readdir(path.join(root, 'dist'))).sort(), ['.rally-static-output', 'assets', 'index.html', 'src']);
  assert.equal(await readFile(path.join(root, 'dist', 'src', 'main.js'), 'utf8'), 'export const working = true;');
  await writeFile(path.join(root, 'src', 'obsolete.js'), 'export const obsolete = true;');
  result = run('build', root);
  assert.equal(result.status, 0, result.stderr);
  await rm(path.join(root, 'src', 'obsolete.js'));
  result = run('build', root);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual((await readdir(path.join(root, 'dist', 'src'))).sort(), ['main.js', 'site.css']);
});

test('build refuses an existing unowned dist without deleting its contents', async (t) => {
  const root = await fixture(t);
  await mkdir(path.join(root, 'dist'));
  await writeFile(path.join(root, 'dist', 'keep.txt'), 'user-owned');
  const result = run('build', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /unowned/i);
  assert.equal(await readFile(path.join(root, 'dist', 'keep.txt'), 'utf8'), 'user-owned');
});

test('build rejects secret and hidden files inside public trees', async (t) => {
  const root = await fixture(t);
  await writeFile(path.join(root, 'assets', '.env'), 'PASSWORD=private');
  const result = run('build', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not public|unsupported|hidden/i);
  await assert.rejects(readFile(path.join(root, 'dist', 'assets', '.env')));
});

test('build copies the exact font license while rejecting arbitrary text assets', async (t) => {
  const root = await fixture(t);
  await mkdir(path.join(root, 'assets', 'fonts'));
  await writeFile(path.join(root, 'assets', 'fonts', 'LICENSE.txt'), 'SIL Open Font License\n');
  let result = run('build', root);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(await readFile(path.join(root, 'dist', 'assets', 'fonts', 'LICENSE.txt'), 'utf8'), 'SIL Open Font License\n');
  const get = await preview(t, root);
  const license = await get('/assets/fonts/LICENSE.txt');
  assert.equal(license.status, 200);
  assert.match(license.headers['content-type'], /^text\/plain(?:;|$)/);
  assert.equal(license.body, 'SIL Open Font License\n');
  await writeFile(path.join(root, 'assets', 'fonts', 'private.txt'), 'private notes');
  result = run('build', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not public.*assets\/fonts\/private\.txt/i);
  await assert.rejects(readFile(path.join(root, 'dist', 'assets', 'fonts', 'private.txt')));
});

test('build rejects public directory links and a linked output directory', async (t) => {
  const root = await fixture(t);
  const outside = await mkdtemp(path.join(tmpdir(), 'rally-outside-'));
  t.after(() => rm(outside, { recursive: true, force: true }));
  await writeFile(path.join(outside, 'keep.txt'), 'outside');
  await symlink(outside, path.join(root, 'assets', 'linked'), process.platform === 'win32' ? 'junction' : 'dir');
  let result = run('build', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /symlink|symbolic link/i);
  await rm(path.join(root, 'assets', 'linked'));
  await symlink(outside, path.join(root, 'dist'), process.platform === 'win32' ? 'junction' : 'dir');
  result = run('build', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /symlink|symbolic link/i);
  assert.equal(await readFile(path.join(outside, 'keep.txt'), 'utf8'), 'outside');
});

test('copied tooling builds an isolated package without repository files or installed dependencies', async (t) => {
  const root = await fixture(t);
  await mkdir(path.join(root, 'scripts'));
  for (const name of ['build', 'check', 'serve']) await copyFile(script(name), path.join(root, 'scripts', `${name}.mjs`));
  for (const name of ['package.json', 'package-lock.json']) await copyFile(path.join(packageRoot, name), path.join(root, name));
  const check = spawnSync(process.execPath, [path.join(root, 'scripts', 'check.mjs')], { cwd: root, encoding: 'utf8' });
  assert.equal(check.status, 0, check.stderr);
  const build = spawnSync(process.execPath, [path.join(root, 'scripts', 'build.mjs')], { cwd: root, encoding: 'utf8' });
  assert.equal(build.status, 0, build.stderr);
  assert.match(await readFile(path.join(root, 'dist', 'index.html'), 'utf8'), /\.\/src\/main\.js/);
  await assert.rejects(readFile(path.join(root, 'dist', '.env')));
  await assert.rejects(readFile(path.join(root, 'dist', 'docs', 'private.txt')));
});

test('check accepts local references, module imports and outbound contact links', async (t) => {
  const root = await fixture(t);
  await writeFile(path.join(root, 'src', 'main.js'), "import { value } from './value.js'; export { value };\n");
  await writeFile(path.join(root, 'src', 'value.js'), 'export const value = 1;');
  const html = await readFile(path.join(root, 'index.html'), 'utf8');
  await writeFile(path.join(root, 'index.html'), html.replace('</body>', '<a href="mailto:verified@example.org">Contact</a><a href="https://example.org/">Reference</a></body>'));
  const result = run('check', root);
  assert.equal(result.status, 0, result.stderr);
});

test('check rejects missing assets and invalid in-page citations', async (t) => {
  const root = await fixture(t);
  await writeFile(path.join(root, 'index.html'), '<img src="./assets/missing.svg"><a href="#absent">Citation</a>');
  const result = run('check', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /missing.*assets\/missing\.svg/i);
  assert.match(result.stderr, /fragment.*absent/i);
});

test('check rejects external runtime dependencies and host-root paths', async (t) => {
  const root = await fixture(t);
  await writeFile(path.join(root, 'src', 'site.css'), '@import "https://fonts.example.org/font.css"; body { background:url(/assets/court.svg) }');
  await writeFile(path.join(root, 'src', 'main.js'), "import('https://example.org/module.js');");
  const result = run('check', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /external runtime/i);
  assert.match(result.stderr, /relative.*subpath/i);
});

test('check rejects parent-repository imports and unpublished documentation links', async (t) => {
  const root = await fixture(t);
  await writeFile(path.join(root, 'src', 'main.js'), "import '../../server-secrets.js';");
  await writeFile(path.join(root, 'index.html'), '<a href="./docs/private.txt">Private</a>');
  const result = run('check', root);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /outside.*package/i);
  assert.match(result.stderr, /not public.*docs\/private\.txt/i);
});

async function preview(t, root, base = '/') {
  const available = await readFile(script('serve'), 'utf8').catch(() => '');
  assert.ok(available, 'The public-only preview server must exist');
  const { createPreviewServer } = await import('../scripts/serve.mjs');
  const server = await createPreviewServer({ directory: root, base });
  t.after(() => new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve())));
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return (url, method = 'GET', headers = {}) => new Promise((resolve, reject) => {
    const req = request({ hostname: '127.0.0.1', port: server.address().port, path: url, method, headers }, (res) => {
      const chunks = [];
      res.on('data', (part) => { chunks.push(part); });
      res.on('end', () => {
        const bytes = Buffer.concat(chunks);
        resolve({ status: res.statusCode, headers: res.headers, body: bytes.toString('utf8'), bytes });
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function videoPreview(t) {
  const root = await fixture(t);
  const video = await readFile(path.join(packageRoot, 'assets', 'tracking-reference.mp4'));
  await writeFile(path.join(root, 'assets', 'reference.mp4'), video);
  return { get: await preview(t, root, '/rally/'), video };
}

test('preview serves bounded video ranges as the exact requested bytes beneath a subpath', async (t) => {
  const { get, video } = await videoPreview(t);
  for (const [range, start, end] of [
    ['bytes=0-31', 0, 31],
    ['bytes=65536-65791', 65536, 65791],
    [`bytes=${video.length - 16}-${video.length + 500}`, video.length - 16, video.length - 1],
    [`bytes=${video.length - 1}-9999999999999999999999`, video.length - 1, video.length - 1],
  ]) {
    const response = await get('/rally/assets/reference.mp4', 'GET', { Range: range });
    assert.equal(response.status, 206, range);
    assert.equal(response.headers['accept-ranges'], 'bytes');
    assert.equal(response.headers['content-type'], 'video/mp4');
    assert.equal(response.headers['content-range'], `bytes ${start}-${end}/${video.length}`);
    assert.equal(response.headers['content-length'], String(end - start + 1));
    assert.deepEqual(response.bytes, video.subarray(start, end + 1));
  }
});

test('preview resolves open and suffix ranges against the actual video length', async (t) => {
  const { get, video } = await videoPreview(t);
  for (const [range, start] of [
    [`bytes=${video.length - 73}-`, video.length - 73],
    ['bytes=-117', video.length - 117],
    [`bytes=-${video.length + 100}`, 0],
    ['bytes=-9999999999999999999999', 0],
  ]) {
    const response = await get('/rally/assets/reference.mp4', 'GET', { Range: range });
    assert.equal(response.status, 206, range);
    assert.equal(response.headers['content-range'], `bytes ${start}-${video.length - 1}/${video.length}`);
    assert.equal(response.headers['content-length'], String(video.length - start));
    assert.deepEqual(response.bytes, video.subarray(start));
  }
});

test('preview rejects invalid, multiple and unsatisfiable ranges without serving video bytes', async (t) => {
  const { get, video } = await videoPreview(t);
  for (const range of ['bytes=', 'bytes=-', 'bytes=two-9', 'bytes=1.5-9', 'bytes=10-2', 'bytes=-0', 'bytes=0-1,4-5', 'items=0-1', `bytes=${video.length}-`, `bytes=${video.length + 1}-${video.length + 50}`, 'bytes=9007199254740993-']) {
    const response = await get('/rally/assets/reference.mp4', 'GET', { Range: range });
    assert.equal(response.status, 416, range);
    assert.equal(response.headers['accept-ranges'], 'bytes');
    assert.equal(response.headers['content-range'], `bytes */${video.length}`);
    assert.equal(response.bytes.length, 0);
  }
});

test('preview keeps complete GET responses and body-free HEAD responses with range metadata', async (t) => {
  const { get, video } = await videoPreview(t);
  const full = await get('/rally/assets/reference.mp4');
  assert.equal(full.status, 200);
  assert.equal(full.headers['accept-ranges'], 'bytes');
  assert.equal(full.headers['content-range'], undefined);
  assert.equal(full.headers['content-length'], String(video.length));
  assert.deepEqual(full.bytes, video);
  const head = await get('/rally/assets/reference.mp4', 'HEAD');
  assert.equal(head.status, 200);
  assert.equal(head.headers['content-length'], String(video.length));
  assert.equal(head.bytes.length, 0);
  const partialHead = await get('/rally/assets/reference.mp4', 'HEAD', { Range: 'bytes=100-199' });
  assert.equal(partialHead.status, 206);
  assert.equal(partialHead.headers['content-range'], `bytes 100-199/${video.length}`);
  assert.equal(partialHead.headers['content-length'], '100');
  assert.equal(partialHead.bytes.length, 0);
  const rejectedHead = await get('/rally/assets/reference.mp4', 'HEAD', { Range: `bytes=${video.length}-` });
  assert.equal(rejectedHead.status, 416);
  assert.equal(rejectedHead.headers['content-range'], `bytes */${video.length}`);
  assert.equal(rejectedHead.bytes.length, 0);
});

test('preview returns 416 for ranges over an empty public file', async (t) => {
  const root = await fixture(t);
  await writeFile(path.join(root, 'assets', 'empty.mp4'), Buffer.alloc(0));
  const get = await preview(t, root);
  const full = await get('/assets/empty.mp4');
  assert.equal(full.status, 200);
  assert.equal(full.headers['content-length'], '0');
  for (const range of ['bytes=0-0', 'bytes=0-', 'bytes=-1']) {
    const response = await get('/assets/empty.mp4', 'GET', { Range: range });
    assert.equal(response.status, 416, range);
    assert.equal(response.headers['content-range'], 'bytes */0');
    assert.equal(response.bytes.length, 0);
  }
});

test('preview serves local pages and MIME types beneath an explicit subpath', async (t) => {
  const root = await fixture(t);
  const get = await preview(t, root, '/rally/');
  const index = await get('/rally/');
  assert.equal(index.status, 200);
  assert.match(index.headers['content-type'], /^text\/html/);
  assert.match(index.body, /Court/);
  assert.equal((await get('/rally')).headers.location, '/rally/');
  assert.equal((await get('/')).status, 404);
  assert.match((await get('/rally/src/main.js?version=1')).headers['content-type'], /^text\/javascript/);
  assert.match((await get('/rally/src/site.css')).headers['content-type'], /^text\/css/);
  assert.match((await get('/rally/assets/court.svg')).headers['content-type'], /^image\/svg\+xml/);
  const head = await get('/rally/index.html', 'HEAD');
  assert.equal(head.status, 200);
  assert.equal(head.body, '');
  assert.equal(head.headers['x-content-type-options'], 'nosniff');
});

test('source preview never serves private files, directory listings or unsupported methods', async (t) => {
  const root = await fixture(t);
  const get = await preview(t, root);
  for (const url of ['/docs/private.txt', '/.env', '/package.json', '/scripts/build.mjs', '/tests/tooling.test.mjs', '/src/', '/assets/', '/missing']) {
    const response = await get(url);
    assert.equal(response.status, 404, url);
    assert.doesNotMatch(response.body, /PASSWORD|methodology/);
  }
  const response = await get('/', 'POST');
  assert.equal(response.status, 405);
  assert.equal(response.headers.allow, 'GET, HEAD');
});

test('preview rejects raw and encoded traversal without relying on URL normalization', async (t) => {
  const root = await fixture(t);
  const get = await preview(t, root);
  for (const url of ['/../.env', '/%2e%2e/.env', '/assets/%2e%2e/%2e%2e/.env', '/assets%2f..%2f.env', '/assets%5c..%5c.env', '/bad%zz', '/src/%00main.js']) {
    const response = await get(url);
    assert.equal(response.status, 400, url);
    assert.doesNotMatch(response.body, /PASSWORD/);
  }
});

test('preview refuses symlinks present initially and directory replacement after startup', async (t) => {
  const root = await fixture(t);
  const outside = await mkdtemp(path.join(tmpdir(), 'rally-preview-outside-'));
  t.after(() => rm(outside, { recursive: true, force: true }));
  await writeFile(path.join(outside, 'secret.js'), 'private source');
  await mkdir(path.join(root, 'src', 'group'));
  await writeFile(path.join(root, 'src', 'group', 'secret.js'), 'public source');
  const get = await preview(t, root);
  await rm(path.join(root, 'src', 'group'), { recursive: true });
  await symlink(outside, path.join(root, 'src', 'group'), process.platform === 'win32' ? 'junction' : 'dir');
  const response = await get('/src/group/secret.js');
  assert.equal(response.status, 403);
  assert.doesNotMatch(response.body, /private source/);
  const { createPreviewServer } = await import('../scripts/serve.mjs');
  await assert.rejects(createPreviewServer({ directory: root }), /symlink/i);
});
