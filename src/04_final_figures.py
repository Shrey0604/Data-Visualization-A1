"""DAS732 A1 — Final report figures (polished versions of selected candidates).

Reads data/processed/ tables produced by 02_prepare.py and writes the 14
report figures to images/ as Fig_01.png .. Fig_14.png, plus copies the three
non-report extras to images/extras/ (documented in images/README.md).

Layout discipline: every save() runs a programmatic overlap audit that
computes rendered bounding boxes of all text artists, legends, and axis
labels, and reports any collisions or figure-clipped labels. The build is
expected to finish with zero overlap issues.

Figure order follows the narrative:
  1-3   corpus overview & the price of fame        (Member A)
  4-8   community comparison & style persistence   (Member B)
  9-12  temporal & relational structure            (Member C)
  13-14 synthesis: profiles & the age of lists     (Member C)
"""
import os
import shutil

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.stats import spearmanr
from sklearn.cluster import KMeans

from vizutils import audit_overlaps, mask_small_groups, place_labels, profile_features, select_k

HERE = os.path.dirname(__file__)
PROC = os.path.join(HERE, "..", "data", "processed")
IMG = os.path.join(HERE, "..", "images")
EXTRAS = os.path.join(IMG, "extras")
CAND = os.path.join(HERE, "..", "exploration", "candidates")
os.makedirs(EXTRAS, exist_ok=True)

# palettes, era labels and era colours come from the shared config
from config import (ERA_COLORS, ERA_LABELS as ERAS, N_INIT, OI, PT_COLORS,
                    RANDOM_STATE)

mpl.rcParams.update({
    "figure.dpi": 100, "savefig.dpi": 200, "font.size": 10.5,
    "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlepad": 10,
    "axes.labelsize": 11, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "savefig.bbox": "tight",
    "savefig.facecolor": "white", "legend.frameon": False,
})

df = pd.read_csv(os.path.join(PROC, "reddit_top_posts_clean.csv"),
                 parse_dates=["created_dt"])
subs = pd.read_csv(os.path.join(PROC, "subreddit_summary.csv"))
subs["rname"] = "r/" + subs["subreddit"]
df["cpi1k"] = df["cpi"] * 1000          # comments per 1,000 upvotes
subs["cpi1k"] = subs["median_cpi"] * 1000
YEARS = df[df["year"] >= 2014]
RHO_SC = spearmanr(df["score"], df["num_comments"]).statistic
RHO_RC = spearmanr(df["num_comments"], df["upvote_ratio"]).statistic

AUDIT_ISSUES = []


def save(fig, n):
    issues = audit_overlaps(fig, f"Fig_{n:02d}")
    if issues:
        AUDIT_ISSUES.extend(f"Fig_{n:02d}: {s}" for s in issues)
        print(f"saved Fig_{n:02d}.png  !! {len(issues)} layout issue(s)")
        for s in issues:
            print("   ", s)
    else:
        print(f"saved Fig_{n:02d}.png  [layout OK]")
    fig.savefig(os.path.join(IMG, f"Fig_{n:02d}.png"))
    plt.close(fig)


# ------------------------------------------------------------------ Member A
def fig01_coverage():
    yearly = df.groupby("year").size()
    era_of_year = pd.cut(yearly.index, [2010, 2015, 2017, 2019, 2021, 2024],
                         labels=ERAS)
    era_colors = [OI["sky"], OI["green"], OI["blue"], OI["orange"], OI["verm"]]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for i, era in enumerate(ERAS):
        mask = era_of_year == era
        ax.bar(yearly.index[mask], yearly[mask], color=era_colors[i],
               label=f"{era}", width=0.72)
    for x, y in yearly.items():
        if y >= 1500:
            ax.text(x, y + 180, f"{y:,}", ha="center", fontsize=9)
    ax.set(title="When were the all-time top posts created? (all 50 subreddits pooled)",
           xlabel="Year of post creation", ylabel="Number of top posts",
           ylim=(0, yearly.max() * 1.15))
    ax.legend(ncol=5, fontsize=9.5, loc="upper left")
    ax.text(0.99, 0.80, "Dataset collected Sep 2024: recent posts have had\n"
            "less time to accumulate upvotes (right edge)",
            transform=ax.transAxes, ha="right", va="top", fontsize=8.8,
            color=OI["grey"])
    save(fig, 1)


