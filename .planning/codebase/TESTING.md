# Testing Patterns

**Analysis Date:** 2025-05-22

## Test Framework

**Runner:**
- `pytest`: Used for running all tests.

**Assertion Library:**
- Standard Python `assert`.

**Run Commands:**
```bash
pytest                  # Run all tests
pytest -f               # Watch mode (if pytest-watch installed)
pytest --cov=src        # Coverage (if pytest-cov installed)
```

## Test File Organization

**Location:**
- Separate directory: All tests are located in `tests/`.

**Naming:**
- `test_*.py`: Matches `pytest` discovery rules.

**Structure:**
```
tests/
├── test_physics.py
├── test_player.py
├── test_slime.py
├── test_health.py
└── ...
```

## Test Structure

**Suite Organization:**
```python
import pytest
from unittest.mock import MagicMock
from src.entities.player import Player

def test_player_take_damage():
    # Setup
    player = Player(10, 10, MagicMock())
    
    # Action
    success = player.take_damage(1)
    
    # Assertion
    assert success == True
    assert player.hp == PLAYER_MAX_HP - 1
```

**Patterns:**
- Setup pattern: Arrange (instantiate entity), Act (call method), Assert (check results).
- Teardown pattern: Not explicitly used (unit tests are generally stateless).
- Assertion pattern: Direct checks on object attributes (e.g., `assert player.hp == 9`).

## Mocking

**Framework:**
- `unittest.mock`: Specifically `MagicMock` and `patch`.

**Patterns:**
```python
# Mocking pyxel before imports that use it
import sys
from unittest.mock import MagicMock
mock_pyxel = MagicMock()
sys.modules['pyxel'] = mock_pyxel

# Local patching
with patch('src.entities.player.pyxel', mock_pyxel):
    # test logic here
```

**What to Mock:**
- `pyxel`: The external game engine must be mocked to avoid display initialization.
- `LevelMap`: Passed as a mock to entity tests to simulate collision behavior.
- `Game`: Used to isolate entity logic from the main game loop.

**What NOT to Mock:**
- Constants: `src.core.constants.py` is usually imported directly for valid values.

## Fixtures and Factories

**Test Data:**
- Manual instantiation: Most tests create the necessary objects locally.
- Stubs: Classes like `MockLevelMap` provide controlled environments for tests.

**Location:**
- Defined within the test files or as simple mock objects in the test directory.

## Coverage

**Requirements:**
- Not explicitly enforced but extensive coverage of core entities exists.

**View Coverage:**
```bash
pytest --cov=src
```

## Test Types

**Unit Tests:**
- Focus on entity state and simple physics (e.g., `tests/test_health.py`, `tests/test_slime.py`).

**Integration Tests:**
- Combat interactions, room transitions, and enemy spawning (e.g., `tests/test_phase05_gaps.py`).

**E2E Tests:**
- Not detected: Full gameplay simulations are not yet implemented.

## Common Patterns

**Async Testing:**
- Not applicable: The engine is frame-based and synchronous.

**Error Testing:**
- Ensuring methods return `False` or do not change state when invalid actions are taken (e.g., taking damage during invulnerability).

---

*Testing analysis: 2025-05-22*
