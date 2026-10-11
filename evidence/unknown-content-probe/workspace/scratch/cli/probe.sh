export PYTHONPATH=/research/claude-workflow-research/unknown-content-probe/workspace
J="python3 /research/claude-workflow-research/unknown-content-probe/workspace/bin/jsonpointer"
cd /research/claude-workflow-research/unknown-content-probe/workspace/scratch/cli
printf '{ "a": [1, 2, 3], "": "empty", "a/b": 1, "m~n": 2, "x y": 3, "é": 4, "a\\n": 5 }' > a.json
printf '{"b": 1, "a": {"b":[1,3,4]}}' > b.json
printf 'notjson' > bad.json
run(){ echo "--- ${@:3}"; "$@"; echo "[rc=$?]"; }
run $J /a/1 a.json
run $J --indent 2 /a a.json b.json
run $J --indent 0 /a a.json
run $J --indent -1 /a a.json
run $J --indent x /a a.json
run $J /a missing.json a.json
run $J /a a.json missing.json
run $J /zzz a.json b.json a.json
run $J /a bad.json
run $J '/a/b' a.json
run $J '/a~1b' a.json
run $J '/m~0n' a.json
run $J '/' a.json
run $J '/é' a.json
run $J '/a/-' a.json
run $J '/a/01' a.json
run $J '/a/x' a.json
run $J '/a/~2' a.json
printf '' > empty.txt; run $J -f empty.txt a.json
printf '\n' > nl.txt; run $J -f nl.txt a.json
printf '/\n\n' > nl2.txt; run $J -f nl2.txt a.json
printf '/a\r\n' > crlf.txt; run $J -f crlf.txt a.json
printf '/a\r' > cr.txt; run $J -f cr.txt a.json
printf '/x y\n' > sp.txt; run $J -f sp.txt a.json
printf '/é\n' > u.txt; run $J -f u.txt a.json
run $J -f nofile.txt a.json
run $J -p '' a.json
run $J -p /a -- a.json b.json
run $J -p /a
run $J
run $J -p /a -f nl.txt a.json
run $J --pointer=/a a.json
run $J --pointer-file=crlf.txt a.json
run $J -p a a.json
run $J -p '/a' '/a' a.json
run $J -p -x a.json
run $J -v
echo '{"a":1}' | $J /a -; echo "[rc=$?]"
run $J /a.b a.json
