#!/usr/bin/env bash
# Run every problem's tests, each inside its own folder so `from solution import ...` resolves.
#
#   ./run_tests.sh                 # run all problems
#   ./run_tests.sh parking_lot     # run only folders whose path matches "parking_lot"
#
# A problem with no solution.py yet shows as "skipped" — that's expected until you write it.

set -uo pipefail
cd "$(dirname "$0")"

filter="${1:-}"
pass=0; fail=0; skip=0; failed_names=()

while IFS= read -r testfile; do
    dir="$(dirname "$testfile")"
    name="${dir#problems/}"
    if [[ -n "$filter" && "$dir" != *"$filter"* ]]; then
        continue
    fi
    out="$(cd "$dir" && python3 -m unittest test_solution.py 2>&1)"
    if echo "$out" | grep -q "OK (skipped"; then
        # skipped because solution.py is missing (module-level setUpModule skip)
        if echo "$out" | grep -q "Ran 0 tests"; then
            printf '  \033[33m•\033[0m %s (no solution.py yet)\n' "$name"
            skip=$((skip+1))
            continue
        fi
    fi
    if echo "$out" | tail -3 | grep -qE '^(OK|OK \(skipped)'; then
        ran="$(echo "$out" | grep -oE 'Ran [0-9]+ test' | grep -oE '[0-9]+')"
        printf '  \033[32m✓\033[0m %s (%s tests)\n' "$name" "${ran:-?}"
        pass=$((pass+1))
    else
        printf '  \033[31m✗\033[0m %s\n' "$name"
        echo "$out" | tail -6 | sed 's/^/      /'
        fail=$((fail+1)); failed_names+=("$name")
    fi
done < <(find problems -name test_solution.py | sort)

echo
echo "Summary: ${pass} passed, ${fail} failed, ${skip} awaiting solution.py"
if (( fail > 0 )); then
    printf 'Failed: %s\n' "${failed_names[*]}"
    exit 1
fi
