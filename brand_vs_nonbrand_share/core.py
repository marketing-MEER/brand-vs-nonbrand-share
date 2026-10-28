"""Branded vs non-branded organic traffic for your site and competitors.

Each keyword is labelled own brand, competitor brand (it names another tracked site)
or non-brand, and every site's branded share of traffic is set against NP Digital's
averages for typical and top-performing sites.
"""
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from .report import find_column, to_number

# Share of search traffic from brand terms, NP Digital analysis of 42,391 sites (Nov/Dec 2024):
# average sites 2.44%, top-performing sites 9.74%.
# Source: https://neilpatel.com/marketing-stats/percentage-search-traffic-brand-terms/
AVERAGE_SITE_PCT = 2.44
TOP_SITE_PCT = 9.74

# Branded query share by company revenue (same dataset):
# under $1M <2%, $1M-$10M ~4%, $10M-$100M >6%, over $100M ~10%.
# Source: https://neilpatel.com/marketing-stats/brand-queries-by-revenue-size/
REVENUE_BANDS = [(2, "under $1M revenue (<2%)"), (4, "$1M-$10M revenue (~4%)"), (6, "$10M-$100M revenue (>6%)"),
                 (10, "$100M+ revenue (~10%)")]

CLASS_ORDER = ["own brand", "competitor brand", "non-brand"]


def compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def default_brand(site: str) -> list[str]:
    """'www.bright-crm.io' -> ['bright-crm', 'bright crm']; the compact match covers 'brightcrm'."""
    label = site.split(".")[0] if site.count(".") <= 1 else site.split(".")[-2]
    return sorted({label, label.replace("-", " ")})


def parse_brand_option(text: str) -> tuple[str, list[str]]:
    if "=" not in text:
        raise ValueError(f"--brand must look like site=term1,term2, got {text!r}")
    site, terms = text.split("=", 1)
    return site.strip().lower().removeprefix("www."), [t.strip().lower() for t in terms.split(",") if t.strip()]


def matches(keyword: str, terms) -> bool:
    kw_compact = compact(keyword)
    for term in terms:
        c = compact(term)
        if len(c) >= 4 and c in kw_compact:
            return True
        if c and re.search(rf"\b{re.escape(term.lower())}\b", keyword):
            return True
    return False


def site_name(raw: pd.DataFrame, url_col: str | None, path) -> str:
    if url_col:
        for url in raw[url_col].dropna().astype(str):
            host = urlparse(url if "://" in url else "https://" + url).netloc.lower()
            if host:
                return host[4:] if host.startswith("www.") else host
    return Path(path).stem


def load_export(path) -> tuple[str, pd.DataFrame]:
    raw = pd.read_csv(path)
    kw = find_column(raw, ["keyword", "query", "top queries", "search term"])
    traffic = find_column(raw, ["traffic", "clicks", "organic traffic", "current traffic", "url clicks"])
    vol = find_column(raw, ["volume", "search volume", "impressions"])
    pos = find_column(raw, ["position", "current position", "rank"])
    url = find_column(raw, ["url", "current url", "landing page", "page"])
    if not kw or not traffic:
        raise ValueError(f"{path}: need keyword and traffic (or clicks) columns. Found: {list(raw.columns)}")
    df = pd.DataFrame({
        "keyword": raw[kw].astype(str).str.strip().str.lower(),
        "traffic": to_number(raw[traffic]),
        "volume": to_number(raw[vol]) if vol else 0,
        "position": to_number(raw[pos]) if pos else 0,
    })
    df = df[df["keyword"] != ""].groupby("keyword", as_index=False).agg(
        traffic=("traffic", "sum"), volume=("volume", "max"), position=("position", "min"))
    return site_name(raw, url, path), df


def benchmark_band(pct: float) -> str:
    if pct >= TOP_SITE_PCT:
        return "top-site level (9.74%+)"
    if pct >= AVERAGE_SITE_PCT:
        return "above average (2.44-9.74%)"
    return "below average (<2.44%)"


def revenue_band(pct: float) -> str:
    label = REVENUE_BANDS[0][1]
    for threshold, name in REVENUE_BANDS:
        if pct >= threshold:
            label = name
    return label


def analyze(paths, brands: dict[str, list[str]] | None = None):
    """Return (keywords, sites, brand_terms)."""
    brands = brands or {}
    loaded, sites = [], []
    for i, path in enumerate(paths):
        name, df = load_export(path)
        name = name if name not in sites else f"{name} ({i + 1})"
        sites.append(name)
        loaded.append(df)
    terms = {s: brands.get(s, default_brand(s)) for s in sites}
    frames = []
    for site, df in zip(sites, loaded):
        df = df.copy()
        others = [t for s in sites if s != site for t in terms[s]]

        def classify(kw, own=terms[site], others=others):
            if matches(kw, own):
                return "own brand"
            if matches(kw, others):
                return "competitor brand"
            return "non-brand"

        df["class"] = df["keyword"].map(classify)
        df.insert(0, "site", site)
        frames.append(df)
    kws = pd.concat(frames, ignore_index=True)
    kws["_c"] = kws["class"].map(CLASS_ORDER.index)
    kws = kws.sort_values(["site", "_c", "traffic"], ascending=[True, True, False]).drop(columns="_c")
    return kws.reset_index(drop=True), sites, terms


def summary(kws: pd.DataFrame, sites: list[str], terms: dict) -> pd.DataFrame:
    rows = []
    for site in sites:
        g = kws[kws["site"] == site]
        total = g["traffic"].sum()
        own = g.loc[g["class"] == "own brand", "traffic"].sum()
        comp = g.loc[g["class"] == "competitor brand", "traffic"].sum()
        pct = round(own / total * 100, 2) if total else 0.0
        rows.append({
            "site": site,
            "brand_terms": ", ".join(terms[site]),
            "keywords": len(g),
            "traffic": int(total),
            "brand_traffic": int(own),
            "brand_share_pct": pct,
            "competitor_brand_traffic": int(comp),
            "non_brand_traffic": int(total - own - comp),
            "vs_benchmark": benchmark_band(pct),
            "similar_to_companies_of": revenue_band(pct),
        })
    return pd.DataFrame(rows)


def competitor_brand_keywords(kws: pd.DataFrame) -> pd.DataFrame:
    """Keywords where a site ranks for another tracked brand ('x alternatives', 'x vs y')."""
    return kws[kws["class"] == "competitor brand"].sort_values("traffic", ascending=False).reset_index(drop=True)


def top_non_brand(kws: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    g = kws[kws["class"] == "non-brand"].sort_values("traffic", ascending=False)
    return g.groupby("site", sort=False).head(n).reset_index(drop=True)
