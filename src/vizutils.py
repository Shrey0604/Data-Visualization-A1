"""Shared visualization utilities for DAS732 A1 figure scripts.

audit_overlaps: render-time collision audit for text artists, legends and
axis labels (the same discipline applied to report figures and exploration
candidates).

place_labels: automatic de-overlapping of point labels via adjustText.
"""
import matplotlib as mpl

try:
    from adjustText import adjust_text
    HAVE_ADJUST = True
except ImportError:
    HAVE_ADJUST = False


def audit_overlaps(fig, name=""):
    """Return a list of layout-issue strings for a rendered figure.

    Detects (a) any pairwise overlap among text artists, legends, axis
    labels and suptitles, and (b) data labels that extend outside the
    figure canvas. Returns an empty list when the layout is clean.
    """
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    items = []  # (label, bbox, is_movable_text)
    for ax in fig.axes:
        for t in ax.texts:
            if t.get_text().strip():
                items.append((t.get_text()[:30].replace("\n", "|"),
                              t.get_window_extent(ren), True))
        leg = ax.get_legend()
        if leg is not None:
            items.append(("<LEGEND>", leg.get_window_extent(ren), False))
        if ax.xaxis.label.get_text():
            items.append(("<xlabel>", ax.xaxis.label.get_window_extent(ren), False))
        if ax.yaxis.label.get_text():
            items.append(("<ylabel>", ax.yaxis.label.get_window_extent(ren), False))
    for t in fig.texts:
        if t.get_text().strip():
            items.append(("<suptitle>", t.get_window_extent(ren), False))
    issues = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i][1].overlaps(items[j][1]):
                issues.append(f"OVERLAP: '{items[i][0]}' <-> '{items[j][0]}'")
    fb = fig.bbox
    for lab, bb, movable in items:
        if movable and (bb.x0 < fb.x0 - 2 or bb.x1 > fb.x1 + 2
                        or bb.y0 < fb.y0 - 2 or bb.y1 > fb.y1 + 2):
            issues.append(f"CLIPPED: '{lab}' extends outside figure")
    return issues


def place_labels(ax, texts, x, y):
    """De-overlap a list of ax.text artists (adjustText if available)."""
    if HAVE_ADJUST and texts:
        adjust_text(texts, x=x, y=y, ax=ax,
                    expand=(1.35, 1.7),
                    force_text=(0.35, 0.7),
                    force_static=(0.35, 0.7),
                    time_lim=4, iter_lim=300,
                    only_move={"points": "y", "text": "xy",
                               "static": "xy", "pull": "xy"},
                    arrowprops=dict(arrowstyle="-", color="#999999", lw=0.6))
