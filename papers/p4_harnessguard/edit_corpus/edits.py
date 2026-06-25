"""Controlled atomic harness edits H -> H' (P4-DATA-002, manual 8.6 / 8.8).

Each Edit is an atomic change to ONE harness component, with a structured
contract: declared intent, expected improvements/risks, static diff features.
The declared fields are author signals, NOT ground truth (manual 8.8: intent
"can be author-generated but must not be treated as truth").

Edits are grouped into lineages (here: one lineage per component family) so the
leave-one-lineage-out split removes a whole correlated group with no leakage.

The corpus deliberately mixes improvement / neutral / harmful edits, and is
constructed so regressions are STRUCTURED (concentrated on the tasks that
exercise the edited component / carry the declared risk), which is what makes
the H2 "selection beats random" measurement valid and detectable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.util import sha256_obj
from papers.p4_harnessguard.modular_harness import HarnessConfig, default_harness


@dataclass
class Edit:
    edit_id: str
    component: str
    lineage: str
    change_scope: str  # local | global
    natural_language_intent: str
    expected_improvements: list[str]
    expected_risks: list[str]
    static_features: dict  # {lines_changed, prompt_tokens_changed, tools_affected}
    base_config: HarnessConfig
    mutation: dict
    intended_effect: str  # declared: improvement | neutral | harmful (NOT a label)
    _new_config: HarnessConfig = field(default=None, repr=False, compare=False)

    @property
    def new_config(self) -> HarnessConfig:
        if self._new_config is None:
            object.__setattr__(self, "_new_config",
                               self.base_config.with_changes(**self.mutation))
        return self._new_config

    def code_diff_hash(self) -> str:
        return sha256_obj({"base": self.base_config.to_dict(), "mutation": self.mutation})


_D = default_harness()


def all_edits() -> list[Edit]:
    edits: list[Edit] = []

    # ---- retry lineage --------------------------------------------------
    edits.append(Edit(
        "e_retry_drop", "retry", "lin_retry", "local",
        "drop retries to cut latency on flaky tools",
        expected_improvements=[], expected_risks=["slow"],
        static_features={"lines_changed": 6, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"retry_count": 0}, intended_effect="harmful"))
    edits.append(Edit(
        "e_retry_raise", "retry", "lin_retry", "local",
        "retry more aggressively to recover transient tool failures",
        expected_improvements=["error_recovery"], expected_risks=["non_idempotent"],
        static_features={"lines_changed": 4, "prompt_tokens_changed": 0, "tools_affected": 1},
        base_config=_D, mutation={"retry_count": 5}, intended_effect="improvement"))
    edits.append(Edit(
        "e_retry_neutral", "retry", "lin_retry", "local",
        "bump retry budget by one (cosmetic)",
        expected_improvements=["error_recovery"], expected_risks=[],
        static_features={"lines_changed": 2, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"retry_count": 3}, intended_effect="neutral"))

    # ---- verifier lineage ----------------------------------------------
    edits.append(Edit(
        "e_verifier_remove", "verifier", "lin_verifier", "local",
        "remove the output verifier to save a model call",
        expected_improvements=[], expected_risks=["slow"],
        static_features={"lines_changed": 18, "prompt_tokens_changed": 40, "tools_affected": 0},
        base_config=_D, mutation={"verifier_on": False}, intended_effect="harmful"))
    edits.append(Edit(
        "e_verifier_threshold", "verifier", "lin_verifier", "local",
        "raise the verifier acceptance threshold to be stricter",
        expected_improvements=["verification"], expected_risks=["slow"],
        static_features={"lines_changed": 3, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"verifier_threshold": 0.95}, intended_effect="harmful"))
    edits.append(Edit(
        "e_verifier_add", "verifier", "lin_verifier", "local",
        "add a read-after-write verification step for correctness",
        expected_improvements=["verification"], expected_risks=["non_idempotent"],
        static_features={"lines_changed": 22, "prompt_tokens_changed": 55, "tools_affected": 1},
        base_config=_D.with_changes(verifier_on=False),
        mutation={"verifier_on": True}, intended_effect="improvement"))
    edits.append(Edit(
        "e_verifier_desc", "verifier", "lin_verifier", "local",
        "reword verifier prompt; tiny threshold nudge",
        expected_improvements=["verification"], expected_risks=[],
        static_features={"lines_changed": 5, "prompt_tokens_changed": 30, "tools_affected": 0},
        base_config=_D, mutation={"verifier_threshold": 0.6}, intended_effect="neutral"))

    # ---- stopping lineage ----------------------------------------------
    edits.append(Edit(
        "e_stop_aggressive", "stopping", "lin_stopping", "local",
        "stop earlier to reduce wasted steps",
        expected_improvements=[], expected_risks=["slow"],
        static_features={"lines_changed": 7, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"stopping_aggressiveness": 0.9}, intended_effect="harmful"))
    edits.append(Edit(
        "e_stop_relaxed", "stopping", "lin_stopping", "local",
        "let the agent run longer to finish long tasks",
        expected_improvements=["long_horizon"],
        expected_risks=["irreversible", "early_termination"],
        static_features={"lines_changed": 7, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"stopping_aggressiveness": 0.0}, intended_effect="improvement"))
    edits.append(Edit(
        "e_stop_neutral", "stopping", "lin_stopping", "local",
        "minor stopping-rule tweak",
        expected_improvements=[], expected_risks=[],
        static_features={"lines_changed": 2, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"stopping_aggressiveness": 0.35}, intended_effect="neutral"))

    # ---- memory lineage -------------------------------------------------
    edits.append(Edit(
        "e_mem_lower", "memory", "lin_memory", "local",
        "shrink memory retrieval to cut context cost",
        expected_improvements=[], expected_risks=["context_loss"],
        static_features={"lines_changed": 3, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"memory_topk": 0}, intended_effect="harmful"))
    edits.append(Edit(
        "e_mem_raise", "memory", "lin_memory", "local",
        "retrieve more memories to improve grounding",
        expected_improvements=["memory"],
        expected_risks=["distraction", "memory_overflow"],
        static_features={"lines_changed": 3, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"memory_topk": 8}, intended_effect="improvement"))

    # ---- context lineage ------------------------------------------------
    edits.append(Edit(
        "e_ctx_tail", "context", "lin_context", "local",
        "switch context compression to cheap tail-truncation",
        expected_improvements=[], expected_risks=["context_loss"],
        static_features={"lines_changed": 12, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"context_truncation": "tail"}, intended_effect="harmful"))
    edits.append(Edit(
        "e_ctx_none", "context", "lin_context", "local",
        "disable truncation, keep full context",
        expected_improvements=["long_context"], expected_risks=[],
        static_features={"lines_changed": 9, "prompt_tokens_changed": 0, "tools_affected": 0},
        base_config=_D, mutation={"context_truncation": "none"}, intended_effect="improvement"))

    # ---- tool-ordering lineage -----------------------------------------
    edits.append(Edit(
        "e_tool_reverse", "tool_ordering", "lin_tool", "global",
        "reorder the tool palette (refactor)",
        expected_improvements=[], expected_risks=["tool_sensitive"],
        static_features={"lines_changed": 14, "prompt_tokens_changed": 60, "tools_affected": 8},
        base_config=_D, mutation={"tool_ordering": "reversed"}, intended_effect="neutral"))
    edits.append(Edit(
        "e_tool_alpha", "tool_ordering", "lin_tool", "global",
        "sort tools alphabetically for readability",
        expected_improvements=[], expected_risks=["tool_sensitive"],
        static_features={"lines_changed": 10, "prompt_tokens_changed": 45, "tools_affected": 8},
        base_config=_D, mutation={"tool_ordering": "alpha"}, intended_effect="neutral"))

    return edits


def edits_by_lineage() -> dict[str, list[Edit]]:
    out: dict[str, list[Edit]] = {}
    for e in all_edits():
        out.setdefault(e.lineage, []).append(e)
    return out


def lineages() -> list[str]:
    seen: list[str] = []
    for e in all_edits():
        if e.lineage not in seen:
            seen.append(e.lineage)
    return seen


def get_edit(edit_id: str) -> Edit:
    for e in all_edits():
        if e.edit_id == edit_id:
            return e
    raise KeyError(edit_id)
