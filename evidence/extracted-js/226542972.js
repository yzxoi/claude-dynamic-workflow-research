// @bun @bytecode
// Claude Code is a Beta product per Anthropic's Commercial Terms of Service.
// By using Claude Code, you agree that all code acceptance or rejection decisions you make,
// and the associated conversations in context, constitute Feedback under Anthropic's Commercial Terms,
// and may be used to improve Anthropic's products, including training models.
// You are responsible for reviewing any code suggestions before use.

// (c) Anthropic PBC. All rights reserved. Use is subject to the Legal Agreements outlined here: https://code.claude.com/docs/en/legal-and-compliance.

// Version: 2.1.296
import{K,vwe}from"/$bunfs/root/chunk-4bw62nzm.js";import{BTe,pat,JNe,fat,mat}from"/$bunfs/root/chunk-dcbjzzq8.js";import{ZL}from"/$bunfs/root/chunk-14rnebpd.js";import{Sz,fze,Xwt,zke,gK,pE}from"/$bunfs/root/chunk-sfn1dbxq.js";import{TDn}from"/$bunfs/root/chunk-zm79vshj.js";import{oKe}from"/$bunfs/root/chunk-v6b7qas5.js";import{aF}from"/$bunfs/root/chunk-9sq8whr4.js";import{Xln}from"/$bunfs/root/chunk-73xj7y72.js";import{tme}from"/$bunfs/root/chunk-eekc1esz.js";import{ONe}from"/$bunfs/root/chunk-e7hwd1w0.js";function rNt(e,o,t,i){aF("conversation_reset"),ZL("conversation_reset"),pE(gK),fat(),JNe(),BTe(),mat(),pat(),oKe();let r=K();for(let s of ONe(e.sessionHooksRegistry,r))e.sessionHooksRegistry.remove(r,"Stop",s);t(),fze(),e.markConversationRemote?.(),TDn(e.readFileState),Sz(e.memorySelector),vwe(),zke(o),Xln(i,r,o.map((s)=>s.uuid)),e.applyMessageOp({type:"replace-all",messages:Xwt(o)}),tme(!0)}
export{rNt};
