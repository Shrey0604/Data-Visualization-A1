"""DAS732 A1 — Build per-member AI Disclosure Statements (professor's template).

Template: report/DAS732-T1-26-27-AI-Disclosure-Statement.docx
Outputs:  report/AI_Declaration_<Member>.docx  (one per team member)

Every statement is pre-filled from the team's actual, shared AI workflow and
the member's task ownership (report Section 9). Each member MUST review
their copy — especially the tool names and the integrity declaration — and
adjust it to their personal usage before signing.

Run: python src/07_build_ai_declarations.py
"""
import os

from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "..", "report")

BOX_YES, BOX_NO = "\u2612", "\u2610"   # ☒, ☐

INTEGRITY = ("I certify that all data interpretations, analytical "
             "conclusions, dashboard layout decisions, and final insights "
             "represent my own critical thinking and understanding of the "
             "dataset. All custom JavaScript logic, Tableau workbooks, and "
             "Python scripts have been fully reviewed and validated by me. "
             "AI tools served exclusively as operational assistants for "
             "debugging, boilerplate, and copyediting.")

NOTE = ("Pre-filled from the team's shared AI-assisted workflow and this "
        "member's task ownership. Review every entry and adjust tool names "
        "to your personal, actual usage before signing.")


def add_doc(doc, text, size=11, bold=False, italic=False, indent=0, space=2):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space)
    if indent:
        p.paragraph_format.left_indent = Pt(indent)
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.size = Pt(size)
    return p


def section(doc, num, title, tools, checked, description):
    add_doc(doc, f"## {num}. {title}", 12.5, bold=True)
    add_doc(doc, f"* Tool(s) Used: {tools}", indent=12)
    add_doc(doc, "* Specific Applications:", indent=12, bold=True)
    for item, yes in checked:
        add_doc(doc, f"   {BOX_YES if yes else BOX_NO} {item}", indent=24)
    add_doc(doc, f"* Prompts Used & Modification Level: {description}",
            indent=12)


def section_desc(doc, num, title, tools, checked, label, description):
    add_doc(doc, f"## {num}. {title}", 12.5, bold=True)
    add_doc(doc, f"* Tool(s) Used: {tools}", indent=12)
    add_doc(doc, "* Specific Applications:", indent=12, bold=True)
    for item, yes in checked:
        add_doc(doc, f"   {BOX_YES if yes else BOX_NO} {item}", indent=24)
    add_doc(doc, f"* {label} {description}", indent=12)


NONE_JS = [("None", True)]
JS_APPS = [("None", True)]

