"""Phase 32 FUS-04 plan 32-02 contract tests for the fusion protocol package.

Verifies the public surface of `src/fusion/`:
    - `src.fusion.protocol` defines `FusionAbility` (typing.Protocol, @runtime_checkable)
      with the D-09 hook surface and `TickResult` (frozen+slots dataclass).
    - `src.fusion` re-exports `FusionAbility` and `TickResult`.
    - `TickResult` constructs cleanly with the documented default + named-arg shapes.
    - A duck-typed object satisfying the D-09 surface passes `isinstance` against
      `FusionAbility` (structural typing per RESEARCH § Pattern 2 recommendation).

Greenfield tests; no existing module behavior is exercised. Per Phase 32 D-09,
the Protocol shape is locked — these tests are the canary that subsequent plans
(04 FusionManager, 05 DrillDive/Pogo) build against.
"""
from dataclasses import is_dataclass
from typing import Protocol


def test_protocol_module_imports() -> None:
    """`from src.fusion.protocol import FusionAbility, TickResult` succeeds."""
    from src.fusion.protocol import FusionAbility, TickResult  # noqa: F401


def test_package_reexports_protocol_symbols() -> None:
    """`from src.fusion import FusionAbility, TickResult` succeeds and matches."""
    from src.fusion import FusionAbility as PkgAbility, TickResult as PkgResult
    from src.fusion.protocol import FusionAbility, TickResult

    assert PkgAbility is FusionAbility
    assert PkgResult is TickResult


def test_tickresult_is_frozen_slots_dataclass() -> None:
    """TickResult MUST be a frozen+slots dataclass per RESEARCH § Pattern 1."""
    from src.fusion.protocol import TickResult

    assert is_dataclass(TickResult)
    # Frozen dataclasses raise FrozenInstanceError on attribute assignment.
    result = TickResult()
    try:
        result.dx = 99.0  # type: ignore[misc]
    except Exception:
        pass
    else:
        raise AssertionError("TickResult is not frozen — assignment succeeded.")


def test_tickresult_default_construction() -> None:
    """TickResult() with no args constructs with documented zero-defaults."""
    from src.fusion.protocol import TickResult

    result = TickResult()
    assert result.dx == 0.0
    assert result.dy == 0.0
    assert result.request_exit is False
    assert result.exit_reason is None


def test_tickresult_full_kwargs_construction() -> None:
    """The behavior contract: TickResult(dx=1.0, dy=2.0, request_exit=True,
    exit_reason='solid_landing') constructs and exposes the supplied values."""
    from src.fusion.protocol import TickResult

    result = TickResult(dx=1.0, dy=2.0, request_exit=True, exit_reason="solid_landing")
    assert result.dx == 1.0
    assert result.dy == 2.0
    assert result.request_exit is True
    assert result.exit_reason == "solid_landing"


def test_tickresult_juice_empty_exit_shape() -> None:
    """Documented exit reasons include 'juice_empty' (drill-dive juice→0 path)."""
    from src.fusion.protocol import TickResult

    result = TickResult(request_exit=True, exit_reason="juice_empty")
    assert result.request_exit is True
    assert result.exit_reason == "juice_empty"


def test_fusionability_is_a_protocol() -> None:
    """FusionAbility MUST inherit from typing.Protocol (D-09)."""
    from src.fusion.protocol import FusionAbility

    assert issubclass(FusionAbility, Protocol)


def test_fusionability_runtime_checkable() -> None:
    """@runtime_checkable allows isinstance() against duck-typed conformers
    (RESEARCH § Pattern 2 recommendation; enables FusionManager construction-time
    validation in Plan 04)."""
    from src.fusion.protocol import FusionAbility, TickResult

    class FakeAbility:
        id = "fake"
        requires_fused = True

        def can_activate(self, player, slime) -> bool:
            return True

        def on_enter(self, player, slime, context: dict) -> None:
            return None

        def on_tick(self, player, slime, dt: float) -> TickResult:
            return TickResult()

        def on_exit(self, player, slime, reason: str) -> None:
            return None

        def on_event(self, name: str, data: dict) -> None:
            return None

    assert isinstance(FakeAbility(), FusionAbility)


def test_fusionability_rejects_incomplete_class() -> None:
    """A class missing one of the 5 D-09 methods is NOT a FusionAbility instance.
    Demonstrates @runtime_checkable detects shape violations at FusionManager
    construction time (Plan 04 wiring guard)."""
    from src.fusion.protocol import FusionAbility

    class IncompleteAbility:
        id = "incomplete"
        requires_fused = False

        def can_activate(self, player, slime) -> bool:
            return True

        # Missing on_enter / on_tick / on_exit / on_event

    assert not isinstance(IncompleteAbility(), FusionAbility)


def test_fusionability_has_d09_method_surface() -> None:
    """The D-09 5-method surface (can_activate, on_enter, on_tick, on_exit,
    on_event) is present on the Protocol — frozen contract for Plans 04+05."""
    from src.fusion.protocol import FusionAbility

    for name in ("can_activate", "on_enter", "on_tick", "on_exit", "on_event"):
        assert hasattr(FusionAbility, name), f"D-09 method missing: {name}"


def test_fusionability_d09_class_attrs_declared() -> None:
    """`id: str` and `requires_fused: bool` are class-level annotations on the
    Protocol per D-09. Verified via __annotations__ since Protocol does not
    materialize them as descriptors."""
    from src.fusion.protocol import FusionAbility

    annotations = getattr(FusionAbility, "__annotations__", {})
    assert "id" in annotations, "D-09 attr missing: id"
    assert "requires_fused" in annotations, "D-09 attr missing: requires_fused"
