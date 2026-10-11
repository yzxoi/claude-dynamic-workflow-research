// @bun @bytecode
// Claude Code is a Beta product per Anthropic's Commercial Terms of Service.
// By using Claude Code, you agree that all code acceptance or rejection decisions you make,
// and the associated conversations in context, constitute Feedback under Anthropic's Commercial Terms,
// and may be used to improve Anthropic's products, including training models.
// You are responsible for reviewing any code suggestions before use.

// (c) Anthropic PBC. All rights reserved. Use is subject to the Legal Agreements outlined here: https://code.claude.com/docs/en/legal-and-compliance.

// Version: 2.1.296
import{ze}from"/$bunfs/root/chunk-yjc18bey.js";import{pr}from"/$bunfs/root/chunk-nqc6v990.js";import{Lbe,j$,RR,G3,qRs,Utn}from"/$bunfs/root/chunk-e4eky0pj.js";import{execFile as c}from"child_process";var l=1e4,Zwo=250,o=null,u;function b6s(){return u===!0}function w6s(){return G3().lastKnown}function E6s(e){G3().lastKnown=e}function s(e){return new Promise((n)=>{try{c("security",["find-generic-password","-a",RR(),"-w","-s",e],{encoding:"utf-8",timeout:l,windowsHide:!0},(t,i)=>{let a=Boolean(t&&"killed"in t&&t.killed);n(a?null:{stdout:t?null:i?.trim()||null})})}catch{n(null)}})}function eEo(){let e=pr();if(o||e)return;let n=G3(),t=n.generation;n.legacyApiKeyPrefetch="pending";let i=s(j$(Lbe)).then((r)=>{if(r?.stdout)Utn(n,!0,t);if(r)qRs(r.stdout,t,n)}),a=s(j$()).then((r)=>{if(r&&n.legacyApiKeyPrefetch==="pending")n.legacyApiKeyPrefetch=r});o=Promise.all([i,a]).then(()=>{})}async function $tn(e){if(!o)return;await(e===void 0?o:ze(o,e))}function WAr(){let e=G3().legacyApiKeyPrefetch;return e==="pending"?null:e}function GAr(){G3().legacyApiKeyPrefetch=null}
export{Zwo,b6s,w6s,E6s,eEo,$tn,WAr,GAr};
