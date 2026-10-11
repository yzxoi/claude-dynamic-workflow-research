export const meta = {
  name: 'context-probe',
  description: 'Tiny 3-agent diagnostic: observe in parallel, then merge',
  phases: [{ title: 'Observe' }, { title: 'Merge' }],
}
const OBS = {type:'object',properties:{worker:{type:'string'},seed:{type:'string'},leadOnlyValue:{type:['string','null']}},required:['worker','seed','leadOnlyValue']}
const MRG = {type:'object',properties:{receivedA:{type:'object'},receivedB:{type:'object'},artifactContents:{type:'string'},leadOnlyValue:{type:['string','null']}},required:['receivedA','receivedB','artifactContents','leadOnlyValue']}
const common = 'Work only inside the current workspace; no Bash, network, or Git. Keep the result under 150 words. leadOnlyValue must be null unless you can already see an actual "LEAD_ONLY" value in your incoming context.'
phase('Observe')
const [a, b] = await parallel([
  () => agent(`You are Worker A. Read seed.txt. Also write artifact-a.txt containing exactly: artifact-A-85192. Return worker "A", the seed contents, and leadOnlyValue. ${common}`, {label:'worker-A', phase:'Observe', schema:OBS}),
  () => agent(`You are Worker B. Read seed.txt. Return worker "B", the seed contents, and leadOnlyValue. ${common}`, {label:'worker-B', phase:'Observe', schema:OBS}),
])
phase('Merge')
const c = await agent(`You are Worker C. Received from A: ${JSON.stringify(a)}\nReceived from B: ${JSON.stringify(b)}\nRead artifact-a.txt. Return receivedA, receivedB (exact objects above), artifactContents, and leadOnlyValue. ${common}`, {label:'worker-C', phase:'Merge', schema:MRG})
return {a, b, c}