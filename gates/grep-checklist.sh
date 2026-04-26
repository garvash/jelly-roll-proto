#!/bin/bash
# gates/grep-checklist.sh -- Phase 31.5 Gate 1
#
# Exits non-zero if any cut symbol survives in src/.
#
# Per CONTEXT D-18 Gate 1 + RESEARCH Code Examples Example 4. The 16 core
# CUT_SYMBOLS list comes from D-18 verbatim; the input.py and physics-schema
# specific checks come from D-18's targeted-file checks. This script is the
# automatable proof-of-work that the Phase 31.5 strip eliminated every cut-
# ability code path from src/.
#
# Usage:
#     bash gates/grep-checklist.sh
#     # exit 0 = Gate 1 PASS; exit 1 = at least one symbol survives
#
# Invariants this script enforces:
#   1. None of the 16 cut symbols appears anywhere in src/ (word-boundary match)
#   2. The "dash" key is gone from src/core/input.py _ACTION_MAP
#   3. The "dash" / "slime_ram" / "charge_shot" / "boost" tuning groups
#      are gone from assets/physics-schema.json

set -e
FAIL=0

# 16 cut symbols enumerated by CONTEXT D-18 Gate 1.
CUT_SYMBOLS=(
    "ram_dx"
    "has_shield"
    "charge_shot"
    "start_boost"
    "start_dash"
    "start_ram"
    "RAMMING"
    "DASHING"
    "BOOSTING"
    "CHARGING_SHOT"
    "is_holding_position"
    "HOLD_SCAN_RANGE"
    "DASH_PICKUP"
    "SHIELD_PICKUP"
    "BOOST_PICKUP"
    "SHIELD_T2"
)

for sym in "${CUT_SYMBOLS[@]}"; do
    if git grep -nE "\b$sym\b" -- 'src/' > /dev/null 2>&1; then
        echo "FAIL: '$sym' still present in src/"
        git grep -nE "\b$sym\b" -- 'src/'
        FAIL=1
    fi
done

# input.py-specific check: the "dash" action key must be gone from _ACTION_MAP.
if grep -nE '^\s*"dash"\s*:' src/core/input.py > /dev/null 2>&1; then
    echo "FAIL: 'dash' still in src/core/input.py _ACTION_MAP"
    grep -nE '^\s*"dash"\s*:' src/core/input.py
    FAIL=1
fi

# physics-schema.json specific check: the four cut tuning groups must be gone.
if grep -nE '^\s*"(dash|slime_ram|charge_shot|boost)"\s*:' assets/physics-schema.json > /dev/null 2>&1; then
    echo "FAIL: cut tuning group still present in assets/physics-schema.json"
    grep -nE '^\s*"(dash|slime_ram|charge_shot|boost)"\s*:' assets/physics-schema.json
    FAIL=1
fi

if [[ $FAIL -eq 0 ]]; then
    echo "Gate 1 PASS: all cut symbols absent from src/"
fi

exit $FAIL
