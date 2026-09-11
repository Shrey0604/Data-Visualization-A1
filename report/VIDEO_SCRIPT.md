# Video Demonstration Script — DAS732 A1 (≤ 5 minutes)

**Team:** Silica — Sidhanth Prabhu (BT2024027, team lead) · Shrey Modi (BT2024125) ·
Parthsarathi Samanta (BT2024083)

**Recording setup (suggested):** one screen-share of the report DOCX/PDF +
the Tableau dashboard; each member records their own segment; the team lead
splices. Keep total ≤ 5:00 (target 4:50). Speak the script naturally, don't
read verbatim — but hit every beat and every number.

---

## 0:00 – 0:55 — Sidhanth (team lead / data processing) — *dataset, question, preprocessing*

> "Hi, we're Sidhanth, Shrey, and Parthsarathi. Our dataset is the all-time
> top thousand posts from each of Reddit's fifty largest subreddits — about
> forty-nine thousand posts spanning September 2011 to September 2024,
> collected through Reddit's official API.
>
> Our question: **what does a decade of top posts reveal about how Reddit's
> biggest communities generate engagement — who discusses versus who
> consumes, what media succeeds where, and how that changed over time?**
>
> I led data preparation. We merged the fifty files, fixed a date-format
> quirk in the AskReddit file, and dropped dead columns — like an awards
> field that was one hundred percent zeros. We kept every post — no rows
> were removed — and derived the measures our story runs on: comments per
> thousand upvotes, which we call *discussion intensity*; a five-level
> creation era; and a media-hosting classifier. Medians and log scales
> everywhere, because upvote counts are extremely skewed.
>
> One caveat we handle openly: this corpus only contains *successes*, and
> recent posts have had less time to accumulate upvotes — so we make no
> causal claims, and we read the time axis carefully."

**On screen:** Fig_01 (coverage) while saying the caveat.

## 0:55 – 2:15 — Shrey — *Task Set 2: comparing communities*

> "My task was comparing the fifty communities on how their audiences
> engage. The key measure: **comments per thousand upvotes** — how much
> discussion a post generates for each unit of approval.
>
> Figure 4 shows the result: a spectrum spanning forty-to-one. AskReddit
> generates two hundred and thirty comments per thousand upvotes; wholesome
> meme feeds generate under six. And notice the colour: text-dominant
> communities sit at the discussion end, image feeds at the consumption end
> — Figure 5 shows this content geometry is structural, near one hundred
> percent for many communities.
>
> Figure 6 puts seven metrics side by side as an engagement fingerprint, and
> two patterns pop out. First, a **scale-intensity trade-off**: the median
> top post in discussion communities scores around sixteen thousand upvotes
> versus a hundred thousand in image communities — six times difference.
> Second, Figure 7 maps all fifty communities by score and discussion, with
> bubble size as subscribers — and **AskReddit is alone in the high-score,
> high-discussion corner**. Size doesn't explain style.
>
> Finally Figure 8: communities keep their style across eras — era-by-era
> rank correlations around point-nine. These are durable identities, not
> phases."

**On screen:** Fig_04 → Fig_05 → Fig_06 → Fig_07 → Fig_08.

## 2:15 – 3:25 — Parthsarathi — *Task Set 3: trends and relationships*

> "My task covered time and relationships. First, what top posts are *made
> of* changed decisively. Figure 9: links fell from about half of top posts
> to roughly a third, images rose to around forty percent in 2024, and video
> appeared only after 2017.
>
> Figure 10 shows *why we can trust that timeline*: imgur — once Reddit's
> de-facto image host — collapsed from twenty percent of top posts to
> essentially zero, while Reddit-native hosting rose from zero to
> forty-five percent. The inflection lands exactly at Reddit's own mid-2016
> native image hosting launch, and video appears with its August 2017
> launch — I verified both dates against the public announcements. Top-post
> media moved *inside* the platform.
>
> On relationships: Figure 11 — upvotes and comments correlate only
> moderately, rho point-five-six, and text posts own the high-comment
> region. Success has **two currencies**. And Figure 12: posts with more
> comments have *lower* upvote ratios, rho minus point-four-five — contested
> posts are discussed posts. We report that as an association, not a cause."

**On screen:** Fig_09 → Fig_10 → Fig_11 → Fig_12.

## 3:25 – 4:20 — Sidhanth (+ Shrey for the Tableau demo) — *synthesis + Tableau demo*

> Sidhanth: "Pulling it together — my synthesis task. Figure 13 is the
> profile map: read the geometry first. Even without colours, the
> communities separate into visible bands — image feeds along the top, text
> communities along the bottom, AskReddit isolated at the far right. A
> k-means colouring with k equal to five — chosen where the silhouette
> curve stops improving without fragmenting into singletons — labels five
> profiles: visual entertainment feeds, advice and Q&A text communities,
> news and media link hubs, a few niche-interest communities, and AskReddit
> in a class of its own. The axes do the organising; the clustering just
> labels what's already visible.
>
> Figure 14: all-time lists age differently — over a third of r/Art's top
> posts are from 2022-24, versus half a percent for r/WritingPrompts."
>
> Shrey: "We also built the same analysis as an interactive Tableau
> dashboard. Filtering to a single community — say memes versus AskReddit —
> you can see the two engagement currencies separate live. And switching
> the era filter shows the coverage caveat we flagged earlier,
> interactively."

**On screen:** Fig_13 → Fig_14 → Tableau dashboard (live filtering, ~30s).

## 4:20 – 4:50 — Sidhanth — *conclusion*

> "To conclude: Reddit's largest communities don't succeed in one way —
> they occupy a small set of stable engagement niches. Discussion spaces
> convert modest approval into enormous conversation; visual feeds convert
> massive approval into almost none. Meanwhile the substrate of top content
> migrated on-platform between 2016 and 2018. The practical takeaway for any
> analyst: measure engagement in more than one currency — upvotes, comments,
> consensus and spread are partly decoupled, and communities specialise.
> Thanks for watching."

**On screen:** Fig_13 (profiles) as the closer.

---

### Segment timing budget

| Segment | Speaker | Target | Cumulative |
|---|---|---|---|
| Intro + preprocessing | Sidhanth | 55 s | 0:55 |
| Community comparison | Shrey | 80 s | 2:15 |
| Trends & relationships | Parthsarathi | 70 s | 3:25 |
| Synthesis + Tableau demo | Sidhanth + Shrey | 55 s | 4:20 |
| Conclusion | Sidhanth | 30 s | 4:50 |

### Recording tips
- Zoom/mouse-highlight the exact figure being discussed; one figure at a time.
- Numbers matter — the graders listen for task → visualization → inference.
- Keep the Tableau segment genuinely interactive (click filters live).
- Re-record segments individually; splice in any editor (even Clipchamp).
