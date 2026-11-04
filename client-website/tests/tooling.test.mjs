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
  return (url, method = 'GET') => new Promise((resolve, reject) => {
    const req = request({ hostname: '127.0.0.1', port: server.address().port, path: url, method }, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', (part) => { body += part; });
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }));
    });
    req.on('error', reject);
    req.end();
  });
}

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
