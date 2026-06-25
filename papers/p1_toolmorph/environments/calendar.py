"""Calendar microenvironment (P1-DATA-001A).

Deterministic, stateful, hidden authoritative state with a transaction log and
an invariant-based final-state oracle. Tools take CANONICAL arguments; the
ToolMorph transforms mutate only the model-visible schema, never these
executors, so any change in agent behaviour is attributable to the interface.
"""
from __future__ import annotations

from core.adapters.base import ToolSpec
from core.environments.base import Environment


class CalendarEnv(Environment):
    name = "calendar"
    version = "1"

    def reset(self, seed: int = 0) -> None:
        self._events: dict[str, dict] = {}
        self._counter = 0
        self._log: list[dict] = []

    # ---- hidden state -------------------------------------------------
    def snapshot(self) -> dict:
        return {"events": {k: dict(v) for k, v in sorted(self._events.items())}}

    def _new_id(self) -> str:
        self._counter += 1
        return f"evt{self._counter}"

    @staticmethod
    def _overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
        return a_start < b_end and b_start < a_end

    # ---- canonical tool implementations -------------------------------
    def _create_event(self, args: dict) -> dict:
        title = args["title"]
        start = int(args["start"]); end = int(args["end"])
        attendees = list(args.get("attendees", []))
        if end <= start:
            raise ValueError("invalid_argument: end must be after start")
        for ev in self._events.values():
            if self._overlaps(start, end, ev["start"], ev["end"]) and \
                    set(attendees) & set(ev["attendees"]):
                raise ValueError("conflict: attendee double-booked")
        eid = self._new_id()
        self._events[eid] = {"title": title, "start": start, "end": end,
                             "attendees": attendees, "status": "active"}
        self._log.append({"op": "create", "id": eid})
        return {"event_id": eid, "start": start, "end": end}

    def _move_event(self, args: dict) -> dict:
        eid = args["event_id"]
        if eid not in self._events or self._events[eid]["status"] != "active":
            raise ValueError("not_found: no such active event")
        start = int(args["start"]); end = int(args["end"])
        if end <= start:
            raise ValueError("invalid_argument: end must be after start")
        ev = self._events[eid]
        for other_id, other in self._events.items():
            if other_id == eid or other["status"] != "active":
                continue
            if self._overlaps(start, end, other["start"], other["end"]) and \
                    set(ev["attendees"]) & set(other["attendees"]):
                raise ValueError("conflict: attendee double-booked")
        ev["start"], ev["end"] = start, end
        self._log.append({"op": "move", "id": eid})
        return {"event_id": eid, "start": start, "end": end}

    def _cancel_event(self, args: dict) -> dict:
        eid = args["event_id"]
        if eid not in self._events:
            raise ValueError("not_found: no such event")
        self._events[eid]["status"] = "cancelled"
        self._log.append({"op": "cancel", "id": eid})
        return {"event_id": eid, "status": "cancelled"}

    def _check_conflict(self, args: dict) -> dict:
        start = int(args["start"]); end = int(args["end"])
        attendees = set(args.get("attendees", []))
        clashes = [eid for eid, ev in self._events.items()
                   if ev["status"] == "active"
                   and self._overlaps(start, end, ev["start"], ev["end"])
                   and attendees & set(ev["attendees"])]
        return {"conflict": bool(clashes), "events": sorted(clashes)}

    def _list_events(self, args: dict) -> dict:
        return {"events": [
            {"event_id": eid, **{k: ev[k] for k in ("title", "start", "end", "status")}}
            for eid, ev in sorted(self._events.items())]}

    # ---- canonical schemas --------------------------------------------
    def tools(self) -> list[ToolSpec]:
        return [
            ToolSpec("create_event", "Create a calendar event.",
                     {"type": "object",
                      "properties": {
                          "title": {"type": "string"},
                          "start": {"type": "integer", "description": "start slot"},
                          "end": {"type": "integer", "description": "end slot"},
                          "attendees": {"type": "array", "items": {"type": "string"}},
                      },
                      "required": ["title", "start", "end"]},
                     executor=self._create_event),
            ToolSpec("move_event", "Move an existing event to a new time.",
                     {"type": "object",
                      "properties": {
                          "event_id": {"type": "string"},
                          "start": {"type": "integer"},
                          "end": {"type": "integer"}},
                      "required": ["event_id", "start", "end"]},
                     executor=self._move_event),
            ToolSpec("cancel_event", "Cancel an event.",
                     {"type": "object",
                      "properties": {"event_id": {"type": "string"}},
                      "required": ["event_id"]},
                     executor=self._cancel_event),
            ToolSpec("check_conflict", "Check whether a time range conflicts.",
                     {"type": "object",
                      "properties": {
                          "start": {"type": "integer"}, "end": {"type": "integer"},
                          "attendees": {"type": "array", "items": {"type": "string"}}},
                      "required": ["start", "end"]},
                     executor=self._check_conflict),
            ToolSpec("list_events", "List events.",
                     {"type": "object", "properties": {}},
                     executor=self._list_events),
        ]
