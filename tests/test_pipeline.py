"""Automated correctness tests for the DAS732 A1 pipeline.

Run from the project root:
    python -m unittest discover -s tests -v

Covers (review item: "no automated correctness tests"):
  - preprocessing: row counts, uniqueness, date parsing, derived variables
  - aggregation: subreddit summary consistency with the raw merge
  - clustering: the documented k-selection rule and seed stability
  - heatmap masking: the "blank = fewer than 5 top posts" contract
  - DOCX builder: paragraph joining, numbered lists, tables, headings
  - domain classifier: every branch
"""
import importlib
import os
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import config  # noqa: E402
import vizutils  # noqa: E402

_prepare = importlib.import_module("02_prepare")
_builder = importlib.import_module("05_build_docx")


class TestPreprocessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = _prepare.load_and_clean()
        cls.subs = _prepare.subreddit_aggregates(cls.df)

    def test_row_count_and_uniqueness(self):
        self.assertEqual(len(self.df), 49_266)
        self.assertEqual(self.df["id"].duplicated().sum(), 0)
        self.assertEqual(self.df["subreddit"].nunique(), 50)

    def test_dates_parse_and_range(self):
        self.assertEqual(self.df["created_dt"].isna().sum(), 0)
        self.assertEqual(int(self.df["year"].min()), 2011)
        self.assertEqual(int(self.df["year"].max()), 2024)

    def test_derived_variables(self):
        expect = self.df["num_comments"] / self.df["score"].clip(lower=1)
        self.assertTrue(np.allclose(self.df["cpi"], expect))
        self.assertTrue(set(self.df["era"].dropna().cat.categories)
                        <= set(config.ERA_LABELS))
        valid = {"no link", "self post", "reddit-native", "imgur",
                 "youtube", "other video hosts", "other external"}
        self.assertTrue(set(self.df["domain_class"]) <= valid)

    def test_no_rows_or_core_columns_dropped(self):
        # the outlier policy: nothing is removed from the merged corpus
        raw_rows = sum(
            len(pd.read_csv(os.path.join(_prepare.RAW, f)))
            for f in os.listdir(_prepare.RAW)
            if f.endswith(".csv") and "50_subreddits_list" not in f)
        self.assertEqual(len(self.df), raw_rows)
        for col in ["id", "title", "score", "num_comments", "upvote_ratio",
                    "created_utc", "subreddit", "post_type"]:
            self.assertIn(col, self.df.columns)
        for dropped in _prepare.DROP_COLS:
            self.assertNotIn(dropped, self.df.columns)


class TestSubredditSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = _prepare.load_and_clean()
        cls.subs = _prepare.subreddit_aggregates(cls.df)

    def test_shape(self):
        self.assertEqual(len(self.subs), 50)
        self.assertEqual(len(self.subs.columns), 17)

    def test_aggregates_match_direct_computation(self):
        for name in ["funny", "AskReddit", "wholesomememes", "IAmA"]:
            row = self.subs[self.subs["subreddit"] == name].iloc[0]
            d = self.df[self.df["subreddit"] == name]
            self.assertEqual(row["median_score"], d["score"].median())
            self.assertEqual(row["median_comments"], d["num_comments"].median())
            self.assertAlmostEqual(row["median_ratio"], d["upvote_ratio"].median())
            self.assertEqual(row["posts"], len(d))


class TestKSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subs = pd.read_csv(os.path.join(
            os.path.dirname(__file__), "..", "data", "processed",
            "subreddit_summary.csv"))
        cls.Z = vizutils.profile_features(cls.subs)

    def test_selection_rule_yields_five(self):
        table = vizutils.k_selection_table(self.Z)
        self.assertEqual(len(table), len(list(config.K_RANGE)))
        self.assertEqual(vizutils.select_k(self.Z), 5)
        # rule check: k=6 is ineligible because two clusters have < 6 members
        row6 = table[table["k"] == 6].iloc[0]
        self.assertGreater(row6["n_small"], config.MAX_SMALL_PROFILES)

    def test_seed_stability(self):
        ari = vizutils.k_stability_ari(self.Z, 5)
        self.assertGreater(ari, 0.75)  # report claims 0.88; loose bound


class TestMaskSmallGroups(unittest.TestCase):
    def test_masking_contract(self):
        values = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]})
        counts = pd.DataFrame({"a": [10, 2, 0], "b": [5, 1, 7]})
        out = vizutils.mask_small_groups(values, counts, min_n=5)
        np.testing.assert_equal(out["a"].tolist(), [1.0, np.nan, np.nan])
        np.testing.assert_equal(out["b"].tolist(), [4.0, np.nan, 6.0])

    def test_missing_counts_are_masked(self):
        values = pd.DataFrame({"a": [1.0, 2.0]})
        counts = pd.DataFrame({"a": [10.0, np.nan]})
        out = vizutils.mask_small_groups(values, counts, min_n=5)
        np.testing.assert_equal(out["a"].tolist(), [1.0, np.nan])


class TestDocxBuilder(unittest.TestCase):
    def build(self, md):
        with tempfile.TemporaryDirectory() as tmp:
            md_path = os.path.join(tmp, "t.md")
            out_path = os.path.join(tmp, "t.docx")
            with open(md_path, "w", encoding="utf-8") as fh:
                fh.write(md)
            doc = _builder.build(md_path, out_path)
            return doc

    def test_wrapped_paragraph_joins(self):
        doc = self.build("First line of a paragraph\nthat continues here.\n")
        paras = [p.text for p in doc.paragraphs if p.text.strip()]
        self.assertEqual(paras, ["First line of a paragraph that continues here."])

    def test_separate_lines_stay_separate(self):
        doc = self.build("**Team:** X\n\n**Members:** Y\n")
        paras = [p.text for p in doc.paragraphs if p.text.strip()]
        self.assertEqual(paras, ["Team: X", "Members: Y"])

    def test_numbered_list(self):
        doc = self.build("1. first item\n2. second item\n")
        styles = [p.style.name for p in doc.paragraphs if p.text.strip()]
        self.assertEqual(styles, ["List Number", "List Number"])

    def test_table_and_headings(self):
        doc = self.build("# Title\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
        self.assertEqual(len(doc.tables), 1)
        self.assertEqual(doc.tables[0].cell(0, 0).text, "a")
        headings = [p.text for p in doc.paragraphs if p.style.name == "Title"]
        self.assertEqual(headings, ["Title"])


class TestDomainClassifier(unittest.TestCase):
    def test_branches(self):
        f = config.classify_domain
        self.assertEqual(f("i.redd.it"), "reddit-native")
        self.assertEqual(f("v.redd.it"), "reddit-native")
        self.assertEqual(f("self.AskReddit"), "self post")
        self.assertEqual(f("i.imgur.com"), "imgur")
        self.assertEqual(f("youtu.be"), "youtube")
        self.assertEqual(f("gfycat.com"), "other video hosts")
        self.assertEqual(f("theguardian.com"), "other external")
        self.assertTrue(pd.isna(f(np.nan)) or f(np.nan) == "no link")


if __name__ == "__main__":
    unittest.main()
