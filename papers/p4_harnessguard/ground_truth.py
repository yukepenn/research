"""Old/new paired ground-truth runner + regression matrix (P4-GT-001, manual 8.9).

For each edit x task we run the OLD harness H (edit.base_config) and the NEW
harness H' (edit.new_config) under PAIRED seeds and label the primary regression

    r_i(e) = 1  iff  pass(H) and not pass(H')

We build the edit x task regression matrix, per-edit regression rates, and the
OLD-harness traces (the only thing feature extraction is allowed to read).

The full label matrix is held by a Custodian (manual 8.9 step 6 / 9.3): the
selector/feature code may RUN canaries (observe labels for chosen pairs) but may
not read held-out full-suite labels before protocol freeze. core.sealed is used
to enforce that gate.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.sealed.access import SealedTest, CUSTODIAN_ROLE
from core.util import sha256_obj
from papers.p4_harnessguard.modular_harness import run_task

# Frozen danger threshold (manual 8.9: defined BEFORE ground truth). An edit is
# dangerous if its regression rate crosses this OR any high-risk task regresses.
DANGER_REGRESSION_RATE = 0.10

GT_VERSION = "p4_ground_truth_v1"


@dataclass
class PairOutcome:
    edit_id: str
    task_id: str
    pass_old: bool
    pass_new: bool
    regression: bool


def run_pair(edit, task, *, seed: int = 0) -> PairOutcome:
    """Run one edit x task pair with paired seeds; return the paired outcome."""
    p_old, _ = run_task(edit.base_config, task, seed=seed)
    p_new, _ = run_task(edit.new_config, task, seed=seed)
    return PairOutcome(edit.edit_id, task.task_id, bool(p_old), bool(p_new),
                       bool(p_old and not p_new))


class RegressionGroundTruth:
    """The full edit x task regression ground truth + old-harness traces."""

    def __init__(self, edits, tasks, *, seed: int = 0, repeats: int = 1):
        self.edits = list(edits)
        self.tasks = list(tasks)
        self.seed = seed
        self.repeats = repeats
        self.edit_ids = [e.edit_id for e in self.edits]
        self.task_ids = [t.task_id for t in self.tasks]
        E, T = len(self.edits), len(self.tasks)
        self.matrix = np.zeros((E, T), dtype=int)
        self.pass_old = np.zeros((E, T), dtype=int)
        self.pass_new = np.zeros((E, T), dtype=int)
        self.old_traces: dict[tuple[str, str], dict] = {}
        for i, edit in enumerate(self.edits):
            for j, task in enumerate(self.tasks):
                # majority vote over paired repeats (deterministic corpus -> stable)
                regs = po = pn = 0
                for r in range(repeats):
                    out = run_pair(edit, task, seed=seed + r)
                    regs += int(out.regression)
                    po += int(out.pass_old)
                    pn += int(out.pass_new)
                self.matrix[i, j] = int(regs * 2 >= repeats)
                self.pass_old[i, j] = int(po * 2 >= repeats)
                self.pass_new[i, j] = int(pn * 2 >= repeats)
                # OLD-harness trace (feature source); never the new-harness run.
                _, trace = run_task(edit.base_config, task, seed=seed)
                self.old_traces[(edit.edit_id, task.task_id)] = trace

    # ---- indexing ------------------------------------------------------
    def _ei(self, edit_id: str) -> int:
        return self.edit_ids.index(edit_id)

    def regression_row(self, edit_id: str) -> np.ndarray:
        return self.matrix[self._ei(edit_id)]

    def regression_set(self, edit_id: str) -> set[str]:
        row = self.regression_row(edit_id)
        return {self.task_ids[j] for j in range(len(self.task_ids)) if row[j]}

    def n_regressions(self, edit_id: str) -> int:
        return int(self.regression_row(edit_id).sum())

    def regression_rate(self, edit_id: str) -> float:
        return self.n_regressions(edit_id) / len(self.task_ids)

    def per_edit_rates(self) -> dict[str, float]:
        return {eid: self.regression_rate(eid) for eid in self.edit_ids}

    def edits_with_regression(self) -> list[str]:
        return [eid for eid in self.edit_ids if self.n_regressions(eid) >= 1]

    def is_dangerous(self, edit_id: str, *, danger_rate: float = DANGER_REGRESSION_RATE) -> bool:
        if self.regression_rate(edit_id) >= danger_rate:
            return True
        reg = self.regression_set(edit_id)
        for t in self.tasks:
            if t.task_id in reg and getattr(t, "is_high_risk", lambda: False)():
                return True
        return False

    def fingerprint(self) -> str:
        """Content hash of the whole matrix for reproducibility checks."""
        return sha256_obj({
            "version": GT_VERSION,
            "edits": self.edit_ids,
            "tasks": self.task_ids,
            "matrix": self.matrix.tolist(),
        })


class Custodian:
    """Holds the full ground truth; exposes only canary observations to method
    code, and gates held-out full labels behind a sealed-test freeze."""

    def __init__(self, gt: RegressionGroundTruth):
        self._gt = gt

    # Running a canary IS allowed: it observes the label for a CHOSEN pair.
    def run_canary(self, edit_id: str, task_id: str) -> int:
        row = self._gt.regression_row(edit_id)
        j = self._gt.task_ids.index(task_id)
        return int(row[j])

    def run_canaries(self, edit_id: str, task_ids) -> dict[str, int]:
        return {tid: self.run_canary(edit_id, tid) for tid in task_ids}

    def is_dangerous(self, edit_id: str) -> bool:
        return self._gt.is_dangerous(edit_id)

    # Sealing the full label matrix so held-out labels are custodian-gated.
    def seal(self, root: str, *, split: str = "test_edits") -> SealedTest:
        st = SealedTest(root, self._gt.fingerprint()[:12])
        labels = {
            "edit_ids": self._gt.edit_ids,
            "task_ids": self._gt.task_ids,
            "matrix": self._gt.matrix.tolist(),
        }
        st.store_labels(split, labels, role=CUSTODIAN_ROLE)
        return st


def build_ground_truth(edits=None, tasks=None, *, seed: int = 0,
                       repeats: int = 1) -> RegressionGroundTruth:
    from papers.p4_harnessguard.edit_corpus.edits import all_edits
    from papers.p4_harnessguard.task_suite import all_tasks
    edits = all_edits() if edits is None else edits
    tasks = all_tasks() if tasks is None else tasks
    return RegressionGroundTruth(edits, tasks, seed=seed, repeats=repeats)