def fig02_distributions():
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.4))
    panels = [
        ("score", "Upvotes per post (score)", np.logspace(3, 6, 60), "{:,.0f}"),
        ("num_comments", "Comments per post", np.logspace(0, 5, 60), "{:,.0f}"),
        ("upvote_ratio", "Upvote ratio (share of votes that are upvotes)",
         np.linspace(0.55, 1.0, 60), "{:.2f}"),
        ("cpi1k", "Comments per 1,000 upvotes (discussion intensity)",
         np.logspace(0, 3, 60), "{:,.0f}"),
    ]
    titles = {"score": "How popular? Upvotes",
              "num_comments": "How discussed? Comments",
              "upvote_ratio": "How contested? Upvote ratio",
              "cpi1k": "Discussion intensity"}
    for ax, (col, label, bins, fmt) in zip(axes.flat, panels):
        vals = df[col].clip(lower=1e-2)
        ax.hist(vals, bins=bins, color=OI["sky"], edgecolor="white", linewidth=0.3)
        med = vals.median()
        ax.axvline(med, color=OI["verm"], lw=1.8)
        ax.text(0.03, 0.92, f"median {fmt.format(med)}",
                transform=ax.transAxes, color=OI["verm"], fontsize=9.5,
                va="top")
        ax.set(xscale="log" if "ratio" not in label else "linear",
               title=titles[col], xlabel=label, ylabel="Posts")
    fig.suptitle("What an all-time top post looks like (n = 49,266 posts, 50 subreddits)",
                 fontweight="bold", fontsize=13.5)
    fig.tight_layout()
    save(fig, 2)


