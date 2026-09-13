"""Shared analysis + visualization utilities for DAS732 A1.

Analysis (used by figure scripts, src/06_k_selection.py, and tests):
  profile_features   - community-level feature matrix for the profile map
  select_k           - deterministic k selection with the documented rule
  k_selection_table  - silhouette/size table for k = config.K_RANGE
  k_stability_ari    - seed-stability of a k-means solution (adjusted Rand)
  mask_small_groups  - hide heatmap cells backed by fewer than n posts

Visualization:
  audit_overlaps     - render-time collision audit for text/legend artists
  place_labels       - automatic de-overlapping of point labels (adjustText)
"""
import matplotlib as mpl
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from config import (K_RANGE, MAX_SMALL_PROFILES, MIN_PROFILE_SIZE, N_INIT,
                    RANDOM_STATE, STABILITY_SEEDS)

try:
    from adjustText import adjust_text
    HAVE_ADJUST = True
except ImportError:
    HAVE_ADJUST = False


# ------------------------------------------------------------------ analysis
def profile_features(subs: pd.DataFrame) -> np.ndarray:
    """Feature matrix for the profile map: log discussion intensity, log
    median score, median upvote ratio, image share, text share."""
    X = np.column_stack([
        np.log1p(subs[["median_cpi", "median_score"]].values),
        subs[["median_ratio", "pct_image", "pct_text"]].values,
    ])
    return StandardScaler().fit_transform(X)


def k_selection_table(Z: np.ndarray) -> pd.DataFrame:
    """Silhouette + cluster-size table for every k in config.K_RANGE."""
    rows = []
    for k in K_RANGE:
        labels = KMeans(k, n_init=N_INIT, random_state=RANDOM_STATE).fit_predict(Z)
        sizes = np.bincount(labels)
        rows.append({"k": k,
                     "silhouette": silhouette_score(Z, labels),
                     "sizes": sorted(sizes.tolist(), reverse=True),
                     "n_small": int((sizes < MIN_PROFILE_SIZE).sum())})
    return pd.DataFrame(rows)


def select_k(Z: np.ndarray) -> int:
    """Deterministic k selection (report Appendix C rule).
    Among k = 2..8, keep the partitions in which all but at most one cluster
    contain at least MIN_PROFILE_SIZE communities (the allowance covers the
    single structural outlier, AskReddit), then take the highest silhouette.
    This yields k = 5 on the current data: k = 6 splits the advice & Q&A
    profile into fragments of 5 and 6, which the rule disallows.
    """
    table = k_selection_table(Z)
    eligible = table[table["n_small"] <= MAX_SMALL_PROFILES]
    return int(eligible.loc[eligible["silhouette"].idxmax(), "k"])


def k_stability_ari(Z: np.ndarray, k: int) -> float:
    """Mean adjusted Rand index of the k-means solution at `k` across
    STABILITY_SEEDS, comparing seeds 1..N against the seed-0 reference
    (i.e. N-1 comparisons, as reported in Appendix C)."""
    base = KMeans(k, n_init=N_INIT, random_state=RANDOM_STATE).fit_predict(Z)
    aris = [adjusted_rand_score(base, KMeans(k, n_init=N_INIT,
                                             random_state=s).fit_predict(Z))
            for s in list(STABILITY_SEEDS)[1:]]
    return float(np.mean(aris))


def mask_small_groups(values: pd.DataFrame, counts: pd.DataFrame,
                      min_n: int = 5) -> pd.DataFrame:
    """Blank out heatmap cells backed by fewer than `min_n` observations.

    `values` and `counts` share the same index/columns. Cells with
    counts < min_n (including missing counts) become NaN so the figure shows
    them as blank, matching its own legend."""
    out = values.copy()
    counts = counts.reindex(index=values.index, columns=values.columns)
    out[counts.isna() | (counts < min_n)] = np.nan
    return out


# ------------------------------------------------------------- visualization
def audit_overlaps(fig, name=""):
    """Return a list of layout-issue strings for a rendered figure.

    Detects (a) any pairwise overlap among text artists, legends, axis
    labels and suptitles, and (b) data labels that extend outside the
    figure canvas. Returns an empty list when the layout is clean.
    """
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    items = []  # (label, bbox, is_movable_text)
    for ax in fig.axes:
        for t in ax.texts:
            if t.get_text().strip():
                items.append((t.get_text()[:30].replace("\n", "|"),
                              t.get_window_extent(ren), True))
        leg = ax.get_legend()
        if leg is not None:
            items.append(("<LEGEND>", leg.get_window_extent(ren), False))
        if ax.xaxis.label.get_text():
            items.append(("<xlabel>", ax.xaxis.label.get_window_extent(ren), False))
        if ax.yaxis.label.get_text():
            items.append(("<ylabel>", ax.yaxis.label.get_window_extent(ren), False))
    for t in fig.texts:
        if t.get_text().strip():
            items.append(("<suptitle>", t.get_window_extent(ren), False))
    issues = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][1].overlaps(items[j][1]):
                issues.append(f"OVERLAP: '{items[i][0]}' <-> '{items[j][0]}'")
    fb = fig.bbox
    for lab, bb, movable in items:
        if movable and (bb.x0 < fb.x0 - 2 or bb.x1 > fb.x1 + 2
                        or bb.y0 < fb.y0 - 2 or bb.y1 > fb.y1 + 2):
            issues.append(f"CLIPPED: '{lab}' extends outside figure")
    return issues


def place_labels(ax, texts, x, y):
    """De-overlap a list of ax.text artists (adjustText if available)."""
    if HAVE_ADJUST and texts:
        adjust_text(texts, x=x, y=y, ax=ax,
                    expand=(1.35, 1.7),
                    force_text=(0.35, 0.7),
                    force_static=(0.35, 0.7),
                    time_lim=4, iter_lim=300,
                    only_move={"points": "y", "text": "xy",
                               "static": "xy", "pull": "xy"},
                    arrowprops=dict(arrowstyle="-", color="#999999", lw=0.6))
