# Video Demonstration Script — DAS732 A1 (≤ 5 minutes)

**Team:** Silica — Sidhanth Prabhu (BT2024027, team lead) · Shrey Modi (BT2024125) ·
Parthsarathi Samanta (BT2024083)

**Why this fits:** the script is ~490 words ≈ 3:45 at a natural pace (135 wpm).
With figure transitions you should land at **4:15–4:30** — a deliberate buffer
under the 5:00 cap. Rehearse once with a timer; if you run long, cut from the
*optional* lines marked "(cut if tight)", never from the numbers.

**Setup:** one screen-share of the report + Tableau dashboard; one figure on
screen at a time; each member records their own segment; the lead splices.

---

## 0:00 – 0:50 — Sidhanth — dataset, question, preprocessing (first minute)

> "Hi — we're Sidhanth, Shrey and Parthsarathi, Team Silica. Our dataset is
> the all-time top thousand posts of Reddit's fifty largest subreddits —
> about forty-nine thousand posts, September 2011 to 2024, from Reddit's
> official API.
>
> Our question: **what does a decade of top posts reveal about how Reddit's
> biggest communities generate engagement — who discusses versus who
> consumes, what media succeeds, and how that changed?**
>
> I led preprocessing. We merged the fifty files, fixed a date-format quirk,
> dropped dead columns — like an awards field that was one hundred percent
> zeros — and kept every post. We derived the measure our story runs on:
> **comments per thousand upvotes**, which we call discussion intensity,
> plus creation eras and a media-hosting classifier. Medians and log scales
> throughout. One caveat: this is a top-posts corpus, so we make no causal
> claims — and recent posts haven't had time to accumulate upvotes."

**On screen:** Fig_01 while saying the caveat.

## 0:50 – 1:55 — Shrey — Task Set 2: comparing communities (Figs 4–8)

> "My task: comparing the fifty communities. **Figure 4** is our key result
> — a spectrum spanning **forty-to-one** in comments per thousand upvotes:
> AskReddit at two-thirty, wholesome meme feeds under six. **Figure 5**
> shows why: content is structural — some communities are one hundred
> percent text, others ninety-five percent images.
>
> **Figure 6** stacks seven metrics as an engagement fingerprint, and
> **Figure 7** maps all fifty communities — AskReddit alone sits in the
> high-score, high-discussion corner: size doesn't explain style. There's a
> **scale-intensity trade-off**: median top scores around sixteen thousand
> in discussion communities versus a hundred thousand in image communities.
>
> And **Figure 8**: styles persist across eras — rank correlations around
> point-nine. These are durable identities, not phases."

## 1:55 – 2:55 — Parthsarathi — Task Set 3: trends & relationships (Figs 9–12)

> "My task: time and relationships. **Figure 9**: links fell from half of
> top posts to a third, images rose to around forty percent, video appears
> only after 2017. **Figure 10** anchors the timeline: imgur collapsed from
> twenty percent of top posts to essentially zero while Reddit-native
> hosting rose to forty-five percent — landing exactly on Reddit's 2016
> image-hosting and 2017 video launches, which I verified. Top-post media
> moved *inside* the platform.
>
> On relationships: **Figure 11** — upvotes and comments correlate only
> moderately, rho point-five-six: success has **two currencies**. And
> **Figure 12** — more comments come with *lower* upvote ratios: contested
> posts are discussed posts. An association, not a cause."

## 2:55 – 3:55 — Sidhanth (Figs 13–14) + Parthsarathi (Tableau demo)

> Sidhanth: "My synthesis — **Figure 13**, the profile map. Even without
> colours, the communities separate into visible bands, and a k-means
> colouring with k equal to five labels five profiles: visual feeds, advice
> and Q&A, news hubs, niche communities — and AskReddit in a class of its
> own. The axes do the organising; the clustering just labels what's
> visible. **Figure 14**: all-time lists age differently — a third of
> r/Art's top posts are from 2022-24, versus half a percent for
> r/WritingPrompts."
>
> Parthsarathi: "I built the same analysis as an interactive **Tableau**
> dashboard — filtering AskReddit versus memes shows the two engagement
> currencies separate live."

**On screen:** Fig_13 → Fig_14 → Tableau dashboard (live filtering, ~20s).

## 3:55 – 4:20 — Sidhanth — conclusion

> "To conclude: Reddit's biggest communities don't succeed one way — they
> occupy stable niches: discussion spaces convert modest approval into
> enormous conversation; visual feeds convert massive approval into almost
> none. And engagement has more than one currency — upvotes, comments,
> consensus and spread are partly decoupled, and communities specialise.
> Thanks for watching."

---

### Segment timing budget

| Segment | Speaker | Target | Cumulative |
|---|---|---|---|
| Intro + preprocessing | Sidhanth | 50 s | 0:50 |
| Community comparison | Shrey | 65 s | 1:55 |
| Trends & relationships | Parthsarathi | 60 s | 2:55 |
| Synthesis + Tableau demo | Sidhanth + Parthsarathi | 60 s | 3:55 |
| Conclusion | Sidhanth | 25 s | 4:20 |

### Recording tips
- One figure at a time; mouse-highlight exactly what is being said.
- Numbers matter — graders listen for **task → visualization → inference**.
- Keep the Tableau demo genuinely interactive (click filters live), ~20 s.
- Re-record segments individually; if the splice exceeds 4:40, drop the
  Figure 14 sentence and the Figure 6 sentence first — never the numbers in
  Figures 4, 10 and 13.
