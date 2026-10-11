// @bun @bytecode
// Claude Code is a Beta product per Anthropic's Commercial Terms of Service.
// By using Claude Code, you agree that all code acceptance or rejection decisions you make,
// and the associated conversations in context, constitute Feedback under Anthropic's Commercial Terms,
// and may be used to improve Anthropic's products, including training models.
// You are responsible for reviewing any code suggestions before use.

// (c) Anthropic PBC. All rights reserved. Use is subject to the Legal Agreements outlined here: https://code.claude.com/docs/en/legal-and-compliance.

// Version: 2.1.296
import"/$bunfs/root/chunk-nfna65jh.js";import"/$bunfs/root/chunk-fdxhcr6b.js";import"/$bunfs/root/chunk-4bw62nzm.js";import"/$bunfs/root/chunk-k1419ccf.js";import"/$bunfs/root/chunk-76anb6yt.js";import"/$bunfs/root/chunk-886tf6ja.js";import"/$bunfs/root/chunk-yjc18bey.js";import"/$bunfs/root/chunk-ae84tp6z.js";import"/$bunfs/root/chunk-gsnbskq4.js";import"/$bunfs/root/chunk-nqc6v990.js";import"/$bunfs/root/chunk-5b8s3gnd.js";import"/$bunfs/root/chunk-gyf58rwf.js";import"/$bunfs/root/chunk-tat46164.js";import"/$bunfs/root/chunk-ax7r0qj7.js";import"/$bunfs/root/chunk-phz47asr.js";import"/$bunfs/root/chunk-yvnhkg35.js";import"/$bunfs/root/chunk-mke1mg83.js";import"/$bunfs/root/chunk-p9frg3mj.js";import"/$bunfs/root/chunk-tadwrn0a.js";import"/$bunfs/root/chunk-g1yqb0n4.js";import{wi}from"/$bunfs/root/chunk-phm7wwmz.js";import"/$bunfs/root/chunk-ts42ykgs.js";import"/$bunfs/root/chunk-ngwfw4c8.js";import{so}from"/$bunfs/root/chunk-dyspjvns.js";import"/$bunfs/root/chunk-xaes9ysz.js";function c(t,o,a,d){let e=(i,r)=>typeof i==="string"&&typeof r==="string"&&i===a(r),s=e(t.saved_pages_dir,o)?`[A quickstart in this conversation saved reference pages of this type on disk in ${so([t.saved_pages_dir])}; its result lists them, so those are not attached here.]`:"";if(t.not_listed===!0)return s===""?"":`

${s}`;let n=s===""?"":` ${s}`;if(typeof t.saved_system==="string"&&e(t.saved_system_dir,t.saved_system))return`

[A quickstart in this conversation already listed the design systems and saved the files of ${wi(t.saved_system,"(unrecognized address)")} on disk \u2014 skip the instructions' step that lists them and reads that README; its result lists the saved files.]${n}`;return s===""?null:`${d}${n}`}export{c as afterQuickstartSavedLine};
