# Phase 23: Converter Handoff - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 23-converter-handoff
**Areas discussed:** Document scope & depth, Relationship to existing doc, Migration guidance level, Entity-schema as source of truth, File placement, Converter mapping updates

---

## Document Scope & Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Before/after diff table | Focused: just the changed values. A converter dev reads it in 2 minutes. | |
| Full migration guide | Comprehensive: before/after plus explanations, affected code, edge cases. | |
| You decide | Claude picks the right depth based on CONV-01 through CONV-03. | ✓ |

**User's choice:** You decide
**Notes:** Claude has discretion on depth, guided by CONV-03 ("maintainer can know exactly what to change without inspecting game code").

---

## Relationship to Existing Doc

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone migration note | One-time v1.3 migration document. PML-to-LDtk Converter.md stays as living reference. | ✓ |
| Replace existing doc | Merge everything into CONVERTER-HANDOFF.md, delete the existing doc. | |
| Update existing + add handoff | Update both docs — two docs, different purposes. | |

**User's choice:** Standalone migration note
**Notes:** No duplication — handoff focuses on "what changed since v1.0.0".

---

## Migration Guidance Level

| Option | Description | Selected |
|--------|-------------|----------|
| What changed only | Before/after values and breaking changes. Let maintainer figure out the how. | |
| What + suggested actions | Before/after plus concrete hints like 'update grid_size parser'. | |
| You decide | Claude picks based on CONV-03 success criterion. | ✓ |

**User's choice:** You decide
**Notes:** Claude has discretion, guided by CONV-03.

---

## Entity-Schema as Source of Truth

| Option | Description | Selected |
|--------|-------------|----------|
| Inline everything | All before/after values directly in the handoff. Self-contained. | ✓ |
| Reference + highlights | Point at entity-schema.json but highlight breaking changes inline. | |
| Just reference schema | Mostly say 'read entity-schema.json v2.0.0'. Minimal duplication. | |

**User's choice:** Inline everything
**Notes:** Self-contained document — no cross-referencing entity-schema.json required.

---

## File Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Repo root | Next to PML-to-LDtk Converter.md. Maximum discoverability. | ✓ |
| assets/ directory | Next to entity-schema.json. Groups schema docs together. | |
| docs/ directory | New directory for converter documentation. | |

**User's choice:** Repo root (Recommended)
**Notes:** None.

---

## Converter Mapping Updates

| Option | Description | Selected |
|--------|-------------|----------|
| Include mapping section | Explicitly document any converter_mapping changes, even if just confirming no change. | |
| Skip if unchanged | Only mention converter_mapping if something actually changed. | ✓ |

**User's choice:** Skip if unchanged
**Notes:** Don't pad the document with "no change" sections.

---

## Claude's Discretion

- Document depth and structure (D-01)
- Whether to include suggested converter actions (D-03)

## Deferred Ideas

None — discussion stayed within phase scope.
