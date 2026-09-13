# DAS732 A1 — Visual Exploration of Reddit's Top Communities (2011–2024)

**Team:** Silica — Sidhanth Prabhu (BT2024027, team lead) · Shrey Modi (BT2024125) · Parthsarathi Samanta (BT2024083)
**Central question:** *What does a decade (2011–2024) of all-time top posts
reveal about how Reddit's 50 largest communities generate engagement — who
discusses versus who consumes, what media succeeds where, and how the content
landscape behind these hits changed over time?*

## Project structure

```
├── requirements.txt               # pinned dependencies
├── data/
│   ├── raw/                       # original Kaggle CSVs, untouched (50 subreddits + list)
│   └── processed/                 # pipeline outputs
│       ├── reddit_top_posts_clean.csv   # 49,266 posts, cleaned + derived vars
│       ├── subreddit_summary.csv        # one row per subreddit (medians, shares)
│       ├── k_selection.csv              # Appendix C output (silhouette table, ARI)
│       └── preprocessing_log.md         # auto-generated decision log
├── src/
│   ├── 01_audit.py                # dataset audit (exploration stats)
│   ├── 02_prepare.py              # reproducible preprocessing pipeline
│   ├── 03_candidates.py           # 17 candidate visualizations → exploration/candidates/
│   ├── 04_final_figures.py        # 14 report figures → images/Fig_01..14.png
│   ├── 05_build_docx.py           # builds report/report.docx from report.md
│   ├── 06_k_selection.py          # regenerates Appendix C (k table + seed stability)
│   ├── config.py                  # shared parameters: eras, palettes, clustering rule
│   └── vizutils.py                # shared analysis (k-selection, masking) + layout audit
├── tests/
│   └── test_pipeline.py           # automated correctness tests (python -m unittest)
├── images/
│   ├── Fig_01.png … Fig_14.png    # report figures (numbered = report order)
│   ├── extras/                    # 3 documented non-report figures (see images/README.md)
│   └── README.md                  # figure index + extras significance
├── report/
│   ├── report.md                  # master report (source of truth)
│   ├── report.docx                # submission-ready DOCX (figures embedded)
│   ├── AI_Declaration_*.docx      # filled instructor-template forms (3 members)
│   └── VIDEO_SCRIPT.md            # ≤5-minute video script with timings
└── tableau/
    └── TABLEAU_SPEC.md            # step-by-step dashboard build + demo guide
```

## Reproducing the analysis

Requires Python 3.13+ with the pinned dependencies in `requirements.txt`:

```
python -m pip install -r requirements.txt

python src/02_prepare.py        # raw → processed (+ preprocessing log)
python src/06_k_selection.py    # Appendix C: k-selection table + stability
python src/03_candidates.py     # exploration candidates
python src/04_final_figures.py  # final report figures
python src/05_build_docx.py     # rebuild report.docx after editing report.md

python -m unittest discover -s tests -v   # automated correctness tests
```

`data/raw/` is not downloaded automatically; fetch the dataset once with
`kagglehub.dataset_download("sachinkanchan92/reddit-top-posts-50-subreddit-analysis-2011-2024")`
and copy the CSVs into `data/raw/` (see the Kaggle dataset page).

**Frozen-snapshot rule:** this repository is the working copy. Running the
pipeline overwrites tracked outputs (`data/processed/`, `images/`, `report/report.docx`)
by design. After submission, do **not** run any script inside the submitted
Drive folder — the assignment records the newest file timestamp as the
submission time. Regenerate outputs only here, and copy results over
deliberately.

- [ ] Report: `report/report.docx` (with figures, captions, inferences,
      contributions, references) — review once, then freeze the folder
- [ ] Code: `src/` (+ this README) — the Python submission component
- [ ] Tableau workbook: build via `tableau/TABLEAU_SPEC.md`, publish to
      Tableau Public, paste the URL here: ______________________
      (and/or include the packaged `.twbx`)
- [ ] Images folder: `images/` with README (extras documented as required)
- [ ] AI declarations: each member reviews + signs their
      `report/AI_Declaration_<Name>.docx` (instructor template; adjust tool
      names to personal usage first)
- [ ] Video: record per `report/VIDEO_SCRIPT.md` (≤ 5 minutes)
- [ ] Contributions table in report Section 9 filled with real names/tasks
- [ ] Upload to the course drive; **do not edit any file after submission**
      (timestamps reset the recorded submission time)
- [ ] Verify TAs/instructor have access to the folder through end of semester

## Key findings (summary)

1. **40× engagement-style spectrum, stable over time** — AskReddit: 230
   comments per 1,000 upvotes vs. wholesomememes: 5.7; era-wise style rank
   correlations +0.85 to +0.92.
2. **Two decoupled success currencies** — score ↔ comments ρ = 0.56;
   text posts dominate high-comment region.
3. **Contested posts are discussed posts** — ratio ↔ comments ρ = −0.45.
4. **Platform migration** — imgur 19.6% → 0.3% of top posts (2015→2024);
   Reddit-native 0% → 45.1%; inflections match Reddit's mid-2016 image
   hosting and Aug-2017 native video launches.
5. **Price of fame tripled** — median top-post score 13k (2014) → 47k
   (2020–21); the 2024 dip is accumulation-time bias, not decline.
6. **Five engagement profiles** — k-means on community metrics alone
   recovers: visual feeds, advice/Q&A text, news & media hubs, niche
   interests, and AskReddit alone.
