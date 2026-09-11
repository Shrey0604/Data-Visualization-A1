# Tableau Workbook Build Guide — "Reddit Engagement Explorer"

The assignment recommends Tableau; our project is a **hybrid**: the full
analysis and all report figures are Python (reproducible via `src/`), and one
interactive Tableau dashboard supports live exploration in the video demo.

**Estimated build time:** 30–45 minutes.

---

## 1. Data connection

1. Open Tableau (Public or Desktop) → Connect → **Text file** → select
   `data/processed/reddit_top_posts_clean.csv` (49,266 rows).
2. On the data-source page, confirm these types:
   - `created_dt` → **Date & Time** (if it came in as string, change it)
   - `score`, `num_comments`, `num_crossposts`, `subscribers` → **Number (whole)**
   - `upvote_ratio`, `cpi` → **Number (decimal)**
   - `post_type`, `domain_class`, `era`, `subreddit` → **String**
3. *(Optional, faster)* also connect `data/processed/subreddit_summary.csv`
   as a second data source for the pre-aggregated community-level sheets.

## 2. Calculated fields (Analysis → Create Calculated Field)

```
Comments per 1,000 upvotes   =  [num_comments] / MAX([score],1) * 1000
Discussion intensity (med)   =  MEDIAN([num_comments] / MAX([score],1) * 1000)
Median top score             =  MEDIAN([score])
Subscribers (M)              =  MAX([subscribers]) / 1000000
```

(`era` and `domain_class` already exist as columns — no calculation needed.)

## 3. Sheets

### Sheet 1 — "Engagement Map" (the report's Figure 7, interactive)
- **Columns:** `MEDIAN(Comments per 1,000 upvotes)` → edit axis → **Logarithmic**
- **Rows:** `MEDIAN([score])` → edit axis → **Logarithmic**
- **Detail:** `subreddit` (convert to *Attribute* via ATTR if needed) —
  this makes one mark per subreddit.
- **Size:** `ATTR(Subscribers (M))`
- **Color:** `ATTR(post_type)` is wrong here (post-level); instead join the
  dominant type: simplest is to use the `subreddit_summary.csv` source with
  `dominant_type` on Color.
- **Label:** `subreddit`
- Tooltip: add MEDIAN(num_comments), MEDIAN(upvote_ratio).

### Sheet 2 — "Engagement Spectrum" (Figure 4, interactive)
- **Rows:** `subreddit` (sorted by `MEDIAN(Comments per 1,000 upvotes)` descending)
- **Columns:** `MEDIAN(Comments per 1,000 upvotes)`
- **Color:** `post_type` (or dominant type from the summary source)

### Sheet 3 — "Media Shift" (Figure 9)
- **Columns:** `YEAR(created_dt)` (filter to ≥ 2014)
- **Rows:** `COUNT(id)` → quick table calculation → **Percent of Total**
  computed using **Table (across)**.
- **Color/Detail:** `post_type`
- Mark type: **Area** (100% stacked area).

### Sheet 4 — "Score vs Comments" (Figure 11)
- **Columns:** `score` (log axis) · **Rows:** `num_comments` (log axis)
- **Color:** `post_type` · **Opacity** ~40% · Mark: Circle, small size.

## 4. Dashboard — "Reddit Engagement Explorer"

1. New Dashboard (1280×800). Drag all four sheets in (Map large, left;
   Spectrum right; Media Shift + Score-vs-Comments along the bottom).
2. Add filters applied to **all sheets**:
   - `era` (single-value dropdown)
   - `post_type` (multiple choice)
   - `subreddit` (multiple choice) — great for the video demo:
     select *only AskReddit*, then *only memes*, and watch the map/spectrum
     selections and the score-vs-comments cloud move.
3. Add a dashboard title: *"Reddit Engagement Explorer — top posts of 50
   communities, 2011–2024"*.

## 5. Publish for assessment

- **Tableau Public:** File → Save to Tableau Public As… → name it
  `Reddit-Engagement-Explorer` → copy the public URL into the root
  `README.md` and the report (it satisfies the assignment's "appropriate
  access shall be managed for assessment").
- If using Tableau Desktop with local files, also export
  **File → Export Packaged Workbook** and include the `.twbx` in the
  submission folder (a `.twbx` embeds the data, so graders need nothing else).

## 6. What to show in the video (≈ 40 seconds)

1. Land on the dashboard: "Here is the same engagement map from Figure 7,
   now interactive."
2. Filter `era` to `2022-24` — note the map thins (accumulation bias, live).
3. Select only `AskReddit` + `memes` in the subreddit filter — the two
   engagement currencies separate visibly in Score-vs-Comments.
4. Close: "Filters let us re-ask every question in the report on any slice."
