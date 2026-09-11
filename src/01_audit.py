"""DAS732 A1 — Dataset audit for Reddit Top Posts (50 subreddits, 2011-2024).

Loads the 50 raw per-subreddit CSVs, applies the two known data fixes
(AskReddit date format, boolean NaN handling), and prints a complete audit:
shape, types, missingness, duplicates, ranges, distributions, correlations,
coverage over time, and per-subreddit contrasts.
"""
import os
import glob

import numpy as np
import pandas as pd
import scipy.stats as st

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", None)


def load_all() -> pd.DataFrame:
    files = [f for f in sorted(glob.glob(os.path.join(RAW, "*.csv")))
             if "50_subreddits_list" not in f]
    frames = []
    for f in files:
        d = pd.read_csv(f)
        d["source_file"] = os.path.basename(f)
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)

    # --- date parsing: main format + AskReddit's Excel-style M/D/YYYY H:MM ---
    df["created_dt"] = pd.to_datetime(df["created_utc"], errors="coerce")
    bad = df["created_dt"].isna()
    df.loc[bad, "created_dt"] = pd.to_datetime(df.loc[bad, "created_utc"],
                                               format="%m/%d/%Y %H:%M")
    assert df["created_dt"].isna().sum() == 0, "unparseable dates remain"

    df["year"] = df["created_dt"].dt.year
    df["era"] = pd.cut(df["year"], [2010, 2015, 2017, 2019, 2021, 2024],
                       labels=["<=2015", "2016-17", "2018-19", "2020-21", "2022-24"])
    df["title_len"] = df["title"].str.len()
    return df


def main() -> None:
    df = load_all()
    print(f"rows={len(df)}  subreddits={df['subreddit'].nunique()}")
    print(f"time range: {df['created_dt'].min()} -> {df['created_dt'].max()}")

    print("\n--- missingness (%) ---")
    print((df.isna().mean().mul(100).round(2)
            .sort_values(ascending=False).head(8).to_string()))

    print(f"\nduplicate ids: {df['id'].duplicated().sum()}")

    print("\n--- numeric summaries ---")
    print(df[["score", "num_comments", "upvote_ratio", "num_crossposts",
              "num_awards", "title_len"]]
          .describe(percentiles=[.25, .5, .75, .99]).T.to_string())

    print("\n--- key rank correlations (Spearman) ---")
    pairs = [("score", "num_comments"), ("score", "upvote_ratio"),
             ("num_comments", "upvote_ratio"), ("score", "title_len"),
             ("num_crossposts", "score"), ("num_crossposts", "num_comments")]
    for a, b in pairs:
        r = st.spearmanr(df[a], df[b]).statistic
        print(f"  {a} vs {b}: {r:+.3f}")

    print("\n--- posts per year ---")
    print(df["year"].value_counts().sort_index().to_string())

    print("\n--- domain share by era (%) ---")
    def dom_share(g):
        d = g["domain"].fillna("(none)")
        return pd.Series({
            "imgur%": round(d.str.contains("imgur").mean() * 100, 1),
            "redd.it%": round(d.str.contains(r"redd\.it").mean() * 100, 1),
            "self%": round(d.str.startswith("self.").mean() * 100, 1),
            "youtube%": round(d.str.contains("youtu").mean() * 100, 1),
            "n": len(g),
        })
    print(df.groupby("era", observed=True).apply(dom_share).to_string())

    print("\n--- post_type mix by era (%) ---")
    pte = df.pivot_table(index="era", columns="post_type", values="id",
                         aggfunc="count").fillna(0)
    print((pte.div(pte.sum(axis=1), axis=0) * 100).round(1).to_string())

    print("\n--- median score by era ---")
    print(df.groupby("era", observed=True)["score"].agg(["median", "count"]).to_string())

    print("\n--- comments-per-upvote (engagement intensity), median by subreddit ---")
    df["cpi"] = df["num_comments"] / df["score"].clip(lower=1)
    cpi = df.groupby("subreddit")["cpi"].median().sort_values()
    print("most discussion-heavy:\n", cpi.tail(6).to_string())
    print("most passive:\n", cpi.head(6).to_string())

    print("\n--- upvote_ratio, median by subreddit ---")
    ur = df.groupby("subreddit")["upvote_ratio"].median().sort_values()
    print("lowest consensus:\n", ur.head(6).to_string())
    print("highest consensus:\n", ur.tail(6).to_string())

    print("\n--- post_type mix by subreddit (extremes, %) ---")
    pt = df.pivot_table(index="subreddit", columns="post_type", values="id",
                        aggfunc="count").fillna(0)
    pt_pct = (pt.div(pt.sum(axis=1), axis=0) * 100).round(1)
    print("most text-heavy:\n", pt_pct.sort_values("text", ascending=False).head(6).to_string())
    print("most image-heavy:\n", pt_pct.sort_values("image", ascending=False).head(4).to_string())

    print("\n--- is_bot missing by subreddit (top) ---")
    print(df.groupby("subreddit")["is_bot"].apply(lambda s: s.isna().mean())
          .sort_values(ascending=False).head(5).to_string())

    print("\n--- top 5 posts overall (sanity) ---")
    cols = ["title", "subreddit", "score", "num_comments", "created_dt"]
    print(df.nlargest(5, "score")[cols].to_string(max_colwidth=60))


if __name__ == "__main__":
    main()
