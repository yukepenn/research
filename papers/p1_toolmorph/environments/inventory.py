"""Inventory/Orders microenvironment (numeric, multi-step, partial-failure)."""
from __future__ import annotations

from core.adapters.base import ToolSpec
from core.environments.base import Environment


class InventoryEnv(Environment):
    name = "inventory"
    version = "1"

    def reset(self, seed: int = 0) -> None:
        # deterministic starting stock
        self._stock = {"sku-a": 10, "sku-b": 5, "sku-c": 0}
        self._orders: dict[str, dict] = {}
        self._counter = 0
        self._log: list[dict] = []

    def snapshot(self) -> dict:
        return {"stock": dict(sorted(self._stock.items())),
                "orders": {k: dict(v) for k, v in sorted(self._orders.items())}}

    def _restock(self, args: dict) -> dict:
        sku = args["sku"]; qty = int(args["quantity"])
        if qty <= 0:
            raise ValueError("invalid_argument: quantity must be positive")
        self._stock[sku] = self._stock.get(sku, 0) + qty
        self._log.append({"op": "restock", "sku": sku, "qty": qty})
        return {"sku": sku, "stock": self._stock[sku]}

    def _place_order(self, args: dict) -> dict:
        sku = args["sku"]; qty = int(args["quantity"])
        if sku not in self._stock:
            raise ValueError("not_found: unknown sku")
        if qty <= 0:
            raise ValueError("invalid_argument: quantity must be positive")
        if self._stock[sku] < qty:
            raise ValueError("conflict: insufficient stock")
        self._stock[sku] -= qty
        self._counter += 1
        oid = f"ord{self._counter}"
        self._orders[oid] = {"sku": sku, "quantity": qty, "status": "placed"}
        self._log.append({"op": "order", "id": oid})
        return {"order_id": oid, "remaining_stock": self._stock[sku]}

    def _refund_order(self, args: dict) -> dict:
        oid = args["order_id"]
        if oid not in self._orders:
            raise ValueError("not_found: unknown order")
        o = self._orders[oid]
        if o["status"] == "refunded":
            raise ValueError("conflict: already refunded")
        self._stock[o["sku"]] += o["quantity"]
        o["status"] = "refunded"
        self._log.append({"op": "refund", "id": oid})
        return {"order_id": oid, "status": "refunded"}

    def _get_stock(self, args: dict) -> dict:
        return {"stock": dict(sorted(self._stock.items()))}

    def tools(self) -> list[ToolSpec]:
        sku_enum = {"type": "string", "enum": ["sku-a", "sku-b", "sku-c"]}
        return [
            ToolSpec("get_stock", "Return current stock levels.",
                     {"type": "object", "properties": {}}, executor=self._get_stock),
            ToolSpec("restock", "Add stock for a SKU.",
                     {"type": "object",
                      "properties": {"sku": sku_enum, "quantity": {"type": "integer"}},
                      "required": ["sku", "quantity"]}, executor=self._restock),
            ToolSpec("place_order", "Place an order, decrementing stock.",
                     {"type": "object",
                      "properties": {"sku": sku_enum, "quantity": {"type": "integer"}},
                      "required": ["sku", "quantity"]}, executor=self._place_order),
            ToolSpec("refund_order", "Refund an order, restoring stock.",
                     {"type": "object",
                      "properties": {"order_id": {"type": "string"}},
                      "required": ["order_id"]}, executor=self._refund_order),
        ]