MEMBERS = [
    {
        "file": "AI_Declaration_Sidhanth_Prabhu.docx",
        "name": "Sidhanth Prabhu", "roll": "BT2024027",
        "role": "Team lead — data preparation pipeline; corpus overview and "
                "synthesis figures (Figures 1–3, 13–14); dataset description.",
        "s1_tools": "Claude (Anthropic), via the team's shared AI-assisted workflow",
        "s1_apps": [("None", False),
                    ("Data cleaning, filtering, or restructuring scripts (Pandas / NumPy)", True),
                    ("Plot/Chart generation boilerplate (Matplotlib / Seaborn / Plotly)", True),
                    ("Statistical calculation code (SciPy / Statsmodels)", True),
                    ("Debugging error logs or fixing code syntax", True)],
        "s1_desc": ("I asked the AI to scaffold the preprocessing pipeline "
                    "(merging 50 per-subreddit CSVs, the dual-format date "
                    "parsing for the AskReddit file, and derived variables "
                    "such as comments-per-upvote, era bins, and the hosting "
                    "classifier) and to draft the overview and synthesis "
                    "figures. I reviewed the scripts line by line, re-ran the "
                    "pipeline myself, corrected an aggregation bug it "
                    "introduced during refactoring, and verified every number "
                    "against the raw files. The preprocessing decisions "
                    "themselves (dropping the all-zero awards column, the "
                    "no-rows-dropped outlier policy, the era binning) were "
                    "made and justified by me, not by the AI."),
        "s2_desc": None,
        "s3_desc": None,
        "s4_tools": "Claude (Anthropic), via the team's shared AI-assisted workflow",
        "s4_apps": [("None", False),
                    ("Outlining the structure of the data analysis report", True),
                    ("Drafting descriptions of visual patterns, trends, or dashboard anomalies", True),
                    ("Translating statistical findings into non-technical stakeholder language", True),
                    ("Proofreading, tone refinement, and formatting text", True),
                    ("Generating inline JSDoc or Python docstrings / comments", True)],
        "s4_desc": ("The AI drafted first-pass section text from my analysis "
                    "notes and figure outputs; I edited every section, "
                    "verified each statistic against the pipeline output, and "
                    "rewrote interpretations where needed. The framing "
                    "choices — accumulation-time bias for the 2024 dip, the "
                    "no-causal-claims policy, the k-selection rule in "
                    "Appendix C — are my own. No verbatim AI text is "
                    "presented as my analysis without review."),
    },
    {
        "file": "AI_Declaration_Shrey_Modi.docx",
        "name": "Shrey Modi", "roll": "BT2024125",
        "role": "Community comparison — engagement spectrum, content geometry, "
                "fingerprint heatmap, engagement map, style-persistence heatmap "
                "(Figures 4–8).",
        "s1_tools": "Claude (Anthropic), via the team's shared AI-assisted workflow",
        "s1_apps": [("None", False),
                    ("Data cleaning, filtering, or restructuring scripts (Pandas / NumPy)", False),
                    ("Plot/Chart generation boilerplate (Matplotlib / Seaborn / Plotly)", True),
                    ("Statistical calculation code (SciPy / Statsmodels)", True),
                    ("Debugging error logs or fixing code syntax", True)],
        "s1_desc": ("I asked the AI to generate candidate versions of the "
                    "comparison figures (the discussion-intensity spectrum, "
                    "content geometry, the z-score fingerprint heatmap, the "
                    "bubble engagement map, and the subreddit-by-era "
                    "persistence heatmap), including the automatic label "
                    "de-overlap code. I selected, tuned, and interpreted the "
                    "final versions, and validated the medians and the "
                    "era-by-era rank-stability statistics by re-running the "
                    "analysis scripts and checking them against the "
                    "subreddit summary table myself."),
        "s2_desc": None,
        "s3_desc": None,
        "s4_tools": "Claude (Anthropic), via the team's shared AI-assisted workflow",
        "s4_apps": [("None", False),
                    ("Outlining the structure of the data analysis report", False),
                    ("Drafting descriptions of visual patterns, trends, or dashboard anomalies", True),
                    ("Translating statistical findings into non-technical stakeholder language", True),
                    ("Proofreading, tone refinement, and formatting text", True),
                    ("Generating inline JSDoc or Python docstrings / comments", False)],
        "s4_desc": ("The AI helped tighten the wording of my findings "
                    "(F1–F3, co-authored F6). The interpretations — the "
                    "consumption-versus-discussion spectrum, the "
                    "scale-intensity trade-off, and the style-persistence "
                    "reading — are my own reading of the figures, "
                    "cross-checked against the summary statistics. No "
                    "verbatim AI text is presented as my analysis without "
                    "review."),
    },
    {
        "file": "AI_Declaration_Parthsarathi_Samanta.docx",
        "name": "Parthsarathi Samanta", "roll": "BT2024083",
        "role": "Temporal trends and relationships (Figures 9–12); external "
                "verification of platform-launch dates; Tableau dashboard "
                "(Reddit Engagement Explorer) built and demonstrated by me.",
        "s1_tools": "Claude (Anthropic), via the team's shared AI-assisted workflow",
        "s1_apps": [("None", False),
                    ("Data cleaning, filtering, or restructuring scripts (Pandas / NumPy)", True),
                    ("Plot/Chart generation boilerplate (Matplotlib / Seaborn / Plotly)", True),
                    ("Statistical calculation code (SciPy / Statsmodels)", True),
                    ("Debugging error logs or fixing code syntax", True)],
        "s1_desc": ("The AI drafted the hosting-domain classifier and the "
                    "temporal/relationship figures (media shift, hosting "
                    "migration, score-vs-comments, ratio-vs-comments) plus "
                    "the Spearman calculations. I reviewed and re-ran them, "
                    "and I personally verified the external timeline against "
                    "Reddit's public announcements (native image hosting, "
                    "mid-2016; native video, August 2017) before the report "
                    "cited it."),
        "s2_desc": None,
        "s3_tools": ("ChatGPT / Claude for calculated-field syntax; no "
                     "Tableau-native AI features (Tableau Pulse, Einstein AI) "
                     "were used"),
        "s3_apps": [("None", False),
                    ("Writing complex Calculated Fields or Level of Detail (LOD) expressions", True),
                    ("Formatting / Regular Expression (RegEx) string cleanup formulas", False),
                    ("AI-driven insight generation or automated trend summaries", False)],
        "s3_desc": ("AI drafted the workbook build specification and the "
                    "calculated-field definitions (notably the 'Comments per "
                    "1,000 upvotes' field and the logarithmic-axis setup). I "
                    "implemented the workbook myself in Tableau: connected "
                    "the processed CSV, built the four sheets (engagement "
                    "map, engagement spectrum, media shift, score vs. "
                    "comments), wired the era / post-type / subreddit filters "
                    "across the dashboard, and chose what to demonstrate in "
                    "the video. All dashboard layout decisions and every "
                    "insight shown are from the team's Python analysis, not "
                    "from any AI-driven insight feature."),
        "s4_tools": "Claude (Anthropic), via the team's shared AI-assisted workflow",
        "s4_apps": [("None", False),
                    ("Outlining the structure of the data analysis report", False),
                    ("Drafting descriptions of visual patterns, trends, or dashboard anomalies", True),
                    ("Translating statistical findings into non-technical stakeholder language", True),
                    ("Proofreading, tone refinement, and formatting text", True),
                    ("Generating inline JSDoc or Python docstrings / comments", False)],
        "s4_desc": ("The AI helped structure the trends section and tighten "
                    "my findings (F4, F7). The decision to report the "
                    "ratio-comments association without causal language, and "
                    "the external verification of the platform-launch dates, "
                    "are my own analytical judgements. No verbatim AI text "
                    "is presented as my analysis without review."),
    },
]

