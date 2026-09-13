"""DAS732 A1 — Build report.docx from report/report.md (single source of truth).

Parses the constrained Markdown subset used in report.md:
  - headings (#/##/###), paragraphs, - bullets, 1. numbered lists
  - | tables |, > blockquotes, ![captions](image paths), --- rules
  - inline **bold** / *italic* / `code` / [text](url)
  - hard-wrapped paragraphs: consecutive plain lines are joined into a
    single paragraph (CommonMark behaviour)

Not supported (report.md deliberately avoids these): nested lists, code
blocks, footnotes, multi-level tables, HTML. If you need them, extend
`build()` — the report is rendered exclusively through this subset, so the
DOCX output is faithful for everything report.md contains.

Output: report/report.docx (US Letter, 1in margins).
"""
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

HERE = os.path.dirname(__file__)
MD = os.path.join(HERE, "..", "report", "report.md")
OUT = os.path.join(HERE, "..", "report", "report.docx")
IMG_WIDTH = Inches(6.5)

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`|\[[^\]]+?\]\([^)]+?\))")
NUM_LIST = re.compile(r"^(\d+)\.\s+(.*)$")
RULE = re.compile(r"^-{3,}\s*$")


def add_inline(par, text, base_italic=False):
    for tok in INLINE.split(text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            r = par.add_run(tok[2:-2]); r.bold = True
        elif tok.startswith("`") and tok.endswith("`"):
            r = par.add_run(tok[1:-1]); r.font.name = "Consolas"
        elif tok.startswith("[") and "](" in tok:
            label, url = tok[1:-1].split("](", 1)
            r = par.add_run(label); r.bold = True
            par.add_run(f" ({url})")
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            r = par.add_run(tok[1:-1]); r.italic = True
        else:
            r = par.add_run(tok)
        if base_italic:
            r.italic = True


def _flush_paragraph(doc, buf, style=None, italic=False):
    if not buf:
        return
    p = doc.add_paragraph(style=style)
    add_inline(p, " ".join(buf), base_italic=italic)
    buf.clear()


def build(md_path: str, out_path: str) -> Document:
    doc = Document()
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Inches(1)
        sec.top_margin = sec.bottom_margin = Inches(1)
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)

    lines = open(md_path, encoding="utf-8").read().splitlines()
    i, first_h1, buf = 0, True, []

    def flush():
        _flush_paragraph(doc, buf)

    while i < len(lines):
        line = lines[i]

        if line.startswith("![") and "](" in line:
            flush()
            cap, path = line[2:].split("](", 1)
            path = path.rstrip(")")
            img_path = os.path.normpath(os.path.join(os.path.dirname(md_path), path))
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(img_path, width=IMG_WIDTH)
            cp = doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(12)
            add_inline(cp, cap)
            for r in cp.runs:
                r.font.size = Pt(9.5)
                if not r.bold:
                    r.italic = True
            i += 1
            continue

        if line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                t = doc.add_table(rows=len(rows), cols=len(rows[0]))
                t.style = "Light Grid Accent 1"
                for ri, row in enumerate(rows):
                    for ci, cell in enumerate(row):
                        c = t.cell(ri, ci)
                        c.text = ""
                        add_inline(c.paragraphs[0], cell)
                        if ri == 0:
                            for r in c.paragraphs[0].runs:
                                r.bold = True
                doc.add_paragraph()
            continue

        if line.startswith("#### "):
            flush(); doc.add_heading(line[5:], level=3); i += 1; continue
        if line.startswith("### "):
            flush(); doc.add_heading(line[4:], level=2); i += 1; continue
        if line.startswith("## "):
            flush(); doc.add_heading(line[3:], level=1); i += 1; continue
        if line.startswith("# "):
            flush()
            doc.add_heading(line[2:], level=0 if first_h1 else 1)
            first_h1 = False
            i += 1; continue

        if line.startswith("> "):
            flush()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35)
            add_inline(p, line[2:], base_italic=True)
            i += 1; continue

        if line.startswith("- "):
            flush()
            p = doc.add_paragraph(style="List Bullet")
            add_inline(p, line[2:])
            i += 1; continue

        m = NUM_LIST.match(line)
        if m:
            flush()
            p = doc.add_paragraph(style="List Number")
            add_inline(p, m.group(2))
            i += 1; continue

        if RULE.match(line) or not line.strip():
            flush()
            i += 1; continue

        # plain text: buffer so hard-wrapped lines join into one paragraph
        buf.append(line.strip())
        i += 1

    flush()
    doc.save(out_path)
    return doc


def main():
    build(MD, OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
