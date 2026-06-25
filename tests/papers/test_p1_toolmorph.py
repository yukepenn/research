"""P1 ToolMorph Tier-0 tests: environments, oracle, equivalence, metamorphic."""
import pytest

from papers.p1_toolmorph.environments.calendar import CalendarEnv
from papers.p1_toolmorph.environments.helpdesk import HelpdeskEnv
from papers.p1_toolmorph.environments.inventory import InventoryEnv
from papers.p1_toolmorph.metamorphic import paired_degradation, run_task
from papers.p1_toolmorph.oracles.state_oracle import (
    empty_state_fails, reference_solution_passes)
from papers.p1_toolmorph.property_tests.equivalence import run_equivalence_suite
from papers.p1_toolmorph.sim_agents import codec_adapter, flaky_adapter
from papers.p1_toolmorph.tasks import all_tasks
from papers.p1_toolmorph.transforms.dsl import apply_transform
from papers.p1_toolmorph.transforms.families import all_strict_transforms, StructuralNesting


# ---- environments --------------------------------------------------------
def test_calendar_conflict_and_move():
    env = CalendarEnv(); env.reset()
    tools = {t.name: t for t in env.tools()}
    tools["create_event"].executor({"title": "A", "start": 9, "end": 10, "attendees": ["x"]})
    with pytest.raises(ValueError, match="conflict"):
        tools["create_event"].executor({"title": "B", "start": 9, "end": 10, "attendees": ["x"]})
    tools["move_event"].executor({"event_id": "evt1", "start": 11, "end": 12})
    assert env.snapshot()["events"]["evt1"]["start"] == 11


def test_inventory_insufficient_stock_and_refund():
    env = InventoryEnv(); env.reset()
    tools = {t.name: t for t in env.tools()}
    with pytest.raises(ValueError, match="conflict"):
        tools["place_order"].executor({"sku": "sku-c", "quantity": 1})  # 0 in stock
    tools["place_order"].executor({"sku": "sku-a", "quantity": 4})
    assert env.snapshot()["stock"]["sku-a"] == 6
    tools["refund_order"].executor({"order_id": "ord1"})
    assert env.snapshot()["stock"]["sku-a"] == 10


def test_helpdesk_cannot_resolve_unassigned():
    env = HelpdeskEnv(); env.reset()
    tools = {t.name: t for t in env.tools()}
    tools["open_ticket"].executor({"subject": "x", "priority": "low"})
    with pytest.raises(ValueError, match="conflict"):
        tools["set_status"].executor({"ticket_id": "tkt1", "status": "resolved"})


# ---- oracle --------------------------------------------------------------
def test_reference_solutions_pass_and_empty_fails():
    for task in all_tasks():
        assert reference_solution_passes(task), f"{task.task_id} reference plan failed oracle"
        assert empty_state_fails(task), f"{task.task_id} trivially passes empty state"


# ---- equivalence (the core Tier-0 guarantee) -----------------------------
def test_all_strict_transforms_are_state_equivalent():
    reports = run_equivalence_suite(n_request_per_tool=350, seed=7)
    total_cases = 0
    for fam, rep in reports.items():
        assert rep.ok, f"{fam}: {rep.mismatches[:2]}"
        assert rep.state_cases == len(all_tasks())
        total_cases += rep.request_cases + rep.response_cases + rep.error_cases + rep.state_cases
    # honor the manual's high-volume property-test intent
    assert total_cases >= 10000, total_cases


def test_transforms_actually_change_the_surface():
    env = CalendarEnv(); env.reset()
    create = next(t for t in env.tools() if t.name == "create_event")
    nested = apply_transform(create, StructuralNesting())
    assert nested.schema != create.schema
    assert "params" in nested.schema["properties"]


# ---- metamorphic harness: negative control -------------------------------
def test_negative_control_zero_degradation():
    """An interface-robust (codec) agent must pass under original AND every
    transform: the harness + transforms inject no artifact."""
    tasks = all_tasks()
    for transform in all_strict_transforms():
        res = paired_degradation(codec_adapter, tasks, transform, repeats=1,
                                 n_boot=500, seed=1)
        assert res.orig_success_rate == 1.0
        assert res.mut_success_rate == 1.0, f"{res.transform} broke a competent agent"
        assert abs(res.ci.point) < 1e-9


def test_pipeline_detects_planted_degradation():
    """Plant a gap (orig p=0.95, transformed p=0.5) and confirm the paired
    cluster bootstrap reports a negative difference."""
    tasks = all_tasks()
    transform = StructuralNesting()

    def agent_for(task, tr):
        p = 0.95 if tr is None else 0.5
        return flaky_adapter(task, tr, p_success=p)

    res = paired_degradation(agent_for, tasks, transform, repeats=5, n_boot=1500, seed=3)
    assert res.ci.point < 0
    assert res.mut_success_rate < res.orig_success_rate
