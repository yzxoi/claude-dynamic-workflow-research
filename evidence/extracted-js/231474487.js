// @bun @bytecode
// Claude Code is a Beta product per Anthropic's Commercial Terms of Service.
// By using Claude Code, you agree that all code acceptance or rejection decisions you make,
// and the associated conversations in context, constitute Feedback under Anthropic's Commercial Terms,
// and may be used to improve Anthropic's products, including training models.
// You are responsible for reviewing any code suggestions before use.

// (c) Anthropic PBC. All rights reserved. Use is subject to the Legal Agreements outlined here: https://code.claude.com/docs/en/legal-and-compliance.

// Version: 2.1.296
import"/$bunfs/root/chunk-nfna65jh.js";import"/$bunfs/root/chunk-fdxhcr6b.js";import"/$bunfs/root/chunk-4bw62nzm.js";import"/$bunfs/root/chunk-k1419ccf.js";import"/$bunfs/root/chunk-76anb6yt.js";import"/$bunfs/root/chunk-886tf6ja.js";import"/$bunfs/root/chunk-yjc18bey.js";import"/$bunfs/root/chunk-ae84tp6z.js";import{c}from"/$bunfs/root/chunk-gsnbskq4.js";import"/$bunfs/root/chunk-gyf58rwf.js";import"/$bunfs/root/chunk-nqc6v990.js";import"/$bunfs/root/chunk-tat46164.js";import"/$bunfs/root/chunk-ax7r0qj7.js";import{ht}from"/$bunfs/root/chunk-r2vtj1kh.js";import{sr}from"/$bunfs/root/chunk-nnctmda1.js";var e="claudecode/editResult",l="1";function i(o,t){return o===ht&&sr(t)&&t[e]===l}async function m(o,t){if(o.isError===!0||t.subagentFrameResult===void 0)return o;try{if(await t.subagentFrameResultHolds?.()===!1)return o}catch(r){return c(r),o}return{...o,_meta:{...o._meta,[e]:t.subagentFrameResult}}}export{i as asksForEditResult,m as withEditResult};