JS_SECTION = dict(
    num=2, title="Interactive Web Dashboards (JavaScript)",
    tools="None — the interactive component of this project was delivered as "
          "a Tableau dashboard, not a JavaScript application",
    checked=NONE_JS,
    label="Description of AI Involvement:",
    description=("No JavaScript pipeline exists in this project, so this section is "
          "not applicable. The interactive filtering demonstrated in the "
          "video (era / post-type / subreddit filters linked across sheets) "
          "was implemented natively in Tableau and is declared under "
          "Section 3."),
)


def build_statement(member):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    add_doc(doc, "DAS732 - Term 1 - 2026-27, IIITB", 12, bold=True)
    add_doc(doc, "# Project & Report AI Disclosure Statement", 13, bold=True)
    add_doc(doc, f"Project: Programming Assignment 1 (A1) — Visual "
                 f"Exploration of Reddit's Top Communities (2011–2024) — "
                 f"Team Silica", italic=True)
    add_doc(doc, NOTE, 9.5, italic=True)
    add_doc(doc, f"Name of Student: {member['name']}", bold=True)
    add_doc(doc, f"Roll Number: {member['roll']}", bold=True)
    add_doc(doc, f"Role in project: {member['role']}", italic=True)

    section(doc, 1, "Data Processing and Python Code Generation",
            member["s1_tools"], member["s1_apps"], member["s1_desc"])

    section_desc(doc, **JS_SECTION)

    if member["s3_desc"] is None:
        section(doc, 3, "Visual Analytics Intelligence Tooling (Tableau)",
                "None — this member did no Tableau work",
                [("None", True)],
                "Description of AI Involvement: Not applicable — this "
                "member performed no Tableau work; the interactive dashboard "
                "was built and demonstrated by Parthsarathi Samanta.")
    else:
        section_desc(doc, 3,
                     "Visual Analytics Intelligence Tooling (Tableau)",
                     member["s3_tools"], member["s3_apps"],
                     "Description of AI Involvement:", member["s3_desc"])

    section_desc(doc, 4,
                 "Report Writing, Data Analysis, and Documentation",
                 member["s4_tools"], member["s4_apps"],
                 "Description of AI Involvement:", member["s4_desc"])

    add_doc(doc, "## 5. Integrity and Originality Validation", 12.5, bold=True)
    add_doc(doc, f"* Core Logic & Analysis Statement: {INTEGRITY}", indent=12)
    add_doc(doc, "* Link to Chat Transcripts (If applicable): "
                 "[insert URL — attach the relevant conversation exports]",
            indent=12)
    add_doc(doc, "Signature: ____________________          Date: ____________",
            bold=True)

    out = os.path.join(OUT_DIR, member["file"])
    doc.save(out)
    print(f"wrote {out}")


def main():
    for m in MEMBERS:
        build_statement(m)


if __name__ == "__main__":
    main()
