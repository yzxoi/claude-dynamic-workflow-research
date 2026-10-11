# Third-party sources and notices

This private repository archives research evidence. Research documents and helper scripts do not change the ownership or licensing of any third-party material. No repository-wide license is applied to the extracted distributions.

| Source | Archived material | Rights / provenance |
|---|---|---|
| Anthropic Claude Code 2.1.296 | Native/wrapper metadata, embedded files, extracted/formatted JS, bundled assets, prompts, official tarballs | Anthropic PBC, all rights reserved; the original native and wrapper LICENSE.md files are retained. Their linked legal terms remain applicable. |
| Anthropic TypeScript SDK 0.133.0 | Selected agents/sessions resources and complete npm tar | Registry metadata declares MIT; the package tar retains its original notices. [Upstream](https://github.com/anthropics/anthropic-sdk-typescript). |
| anthropics/skills | Four Managed Agents quickstarts at fixed commit dbd4588f9e1033efb41dad4bef2f7947c8993d44 | Per-file/upstream ownership and license remain applicable; no blanket license inferred from the root repository. Exact source URLs are in evidence/official-skill/comparison.json. |
| anthropics/anthropic-cli 1.40.0 | Public release metadata, help output, official macOS arm64 zip | Anthropic CLI distribution, retained as an upstream artifact. [Fixed release](https://github.com/anthropics/anthropic-cli/releases/tag/v1.40.0). |
| Bun | Selected Rust references used to decode standalone module graph | Upstream source references retained in the historical report. [Bun repository](https://github.com/oven-sh/bun); original file notices remain. |
| python-json-pointer 3.2.1 | Unmodified upstream snapshot, tests, documentation and diagnostic workspace | Copyright Stefan Kögl and contributors; BSD 3-clause notice is retained at evidence/unknown-content-probe/workspace/LICENSE.txt. Fixed commit is recorded in provenance.json. |
| RFC 6901 | Normative JSON Pointer reference in the experiment | [RFC Editor](https://www.rfc-editor.org/rfc/rfc6901), referenced for behavior; any retained original notice applies. |
| Bundled dependencies | Embedded native extensions, JS libraries, fonts, notices | Their individual copyright/license notices are preserved wherever included in the source distribution. |
| REA / rea-agents 6.3.0 | Analysis output and inventory used in research | [morluto/rea](https://github.com/morluto/rea); analysis output is evidence, not a copy of the entire REA implementation. |

Original Claude Code license notices:

- [Native LICENSE.md](evidence/native-latest/package/LICENSE.md)
- [Wrapper LICENSE.md](evidence/wrapper-latest/package/LICENSE.md)
- [python-json-pointer LICENSE.txt](evidence/unknown-content-probe/workspace/LICENSE.txt)

Publication redacts private host paths and account metadata without claiming the redacted copies are byte-identical upstream distributions. Original and published hashes are recorded separately. Official release packages contain the unmodified public distributions, rather than authenticated local state.
