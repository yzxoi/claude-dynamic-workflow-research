// @bun @bytecode
// Claude Code is a Beta product per Anthropic's Commercial Terms of Service.
// By using Claude Code, you agree that all code acceptance or rejection decisions you make,
// and the associated conversations in context, constitute Feedback under Anthropic's Commercial Terms,
// and may be used to improve Anthropic's products, including training models.
// You are responsible for reviewing any code suggestions before use.

// (c) Anthropic PBC. All rights reserved. Use is subject to the Legal Agreements outlined here: https://code.claude.com/docs/en/legal-and-compliance.

// Version: 2.1.296
import{t}from"/$bunfs/root/chunk-gyf58rwf.js";import{L$}from"/$bunfs/root/chunk-64ag51qf.js";import{xe}from"/$bunfs/root/chunk-sfn1dbxq.js";import{k6e}from"/$bunfs/root/chunk-j8hqhz0c.js";import{YEe}from"/$bunfs/root/chunk-dr63q6zt.js";import{Ws}from"/$bunfs/root/chunk-6p4kvraw.js";function A8n(e,r,s){if(s.get(e)?.status!=="running")return;s.updateTranscript(e,(a)=>({...a,messages:k6e(a.messages,r)}))}function _1t(e,r,s,a){let n=s.get(e);if(!n||Ws(n.status)){t(`Dropping message for teammate task ${e}: task status is "${n?.status}"`);return}s.update(e,(m)=>({...m,pendingUserMessages:[...m.pendingUserMessages,{text:r,origin:a}]})),s.updateTranscript(e,(m)=>({...m,messages:k6e(m.messages,xe({content:r,origin:a}))}))}function g1r(e,r,s){let a=YEe(L$(r,s),e);if(a?.status==="running")a.retryWake?.emit()}
export{A8n,_1t,g1r};
