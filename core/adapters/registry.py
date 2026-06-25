"""Adapter factory that enforces the human budget/credential gate.

The mock adapter is always available (Tier-0). Real providers can only be
instantiated when (a) credentials are present in the environment and (b) the
program budget has been explicitly configured (not null) — matching the
CLAUDE.md human gate "configure provider credentials and hard budget ceilings".
Until then, requesting a paid adapter raises a clear, actionable error instead
of silently spending money.
"""
from __future__ import annotations

import os

from core.adapters.base import ModelAdapter
from core.adapters.mock import DeterministicMockAdapter

# provider -> (env var that must be set, human-readable note)
_PAID_PROVIDERS = {
    "anthropic": ("ANTHROPIC_API_KEY", "Claude models"),
    "openai": ("OPENAI_API_KEY", "GPT/Codex models"),
    "google": ("GOOGLE_API_KEY", "Gemini models"),
}


class BudgetGateError(RuntimeError):
    """Raised when a paid adapter is requested before the human gate is cleared."""


def get_adapter(provider: str, model_id: str, *, budget_configured: bool = False,
                **kw) -> ModelAdapter:
    provider = provider.lower()
    if provider in ("mock", "deterministic"):
        return DeterministicMockAdapter(model_id, **kw)
    if provider not in _PAID_PROVIDERS:
        raise ValueError(f"unknown provider {provider!r}")
    env_var, note = _PAID_PROVIDERS[provider]
    if not budget_configured:
        raise BudgetGateError(
            f"Paid provider '{provider}' ({note}) is gated. "
            "Set program/budget.yaml limits (non-null) and pass budget_configured=True. "
            "This is a human decision per CLAUDE.md."
        )
    if not os.environ.get(env_var):
        raise BudgetGateError(
            f"Missing credential {env_var} for provider '{provider}'. "
            "Provide it via environment (never commit secrets)."
        )
    # Real adapter implementations are intentionally not bundled here; they are
    # added under the budget gate. We fail loudly rather than pretend.
    raise BudgetGateError(
        f"Real adapter for '{provider}' not installed in this Tier-0 build. "
        "Install the provider adapter module after the budget gate is cleared."
    )
