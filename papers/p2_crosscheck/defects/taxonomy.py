"""CrossCheck defect taxonomy (manual 6.7 / 6.9; contract H3 is defect-conditioned).

A small, fixed catalogue of defect categories used everywhere in p2_crosscheck:

- the mutation injectors (``mutations.injectors``) plant exactly one of these
  into a self-contained toy repository;
- the detection-only verdict schema (``review_protocols.schemas``) constrains
  ``finding.defect_type`` to this enum;
- the complementarity model (``complementarity``) conditions the author x
  reviewer interaction on it (H3);
- coarse, descriptive "channel" hints (touches_api / state / serialization)
  mirror the *pre-review* signals the router is allowed to look at. The hints are
  metadata only -- they are NEVER fed to the router as labels.

Eight categories are required; ten are provided to match the manual list.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DefectType(str, Enum):
    """Defect categories. ``str`` mixin so values serialise cleanly to JSON."""

    BOUNDARY = "boundary"
    API_MISUSE = "api_misuse"
    CROSS_FILE_INCONSISTENCY = "cross_file_inconsistency"
    STATE_ORDER = "state_order"
    EXCEPTION_OMISSION = "exception_omission"
    TYPE_SERIALIZATION = "type_serialization"
    REQUIREMENT_MISREAD = "requirement_misread"
    COLLATERAL_REGRESSION = "collateral_regression"
    MISSING_TEST = "missing_test"
    PERF = "perf"

    def __str__(self) -> str:  # f"{d}" -> "boundary", not "DefectType.BOUNDARY"
        return self.value


@dataclass(frozen=True)
class DefectSpec:
    """Human-readable metadata + coarse pre-review channel hints for a defect."""

    defect: DefectType
    description: str
    touches_api: bool = False
    touches_state: bool = False
    touches_serialization: bool = False
    # Tendency of the class to be visible to a SAME-family vs a CROSS-family
    # reviewer. Used only by the SIMULATED generator to plant a complementarity
    # signal; never used as a routing label.
    same_family_detectable: bool = True
    cross_family_detectable: bool = True


_SPECS: dict[DefectType, DefectSpec] = {
    DefectType.BOUNDARY: DefectSpec(
        DefectType.BOUNDARY,
        "Off-by-one / inclusive-vs-exclusive boundary handling.",
    ),
    DefectType.API_MISUSE: DefectSpec(
        DefectType.API_MISUSE,
        "Misuse of a library/stdlib API (e.g. relying on an in-place method's "
        "None return value).",
        touches_api=True,
        cross_family_detectable=True,
        same_family_detectable=False,
    ),
    DefectType.CROSS_FILE_INCONSISTENCY: DefectSpec(
        DefectType.CROSS_FILE_INCONSISTENCY,
        "A value/contract duplicated across modules drifts out of sync.",
    ),
    DefectType.STATE_ORDER: DefectSpec(
        DefectType.STATE_ORDER,
        "Mutating state before validating it, leaving corrupt state on error.",
        touches_state=True,
    ),
    DefectType.EXCEPTION_OMISSION: DefectSpec(
        DefectType.EXCEPTION_OMISSION,
        "A required guard / raised error is dropped.",
    ),
    DefectType.TYPE_SERIALIZATION: DefectSpec(
        DefectType.TYPE_SERIALIZATION,
        "Returns a non-serialisable / wrongly-typed payload.",
        touches_serialization=True,
        cross_family_detectable=True,
        same_family_detectable=False,
    ),
    DefectType.REQUIREMENT_MISREAD: DefectSpec(
        DefectType.REQUIREMENT_MISREAD,
        "Implements a plausible-but-wrong reading of the spec (e.g. wrong sort key).",
    ),
    DefectType.COLLATERAL_REGRESSION: DefectSpec(
        DefectType.COLLATERAL_REGRESSION,
        "A local change silently breaks a dependent function elsewhere.",
    ),
    DefectType.MISSING_TEST: DefectSpec(
        DefectType.MISSING_TEST,
        "An untested edge case is handled incorrectly (author's tests don't cover it).",
    ),
    DefectType.PERF: DefectSpec(
        DefectType.PERF,
        "Correct output but blows a deterministic work/complexity budget.",
        touches_state=False,
    ),
}

# Tuple of every defect in declaration order (stable for matrix labelling).
ALL_DEFECTS: tuple[DefectType, ...] = tuple(DefectType)


def all_defect_values() -> list[str]:
    """JSON-schema-friendly list of the string values, in declaration order."""
    return [d.value for d in DefectType]


def spec(defect: DefectType) -> DefectSpec:
    return _SPECS[DefectType(defect)]


def defect_index() -> dict[str, int]:
    """Map each defect value -> stable integer index (for confusion matrices)."""
    return {d.value: i for i, d in enumerate(DefectType)}
