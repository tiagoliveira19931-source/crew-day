#!/usr/bin/env bash
# Runs every Crew Day test against dev/crew-day.html. Needs python3 + playwright (pre-installed in Claude's cloud workspace).
# Usage: bash dev/run_tests.sh        → prints one line per test and "ALL PASSED" or the failures.
set -u
DEV="$(cd "$(dirname "$0")" && pwd)"
cp "$DEV/crew-day.html" /home/claude/crew-day.html   # tests read the app from this fixed path
cd "$DEV/tests"
fail=0
for t in *.py; do
  out=$(TZ=Europe/London timeout 300 python3 "$t" /home/claude/crew-day.html roster2.ics 2>&1 | grep -v agent-proxy)
  last=$(printf "%s" "$out" | tail -1)
  if printf "%s" "$last" | grep -q "ERRORS: none"; then echo "ok    $t"; else echo "FAIL  $t: $last"; fail=1; fi
done
[ $fail = 0 ] && echo "ALL PASSED" || { echo "SOME TESTS FAILED"; exit 1; }
