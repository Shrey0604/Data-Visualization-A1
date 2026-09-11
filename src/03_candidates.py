"""DAS732 A1 — Candidate visualizations (exploration phase).

Generates ~19 candidate figures into exploration/candidates/ and prints the
statistics behind each figure so every claimed pattern is verifiable.
Figure quality here is exploratory; selected figures get report polish later.
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

HERE = os.path.dirname(__file__)
PROC = os.path.join(HERE, "..", "data", "processed")
IMG = os.path.join(HERE, "..", "exploration", "candidates")
os.makedirs(IMG, exist_ok=True)

# Okabe-Ito colorblind-safe palette
OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
      "verm": "#D55E00", "purple": "#CC79A7", "sky": "#56B4E9",
      "yellow": "#F0E442", "black": "#000000", "grey": "#7F7F7F"}
PT_COLORS = {"image": OI["blue"], "link": OI["orange"],
             "text": OI["green"], "video": OI["verm"]}
ERAS = ["<=2015", "2016-17", "2018-19", "2020-21", "2022-24"]

mpl.rcParams.update({
    "figure.dpi": 100, "savefig.dpi": 200, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlepad": 10,
    "axes.labelsize": 10.5, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "savefig.bbox": "tight", "savefig.facecolor": "white",
})

df = pd.read_csv(os.path.join(PROC, "reddit_top_posts_clean.csv"),
                 parse_dates=["created_dt"])
subs = pd.read_csv(os.path.join(PROC, "subreddit_summary.csv"))
df["rname"] = "r/" + df["subreddit"]
subs["rname"] = "r/" + subs["subreddit"]
YEARS = df[df["year"] >= 2014]  # pre-2014 has <10 posts/year total


def save(fig, name):
    from vizutils import audit_overlaps
    issues = audit_overlaps(fig, name)
    path = os.path.join(IMG, name)
    fig.savefig(path)
    plt.close(fig)
    if issues:
        print(f"saved {name}  !! {len(issues)} layout issue(s)")
        for s in issues:
            print("   ", s)
    else:
        print(f"saved {name}  [layout OK]")

# ---------------------------------------------------------------- T1 overview
def c01_posts_per_year():
    yearly = df.groupby("year").size()
    era_of_year = pd.cut(yearly.index, [2010, 2015, 2017, 2019, 2021, 2024],
                         labels=ERAS)
    era_colors = [OI["sky"], OI["green"], OI["blue"], OI["orange"], OI["verm"]]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for i, era in enumerate(ERAS):
        mask = era_of_year == era
        ax.bar(yearly.index[mask], yearly[mask], color=era_colors[i],
               label=f"{era} era", width=0.72)
    for x, y in yearly.items():
        if y >= 600:
            ax.text(x, y + 150, f"{y:,}", ha="center", fontsize=8.5)
    ax.set(title="When were Reddit's all-time top posts created? (50 subreddits combined)",
           xlabel="Year of post creation", ylabel="Number of top posts")
    ax.legend(frameon=False, ncol=5, fontsize=9, loc="upper left")
    ax.set_ylim(0, yearly.max() * 1.14)
    ax.text(0.99, 0.78, "Collection date: Sep 2024 — recent posts have had less\ntime to accumulate upvotes",
            transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color=OI["grey"])
    save(fig, "C01_posts_per_year.png")
    print(yearly.to_string())


def c02_distributions():
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.2))
    panels = [
        ("score", "Post score (upvotes, log scale)", np.logspace(3, 6, 60)),
        ("num_comments", "Number of comments (log scale)", np.logspace(0, 5, 60)),
        ("upvote_ratio", "Upvote ratio", np.linspace(0.55, 1.0, 60)),
        ("cpi", "Comments per upvote (log scale)", np.logspace(-3, 0, 60)),
    ]
    for ax, (col, label, bins) in zip(axes.flat, panels):
        vals = df[col].clip(lower=1e-3)
        ax.hist(vals, bins=bins, color=OI["sky"], edgecolor="white", linewidth=0.3)
        med = vals.median()
        ax.axvline(med, color=OI["verm"], lw=1.6)
        ax.text(med, ax.get_ylim()[1] * 0.95, f" median {med:,.3f}" if col == "cpi"
                else f" median {med:,.0f}" if col != "upvote_ratio" else f" median {med:.2f}",
                color=OI["verm"], fontsize=9, va="top")
        ax.set(xscale="log" if "log" in label else "linear",
               title=f"Distribution of {col}", xlabel=label, ylabel="Posts")
    fig.suptitle("What does an all-time top post look like? (n = 49,266 posts)",
                 fontweight="bold", fontsize=13)
    fig.tight_layout()
    save(fig, "C02_distributions.png")
    print(df[["score", "num_comments", "upvote_ratio", "cpi"]].describe().round(2).to_string())


def c03_score_by_year():
    g = df[df["year"] >= 2014].groupby("year")["score"]
    med, q25, q75 = g.median(), g.quantile(.25), g.quantile(.75)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.fill_between(med.index, q25, q75, alpha=0.22, color=OI["blue"], label="Middle 50% of posts")
    ax.plot(med.index, med, color=OI["blue"], lw=2.4, marker="o", ms=5, label="Median score")
    ax.annotate("Peak score years for\nall-time top posts", xy=(2020.5, med[2020]),
                xytext=(2017.4, med[2020] + 3000), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.annotate("Posts < 1 year old at\ndata collection (Sep 2024)", xy=(2024, med[2024]),
                xytext=(2021.9, med[2024] - 7000), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.set(title="The rising 'price of fame': score of a typical all-time top post, by creation year",
           xlabel="Year of post creation", ylabel="Median post score (upvotes)")
    ax.legend(frameon=False, fontsize=9)
    save(fig, "C03_score_by_year.png")
    print(pd.DataFrame({"median": med, "q25": q25, "q75": q75, "n": g.size()}).to_string())


# ------------------------------------------------------- T2 community compare
def c05_cpi_ranking():
    d = subs.sort_values("median_cpi")
    fig, ax = plt.subplots(figsize=(9.5, 12.5))
    colors = d["dominant_type"].map(PT_COLORS)
    ax.barh(d["rname"], d["median_cpi"], color=colors, height=0.72)
    ax.set_xscale("log")
    ax.set(title="Consumers vs. discussants: comments generated per upvote,\nby subreddit (median over its top posts)",
           xlabel="Median comments per upvote (log scale) — higher = more discussion per unit of approval")
    for y, (rn, v) in enumerate(zip(d["rname"], d["median_cpi"])):
        if v > 0.06 or y % 2 == 0:
            ax.text(v * 1.12, y, f"{v:.3f}", va="center", fontsize=7.3, color=OI["grey"])
    handles = [Line2D([], [], marker="s", ls="", color=c, label=f"{t} posts dominant")
               for t, c in PT_COLORS.items()]
    ax.legend(handles=handles, frameon=False, fontsize=9, loc="lower right")
    save(fig, "C05_cpi_ranking.png")
    print(d[["rname", "median_cpi"]].head(3).to_string())
    print(d[["rname", "median_cpi"]].tail(3).to_string())


def c06_fingerprint_heatmap():
    d = subs.sort_values("median_cpi", ascending=False)
    metrics = ["median_score", "median_comments", "median_ratio",
               "median_cpi", "median_crossposts", "pct_image", "pct_text"]
    labels = ["Median\nscore", "Median\ncomments", "Median\nupvote ratio",
              "Median comments\nper upvote", "Median\ncrossposts", "% image\nposts", "% text\nposts"]
    z = (d[metrics] - d[metrics].mean()) / d[metrics].std()
    fig, ax = plt.subplots(figsize=(17, 5.6))
    im = ax.imshow(z.T, cmap="RdBu", aspect="auto", vmin=-2.6, vmax=2.6)
    ax.set_xticks(range(len(d)), d["rname"], rotation=90, fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=9)
    ax.set_title("Engagement fingerprints of 50 subreddits (z-scores; red = high, blue = low)", pad=12)
    fig.colorbar(im, ax=ax, shrink=0.85, label="z-score within 50 subreddits")
    save(fig, "C06_fingerprint_heatmap.png")


def c07_bubble():
    d = subs.copy()
    fig, ax = plt.subplots(figsize=(11, 7.6))
    sizes = d["subscribers"] / d["subscribers"].max() * 2400 + 25
    colors = d["dominant_type"].map(PT_COLORS)
    ax.scatter(d["median_cpi"], d["median_score"], s=sizes, c=colors,
               alpha=0.75, edgecolors="white", linewidths=1.2)
    ax.set_xscale("log"); ax.set_yscale("log")
    label_these = ["AskReddit", "IAmA", "memes", "aww", "funny", "pics", "worldnews",
                   "news", "askscience", "explainlikeimfive", "personalfinance",
                   "relationship_advice", "gaming", "movies", "Music", "tifu",
                   "wholesomememes", "todayilearned", "science", "Jokes"]
    texts = [ax.text(row["median_cpi"], row["median_score"], row["subreddit"],
                     fontsize=8.6, fontweight="bold", color="#333333")
             for _, row in d[d["subreddit"].isin(label_these)].iterrows()]
    from vizutils import place_labels
    place_labels(ax, texts, x=d["cpi1k"].values if "cpi1k" in d else d["median_cpi"].values,
                 y=d["median_score"].values)
    # legend: post-type colors + reference bubble sizes
    handles = [Line2D([], [], marker="o", ls="", color=c, markersize=9,
                      label=f"{t}-dominant") for t, c in PT_COLORS.items()]
    for s_ref in [5_000_000, 25_000_000, 60_000_000]:
        ms = np.sqrt((s_ref / d["subscribers"].max() * 2400 + 25) / np.pi)
        handles.append(Line2D([], [], marker="o", ls="", markerfacecolor=OI["grey"],
                              markeredgecolor="none", alpha=0.55,
                              markersize=ms, label=f"{s_ref/1e6:.0f}M subscribers"))
    ax.legend(handles=handles, frameon=False, fontsize=8.6, loc="upper center",
              bbox_to_anchor=(0.5, -0.11), ncol=4)
    ax.set(title="The engagement map of Reddit's top communities",
           xlabel="Median comments per upvote (log) — discussion intensity",
           ylabel="Median top-post score (log) — approval scale")
    save(fig, "C07_bubble.png")
    print("upper-right (high score, high discussion):",
          d[(np.log10(d.median_cpi) > -1.1) & (np.log10(d.median_score) > 4.6)]["subreddit"].tolist())
    print("lower-right consumers (high score, low discussion):",
          d[(np.log10(d.median_cpi) < -1.7) & (np.log10(d.median_score) > 4.6)]["subreddit"].tolist())


def c08_type_mix():
    d = subs.sort_values("pct_image", ascending=False)
    fig, ax = plt.subplots(figsize=(9.5, 12.5))
    left = np.zeros(len(d))
    for t in ["image", "link", "text", "video"]:
        ax.barh(d["rname"], d[f"pct_{t}"], left=left, color=PT_COLORS[t], label=t, height=0.72)
        left += d[f"pct_{t}"].values
    ax.set(title="Content geometry: what its top posts are made of, per subreddit",
           xlabel="Share of the subreddit's top posts (%)")
    ax.set_xlim(0, 100)
    ax.legend(frameon=False, ncol=4, fontsize=9, loc="lower right", title="Post type")
    save(fig, "C08_type_mix.png")
    print(d[["rname", "pct_text", "pct_image", "pct_link", "pct_video"]].head(4).to_string())


def c09_ratio_boxes():
    order = subs.sort_values("median_ratio")["subreddit"]
    sel = list(order[:6]) + list(order[-6:])
    d = df[df["subreddit"].isin(sel)]
    fig, ax = plt.subplots(figsize=(11, 5.4))
    med = subs.set_index("subreddit").loc[sel, "median_ratio"]
    sel_sorted = sorted(sel, key=lambda s: med[s])
    data = [df[df["subreddit"] == s]["upvote_ratio"] for s in sel_sorted]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55, showfliers=False,
                    medianprops=dict(color="black", lw=1.5))
    for patch, s in zip(bp["boxes"], sel_sorted):
        patch.set_facecolor(OI["verm"] if med[s] < 0.89 else OI["blue"])
        patch.set_alpha(0.65)
    ax.set_xticklabels([f"r/{s}" for s in sel_sorted], rotation=40, ha="right", fontsize=9)
    ax.set(title="Consensus on top posts: upvote-ratio spread for the 6 most contested\nand 6 most unanimous subreddits",
           ylabel="Upvote ratio (share of upvotes among all votes)")
    save(fig, "C09_ratio_boxes.png")
    print(subs.set_index("subreddit").loc[sel_sorted, "median_ratio"].to_string())


# ------------------------------------------------------------- T3 temporal
def c10_type_share_time():
    t = (YEARS.groupby(["year", "post_type"]).size().unstack(fill_value=0))
    share = t.div(t.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.stackplot(share.index, [share[c] for c in ["link", "image", "text", "video"]],
                 colors=[PT_COLORS[c] for c in ["link", "image", "text", "video"]],
                 labels=["link", "image", "text", "video"], alpha=0.9)
    ax.set(title="The media shift in Reddit's top posts, by creation year",
           xlabel="Year of post creation", ylabel="Share of top posts (%)",
           xlim=(2014, 2024), ylim=(0, 100))
    ax.legend(frameon=False, ncol=4, fontsize=9, loc="lower left")
    save(fig, "C10_type_share_time.png")
    print(share.round(1).to_string())


def c11_domain_migration():
    t = YEARS.groupby(["year", "domain_class"]).size().unstack(fill_value=0)
    share = (t.div(t.sum(axis=1), axis=0) * 100)
    focus = ["reddit-native", "imgur", "self post", "youtube", "other external"]
    colors = {"reddit-native": OI["verm"], "imgur": OI["blue"],
              "self post": OI["green"], "youtube": OI["orange"],
              "other external": OI["grey"]}
    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    for c in focus:
        lw = 3.2 if c in ("reddit-native", "imgur") else 1.8
        ax.plot(share.index, share[c], color=colors[c], lw=lw, marker="o", ms=4, label=c)
    ax.annotate("Reddit launches native\nimage hosting (mid-2016)", xy=(2016.15, share.loc[2016, "reddit-native"] + 1),
                xytext=(2014.1, 22), fontsize=9, arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.annotate("imgur collapses\nfrom ~30% to ~2%", xy=(2020, share.loc[2020, "imgur"]),
                xytext=(2020.6, 14), fontsize=9, arrowprops=dict(arrowstyle="->", color=OI["grey"]))
    ax.set(title="Where top-post media lives: the fall of imgur and rise of Reddit-native hosting",
           xlabel="Year of post creation", ylabel="Share of top posts (%)",
           xlim=(2014, 2024))
    ax.legend(frameon=False, fontsize=9)
    save(fig, "C11_domain_migration.png")
    print(share[focus].round(1).to_string())


def c13_cpi_heatmap():
    piv = (df.groupby(["subreddit", "era"], observed=True)["cpi"]
             .median().unstack())
    piv = piv.reindex(columns=[e for e in ERAS if e in piv.columns])
    order = subs.sort_values("median_cpi", ascending=False)["subreddit"]
    piv = piv.loc[order]
    logv = np.log10(piv)
    fig, ax = plt.subplots(figsize=(8.6, 13))
    im = ax.imshow(logv, cmap="viridis", aspect="auto")
    ax.set_xticks(range(piv.shape[1]), piv.columns, fontsize=9)
    ax.set_yticks(range(len(piv)), ["r/" + s for s in piv.index], fontsize=8)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.iloc[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.8,
                        color="white" if logv.iloc[i, j] < np.nanpercentile(logv, 55) else "black")
    ax.set_title("Is engagement style stable? Comments per upvote by subreddit and era", pad=12)
    fig.colorbar(im, ax=ax, shrink=0.6, label="log10(comments per upvote)")
    save(fig, "C13_cpi_heatmap.png")
    # rank stability: spearman of era-wise cpi rankings vs overall,
    # restricted to subreddits with >=5 top posts in that era
    counts = (df.groupby(["subreddit", "era"], observed=True).size()
                .unstack(fill_value=0))
    overall = piv.mean(axis=1)
    for e in ERAS:
        ok = counts[e] >= 5
        r = spearmanr(piv.loc[ok, e], overall[ok]).statistic
        print(f"rank correlation era {e} vs overall (n={int(ok.sum())}): {r:+.2f}")


# ---------------------------------------------------------- T4 relationships
def c14_corr_matrix():
    cols = ["score", "num_comments", "upvote_ratio", "num_crossposts",
            "title_len", "is_question"]
    rho = df[cols].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    im = ax.imshow(rho, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)), cols, rotation=35, ha="right")
    ax.set_yticks(range(len(cols)), cols)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{rho.iloc[i, j]:+.2f}", ha="center", va="center",
                    fontsize=9.5, color="white" if abs(rho.iloc[i, j]) > 0.55 else "black")
    ax.set_title("What goes with what on top posts? (Spearman rank correlations)")
    fig.colorbar(im, ax=ax, shrink=0.85)
    save(fig, "C14_corr_matrix.png")
    print(rho.round(3).to_string())


def c15_score_vs_comments():
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    samp = df.sample(15000, random_state=1)
    for t in ["image", "link", "text", "video"]:
        d = samp[samp["post_type"] == t]
        ax.scatter(d["score"], d["num_comments"], s=7, alpha=0.3,
                   color=PT_COLORS[t], label=t, rasterized=True, edgecolors="none")
    ax.set_xscale("log"); ax.set_yscale("log")
    lim = np.array([1e3, 1e6])
    ax.plot(lim, lim, color=OI["grey"], ls="--", lw=1.2)
    ax.text(1.1e3, 1.6e3, "1 comment per upvote", rotation=38, fontsize=8.5, color=OI["grey"])
    rho = spearmanr(df["score"], df["num_comments"]).statistic
    ax.set(title=f"Do upvotes and comments measure the same success? (ρ = {rho:.2f})",
           xlabel="Post score (upvotes, log)", ylabel="Number of comments (log)")
    ax.legend(frameon=False, fontsize=9, title="Post type", markerscale=3)
    save(fig, "C15_score_vs_comments.png")
    # the outliers: posts with more comments than upvotes
    more = df[df["num_comments"] > df["score"]]
    print(f"posts with more comments than upvotes: {len(more)} "
          f"({len(more)/len(df)*100:.1f}%), top subreddit:",
          more["subreddit"].value_counts().head(3).to_dict())


def c16_ratio_vs_comments():
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    hb = ax.hexbin(df["num_comments"].clip(lower=1), df["upvote_ratio"],
                   xscale="log", gridsize=55, bins="log", cmap="Blues", mincnt=3)
    rho = spearmanr(df["num_comments"], df["upvote_ratio"]).statistic
    ax.set(title=f"Contested posts are discussed posts (ρ = {rho:.2f})",
           xlabel="Number of comments (log scale)",
           ylabel="Upvote ratio")
    fig.colorbar(hb, ax=ax, label="Posts (log count)")
    save(fig, "C16_ratio_vs_comments.png")


def c17_crossposts():
    fig, ax = plt.subplots(figsize=(10.5, 6))
    samp = df.sample(20000, random_state=2)
    ax.scatter(samp["score"], samp["num_crossposts"].clip(lower=0) + 0.05,
               s=8, alpha=0.35, color=OI["blue"], rasterized=True, edgecolors="none")
    ax.set_xscale("log"); ax.set_yscale("log")
    top = df.nlargest(4, "num_crossposts")
    labels = [ax.text(r["score"], r["num_crossposts"],
                      f"{r['subreddit']} ({r['num_crossposts']} crossposts)",
                      fontsize=8.5, color="#333333")
              for _, r in top.iterrows()]
    try:
        from adjustText import adjust_text
        adjust_text(labels, x=samp["score"].values,
                    y=samp["num_crossposts"].values, ax=ax,
                    expand=(1.3, 1.6), force_text=(0.35, 0.7),
                    time_lim=4, iter_lim=300,
                    arrowprops=dict(arrowstyle="-", color=OI["grey"], lw=0.7))
    except ImportError:
        for t in labels:
            t.set_text(t.get_text())
    rho = spearmanr(df["score"], df["num_crossposts"]).statistic
    ax.set(title=f"Crossposting tracks virality (ρ = {rho:.2f})",
           xlabel="Post score (upvotes, log)", ylabel="Times crossposted to other subreddits (log)")
    save(fig, "C17_crossposts.png")
    print(top[["subreddit", "num_crossposts", "score"]].to_string())


# ------------------------------------------------------------- T5 synthesis
def c18_clusters():
    feats = ["median_cpi", "median_ratio", "median_score", "pct_image", "pct_text"]
    X = np.log1p(subs[["median_cpi", "median_score"]].values)
    X = np.column_stack([X, subs[["median_ratio", "pct_image", "pct_text"]].values])
    Z = StandardScaler().fit_transform(X)
    best = max(range(3, 6), key=lambda k: silhouette_score(Z, KMeans(k, n_init=10, random_state=0).fit_predict(Z)))
    km = KMeans(best, n_init=10, random_state=0).fit(Z)
    subs["cluster"] = km.labels_.astype(str)
    print(f"k={best}, silhouette={silhouette_score(Z, km.labels_):.3f}")
    for c in sorted(subs.cluster.unique()):
        print(c, ":", ", ".join(sorted(subs[subs.cluster == c]["subreddit"])))
    def name_cluster(row):
        if row["pct_text"] > 95 and row["median_cpi"] > 0.15:
            return "AskReddit: text Q&A giant"
        if row["pct_image"] > 40:
            return "Visual entertainment feeds"
        if row["pct_text"] > 60:
            return "Advice & Q&A text communities"
        if row["median_score"] < 12000:
            return "Niche interests (lower score scale)"
        return "News & media link hubs"

    prof = subs.groupby("cluster")[feats].mean().apply(name_cluster, axis=1)
    name_color = {"AskReddit: text Q&A giant": OI["verm"],
                  "Visual entertainment feeds": OI["blue"],
                  "Advice & Q&A text communities": OI["green"],
                  "News & media link hubs": OI["orange"],
                  "Niche interests (lower score scale)": OI["purple"]}
    fig, ax = plt.subplots(figsize=(11, 7.2))
    for c in sorted(subs.cluster.unique()):
        d = subs[subs.cluster == c]
        nm = prof[c]
        ax.scatter(d["median_cpi"], d["pct_image"], s=110, color=name_color[nm],
                   alpha=0.8, edgecolors="white", linewidths=1.2,
                   label=f"{nm} ({len(d)})")
        for _, r in d.iterrows():
            if r["subreddit"] in ("AskReddit", "memes", "aww", "worldnews", "funny",
                                  "askscience", "pics", "personalfinance", "tifu",
                                  "Documentaries", "gaming", "Art", "news", "IAmA"):
                ax.text(r["median_cpi"], r["pct_image"], r["subreddit"],
                        fontsize=8.6, color="#333333")
    from vizutils import place_labels
    place_labels(ax, [t for t in ax.texts], x=subs["median_cpi"].values,
                 y=subs["pct_image"].values)
    save(fig, "C18_clusters.png")


def c19_era_composition():
    piv = (df.groupby(["subreddit", "era"], observed=True).size()
             .unstack(fill_value=0))
    piv = piv.div(piv.sum(axis=1), axis=0) * 100
    piv = piv[[e for e in ERAS if e in piv.columns]]
    piv = piv.sort_values("2022-24", ascending=False)
    fig, ax = plt.subplots(figsize=(9.5, 12.5))
    left = np.zeros(len(piv))
    colors = {"<=2015": OI["sky"], "2016-17": OI["green"], "2018-19": OI["blue"],
              "2020-21": OI["orange"], "2022-24": OI["verm"]}
    for e in piv.columns:
        ax.barh(["r/" + s for s in piv.index], piv[e], left=left,
                color=colors[e], label=e, height=0.72)
        left += piv[e].values
    ax.set(title="How old is each community's all-time list?\n(share of top posts created in each era)",
           xlabel="Share of the subreddit's top posts (%)")
    ax.set_xlim(0, 100)
    ax.legend(frameon=False, ncol=5, fontsize=9, loc="lower right", title="Creation era")
    save(fig, "C19_era_composition.png")
    print(piv["2022-24"].sort_values(ascending=False).head(5).to_string())
    print(piv["2022-24"].sort_values().head(5).to_string())


if __name__ == "__main__":
    c01_posts_per_year()
    c02_distributions()
    c03_score_by_year()
    c05_cpi_ranking()
    c06_fingerprint_heatmap()
    c07_bubble()
    c08_type_mix()
    c09_ratio_boxes()
    c10_type_share_time()
    c11_domain_migration()
    c13_cpi_heatmap()
    c14_corr_matrix()
    c15_score_vs_comments()
    c16_ratio_vs_comments()
    c17_crossposts()
    c18_clusters()
    c19_era_composition()
    print("\nALL CANDIDATES DONE")
