# 📂 Sample data

Three **made-up** organic keyword exports with traffic for a fictional CRM market:

| File | Format | Site |
|---|---|---|
| `brightcrm_keywords.csv` | Ahrefs style (`Keyword`, `Volume`, `Current position`, `Traffic`, `Current URL`) | brightcrm.io ("you") |
| `pipelinehq_keywords.csv` | Semrush style (`Keyword`, `Position`, `Search Volume`, `Traffic`, `URL`) | pipelinehq.com |
| `salesdeck_keywords.csv` | Ahrefs style | salesdeck.io |

The sites, keywords and traffic are fictional.

```bash
brand-vs-nonbrand-share examples/brightcrm_keywords.csv examples/pipelinehq_keywords.csv examples/salesdeck_keywords.csv --brand "pipelinehq.com=pipelinehq,pipeline hq" --brand "salesdeck.io=salesdeck,sales deck"
```
