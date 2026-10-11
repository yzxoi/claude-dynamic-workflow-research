const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const parser = require('@babel/parser');
const source = fs.readFileSync(__dirname + '/bun-files/chunk-hedqf2m1.js', 'utf8');
const ast = parser.parse(source, { sourceType: 'module' });
const nodes = new Map();
function walk(n) {
  if (!n || typeof n !== 'object') return;
  if (n.type === 'FunctionDeclaration' && n.id) nodes.set('fn:' + n.id.name, n);
  if (n.type === 'VariableDeclarator' && n.id.type === 'Identifier' && ['Sr', 'Tr', 'Or'].includes(n.id.name)) nodes.set('var:' + n.id.name, n.init);
  for (const [k, v] of Object.entries(n)) {
    if (['loc', 'start', 'end', 'extra'].includes(k)) continue;
    if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === 'object') walk(v);
  }
}
walk(ast.program);
function expression(key) { const n = nodes.get(key); assert(n, key); return source.slice(n.start, n.end); }
const logs = [];
const context = vm.createContext({ Nt: x => x, j: {}, Q: async () => {}, lwr: x => x, n: x => x, o: x => x, we: () => {}, Me: () => {}, me: async x => ({ v: await x }), y: (fn, ...args) => fn(...args), PFe: e => ({ name: e.name, msg: e.message }), re: x => logs.push(x), ae: logs, I: (n, word) => word + (n === 1 ? '' : 's'), _: JSON.stringify, Mr: 'clock disabled', Wr: 'random disabled', Fr: crypto.createHash, Br: 'probe' });
const parallel = vm.runInContext(expression('var:Sr'), context);
const pipeline = vm.runInContext(expression('var:Tr'), context);
vm.runInContext(expression('fn:Hr') + '\n' + expression('fn:No'), context);
const output = { method: 'execute exact extracted functions with explicit host-boundary stubs; no CLI, agent model, authentication or cloud session', source: 'bun-files/chunk-hedqf2m1.js', source_sha256: crypto.createHash('sha256').update(source).digest('hex'), observations: [] };
const deferred = () => { let resolve; const promise = new Promise(r => resolve = r); return { promise, resolve }; };
(async () => {
  const hold = deferred(), reached = deferred(), events = [];
  const run = pipeline(['fast', 'slow'], async item => {
    events.push('start:' + item);
    if (item === 'slow') await hold.promise;
    events.push('first:' + item);
    return item.toUpperCase();
  }, async (previous, original, index) => {
    events.push('second:' + original);
    if (original === 'fast') reached.resolve();
    return { previous, original, index };
  });
  await reached.promise;
  assert(events.includes('second:fast'));
  assert(!events.includes('first:slow'));
  hold.resolve();
  const result = await run;
  assert.equal(result[1].index, 1);
  assert.equal(result[1].original, 'slow');
  output.observations.push({ invariant: 'pipeline has no barrier between stages; callbacks receive previous, original, index', events, result });
  let followups = 0;
  const failures = await pipeline([0, 1, 2], async item => {
    if (item === 0) throw Error('intentional');
    if (item === 1) return null;
    return item;
  }, item => { followups++; return item * 2; });
  assert.equal(JSON.stringify(failures), '[null,null,4]');
  assert.equal(followups, 1);
  output.observations.push({ invariant: 'pipeline drops throwing/null items and skips remaining stages', result: failures });
  const gate = deferred(), firstDone = deferred(); let settled = false;
  const fanout = parallel([async () => { firstDone.resolve(); return 'first'; }, async () => { await gate.promise; return 'second'; }, async () => { throw Error('intentional'); }]).then(r => { settled = true; return r; });
  await firstDone.promise;
  assert.equal(settled, false);
  gate.resolve();
  const barrierResult = await fanout;
  assert.equal(JSON.stringify(barrierResult), '["first","second",null]');
  await assert.rejects(parallel([Promise.resolve('bad')]), /functions, not promises/);
  output.observations.push({ invariant: 'parallel waits for every thunk, preserves order, turns failures into null, and rejects promise inputs', result: barrierResult });
  context.opts = { schema: { type: 'object', properties: { b: { type: 'number' }, a: { type: 'string' } } }, model: 'm', label: 'first', phase: 'Scan' };
  const original = vm.runInContext('No("task", opts, "seed")', context);
  context.opts.label = 'renamed'; context.opts.phase = 'Verify';
  assert.equal(vm.runInContext('No("task", opts, "seed")', context), original);
  context.opts.model = 'other';
  assert.notEqual(vm.runInContext('No("task", opts, "seed")', context), original);
  const nextOriginal = vm.runInContext('No("next", {}, "' + original + '")', context);
  context.opts.model = 'other'; const changed = vm.runInContext('No("task", opts, "seed")', context);
  const nextChanged = vm.runInContext('No("next", {}, "' + changed + '")', context);
  assert.notEqual(nextOriginal, nextChanged);
  output.observations.push({ invariant: 'journal keys chain through the previous key; model changes invalidate downstream keys; display label/phase do not change keys', original, changed, nextOriginal, nextChanged });
  vm.runInContext(expression('var:Or'), context);
  vm.runInContext(vm.runInContext(expression('var:Or'), context), context);
  for (const code of ['Date.now()', 'new Date()', 'Math.random()']) assert.throws(() => vm.runInContext(code, context));
  assert.equal(vm.runInContext('new Date("2020-01-01").getUTCFullYear()', context), 2020);
  output.observations.push({ invariant: 'determinism shim rejects live clocks and randomness but accepts explicit dates' });
  output.status = 'passed'; output.logs = logs;
  fs.writeFileSync(__dirname + '/semantics-probe.json', JSON.stringify(output, null, 2));
  console.log(JSON.stringify({ status: output.status, observations: output.observations.length }));
})().catch(error => { console.error(error); process.exitCode = 1; });
