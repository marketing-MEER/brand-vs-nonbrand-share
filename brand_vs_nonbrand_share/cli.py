"""Command line entry point: `brand-vs-nonbrand-share YOU.csv [COMPETITOR.csv ...]`."""
from pathlib import Path

import click

from . import __version__, core
from .benchmark import STATS
from .report import Report, write_excel


@click.command()
@click.argument("keyword_csv", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--brand", "brand_opts", multiple=True, metavar="SITE=TERM1,TERM2",
              help="Brand terms for a site, e.g. --brand 'brightcrm.io=brightcrm,bright crm'. Repeatable. "
                   "Default: the domain name.")
@click.option("-o", "--output", default="brand_share", show_default=True,
              help="Report name; writes <name>.html and <name>.xlsx")
@click.version_option(__version__)
def main(keyword_csv, brand_opts, output):
    """Split organic traffic into own brand, competitor brand and non-brand for each KEYWORD_CSV (you first).

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """
    if len(keyword_csv) > 6:
        raise click.BadParameter("use up to 6 files (you + 5 competitors)")
    try:
        brands = dict(core.parse_brand_option(b) for b in brand_opts)
    except ValueError as exc:
        raise click.BadParameter(str(exc))
    kws, sites, terms = core.analyze(keyword_csv, brands)
    summ = core.summary(kws, sites, terms)
    me = summ.iloc[0]

    report = Report(title="Brand vs non-brand traffic", subtitle=f"{sites[0]} vs {', '.join(sites[1:]) or 'no competitors'}",
                    tool="brand-vs-nonbrand-share")
    tone = "good" if me["brand_share_pct"] >= core.AVERAGE_SITE_PCT else "warn"
    leader = summ.sort_values("brand_share_pct", ascending=False).iloc[0]
    report.add_cards([
        (f"{me['site']}: brand share", f"{me['brand_share_pct']}%", tone),
        ("Average site (benchmark)", f"{core.AVERAGE_SITE_PCT}%"),
        ("Top-performing site (benchmark)", f"{core.TOP_SITE_PCT}%"),
        (f"Highest brand share: {leader['site']}", f"{leader['brand_share_pct']}%"),
        ("Competitor-brand keywords", int((kws["class"] == "competitor brand").sum()), "warn"),
    ])
    report.add_benchmark(STATS[0], how_used="Each site's branded share of traffic is placed in a band: below the "
                         "2.44% average, between average and top sites, or at the 9.74% top-site level.")
    report.add_benchmark(STATS[1], how_used="The share is also matched to the revenue band with a similar brand "
                         "query share. That is a reference point, not an estimate of the company's revenue.")
    report.add_table("Brand share per site", summ, sheet="Summary",
                     note="Brand share = traffic from keywords that contain the site's own brand terms.")
    report.add_table("Competitor-brand keywords", core.competitor_brand_keywords(kws), sheet="Competitor brand",
                     note="A site ranks for another tracked brand: 'x alternatives', 'x vs y', 'x pricing'.")
    report.add_table("Own-brand keywords", kws[kws["class"] == "own brand"], sheet="Own brand")
    report.add_table("Top non-brand keywords per site", core.top_non_brand(kws), sheet="Top non-brand",
                     note="Where each site's non-brand traffic comes from (top 15 per site).")
    report.add_table("All keywords", kws, sheet="All keywords")

    html_path = report.save_html(Path(output).with_suffix(".html"))
    xlsx_path = write_excel(report.sheets, Path(output).with_suffix(".xlsx"))
    click.secho(f"Report: {html_path}\nData:   {xlsx_path}", fg="green", bold=True)
    click.echo(summ[["site", "traffic", "brand_share_pct", "vs_benchmark"]].to_string(index=False))


if __name__ == "__main__":
    main()
