# Phase 06: Physics Refinement & Test Gaps - Validation

## Requirements Coverage

| ID | Description | Test/Evidence | Status |
|----|-------------|---------------|--------|
| **PHY-01** | Fix Slime wall lodging | `tests/test_slime.py` | ⬜ pending |
| **PHY-02** | Refine Slime floatiness | `tests/test_slime.py` | ⬜ pending |
| **PHY-03** | Fix Projectile point-blank collision | `tests/test_projectile.py` | ⬜ pending |
| **VIS-01** | Enemy destruction animation | Manual + `tests/test_enemies.py` | ⬜ pending |
| **TST-01** | Implement Phase 01 Physics Tests | `tests/test_physics.py` | ⬜ pending |
| **ORG-01** | Phase 04 Directory Split | `ls .planning/phases/04-...` | ⬜ pending |

## Automated Verification

- `pytest tests/test_physics.py`
- `pytest tests/test_slime.py`
- `pytest tests/test_projectile.py`
- `pytest tests/test_enemies.py`

## Manual Verification

- [ ] Verify Slime movement feels "heavier" and matches Heroine's rules.
- [ ] Verify Slime doesn't jitter or get stuck when following into corners.
- [ ] Verify Projectile spit at point-blank range triggers impact effect immediately.
- [ ] Verify Enemy destruction triggers the EXPLOSION effect from `effects.py`.
- [ ] Verify Phase 04 documentation is clean in its new directory.
