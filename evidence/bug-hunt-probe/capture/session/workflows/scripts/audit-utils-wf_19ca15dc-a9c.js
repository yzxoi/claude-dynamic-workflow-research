export const meta = {
  name: 'audit-utils',
  description: 'Per-module audit with runtime proofs under scratch/',
  phases: [{ title: 'Audit', detail: 'one worker per module' }],
}
const nativeAgent = agent;
let dispatched = 0;
agent = (...callArgs) => {
  if (dispatched >= 4) throw new Error("Experiment limit: four worker invocations");
  dispatched++;
  return nativeAgent(...callArgs);
};
const SCHEMA = {type:'object',properties:{findings:{type:'array',items:{type:'object',properties:{
  module:{type:'string'},title:{type:'string'},status:{enum:['confirmed','rejected','unverified']},
  repro:{type:'string'},expected:{type:'string'},actual:{type:'string'}},
  required:['module','title','status','repro','expected','actual']}}},required:['findings']};
const mods = ['inventory','pricing','scheduling','metrics'];
phase('Audit');
const res = await parallel(mods.map(m => () => agent(
`Audit ${m}.py in the current directory against its section of SPEC.md. Read only those two files (Read tool). Find implementation bugs vs the spec, including boundary conditions, mutation, and state-on-failure. For each suspected bug, write a small proof script under scratch/${m}_proof.py (python3 stdlib, run with python3 from the workspace root, importing the module via sys.path) and RUN it; report actual output. Mark status confirmed only if the runtime output contradicts the spec; rejected if you checked and it conforms; unverified otherwise. Do not modify the audited modules or SPEC.md. Keep the result concise.`,
{label:'audit:'+m, phase:'Audit', schema:SCHEMA})));
return res;