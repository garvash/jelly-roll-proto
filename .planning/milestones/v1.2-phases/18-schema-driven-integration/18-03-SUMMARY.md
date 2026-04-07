---
phase: 18-schema-driven-integration
plan: 03
subsystem: schema
tags: [testing, integration, schema, converter-contract]
dependency_graph:
  requires: [18-01]
  provides: [schema-mutation-test, converter-contract-verification]
  affects: [tests/test_schema.py]
tech_stack:
  added: []
  patterns: [schema-mutation-test, contract-presence-verification]
key_files:
  created: []
  modified:
    - tests/test_schema.py
decisions:
  - "Integration tests verify existing schema data (pass immediately) -- correct for verification-type TDD"
  - "SCHEMA-03 partially satisfied: game-side contract sections verified present; converter code changes deferred per D-14"
metrics:
  duration: 53s
  completed: "2026-04-05T16:12:21Z"
---

# Phase 18 Plan 03: Schema Mutation Test & Converter Contract Summary

Schema mutation integration test proves dynamic tile lookup (Success Criterion 3) and converter contract sections verified present in entity-schema.json (SCHEMA-03 partial).

## What Was Done

### Task 1: Schema mutation integration test and converter contract verification

Added two test functions to `tests/test_schema.py`:

1. **`test_schema_mutation()`** -- Copies entity-schema.json to a temp file, mutates IntGrid 1 tile_coords from `[0,1]` to `[5,5]`, calls `schema.init(tmp_path)`, verifies `get_val_to_tile()[1] == (5,5)`. Proves Success Criterion 3: changing a tile mapping in the schema changes the game's lookup result without code edits.

2. **`test_converter_contract_sections()`** -- Loads entity-schema.json directly and asserts `converter_mapping`, `intgrid` (with `values` sub-key), `entities`, and `simplified_export` sections are all present. Verifies SCHEMA-03 partial: the shared schema contains all sections the pml-to-ldtk converter needs.

**Commit:** `e6cbca3`

## Verification Results

- `python -m pytest tests/test_schema.py -x -q` -- 20 passed, 1 xfailed
- `python -m pytest tests/test_schema.py::test_schema_mutation -x -q` -- passed
- `python -m pytest tests/test_schema.py::test_converter_contract_sections -x -q` -- passed

## Deviations from Plan

None -- plan executed exactly as written.

## Out-of-Scope Discovery

- `tests/test_map_identification.py` fails with `ImportError: cannot import name 'TILE_GATE'` -- this is a pre-existing issue related to Plan 18-02's TILE_* constant removal, handled by the parallel agent executing that plan.

## Known Stubs

None.

## Self-Check: PASSED

- tests/test_schema.py: FOUND
- 18-03-SUMMARY.md: FOUND
- Commit e6cbca3: FOUND
