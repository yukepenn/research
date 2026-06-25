"""Defect-type-conditioned author x reviewer error complementarity (manual 6.9; H3).

The central mechanism: the value of heterogeneous review is governed by
defect-type-conditioned author/reviewer error COMPLEMENTARITY, not raw reviewer
strength. Given an outcome table (one row per reviewed patch) this module
computes:

  - DetectionComplementarity(a, r, d) = P(reviewer r detects d | author a produced d)
  - reviewer standalone strength(r, d) = marginal detection of r on d (over authors)
  - ResidualComplementarity(a, r, d)  = detection complementarity MINUS the
    reviewer-standalone-strength expectation -> the author x reviewer interaction
    that survives after removing the reviewer main effect.
  - defect-category confusion matrix (true defect vs reviewer-claimed defect)
  - same-family vs cross-family error correlation (shared blind spots)
  - review-induced regression matrix (P(regression) by reviewer x defect)

Pure numpy / pandas; deterministic. Input rows are dicts (or a DataFrame) with:
  author, author_family, reviewer, reviewer_family, defect_type,
  author_produced_defect (bool), reviewer_detected (bool),
  [reviewer_claimed_defect], [review_induced_regression], [same_family]
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from papers.p2_crosscheck.defects.taxonomy import DefectType, defect_index


def _as_df(table) -> pd.DataFrame:
    if isinstance(table, pd.DataFrame):
        df = table.copy()
    else:
        df = pd.DataFrame(list(table))
    if "same_family" not in df.columns and {"author_family", "reviewer_family"} <= set(df.columns):
        df["same_family"] = df["author_family"] == df["reviewer_family"]
    # normalise defect labels to their string values
    if "defect_type" in df.columns:
        df["defect_type"] = df["defect_type"].map(lambda d: str(d))
    if "reviewer_claimed_defect" in df.columns:
        df["reviewer_claimed_defect"] = df["reviewer_claimed_defect"].map(
            lambda d: None if d is None or (isinstance(d, float) and np.isnan(d)) else str(d)
        )
    return df


def _produced(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["author_produced_defect"].astype(bool)]


# --------------------------------------------------------------------------
# Detection complementarity & residual interaction
# --------------------------------------------------------------------------
def detection_complementarity(table, author, reviewer, defect_type) -> float:
    """P(reviewer detects d | author produced d) for the (a, r, d) cell."""
    df = _produced(_as_df(table))
    d = str(defect_type)
    cell = df[(df["author"] == author) & (df["reviewer"] == reviewer)
              & (df["defect_type"] == d)]
    if len(cell) == 0:
        return float("nan")
    return float(cell["reviewer_detected"].astype(float).mean())


def reviewer_standalone_strength(table, reviewer, defect_type) -> float:
    """Marginal detection rate of reviewer r on defect d, pooled over authors.

    This is the reviewer main effect we subtract off to isolate the pair-specific
    interaction (manual 6.9: "expected gain from reviewer standalone strength").
    """
    df = _produced(_as_df(table))
    d = str(defect_type)
    cell = df[(df["reviewer"] == reviewer) & (df["defect_type"] == d)]
    if len(cell) == 0:
        return float("nan")
    return float(cell["reviewer_detected"].astype(float).mean())


def residual_complementarity(table, author, reviewer, defect_type) -> float:
    """DetectionComplementarity(a,r,d) - reviewer_standalone_strength(r,d).

    Positive => this author x reviewer pair is *more* complementary on this
    defect than the reviewer's strength alone predicts (the H3 interaction).
    """
    return (detection_complementarity(table, author, reviewer, defect_type)
            - reviewer_standalone_strength(table, reviewer, defect_type))


def residual_matrix(table):
    """Return (authors, reviewers, defects, residual_tensor) where the tensor
    has shape (n_authors, n_reviewers, n_defects)."""
    df = _produced(_as_df(table))
    authors = sorted(df["author"].unique().tolist())
    reviewers = sorted(df["reviewer"].unique().tolist())
    defects = sorted(df["defect_type"].unique().tolist())
    tensor = np.full((len(authors), len(reviewers), len(defects)), np.nan)
    for i, a in enumerate(authors):
        for j, r in enumerate(reviewers):
            for k, d in enumerate(defects):
                tensor[i, j, k] = residual_complementarity(df, a, r, d)
    return authors, reviewers, defects, tensor


# --------------------------------------------------------------------------
# Defect-category confusion
# --------------------------------------------------------------------------
def defect_confusion(table):
    """Confusion matrix of true defect_type vs reviewer_claimed_defect.

    Rows = true defect, cols = claimed defect (taxonomy order). Only rows where
    the reviewer detected something (claimed is not None) are counted.
    """
    df = _produced(_as_df(table))
    idx = defect_index()
    labels = list(idx.keys())
    n = len(labels)
    mat = np.zeros((n, n), dtype=int)
    if "reviewer_claimed_defect" not in df.columns:
        return labels, mat
    for _, row in df.iterrows():
        claimed = row.get("reviewer_claimed_defect")
        if claimed is None or claimed != claimed:  # None / NaN
            continue
        true_d = str(row["defect_type"])
        if true_d in idx and claimed in idx:
            mat[idx[true_d], idx[claimed]] += 1
    return labels, mat


# --------------------------------------------------------------------------
# Same-family vs cross-family error correlation (shared blind spots)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ErrorCorrelation:
    same_family_miss_rate: float
    cross_family_miss_rate: float
    phi: float          # corr(same_family, reviewer_miss) over produced rows
    n_same: int
    n_cross: int


def same_vs_cross_error_correlation(table) -> ErrorCorrelation:
    """On produced-defect rows, compare reviewer MISS rate for same-family vs
    cross-family pairs, and the phi correlation between same-family membership
    and a miss. Positive phi => same-family pairs share blind spots (correlated
    errors); cross-family review is then complementary."""
    df = _produced(_as_df(table))
    if "same_family" not in df.columns:
        raise ValueError("table needs same_family or author_family/reviewer_family")
    miss = 1.0 - df["reviewer_detected"].astype(float).to_numpy()
    same = df["same_family"].astype(float).to_numpy()
    same_mask = same == 1.0
    cross_mask = same == 0.0
    same_rate = float(miss[same_mask].mean()) if same_mask.any() else float("nan")
    cross_rate = float(miss[cross_mask].mean()) if cross_mask.any() else float("nan")
    if same.std() == 0 or miss.std() == 0:
        phi = float("nan")
    else:
        phi = float(np.corrcoef(same, miss)[0, 1])
    return ErrorCorrelation(same_rate, cross_rate, phi,
                            int(same_mask.sum()), int(cross_mask.sum()))


# --------------------------------------------------------------------------
# Review-induced regression matrix
# --------------------------------------------------------------------------
def review_induced_regression_matrix(table, by: str = "reviewer"):
    """P(review_induced_regression) grouped by ``by`` x defect_type.

    Returns (row_labels, defect_labels, rate_matrix). A review that fixes one bug
    but introduces another is a real cost of heterogeneous review (manual 6.9).
    """
    df = _as_df(table)
    if "review_induced_regression" not in df.columns:
        raise ValueError("table needs a review_induced_regression column")
    rows = sorted(df[by].unique().tolist())
    defects = sorted(df["defect_type"].unique().tolist())
    mat = np.full((len(rows), len(defects)), np.nan)
    for i, rv in enumerate(rows):
        for j, d in enumerate(defects):
            cell = df[(df[by] == rv) & (df["defect_type"] == d)]
            if len(cell):
                mat[i, j] = float(cell["review_induced_regression"].astype(float).mean())
    return rows, defects, mat


# --------------------------------------------------------------------------
# Full report
# --------------------------------------------------------------------------
@dataclass
class ComplementarityReport:
    authors: list
    reviewers: list
    defects: list
    residual_tensor: np.ndarray
    error_correlation: ErrorCorrelation
    confusion_labels: list
    confusion_matrix: np.ndarray
    regression_rows: list
    regression_defects: list
    regression_matrix: np.ndarray


def complementarity_report(table) -> ComplementarityReport:
    authors, reviewers, defects, tensor = residual_matrix(table)
    ec = same_vs_cross_error_correlation(table)
    clabels, cmat = defect_confusion(table)
    rrows, rdefects, rmat = review_induced_regression_matrix(table)
    return ComplementarityReport(
        authors=authors, reviewers=reviewers, defects=defects,
        residual_tensor=tensor, error_correlation=ec,
        confusion_labels=clabels, confusion_matrix=cmat,
        regression_rows=rrows, regression_defects=rdefects, regression_matrix=rmat,
    )
