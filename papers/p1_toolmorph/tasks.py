"""ToolMorph base tasks with reference solutions and invariant oracles.

Each task carries:
- env_factory: builds a fresh stateful environment
- task_prompt: natural-language goal shown to the agent (real-model study)
- plan: a deterministic reference solution (sequence of canonical tool calls)
  proving the task is solvable and the oracle is correct (P1-DATA-002)
- goal: an INVARIANT predicate over the final hidden state, so any correct
  trajectory passes — the oracle scores outcomes, not fixed paths (manual 5.6)

Environment ids are deterministic (evt1, ord1, tkt1, ...) given the reference
plan order, so plans can reference them by literal id.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from papers.p1_toolmorph.environments.calendar import CalendarEnv
from papers.p1_toolmorph.environments.helpdesk import HelpdeskEnv
from papers.p1_toolmorph.environments.inventory import InventoryEnv


@dataclass
class Task:
    task_id: str
    domain: str
    env_factory: Callable
    task_prompt: str
    plan: list[tuple[str, dict]]
    goal: Callable[[dict], bool]
    difficulty: str = "multi_call"
    family: str = field(default="")

    def __post_init__(self):
        if not self.family:
            self.family = self.domain


SYSTEM_PROMPT = (
    "You are a precise tool-using assistant. Use the provided tools to reach the "
    "goal. Make only the calls you need. Stop when the goal is satisfied."
)


def _calendar_tasks() -> list[Task]:
    return [
        Task("cal_create_basic", "calendar", CalendarEnv,
             "Schedule a 'Standup' meeting from slot 9 to 10 for alice.",
             [("create_event", {"title": "Standup", "start": 9, "end": 10,
                                 "attendees": ["alice"]})],
             lambda s: any(e["title"] == "Standup" and e["start"] == 9 and e["end"] == 10
                           and e["status"] == "active" and "alice" in e["attendees"]
                           for e in s["events"].values()),
             difficulty="single_call"),
        Task("cal_avoid_conflict", "calendar", CalendarEnv,
             "Book 'A' (9-10) and 'B' (10-11) for bob so neither overlaps.",
             [("create_event", {"title": "A", "start": 9, "end": 10, "attendees": ["bob"]}),
              ("create_event", {"title": "B", "start": 10, "end": 11, "attendees": ["bob"]})],
             lambda s: sum(1 for e in s["events"].values()
                           if e["status"] == "active" and "bob" in e["attendees"]) == 2),
        Task("cal_move", "calendar", CalendarEnv,
             "Create 'Review' (9-10) for cara then move it to 11-12.",
             [("create_event", {"title": "Review", "start": 9, "end": 10, "attendees": ["cara"]}),
              ("move_event", {"event_id": "evt1", "start": 11, "end": 12})],
             lambda s: any(e["title"] == "Review" and e["start"] == 11 and e["end"] == 12
                           for e in s["events"].values())),
        Task("cal_cancel", "calendar", CalendarEnv,
             "Create 'Old' (8-9) for dan and then cancel it.",
             [("create_event", {"title": "Old", "start": 8, "end": 9, "attendees": ["dan"]}),
              ("cancel_event", {"event_id": "evt1"})],
             lambda s: any(e["title"] == "Old" and e["status"] == "cancelled"
                           for e in s["events"].values())),
    ]


def _inventory_tasks() -> list[Task]:
    return [
        Task("inv_order", "inventory", InventoryEnv,
             "Place an order for 3 units of sku-a.",
             [("place_order", {"sku": "sku-a", "quantity": 3})],
             lambda s: s["stock"]["sku-a"] == 7
             and any(o["sku"] == "sku-a" and o["quantity"] == 3 and o["status"] == "placed"
                     for o in s["orders"].values()),
             difficulty="single_call"),
        Task("inv_order_refund", "inventory", InventoryEnv,
             "Order 2 of sku-b, then refund that order.",
             [("place_order", {"sku": "sku-b", "quantity": 2}),
              ("refund_order", {"order_id": "ord1"})],
             lambda s: s["stock"]["sku-b"] == 5
             and any(o["status"] == "refunded" for o in s["orders"].values())),
        Task("inv_restock_then_order", "inventory", InventoryEnv,
             "Restock 4 units of sku-c, then order 4 of sku-c.",
             [("restock", {"sku": "sku-c", "quantity": 4}),
              ("place_order", {"sku": "sku-c", "quantity": 4})],
             lambda s: s["stock"]["sku-c"] == 0
             and any(o["sku"] == "sku-c" and o["quantity"] == 4 for o in s["orders"].values())),
    ]


def _helpdesk_tasks() -> list[Task]:
    return [
        Task("hd_open_assign_resolve", "helpdesk", HelpdeskEnv,
             "Open a ticket 'login broken', assign to ren, then mark resolved.",
             [("open_ticket", {"subject": "login broken", "priority": "high"}),
              ("assign_ticket", {"ticket_id": "tkt1", "assignee": "ren"}),
              ("set_status", {"ticket_id": "tkt1", "status": "resolved"})],
             lambda s: any(t["status"] == "resolved" and t["assignee"] == "ren"
                           for t in s["tickets"].values())),
        Task("hd_priority", "helpdesk", HelpdeskEnv,
             "Open ticket 'server down' at medium, then raise priority to urgent.",
             [("open_ticket", {"subject": "server down", "priority": "medium"}),
              ("set_priority", {"ticket_id": "tkt1", "priority": "urgent"})],
             lambda s: any(t["priority"] == "urgent" for t in s["tickets"].values()),
             difficulty="multi_call"),
        Task("hd_assign_close", "helpdesk", HelpdeskEnv,
             "Open 'disk full', assign to sam, resolve, then close it.",
             [("open_ticket", {"subject": "disk full", "priority": "low"}),
              ("assign_ticket", {"ticket_id": "tkt1", "assignee": "sam"}),
              ("set_status", {"ticket_id": "tkt1", "status": "resolved"}),
              ("set_status", {"ticket_id": "tkt1", "status": "closed"})],
             lambda s: any(t["status"] == "closed" and t["assignee"] == "sam"
                           for t in s["tickets"].values())),
    ]


def all_tasks() -> list[Task]:
    return _calendar_tasks() + _inventory_tasks() + _helpdesk_tasks()


def tasks_by_domain() -> dict[str, list[Task]]:
    out: dict[str, list[Task]] = {}
    for t in all_tasks():
        out.setdefault(t.domain, []).append(t)
    return out
