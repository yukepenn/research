"""Tests for shared infra: runner loop, sealed access, budget, citations,
claims/manuscript checker, dashboard, plotting."""
import os
import tempfile

import pytest

from core.adapters.base import Message, ModelResponse, ToolCall, ToolSpec
from core.adapters.mock import DeterministicMockAdapter, scripted_policy
from core.audit import claims as C
from core.budget import estimator as B
from core.citations.db import CitationDB, Source
from core.environments.base import Environment
from core.runner.loop import run_episode
from core.sealed.access import SealedAccessError, SealedTest, CUSTODIAN_ROLE
from core.tracing.events import Trajectory


# ---- a toy environment for the runner ------------------------------------
class CounterEnv(Environment):
    name = "counter"
    version = "1"

    def reset(self, seed: int = 0) -> None:
        self.value = 0
        self._log = []

    def snapshot(self) -> dict:
        return {"value": self.value}

    def tools(self):
        def _inc(args):
            self.value += int(args.get("by", 1))
            self._log.append(("inc", args))
            return {"value": self.value}
        return [ToolSpec("increment", "increment the counter",
                         {"type": "object", "properties": {"by": {"type": "integer"}}},
                         executor=_inc)]


def test_runner_executes_tools_and_reaches_goal():
    steps = [
        ModelResponse(tool_calls=[ToolCall("increment", {"by": 2}, "c1")]),
        ModelResponse(tool_calls=[ToolCall("increment", {"by": 3}, "c2")]),
        ModelResponse(text="done", finish_reason="stop"),
    ]
    adapter = DeterministicMockAdapter(policy=scripted_policy(steps))
    env = CounterEnv()
    res = run_episode(adapter, env, system="be a counter agent",
                      task_prompt="make the counter equal 5", max_steps=8)
    assert res.status == "SUCCESS"
    assert res.final_state == {"value": 5}
    assert res.usage.input_tokens > 0
    # deterministic structural fingerprint
    fp1 = res.trajectory.structural_fingerprint()
    res2 = run_episode(DeterministicMockAdapter(policy=scripted_policy(steps)),
                       CounterEnv(), system="be a counter agent",
                       task_prompt="make the counter equal 5", max_steps=8)
    assert fp1 == res2.trajectory.structural_fingerprint()


def test_runner_times_out():
    steps = [ModelResponse(tool_calls=[ToolCall("increment", {"by": 1}, "c")])]
    adapter = DeterministicMockAdapter(policy=scripted_policy(steps))
    res = run_episode(adapter, CounterEnv(), system="s", task_prompt="loop", max_steps=3)
    assert res.status == "TIMEOUT"


def test_runner_records_tool_error_without_crashing():
    steps = [ModelResponse(tool_calls=[ToolCall("nonexistent", {}, "c")]),
             ModelResponse(text="give up", finish_reason="stop")]
    adapter = DeterministicMockAdapter(policy=scripted_policy(steps))
    res = run_episode(adapter, CounterEnv(), system="s", task_prompt="t", max_steps=4)
    assert any(e.type == "tool_result" and not e.payload.get("ok")
               for e in res.trajectory.events)


# ---- sealed access -------------------------------------------------------
def test_sealed_blocks_labels_until_frozen():
    with tempfile.TemporaryDirectory() as d:
        s = SealedTest(d, "p1_toolmorph")
        s.store_labels("test", {"t1": 1, "t2": 0}, role=CUSTODIAN_ROLE)
        with pytest.raises(SealedAccessError):
            s.get_labels("test", role="method_builder")
        # custodian can always read
        assert s.get_labels("test", role=CUSTODIAN_ROLE) == {"t1": 1, "t2": 0}
        # aggregate metrics allowed pre-freeze (no labels leak)
        m = s.aggregate_metrics("test", lambda labels, preds:
                                {"acc": sum(1 for k in labels if labels[k] == preds.get(k)) / len(labels)},
                                {"t1": 1, "t2": 1}, role="method_builder")
        assert 0 <= m["acc"] <= 1
        # after freeze, method builder may read labels
        s.freeze("protohash", role=CUSTODIAN_ROLE)
        assert s.get_labels("test", role="method_builder") == {"t1": 1, "t2": 0}


def test_sealed_write_requires_custodian():
    with tempfile.TemporaryDirectory() as d:
        s = SealedTest(d, "p2_crosscheck")
        with pytest.raises(SealedAccessError):
            s.store_labels("test", {"x": 1}, role="method_builder")


# ---- budget --------------------------------------------------------------
def test_budget_estimate_gates_when_unconfigured():
    # repo budget.yaml ships with null limits and no pricing.yaml -> human gate
    est = B.estimate_experiment(paper_id="p1_toolmorph", episodes=720,
                                avg_input_tokens=1500, avg_output_tokens=400,
                                model_id="some-model", budget_key="pilot_api")
    assert est.input_tokens == 720 * 1500
    assert est.requires_human_gate  # pricing or budget unconfigured


# ---- citations -----------------------------------------------------------
def test_citation_db_verify_and_bibtex():
    db = CitationDB()
    db.add(Source(source_id="tscg2026", title="TSCG", url="https://arxiv.org/abs/2605.04107",
                  authors="Sakizli", year="2026"))
    assert db.unverified()
    db.mark_verified("tscg2026", content_hash="deadbeef")
    assert not db.unverified()
    bib = db.to_bibtex()
    assert "tscg2026" in bib and "2605.04107" in bib


# ---- claims + manuscript -------------------------------------------------
def test_claim_registry_flags_manuscript_violations():
    with tempfile.TemporaryDirectory() as d:
        reg = C.ClaimRegistry(os.path.join(d, "claims.csv"))
        reg.add(C.Claim(claim_id="cl1", paper="p1", claim_text="x",
                        status="UNTESTED", manuscript_location="sec4"))
        reg.add(C.Claim(claim_id="cl2", paper="p1", claim_text="y",
                        status="SUPPORTED", manuscript_location="sec5"))  # no evidence
        v = reg.manuscript_violations()
        assert any("cl1" in x for x in v)
        assert any("cl2" in x for x in v)
        reg.save()
        assert os.path.exists(reg.path)


def test_manuscript_number_and_citation_check():
    text = ("We observe a 12.5 point drop \\cite{tscg2026}. "
            "See Section 4. Another value 99.9 appears here [@mrdre2026].")
    rep = C.check_manuscript(
        text,
        allowed_numbers={"12.5"},          # only 12.5 came from a ledger table
        known_citation_keys={"tscg2026"},  # mrdre2026 not in DB
        ignore_numbers={"4"},              # section ref
    )
    assert "99.9" in rep.untraceable_numbers
    assert "mrdre2026" in rep.missing_citation_keys
    assert not rep.ok


# ---- dashboard -----------------------------------------------------------
def test_dashboard_builds_report():
    from core.dashboard.status import build_status_report
    report = build_status_report()
    assert "# Research Status" in report
    assert "p1_toolmorph" in report
    assert "Human decisions required" in report