def fig03_score_by_year():
    g = df[df["year"] >= 2014].groupby("year")["score"]
    med, q25, q75 = g.median(), g.quantile(.25), g.quantile(.75)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.fill_between(med.index, q25, q75, alpha=0.22, color=OI["blue"],
                    label="Middle 50% of posts")
    ax.plot(med.index, med, color=OI["blue"], lw=2.6, marker="o", ms=5.5,
            label="Median score")
    ax.set_ylim(0, 108000)
    ax.annotate("Peak years for all-time\nscores (2020-21)", xy=(2020.5, med[2020]),
                xytext=(2014.05, 95000), fontsize=9.5, va="center",
                arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.annotate("Posts under 1 year old\nat collection (Sep 2024)",
                xy=(2024, med[2024]), xytext=(2020.6, 4500), fontsize=9.5,
                va="center",
                arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.set(title="The rising 'price of fame': median score of top posts, by creation year",
           xlabel="Year of post creation", ylabel="Median post score (upvotes)")
    ax.legend(fontsize=9.5, loc="upper right")
    save(fig, 3)


# ------------------------------------------------------------------ Member B
def fig04_cpi_spectrum():
    d = subs.sort_values("cpi1k", ascending=True)
    fig, ax = plt.subplots(figsize=(9.5, 12.8))
    colors = d["dominant_type"].map(PT_COLORS)
    ax.barh(d["rname"], d["cpi1k"], color=colors, height=0.72)
    ax.set_xscale("log")
    ax.set_xlim(4, 420)
    ax.set(title="The engagement spectrum: from consumption to discussion\n"
                 "(median comments per 1,000 upvotes on each subreddit's top posts)",
           xlabel="Comments per 1,000 upvotes (log scale) - higher = more discussion per unit of approval")
    for y, v in enumerate(d["cpi1k"]):
        if y < 3 or y > len(d) - 4 or y % 2 == 0:
            ax.text(v * 1.15, y, f"{v:,.0f}", va="center", fontsize=7.4,
                    color=OI["grey"])
    handles = [Line2D([], [], marker="s", ls="", color=c, markersize=10,
                      label=f"{t}-dominant subreddit") for t, c in PT_COLORS.items()]
    ax.legend(handles=handles, fontsize=9.5, loc="lower right")
    save(fig, 4)


def fig05_type_mix():
    d = subs.sort_values("pct_image", ascending=False)
    fig, ax = plt.subplots(figsize=(9.5, 12.8))
    left = np.zeros(len(d))
    for t in ["image", "link", "text", "video"]:
        ax.barh(d["rname"], d[f"pct_{t}"], left=left, color=PT_COLORS[t],
                label=t, height=0.72)
        left += d[f"pct_{t}"].values
    ax.set(title="Content geometry: what each community's top posts are made of",
           xlabel="Share of the subreddit's top posts (%)", xlim=(0, 100))
    ax.legend(ncol=4, fontsize=9.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.045), title="Post type")
    save(fig, 5)


def fig06_fingerprint():
    d = subs.sort_values("median_cpi", ascending=False)
    metrics = ["median_score", "median_comments", "median_ratio", "median_cpi",
               "median_crossposts", "pct_image", "pct_text"]
    labels = ["Median\nscore", "Median\ncomments", "Median\nupvote ratio",
              "Median comments\nper upvote", "Median\ncrossposts",
              "% image\nposts", "% text\nposts"]
    z = (d[metrics] - d[metrics].mean()) / d[metrics].std()
    fig, ax = plt.subplots(figsize=(17, 5.8))
    im = ax.imshow(z.T, cmap="RdBu", aspect="auto", vmin=-2.6, vmax=2.6)
    ax.set_xticks(range(len(d)), d["rname"], rotation=90, fontsize=8.5)
    ax.set_yticks(range(len(labels)), labels, fontsize=9.5)
    ax.set_title("Engagement fingerprints of the 50 subreddits "
                 "(red = high, blue = low, relative to the 50-subreddit average)",
                 pad=12)
    fig.colorbar(im, ax=ax, shrink=0.85, label="z-score across 50 subreddits")
    save(fig, 6)


def fig07_bubble():
    d = subs.copy()
    smax = d["subscribers"].max()
    fig, ax = plt.subplots(figsize=(11.5, 8.0))
    sizes = d["subscribers"] / smax * 2300 + 30
    ax.scatter(d["cpi1k"], d["median_score"], s=sizes,
               c=d["dominant_type"].map(PT_COLORS), alpha=0.75,
               edgecolors="white", linewidths=1.3)
    ax.set_xscale("log"); ax.set_yscale("log")
    label_these = ["AskReddit", "IAmA", "memes", "aww", "funny", "pics",
                   "worldnews", "news", "askscience", "explainlikeimfive",
                   "personalfinance", "relationship_advice", "gaming",
                   "movies", "Music", "tifu", "wholesomememes",
                   "todayilearned", "science", "Jokes"]
    texts = []
    for _, row in d.iterrows():
        if row["subreddit"] in label_these:
            texts.append(ax.text(row["cpi1k"], row["median_score"],
                                 row["subreddit"], fontsize=8.8,
                                 fontweight="bold", color="#333333"))
    place_labels(ax, texts, x=d["cpi1k"].values, y=d["median_score"].values)
    handles = [Line2D([], [], marker="o", ls="", color=c, markersize=10,
                      label=f"{t}-dominant") for t, c in PT_COLORS.items()]
    for s_ref in [5_000_000, 25_000_000, 60_000_000]:
        ms = np.sqrt((s_ref / smax * 2300 + 30) / np.pi)
        handles.append(Line2D([], [], marker="o", ls="",
                              markerfacecolor=OI["grey"], markeredgecolor="none",
                              alpha=0.55, markersize=ms,
                              label=f"{s_ref/1e6:.0f}M subscribers"))
    ax.legend(handles=handles, fontsize=9, loc="upper center",
              bbox_to_anchor=(0.5, -0.11), ncol=4)
    ax.set(title="The engagement map: discussion intensity vs. approval scale\n"
                 "(one bubble per subreddit; bubble size = 2024 subscribers)",
           xlabel="Comments per 1,000 upvotes (median, log) - discussion intensity",
           ylabel="Median top-post score (log) - approval scale")
    save(fig, 7)


def fig08_style_persistence():
    counts = (df.groupby(["subreddit", "era"], observed=True).size()
                .unstack(fill_value=0))
    piv = (df.groupby(["subreddit", "era"], observed=True)["cpi"]
             .median().unstack())
    piv = piv.reindex(columns=[e for e in ERAS if e in piv.columns])
    order = subs.sort_values("median_cpi", ascending=False)["subreddit"]
    piv = piv.loc[order]
    # blank out cells backed by fewer than 5 top posts — the legend promises
    # "blank = fewer than 5 top posts", so the data must honour it
    piv = mask_small_groups(piv, counts, min_n=5)
    piv1k = piv * 1000
    logv = np.log10(piv1k)
    fig, ax = plt.subplots(figsize=(8.8, 13.2))
    im = ax.imshow(logv, cmap="viridis", aspect="auto")
    ax.set_xticks(range(piv1k.shape[1]), piv1k.columns, fontsize=10)
    ax.set_yticks(range(len(piv1k)), ["r/" + s for s in piv1k.index], fontsize=8.2)
    thresh = np.nanpercentile(logv, 55)
    for i in range(piv1k.shape[0]):
        for j in range(piv1k.shape[1]):
            v = piv1k.iloc[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                        color="white" if logv.iloc[i, j] < thresh else "black")
    ax.set_title("Engagement style is persistent: comments per 1,000 upvotes\n"
                 "by subreddit and creation era (blank = fewer than 5 top posts)",
                 pad=12)
    fig.colorbar(im, ax=ax, shrink=0.6,
                 label="log10(comments per 1,000 upvotes)")
    save(fig, 8)
    counts = (df.groupby(["subreddit", "era"], observed=True).size()
                .unstack(fill_value=0))
    overall = piv.mean(axis=1)
    for e in ERAS:
        ok = counts[e] >= 5
        r = spearmanr(piv.loc[ok, e], overall[ok]).statistic
        print(f"  style-rank stability {e}: rho={r:+.2f} (n={int(ok.sum())})")


# ------------------------------------------------------------------ Member C
def fig09_media_mix_time():
    t = YEARS.groupby(["year", "post_type"]).size().unstack(fill_value=0)
    share = t.div(t.sum(axis=1), axis=0) * 100
    order = ["link", "image", "text", "video"]
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.stackplot(share.index, [share[c] for c in order],
                 colors=[PT_COLORS[c] for c in order], labels=order, alpha=0.92)
    ax.set(title="The media shift: what top posts are made of, by creation year",
           xlabel="Year of post creation", ylabel="Share of top posts (%)",
           xlim=(2014, 2024), ylim=(0, 100))
    ax.legend(ncol=4, fontsize=10, loc="upper center",
              bbox_to_anchor=(0.5, -0.14))
    save(fig, 9)
    print(share[order].round(1).to_string())


def fig10_platform_migration():
    t = YEARS.groupby(["year", "domain_class"]).size().unstack(fill_value=0)
    share = (t.div(t.sum(axis=1), axis=0) * 100)
    focus = ["reddit-native", "imgur", "self post", "youtube", "other external"]
    colors = {"reddit-native": OI["verm"], "imgur": OI["blue"],
              "self post": OI["green"], "youtube": OI["orange"],
              "other external": OI["grey"]}
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    for c in focus:
        lw = 3.4 if c in ("reddit-native", "imgur") else 1.9
        ax.plot(share.index, share[c], color=colors[c], lw=lw, marker="o",
                ms=4.5, label=c)
    ax.set_ylim(0, 63)
    ax.annotate("Reddit launches native\nimage hosting (2016)",
                xy=(2016.15, share.loc[2016, "reddit-native"] + 1.5),
                xytext=(2014.05, 55), fontsize=9.5, va="center",
                arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.annotate("imgur collapses\nfrom ~20% to near 0%",
                xy=(2020, share.loc[2020, "imgur"]),
                xytext=(2020.7, 13), fontsize=9.5, va="center",
                arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.set(title="Where top-post media lives: the fall of imgur and the rise of\n"
                 "Reddit-native hosting",
           xlabel="Year of post creation", ylabel="Share of top posts (%)",
           xlim=(2014, 2024))
    ax.legend(fontsize=9.5, loc="center left", bbox_to_anchor=(1.02, 0.5))
    save(fig, 10)
    print(share[focus].round(1).to_string())


def fig11_score_vs_comments():
    fig, ax = plt.subplots(figsize=(10.5, 6.6))
    samp = df.sample(15000, random_state=1)
    for t in ["image", "link", "text", "video"]:
        d = samp[samp["post_type"] == t]
        ax.scatter(d["score"], d["num_comments"], s=8, alpha=0.3,
                   color=PT_COLORS[t], label=t, rasterized=True,
                   edgecolors="none")
    ax.set_xscale("log"); ax.set_yscale("log")
    # reference line y = x, labelled along its rendered angle
    lim = np.array([1e3, 1e6])
    ax.plot(lim, lim, color=OI["grey"], ls="--", lw=1.3)
    p1 = ax.transData.transform((1e4, 1e4))
    p2 = ax.transData.transform((1e5, 1e5))
    angle = np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
    ax.text(2.4e4, 2.4e4, "1 comment per upvote", fontsize=8.8,
            color=OI["grey"], rotation=angle, rotation_mode="anchor",
            ha="left", va="bottom")
    ax.set(title=f"Upvotes and comments measure different kinds of success "
                 f"(Spearman rho = {RHO_SC:.2f})",
           xlabel="Post score (upvotes, log scale)",
           ylabel="Number of comments (log scale)")
    ax.legend(fontsize=9.5, title="Post type", markerscale=3,
              loc="upper left", bbox_to_anchor=(1.02, 1))
    save(fig, 11)


def fig12_contested_discussed():
    fig, ax = plt.subplots(figsize=(10.5, 5.9))
    hb = ax.hexbin(df["num_comments"].clip(lower=1), df["upvote_ratio"],
                   xscale="log", gridsize=55, bins="log", cmap="Blues",
                   mincnt=3)
    ax.set(title=f"Contested posts are discussed posts "
                 f"(Spearman rho = {RHO_RC:.2f})",
           xlabel="Number of comments (log scale)", ylabel="Upvote ratio")
    fig.colorbar(hb, ax=ax, label="Posts (log count)")
    save(fig, 12)


# ------------------------------------------------------------------ synthesis
def fig13_profiles():
    feats = ["median_cpi", "median_ratio", "median_score", "pct_image", "pct_text"]
    Z = profile_features(subs)
    best = select_k(Z)
    km = KMeans(best, n_init=N_INIT, random_state=RANDOM_STATE).fit(Z)
    subs["cluster"] = km.labels_.astype(str)

    def name_cluster(row):
        if row["pct_text"] > 95 and row["median_cpi"] > 0.15:
            return "AskReddit: text Q&A giant"
        if row["pct_image"] > 40:
            return "Visual entertainment feeds"
        if row["pct_text"] > 60:
            return "Advice & Q&A text communities"
        if row["median_score"] < 12000:
            return "Niche interests (smaller score scale)"
        return "News & media link hubs"

    prof = subs.groupby("cluster")[feats].mean().apply(name_cluster, axis=1)
    name_color = {"AskReddit: text Q&A giant": OI["verm"],
                  "Visual entertainment feeds": OI["blue"],
                  "Advice & Q&A text communities": OI["green"],
                  "News & media link hubs": OI["orange"],
                  "Niche interests (smaller score scale)": OI["purple"]}
    fig, ax = plt.subplots(figsize=(11.5, 7.8))
    label_these = ("AskReddit", "memes", "aww", "worldnews", "funny",
                   "askscience", "pics", "personalfinance", "tifu",
                   "gaming", "Art", "news", "IAmA", "history",
                   "space", "food")
    for c in sorted(subs.cluster.unique()):
        d = subs[subs.cluster == c]
        nm = prof[c]
        ax.scatter(d["cpi1k"], d["pct_image"], s=120, color=name_color[nm],
                   alpha=0.8, edgecolors="white", linewidths=1.3,
                   label=f"{nm} ({len(d)})")
        for _, r in d.iterrows():
            if r["subreddit"] in label_these:
                ax.text(r["cpi1k"], r["pct_image"], r["subreddit"],
                        fontsize=8.8, color="#333333")
    place_labels(ax, [t for t in ax.texts],
                 x=subs["cpi1k"].values, y=subs["pct_image"].values)
    ax.set_xscale("log")
    ax.set(title="The profile map: five engagement profiles among the 50 communities",
           xlabel="Comments per 1,000 upvotes (median, log) - discussion intensity",
           ylabel="Share of top posts that are images (%)")
    ax.legend(fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.11),
              ncol=2)
    save(fig, 13)
    for c in sorted(subs.cluster.unique()):
        print(f"  {prof[c]}: "
              + ", ".join(sorted(subs[subs.cluster == c]["subreddit"])))


def fig14_age_of_lists():
    piv = (df.groupby(["subreddit", "era"], observed=True).size()
             .unstack(fill_value=0))
    piv = piv.div(piv.sum(axis=1), axis=0) * 100
    piv = piv[[e for e in ERAS if e in piv.columns]]
    piv = piv.sort_values("2022-24", ascending=False)
    fig, ax = plt.subplots(figsize=(9.5, 12.8))
    left = np.zeros(len(piv))
    colors = {"<=2015": OI["sky"], "2016-17": OI["green"],
              "2018-19": OI["blue"], "2020-21": OI["orange"],
              "2022-24": OI["verm"]}
    for e in piv.columns:
        ax.barh(["r/" + s for s in piv.index], piv[e], left=left,
                color=colors[e], label=e, height=0.72)
        left += piv[e].values
    ax.set(title="How old is each community's all-time list?\n"
                 "(share of a subreddit's top posts created in each era)",
           xlabel="Share of the subreddit's top posts (%)", xlim=(0, 100))
    ax.legend(ncol=5, fontsize=9.5, loc="upper center",
              bbox_to_anchor=(0.5, -0.045), title="Creation era")
    save(fig, 14)
    print("  most recent-heavy:", piv["2022-24"].head(3).round(1).to_dict())
    print("  most classic-heavy:", piv["2022-24"].tail(3).round(1).to_dict())


def copy_extras():
    for c in ["C08_ratio_boxes.png", "C12_corr_matrix.png",
              "C15_crossposts.png"]:
        src = os.path.join(CAND, c)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(EXTRAS, c))
            print(f"copied extra {c}")


if __name__ == "__main__":
    fig01_coverage()
    fig02_distributions()
    fig03_score_by_year()
    fig04_cpi_spectrum()
    fig05_type_mix()
    fig06_fingerprint()
    fig07_bubble()
    fig08_style_persistence()
    fig09_media_mix_time()
    fig10_platform_migration()
    fig11_score_vs_comments()
    fig12_contested_discussed()
    fig13_profiles()
    fig14_age_of_lists()
    copy_extras()
    print("\nALL FINAL FIGURES DONE")
    if AUDIT_ISSUES:
        print(f"\n!!! {len(AUDIT_ISSUES)} LAYOUT ISSUE(S) REMAIN:")
        for s in AUDIT_ISSUES:
            print("  -", s)
    else:
        print("LAYOUT AUDIT: all figures clean (no text/legend overlaps)")
