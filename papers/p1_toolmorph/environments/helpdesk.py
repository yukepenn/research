"""Helpdesk microenvironment (ticket workflow: priority, assignment, status)."""
from __future__ import annotations

from core.adapters.base import ToolSpec
from core.environments.base import Environment

_PRIORITIES = ["low", "medium", "high", "urgent"]
_STATUSES = ["open", "in_progress", "resolved", "closed"]


class HelpdeskEnv(Environment):
    name = "helpdesk"
    version = "1"

    def reset(self, seed: int = 0) -> None:
        self._tickets: dict[str, dict] = {}
        self._counter = 0
        self._log: list[dict] = []

    def snapshot(self) -> dict:
        return {"tickets": {k: dict(v) for k, v in sorted(self._tickets.items())}}

    def _open_ticket(self, args: dict) -> dict:
        prio = args.get("priority", "medium")
        if prio not in _PRIORITIES:
            raise ValueError("invalid_argument: bad priority")
        self._counter += 1
        tid = f"tkt{self._counter}"
        self._tickets[tid] = {"subject": args["subject"], "priority": prio,
                              "status": "open", "assignee": None}
        self._log.append({"op": "open", "id": tid})
        return {"ticket_id": tid, "status": "open"}

    def _assign(self, args: dict) -> dict:
        tid = args["ticket_id"]
        if tid not in self._tickets:
            raise ValueError("not_found: no such ticket")
        self._tickets[tid]["assignee"] = args["assignee"]
        if self._tickets[tid]["status"] == "open":
            self._tickets[tid]["status"] = "in_progress"
        self._log.append({"op": "assign", "id": tid})
        return {"ticket_id": tid, "assignee": args["assignee"],
                "status": self._tickets[tid]["status"]}

    def _set_status(self, args: dict) -> dict:
        tid = args["ticket_id"]; status = args["status"]
        if tid not in self._tickets:
            raise ValueError("not_found: no such ticket")
        if status not in _STATUSES:
            raise ValueError("invalid_argument: bad status")
        cur = self._tickets[tid]["status"]
        # cannot resolve an unassigned ticket
        if status == "resolved" and not self._tickets[tid]["assignee"]:
            raise ValueError("conflict: cannot resolve unassigned ticket")
        # cannot reopen a closed ticket
        if cur == "closed":
            raise ValueError("conflict: ticket is closed")
        self._tickets[tid]["status"] = status
        self._log.append({"op": "status", "id": tid, "to": status})
        return {"ticket_id": tid, "status": status}

    def _set_priority(self, args: dict) -> dict:
        tid = args["ticket_id"]; prio = args["priority"]
        if tid not in self._tickets:
            raise ValueError("not_found: no such ticket")
        if prio not in _PRIORITIES:
            raise ValueError("invalid_argument: bad priority")
        self._tickets[tid]["priority"] = prio
        self._log.append({"op": "priority", "id": tid})
        return {"ticket_id": tid, "priority": prio}

    def tools(self) -> list[ToolSpec]:
        prio_enum = {"type": "string", "enum": _PRIORITIES}
        status_enum = {"type": "string", "enum": _STATUSES}
        return [
            ToolSpec("open_ticket", "Open a support ticket.",
                     {"type": "object",
                      "properties": {"subject": {"type": "string"}, "priority": prio_enum},
                      "required": ["subject"]}, executor=self._open_ticket),
            ToolSpec("assign_ticket", "Assign a ticket to an agent.",
                     {"type": "object",
                      "properties": {"ticket_id": {"type": "string"},
                                     "assignee": {"type": "string"}},
                      "required": ["ticket_id", "assignee"]}, executor=self._assign),
            ToolSpec("set_status", "Change ticket status.",
                     {"type": "object",
                      "properties": {"ticket_id": {"type": "string"}, "status": status_enum},
                      "required": ["ticket_id", "status"]}, executor=self._set_status),
            ToolSpec("set_priority", "Change ticket priority.",
                     {"type": "object",
                      "properties": {"ticket_id": {"type": "string"}, "priority": prio_enum},
                      "required": ["ticket_id", "priority"]}, executor=self._set_priority),
        ]
