import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from brand_vs_nonbrand_share import cli, core

EXAMPLES = Path(__file__).parent.parent / "examples"

YOU = """Keyword,Traffic,Current URL
acme crm,30,https://www.acme-crm.com/
acmecrm login,20,https://www.acme-crm.com/login
free crm,900,https://www.acme-crm.com/free
rival alternatives,50,https://www.acme-crm.com/vs
"""
RIVAL = """Query,Clicks
rival,100
crm software,100
"""


class MatchTest(unittest.TestCase):
    def test_default_brand_and_matching(self):
        self.assertEqual(core.default_brand("acme-crm.com"), ["acme crm", "acme-crm"])
        self.assertTrue(core.matches("acmecrm login", ["acme crm"]))      # compact match
        self.assertTrue(core.matches("acme crm pricing", ["acme-crm"]))
        self.assertFalse(core.matches("free crm", ["acme crm"]))
        self.assertTrue(core.matches("hp laptop", ["hp"]))                 # short term: whole word only
        self.assertFalse(core.matches("php tutorial", ["hp"]))

    def test_bands(self):
        self.assertEqual(core.benchmark_band(1.0), "below average (<2.44%)")
        self.assertEqual(core.benchmark_band(5.0), "above average (2.44-9.74%)")
        self.assertEqual(core.benchmark_band(9.74), "top-site level (9.74%+)")
        self.assertEqual(core.revenue_band(1.5), "under $1M revenue (<2%)")
        self.assertEqual(core.revenue_band(6.5), "$10M-$100M revenue (>6%)")

    def test_parse_brand_option(self):
        self.assertEqual(core.parse_brand_option("www.a.com=A, a app"), ("a.com", ["a", "a app"]))
        with self.assertRaises(ValueError):
            core.parse_brand_option("a.com")


class CoreTest(unittest.TestCase):
    def test_classes_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "you.csv").write_text(YOU, encoding="utf-8")
            (d / "rival.csv").write_text(RIVAL, encoding="utf-8")
            kws, sites, terms = core.analyze([d / "you.csv", d / "rival.csv"])
        self.assertEqual(sites, ["acme-crm.com", "rival"])
        c = kws.set_index(["site", "keyword"])["class"]
        self.assertEqual(c[("acme-crm.com", "acmecrm login")], "own brand")
        self.assertEqual(c[("acme-crm.com", "rival alternatives")], "competitor brand")
        self.assertEqual(c[("acme-crm.com", "free crm")], "non-brand")
        summ = core.summary(kws, sites, terms).set_index("site")
        self.assertEqual(summ.at["acme-crm.com", "brand_share_pct"], 5.0)   # 50 of 1000
        self.assertEqual(summ.at["rival", "brand_share_pct"], 50.0)
        self.assertEqual(summ.at["acme-crm.com", "competitor_brand_traffic"], 50)


class CliTest(unittest.TestCase):
    def test_example_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "brand"
            args = [str(EXAMPLES / f) for f in ["brightcrm_keywords.csv", "pipelinehq_keywords.csv",
                                                 "salesdeck_keywords.csv"]]
            args += ["--brand", "pipelinehq.com=pipelinehq,pipeline hq", "-o", str(out)]
            res = CliRunner().invoke(cli.main, args)
            self.assertEqual(res.exit_code, 0, res.output)
            self.assertIn("Brand vs non-brand traffic", out.with_suffix(".html").read_text(encoding="utf-8"))
            self.assertTrue(out.with_suffix(".xlsx").exists())


if __name__ == "__main__":
    unittest.main()
