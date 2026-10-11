const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const parser = require('@babel/parser');
const root = __dirname;
const dest = path.join(root, 'prompts');
fs.mkdirSync(dest, { recursive: true });
const manifest = [];
function save(name, text, source, kind) {
  const file = path.join(dest, name);
  fs.writeFileSync(file, text);
  manifest.push({ path: 'prompts/' + name, source, kind, bytes: Buffer.byteLength(text), sha256: crypto.createHash('sha256').update(text).digest('hex') });
}
function parse(name) {
  const text = fs.readFileSync(path.join(root, 'bun-files', name), 'utf8');
  return { text, ast: parser.parse(text, { sourceType: 'module' }) };
}
function walk(node, visit, parent) {
  if (!node || typeof node !== 'object') return;
  if (node.type) visit(node, parent);
  for (const [key, value] of Object.entries(node)) {
    if (['loc', 'start', 'end', 'extra', 'comments', 'tokens'].includes(key)) continue;
    if (Array.isArray(value)) value.forEach(item => walk(item, visit, node));
    else if (value && typeof value === 'object') walk(value, visit, node);
  }
}
function codeWithoutImports(parsed) {
  return parsed.ast.program.body.filter(n => !['ImportDeclaration', 'ExportNamedDeclaration', 'ExportAllDeclaration'].includes(n.type)).map(n => parsed.text.slice(n.start, n.end)).join('\n');
}
const author = parse('chunk-62rej6c1.js');
const authorContext = vm.createContext({ BW: '▸', a: {}, yt: 'Agent', oCe: () => undefined, X0: 'workflow-authoring', hR: 4096 });
vm.runInContext(codeWithoutImports(author), authorContext, { timeout: 1000 });
for (const [name, expr] of [
  ['workflow-tool-with-skill.txt', 'O1r(true)'],
  ['workflow-tool-inline-reference.txt', 'O1r(false)'],
  ['workflow-authoring.txt', 'I1r()'],
]) save(name, vm.runInContext(expr, authorContext), 'bun-files/chunk-62rej6c1.js', 'rendered-pure-prompt-function');
const guideline = parse('chunk-c5zwk83v.js');
const guidelineContext = vm.createContext({});
const pureGuidelineCode = guideline.ast.program.body.filter(node =>
  node.type === 'VariableDeclaration' && node.declarations.some(d => d.id.name === 'n') ||
  node.type === 'FunctionDeclaration' && ['f', 'd', 'eys'].includes(node.id.name)
).map(node => guideline.text.slice(node.start, node.end)).join('\n');
vm.runInContext(pureGuidelineCode, guidelineContext, { timeout: 1000 });
for (const size of ['small', 'medium', 'large']) {
  for (const isDefault of [false, true]) {
    const suffix = vm.runInContext(`eys(${JSON.stringify(size)}, ${isDefault})`, guidelineContext);
    const variant = size + (isDefault ? '-default' : '-configured');
    save('size-guideline-' + variant + '.txt', suffix, 'bun-files/chunk-c5zwk83v.js', 'rendered-pure-size-guideline-function');
    if (isDefault && size !== 'large') {
      for (const hasSkill of [false, true]) {
        const lead = vm.runInContext(`O1r(${hasSkill})`, authorContext);
        save('workflow-tool-complete-' + (hasSkill ? 'with-skill' : 'inline') + '-' + size + '.txt', lead + '\n\n' + suffix,
          'bun-files/chunk-62rej6c1.js + chunk-c5zwk83v.js + NQr from chunk-04v7vxqn.js', 'rendered-composite-tool-prompt-variant');
      }
    }
  }
}
authorContext.a.CLAUDE_CODE_SUBAGENT_MODEL_FORCE = true;
save('workflow-authoring-model-forced.txt', vm.runInContext('I1r()', authorContext), 'bun-files/chunk-62rej6c1.js', 'rendered-pure-prompt-function');
const runtime = parse('chunk-hedqf2m1.js');
for (const node of runtime.ast.program.body) {
  if (node.type !== 'VariableDeclaration') continue;
  for (const d of node.declarations) {
    if (!['ks', 'ys', 'bs', 'Ss'].includes(d.id.name)) continue;
    const text = vm.runInNewContext(runtime.text.slice(d.init.start, d.init.end), { Ea: 'StructuredOutput' });
    save({ ks: 'worker-text-system.txt', ys: 'custom-worker-text-suffix.txt', bs: 'custom-worker-structured-suffix.txt', Ss: 'worker-structured-system.txt' }[d.id.name], text, 'bun-files/chunk-hedqf2m1.js:' + d.init.loc.start.line, 'rendered-literal');
  }
}
const provenance = parse('chunk-6f3cp7aa.js');
for (const node of provenance.ast.program.body) {
  if (node.type !== 'VariableDeclaration') continue;
  for (const d of node.declarations) {
    if (!['i', 'u', 'd', 'a'].includes(d.id.name)) continue;
    save('provenance-' + ({ i: 'computed-task', u: 'user-request', d: 'assistant-context', a: 'automated-trigger' }[d.id.name]) + '.txt', vm.runInNewContext(provenance.text.slice(d.init.start, d.init.end)), 'bun-files/chunk-6f3cp7aa.js', 'literal-concatenation');
  }
}
const bundled = parse('chunk-qajs04tk.js');
const builtins = [];
const builtinContext = vm.createContext({ czo: (script, options) => builtins.push({ script, options }), k: () => false });
vm.runInContext(codeWithoutImports(bundled), builtinContext, { timeout: 1000 });
vm.runInContext('a()', builtinContext, { timeout: 1000 });
fs.mkdirSync(path.join(root, 'builtins'), { recursive: true });
builtins.forEach((item, index) => {
  const file = 'builtins/deep-research-' + index + '.js';
  fs.writeFileSync(path.join(root, file), item.script);
  manifest.push({ path: file, source: 'bun-files/chunk-qajs04tk.js', kind: 'rendered-bundled-workflow', bytes: Buffer.byteLength(item.script), sha256: crypto.createHash('sha256').update(item.script).digest('hex') });
});
for (const name of ['chunk-c5zwk83v.js', 'chunk-sfn1dbxq.js', 'chunk-hedqf2m1.js', 'chunk-36h1wcr3.js']) {
  const parsed = parse(name);
  let count = 0;
  walk(parsed.ast.program, (node, parent) => {
    if (!['StringLiteral', 'TemplateLiteral'].includes(node.type)) return;
    if (node.type === 'StringLiteral' && parent?.type === 'TemplateElement') return;
    const raw = parsed.text.slice(node.start, node.end);
    if (raw.length < 200 || !/workflow|StructuredOutput|Ultracode/i.test(raw)) return;
    const label = parent?.type === 'VariableDeclarator' ? parent.id.name : node.start;
    save('template-' + name.replace('.js', '') + '-' + label + '-' + (++count) + '.js.txt', raw, 'bun-files/' + name + ':utf16:' + node.start + '-' + node.end, 'exact-source-expression-unrendered');
  });
}
for (const name of ['bug-hunter-t77r14b6.md', 'deep-researcher-kr59y5yh.md', 'watchlist-scanner-kfkrzjrr.md', 'explainer-video-maker-sm29032a.md']) {
  save('cloud-template-' + name, fs.readFileSync(path.join(root, 'bun-files', name), 'utf8'), 'bun-files/' + name, 'shipped-console-agent-template-not-server-internal-prompt');
}
save('cloud-template-performance-tuner-6c866b59.md', fs.readFileSync(path.join(root, 'decoded-assets/performance-tuner-6c866b59.md'), 'utf8'), 'bun-files/performance-tuner-6c866b59.md.zst decoded with zstd; see decoded-assets-manifest.json', 'shipped-console-agent-template-not-server-internal-prompt');
fs.writeFileSync(path.join(root, 'prompt-manifest.json'), JSON.stringify(manifest, null, 2));
console.log(JSON.stringify({ files: manifest.length, rendered: manifest.filter(x => !x.kind.includes('unrendered')).length, builtins: builtins.length, bytes: manifest.reduce((n, x) => n + x.bytes, 0) }));
