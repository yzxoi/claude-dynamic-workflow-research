## Audit result: one reproducible bug (CLI crashes on a pointer ending in `-`), plus a few ambiguities

I used one Workflow run with three workers and made no follow-up dispatch. I ran the minimal repro for the one bug myself, and my own spot-checks of the library and CLI found nothing else.

### Confirmed bug
**`bin/jsonpointer` crashes with a traceback when the pointer ends in `-` and the target is an array.**

This contradicts `doc/commandline.rst`. It says an unresolvable pointer gives exit status 1 with the remaining files still processed. RFC 6901 §4 says `-` refers to a nonexistent element.

Repro, run from `scratch/lead/`:
```
printf '{"a":[1]}' > c.json; printf '{"a":[1,2,3]}' > a.json
PYTHONPATH=<workspace> python3 <workspace>/bin/jsonpointer /a/- c.json a.json; echo rc=$?
```
- **Expected:** `Could not resolve pointer: …` on stderr for each file, exit 1, and `a.json` still processed.
- **Actual:** a `TypeError: Object of type EndOfList is not JSON serializable` traceback, raised from `json.dumps` at `bin/jsonpointer:96`. That line is outside the `try` that catches `JsonPointerException`. Exit status is 1, but the second file is never processed.
- **Contrast:** `/a/9` and `/a/-/x` correctly print "Could not resolve pointer" for both files.
- **Cause:** `resolve_pointer({'a':[1]}, '/a/-')` returns `EndOfList([1])` (even with a default), and the CLI tries to serialize that object.

Whether the library should return `EndOfList` is a design question. The CLI's contract violation is clear regardless.

### Ambiguities (not counted as bugs)
- **Library:** `set_pointer({'a':(1,2)}, '/a/-', 3)` raises `AttributeError`, while `/a/0` raises `JsonPointerException`. Tuples aren't JSON.
- **Library:** a custom `__getitem__` object that raises `IndexError` is not mapped to `JsonPointerException`, so the `default` argument is ignored. The docs and tests only cover `KeyError`.
- **Class API:** `contains('/a')` and `'/a' in ptr` raise `AttributeError` for a `str` argument. `join` accepts strings, but `contains` isn't documented to.
- **Class API:** `get_parts()` returns the internal list, so mutating it changes the pointer, its equality and its hash.
- **Class API:** `join(b'/a')` yields `/…/47/97`.
- **Class API:** the `#/a` URI-fragment form is rejected. The library never claims to support it.
- **CLI:** invalid JSON or non-UTF-8 input gives a traceback, exit 1, and stops processing later files. The docs say nothing about this case.
- **CLI:** `-f` strips all trailing CR/LF, so a member name ending in a newline can't be addressed.
- **CLI:** `--indent 0` and negative values still insert newlines (Python `json.dumps` behaviour).

### Rejected
- **Library:** array-index grammar, escape order, empty-string keys, `set_pointer` `inplace` semantics, `default` handling, and `to_last`/EndOfList traversal all behaved as documented or as the RFC requires.
- **Class API:** `path`/`from_parts` round trips, `join`, `contains` direction, `__eq__`/`__hash__`, the module doctests, and a small-alphabet enumeration were all fine.
- **CLI:** the exit-status contract (0, 1, 2) and the special-character cases behaved as documented.
- **Tutorial:** `doc/tutorial.rst` doctests fail on dict key order only. That is a documentation artefact, not a library bug.

### Coverage gaps
- Each worker did about 12 hand-picked probes, with no fuzzing and no comparison against a reference implementation.
- `VERBOSE_EXCEPTIONS=False`, mutable sequences other than `list`, and `--help` text against the docs were not tested.
- I could not run `tests.py` directly. It does `import jsonpointer`, and under `-I` the workspace isn't on the path.
- The workers' ambiguity reports were not independently verified.

### Division of work and workers
Three workers ran in parallel, each with a separate scratch directory:
- `resolve-set`: resolve, set, walk, `get_part` and `to_last` against the RFC.
- `class-api`: the rest of the `JsonPointer` class.
- `cli`: `bin/jsonpointer` against `doc/commandline.rst`.

Actual worker count: 3 of the 4 allowed. All three returned results and none were retried.

### Follow-up
I did not dispatch a fourth worker. The only claimed bug was a deterministic one-line repro, so I verified it directly, as shown above. The ambiguities are documentation questions that more workers couldn't settle, and the three workers' accounts showed no discrepancy that needed investigating. No later prompt received earlier results, and no shared files were passed between workers.

- **runId:** `wf_b793799a-8e3`
- **scriptPath:** `/home/researcher/.claude/projects/research-workspace-unknown-content-probe-workspace/038bab64-a868-4ca3-981a-3a146d35bcda/workflows/scripts/jsonpointer-audit-wf_b793799a-8e3.js`
- **Evidence files:** `scratch/resolve-set/`, `scratch/class-api/`, `scratch/cli/probe.sh`, `scratch/lead/`

I did not modify any upstream source, tests or docs.
