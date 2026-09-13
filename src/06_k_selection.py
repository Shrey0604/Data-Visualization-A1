"""DAS732 A1 — Reproducible k-selection analysis (report Appendix C).

Regenerates every number quoted in Appendix C of the report:
  - silhouette + cluster sizes for k = 2..8 (config.K_RANGE)
  - the deterministic selection rule (vizutils.select_k)
  - seed stability of the selected solution (mean adjusted Rand index over
    the 19 non-reference seeds)

Writes data/processed/k_selection.csv and prints the markdown table used in
the report. Run: python src/06_k_selection.py
"""
import os

import pandas as pd

from config import MIN_PROFILE_SIZE, MAX_SMALL_PROFILES
from vizutils import k_selection_table, k_stability_ari, profile_features, select_k

HERE = os.path.dirname(__file__)
PROC = os.path.join(HERE, "..", "data", "processed")


def main():
    subs = pd.read_csv(os.path.join(PROC, "subreddit_summary.csv"))
    Z = profile_features(subs)

    table = k_selection_table(Z)
    best_k = select_k(Z)
    ari = k_stability_ari(Z, best_k)

    out = table.copy()
    out["selected"] = out["k"] == best_k
    out.to_csv(os.path.join(PROC, "k_selection.csv"), index=False)

    print(f"selection rule: largest-silhouette k in 2..8 with at most "
          f"{MAX_SMALL_PROFILES} cluster(s) smaller than {MIN_PROFILE_SIZE} "
          f"of the 50 communities")
    print(f"selected k = {best_k}")
    print(f"seed stability (k={best_k}): mean ARI over 19 non-reference seeds = {ari:.3f}")
    print("\n| k | Silhouette | Cluster sizes |")
    print("|---|---|---|")
    for _, r in table.iterrows():
        mark = " **(selected)**" if r["k"] == best_k else ""
        print(f"| {r['k']} | {r['silhouette']:.3f}{mark} | {', '.join(map(str, r['sizes']))} |")


if __name__ == "__main__":
    main()
