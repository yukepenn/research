"""Tests for the core kernel: util, ledger, adapters, statistics."""
import os
import tempfile

import numpy as np
import pytest

from core import util
from core.adapters.base import Message, ModelResponse, ToolCall, ToolSpec
from core.adapters.mock import DeterministicMockAdapter, scripted_policy
from core.adapters.registry import BudgetGateError, get_adapter
from core.experiment_registry import ledger as L
from core.statistics import resampling as R


# ---- util ----------------------------------------------------------------
def test_canonical_json_stable_and_order_independent():
    a = {"b": 1, "a": [3, 2, 1]}
    b = {"a": [3, 2, 1], "b": 1}
    assert util.canonical_json(a) == util.canonical_json(b)
    assert util.sha256_obj(a) == util.sha256_obj(b)


def test_stable_seed_deterministic():
    assert util.stable_seed("x", 1) == util.stable_seed("x", 1)
    assert util.rng_for("k").random() == util.rng_for("k").random()


def test_content_addressed_write_idempotent():
    with tempfile.TemporaryDirectory() as d:
        h1, p1 = util.write_content_addressed(d, '{"a":1}')
        h2, p2 = util.write_content_addressed(d, '{"a":1}')
        assert h1 == h2 and p1 == p2 and os.path.exists(p1)


# ---- ledger --------------------------------------------------------------
def _entry(rl, run_id, status="SUCCESS", **kw):
    th = rl.store_trace({"run": run_id, "events": kw.pop("events", [])})
    return L.make_entry(
        run_id=run_id, paper_id="p1_toolmorph", git_commit="abc",
        task_hash="t1", environment_hash="e1", model_provider="mock",
        model_id="mock-1", harness_hash="h1", oracle_version="o1",
        raw_trace_hash=th, status=status, **kw,
    )


def test_ledger_append_verify_and_dupe_rejected():
    with tempfile.TemporaryDirectory() as d:
        rl = L.RunLedger(os.path.join(d, "ledger.jsonl"))
        rl.append(_entry(rl, "r1", cost_usd=0.01))
        rl.append(_entry(rl, "r2", status="AGENT_FAILURE"))
        ok, problems = rl.verify()
        assert ok, problems
        with pytest.raises(L.LedgerError):
            rl.append(_entry(rl, "r1"))  # duplicate run_id


def test_ledger_rejects_bad_status_and_missing_required():
    with tempfile.TemporaryDirectory() as d:
        rl = L.RunLedger(os.path.join(d, "ledger.jsonl"))
        with pytest.raises(L.LedgerError):
            _entry(rl, "rx", status="WAT")
        with pytest.raises(L.LedgerError):
            rl.append({"run_id": "z"})  # fails schema


def test_ledger_aggregate():
    with tempfile.TemporaryDirectory() as d:
        rl = L.RunLedger(os.path.join(d, "ledger.jsonl"))
        rl.append(_entry(rl, "r1", cost_usd=0.02))
        rl.append(_entry(rl, "r2", status="AGENT_FAILURE", cost_usd=0.03))
        agg = L.aggregate(rl.read_all())
        assert agg["n_runs"] == 2
        assert abs(agg["total_cost_usd"] - 0.05) < 1e-9
        assert abs(agg["success_rate"] - 0.5) < 1e-9


# ---- adapters ------------------------------------------------------------
def test_mock_adapter_deterministic_usage():
    a = DeterministicMockAdapter("mock-1", cost_per_mtok_in=1.0, cost_per_mtok_out=2.0)
    msgs = [Message("system", "you are a tool agent"), Message("user", "do x")]
    r1 = a.generate(msgs)
    r2 = a.generate(msgs)
    assert r1.text == r2.text
    assert r1.usage.input_tokens > 0
    assert r1.usage.cost_usd >= 0


def test_scripted_policy_drives_tool_calls():
    steps = [
        ModelResponse(tool_calls=[ToolCall("create", {"x": 1}, "c1")]),
        ModelResponse(text="done", finish_reason="stop"),
    ]
    a = DeterministicMockAdapter(policy=scripted_policy(steps))
    tool = ToolSpec("create", "create x", {"type": "object"})
    r1 = a.generate([Message("user", "go")], [tool])
    r2 = a.generate([Message("user", "go")], [tool])
    assert r1.tool_calls and r1.tool_calls[0].name == "create"
    assert r2.text == "done"


def test_registry_mock_ok_paid_gated():
    assert get_adapter("mock", "mock-1").provider == "mock"
    with pytest.raises(BudgetGateError):
        get_adapter("anthropic", "claude-x")  # budget not configured
    with pytest.raises(BudgetGateError):
        get_adapter("openai", "gpt-x", budget_configured=True)  # no key / not installed


# ---- statistics ----------------------------------------------------------
def test_wilson_and_clopper_pearson_bounds():
    w = R.wilson_ci(8, 10)
    assert 0 <= w.lo <= w.point <= w.hi <= 1
    cp = R.clopper_pearson_ci(0, 10)
    assert cp.lo == 0.0 and cp.hi < 1.0
    cp2 = R.clopper_pearson_ci(10, 10)
    assert cp2.hi == 1.0 and cp2.lo > 0.0


def test_mcnemar_detects_degradation():
    # strong degradation: many original-pass -> mutated-fail, few reverse
    res = R.mcnemar_test(b=20, c=2)
    assert res.p_value < 0.01
    null = R.mcnemar_test(b=5, c=5)
    assert null.p_value > 0.5


def test_paired_cluster_bootstrap_recovers_known_diff():
    rng = np.random.default_rng(0)
    n_tasks = 60
    clusters, a, b = [], [], []
    for t in range(n_tasks):
        for _ in range(3):  # 3 nested repeats per task
            clusters.append(t)
            orig = rng.random() < 0.8
            mut = rng.random() < 0.6  # ~20pt degradation
            a.append(float(orig))
            b.append(float(mut))
    ci = R.paired_cluster_bootstrap_diff(a, b, clusters, n_boot=2000, seed=1)
    assert ci.point < 0  # mutated worse than original
    assert ci.lo < ci.point < ci.hi


def test_kendall_tau_bootstrap_ranking_reversal():
    # interface A ranks model0>model1; interface B reverses it
    n_tasks = 40
    a = np.zeros((n_tasks, 2))
    b = np.zeros((n_tasks, 2))
    a[:, 0] = 0.9; a[:, 1] = 0.4
    b[:, 0] = 0.4; b[:, 1] = 0.9
    ci = R.kendall_tau_bootstrap(a, b, n_boot=1000, seed=2)
    assert ci.point < 0  # ranking flipped


def test_multiple_testing_corrections():
    pvals = [0.001, 0.01, 0.2, 0.04, 0.5]
    bh = R.benjamini_hochberg(pvals, 0.05)
    hl = R.holm(pvals, 0.05)
    assert bh[0] and not bh[2]
    assert hl[0] and not hl[4]
    # Holm is at least as conservative as BH
    assert sum(hl) <= sum(bh)
