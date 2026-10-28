<div align="center">

# 🏷️ brand-vs-nonbrand-share

### Split your and your competitors' organic traffic into branded and non-branded, and see how it compares with typical and top sites.

[![tests](https://github.com/marketing-MEER/brand-vs-nonbrand-share/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/brand-vs-nonbrand-share/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![Part of SEO Toolbox](https://img.shields.io/badge/part%20of-SEO%20Toolbox-orange)](https://github.com/marketing-MEER/seo-toolbox)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#quick-start) · [⚙️ How it works](#how-it-works) · [📄 Report](#report) · [❓ FAQ](#faq) · [👤 Author](#author)

</div>

---

## 💡 What it does

When organic traffic grows, the first question is whether the rankings did it or the brand did. Answering it means tagging every keyword as branded or not, for you and for each competitor, usually with a pile of spreadsheet filters.

`brand-vs-nonbrand-share` does the tagging for up to 6 keyword exports. Each keyword becomes **own brand**, **competitor brand** (it names another site you track, like "x alternatives") or **non-brand**, and each site's branded share is set against published averages.

- ✅ Brand share of traffic per site, with a band: below average, above average or top-site level
- ✅ Competitor-brand keywords: who ranks for "your brand alternatives" and "your brand pricing"
- ✅ Brand terms from the domain by default, or your own with `--brand`
- ✅ Free, MIT licensed, no API keys. Works with Ahrefs, Semrush or GSC exports

## 📊 Why this matters

> **Brand Search Traffic Difference Between Average and Top Sites** · NP Digital, November 2024 (42,391 websites)
> - Average websites generate just 2.44 percent of search traffic from branded terms.
> - Top-performing websites receive 9.74 percent of their search traffic from branded queries.
> - Brand demand acts as a traffic stabilizer during algorithm updates.
>
> **How Brand Search Scales With Revenue** · NP Digital, December 2024 (42,391 websites)
> - Companies under $1M in revenue see under 2 percent branded queries.
> - Companies between $10M and $100M exceed 6 percent branded queries.
> - Companies over $100M approach 10 percent branded queries.
>
> Data: [brand traffic, average vs top sites](https://neilpatel.com/marketing-stats/percentage-search-traffic-brand-terms/) · [brand search by revenue](https://neilpatel.com/marketing-stats/brand-queries-by-revenue-size/)

**How brand-vs-nonbrand-share uses this:** the insight is to *"monitor branded impressions and clicks separately from non-branded terms to understand whether your SEO efforts are creating long-term demand or short-term traffic spikes."* So the report splits every site's traffic that way and places its brand share in a band: below the 2.44% average, between average and the 9.74% top-site level, or above it. The revenue-size data adds a second reference point (which company size has a similar brand share). It is not an estimate of anyone's revenue.

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/brand-vs-nonbrand-share.git
cd brand-vs-nonbrand-share
pip install -e .
brand-vs-nonbrand-share examples/brightcrm_keywords.csv examples/pipelinehq_keywords.csv examples/salesdeck_keywords.csv --brand "pipelinehq.com=pipelinehq,pipeline hq" --brand "salesdeck.io=salesdeck,sales deck"
```

The first file is **you**; the rest (up to 5) are competitors. This writes **`brand_share.html`** (a formatted report you can share or print to PDF) and **`brand_share.xlsx`** (all data).

> [!TIP]
> If the `brand-vs-nonbrand-share` command isn't found, use `python -m brand_vs_nonbrand_share`.

## 📥 Input

One keyword export per site, with traffic or clicks:

| Source | How to export | Columns detected |
|---|---|---|
| Ahrefs | Site Explorer → Organic keywords → Export | `Keyword`, `Traffic`, `Volume`, `Current position`, `Current URL` |
| Semrush | Organic Research → Positions → Export | `Keyword`, `Traffic`, `Search Volume`, `Position`, `URL` |
| Google Search Console (your site only) | Performance → Queries → Export | `Top queries`, `Clicks` |

Each site is named from the domain in its URLs, or from the file name.

<a id="how-it-works"></a>

## ⚙️ How it works

1. **Brand terms** per site: the domain name (`brightcrm.io` → `brightcrm`), or what you pass with `--brand "site=term1,term2"`. Add misspellings and product names there.
2. **Match** each keyword. Terms of 4+ characters match with spaces and dashes ignored, so `brightcrm` also catches "bright crm pricing". Shorter terms must appear as a whole word, so `hp` does not match "php".
3. **Classify**: own brand first, then competitor brand (another tracked site's terms), else non-brand.
4. **Sum traffic** per site and class, and compute the brand share.
5. **Band** the brand share:

| Band | Brand share |
|---|---|
| below average | under 2.44% |
| above average | 2.44% to 9.74% |
| top-site level | 9.74% or more |

### Options

| Option | Default | What it does |
|---|---|---|
| `--brand` | domain name | `SITE=TERM1,TERM2` brand terms for a site, repeatable |
| `-o`, `--output` | `brand_share` | Report name; writes `.html` and `.xlsx` |

<a id="report"></a>

## 📄 The report

| Section / Excel sheet | Shows |
|---|---|
| Summary cards | Your brand share, the two benchmarks, the highest brand share, competitor-brand keywords |
| Benchmark panels | The two Neil Patel stats behind the bands |
| **Summary** | Per site: brand terms, keywords, traffic, brand traffic and share, competitor-brand and non-brand traffic, bands |
| **Competitor brand** | Keywords where a site ranks for another tracked brand |
| **Own brand** | Every branded keyword per site |
| **Top non-brand** | The 15 biggest non-brand keywords per site |
| **All keywords** | Everything with its class |

<details>
<summary>📄 Example: real output from <code>examples/</code> (fictional CRM sites)</summary>

**Brand share per site**

| site | brand terms | keywords | traffic | brand traffic | brand share pct | competitor brand traffic | non brand traffic | vs benchmark | similar to companies of |
|---|---|---|---|---|---|---|---|---|---|
| brightcrm.io | brightcrm | 22 | 21,067 | 377 | 1.79 | 96 | 20,594 | below average (<2.44%) | under $1M revenue (<2%) |
| pipelinehq.com | pipelinehq, pipeline hq | 25 | 22,563 | 1,704 | 7.55 | 891 | 19,968 | above average (2.44-9.74%) | $10M-$100M revenue (>6%) |
| salesdeck.io | salesdeck, sales deck | 22 | 22,824 | 2,510 | 11 | 0 | 20,314 | top-site level (9.74%+) | $100M+ revenue (~10%) |

**Competitor-brand keywords.** pipelinehq.com picks up traffic from "brightcrm alternatives":

| site | keyword | traffic | volume | position |
|---|---|---|---|---|
| pipelinehq.com | brightcrm alternatives | 446 | 2,230 | 12 |
| pipelinehq.com | salesdeck pricing | 445 | 2,670 | 12 |
| brightcrm.io | pipelinehq alternatives | 96 | 480 | 5 |

</details>

## 🧰 More free SEO tools

This repo is one tool in the **[SEO Toolbox](https://github.com/marketing-MEER/seo-toolbox)**, a family of free, single-purpose SEO tools. Related:
- [keyword-gap-analyzer](https://github.com/marketing-MEER/keyword-gap-analyzer): keywords competitors win and you don't, ranked by revenue potential
- [serp-competitor-finder](https://github.com/marketing-MEER/serp-competitor-finder): find who you really compete with, by share of voice
- [seo-workhorse](https://github.com/marketing-MEER/seo-workhorse): audit, clustering, redirects and GSC quick wins in one CLI

<a id="faq"></a>

## ❓ FAQ

<details><summary><b>My brand is a common word. Won't it match too much?</b></summary>

It can. Pass precise terms with `--brand`, such as `"orbit.io=orbit crm,orbit app"`, and check the Own brand sheet for false matches.
</details>

<details><summary><b>Is a low brand share bad?</b></summary>

Not on its own. It means traffic comes from rankings, which is good, but it also means less of a cushion when rankings move. The insight from the data is to grow brand demand alongside SEO, through PR, content and mentions.
</details>

<details><summary><b>Why use estimated traffic from Ahrefs or Semrush?</b></summary>

It is the only way to see competitors. For your own site, the GSC export gives real clicks. Compare like with like: tool estimates for everyone, or GSC for trends on your site only.
</details>

<details><summary><b>Is my data sent anywhere?</b></summary>

No. It reads your CSV files and writes the report on your computer. It makes no network requests.
</details>

## 🧪 Tests

```bash
python -m unittest discover -s tests -t . -v
```

## 📄 License

[MIT](LICENSE). Free for personal and commercial use. Benchmark figures © their original publishers, quoted with a link to the source.

<a id="author"></a>

## 👤 Author

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪
10+ years in SEO, AEO and GEO. I build small tools that take the spreadsheet work out of SEO.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

<div align="center">

**If this saved you time, a ⭐ helps other SEOs find it.**

</div>
