"""Structured (edit, task) feature extraction (P4-METHOD-001/002, manual 8.8).

Three feature groups, concatenated into one fixed-order vector per (edit, task):

  edit_features  - component one-hot, declared intent, static diff features
  task_fingerprint - capability tags + OLD-harness trace stats (NO new-harness peek)
  pair_features  - edit x task interactions that GENERALIZE across components
                   (comp/capability match, trace-exercise, declared-risk overlap)

The pair features are deliberately component-AGNOSTIC (a single "comp_cap_match"
rather than per-component cross terms) so a risk model trained on some
components/lineages transfers to held-out ones (manual 8.13 OOD selector study).

Hard rule: feature extraction reads only the OLD-harness trace. The new-harness
outcome is never an argument here (manual 9.3 / no-leakage).
"""
from __future__ import annotations

import numpy as np

from papers.p4_harnessguard.modular_harness import (
    COMPONENTS, COMPONENT_CAPABILITY, COMPONENT_TRACE_SIGNAL)
from papers.p4_harnessguard.task_suite import CAPABILITY_VOCAB, RISK_TAG_VOCAB

_INTENT = ["improvement", "neutral", "harmful"]
_SCOPE = ["local", "global"]
_DIRECTION = {"improvement": 1.0, "neutral": 0.0, "harmful": -1.0}

_TRACE_KEYS = ["n_steps", "n_retries", "n_verification_actions", "memory_lookups",
               "context_length", "n_tool_calls", "n_errors", "key_tool_position"]


def _onehot(value, vocab):
    return [1.0 if value == v else 0.0 for v in vocab]


def _multihot(values, vocab):
    vs = set(values or [])
    return [1.0 if v in vs else 0.0 for v in vocab]


# --------------------------------------------------------------------------
# Edit features
# --------------------------------------------------------------------------
def edit_feature_names() -> list[str]:
    names = [f"edit_comp::{c}" for c in COMPONENTS]
    names += [f"edit_intent::{i}" for i in _INTENT]
    names += [f"edit_scope::{s}" for s in _SCOPE]
    names += ["edit_lines_changed", "edit_prompt_tokens_changed", "edit_tools_affected"]
    names += ["edit_n_expected_improvements", "edit_n_expected_risks"]
    return names


def edit_features(edit) -> np.ndarray:
    sf = edit.static_features
    feats = []
    feats += _onehot(edit.component, COMPONENTS)
    feats += _onehot(edit.intended_effect, _INTENT)
    feats += _onehot(edit.change_scope, _SCOPE)
    feats += [float(sf.get("lines_changed", 0)) / 20.0,
              float(sf.get("prompt_tokens_changed", 0)) / 60.0,
              float(sf.get("tools_affected", 0)) / 8.0]
    feats += [float(len(edit.expected_improvements)), float(len(edit.expected_risks))]
    return np.asarray(feats, dtype=float)


# --------------------------------------------------------------------------
# Task fingerprint (from OLD-harness trace only)
# --------------------------------------------------------------------------
def task_fingerprint_names() -> list[str]:
    names = [f"task_cap::{c}" for c in CAPABILITY_VOCAB]
    names += [f"task_trace::{k}" for k in _TRACE_KEYS]
    names += ["task_n_risk_tags"]
    return names


def task_fingerprint(task, old_trace: dict) -> np.ndarray:
    """Fingerprint a task from its capability tags + OLD-harness trace.

    `old_trace` MUST be the OLD (base) harness trace; passing a new-harness trace
    would leak the label and is a protocol violation.
    """
    feats = []
    feats += _multihot(task.capabilities, CAPABILITY_VOCAB)
    feats += [float(old_trace.get(k, 0)) for k in _TRACE_KEYS]
    feats += [float(len(getattr(task, "risk_tags", [])))]
    return np.asarray(feats, dtype=float)


# --------------------------------------------------------------------------
# Pairwise interaction features (component-agnostic -> OOD transferable)
# --------------------------------------------------------------------------
def pair_feature_names() -> list[str]:
    return [
        "pair_comp_cap_match",
        "pair_trace_exercise",
        "pair_match_x_exercise",
        "pair_risk_overlap",
        "pair_improve_overlap",
        "pair_direction_x_match",
    ]


def _trace_exercise(edit, old_trace: dict) -> float:
    key = COMPONENT_TRACE_SIGNAL.get(edit.component)
    raw = float(old_trace.get(key, 0.0)) if key else 0.0
    # light per-signal scaling so the magnitude is comparable across components
    scale = {"n_steps": 6.0, "context_length": 80.0, "n_tool_calls": 5.0}.get(key, 3.0)
    return raw / scale


def pair_features(edit, task, old_trace: dict) -> np.ndarray:
    cap = COMPONENT_CAPABILITY.get(edit.component)
    comp_cap_match = 1.0 if cap in set(task.capabilities) else 0.0
    exercise = _trace_exercise(edit, old_trace)
    risk_overlap = float(len(set(edit.expected_risks) & set(getattr(task, "risk_tags", []))))
    improve_overlap = float(len(set(edit.expected_improvements) & set(task.capabilities)))
    direction = _DIRECTION.get(edit.intended_effect, 0.0)
    return np.asarray([
        comp_cap_match,
        exercise,
        comp_cap_match * exercise,
        risk_overlap,
        improve_overlap,
        direction * comp_cap_match,
    ], dtype=float)


# --------------------------------------------------------------------------
# Full vector + matrix
# --------------------------------------------------------------------------
def feature_names() -> list[str]:
    return edit_feature_names() + task_fingerprint_names() + pair_feature_names()


def pair_vector(edit, task, old_trace: dict) -> np.ndarray:
    return np.concatenate([
        edit_features(edit),
        task_fingerprint(task, old_trace),
        pair_features(edit, task, old_trace),
    ])


def build_matrix(edits, tasks, old_traces: dict):
    """Build the (n_pairs x n_features) design matrix and a parallel index of
    (edit_id, task_id). `old_traces[(edit_id, task_id)] -> old trace dict`."""
    rows = []
    index = []
    for edit in edits:
        for task in tasks:
            tr = old_traces[(edit.edit_id, task.task_id)]
            rows.append(pair_vector(edit, task, tr))
            index.append((edit.edit_id, task.task_id))
    X = np.vstack(rows) if rows else np.zeros((0, len(feature_names())))
    return X, index
