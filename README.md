# Robi-Live-Site-Data-_WEB-Based-Dashboard

Web dashboard for `Robi Live Site_Aug_2026.xlsx`: pick a **District** (its chart is the first row of the list) or a **Thana**. Two charts open side by side, `On Air Year` vs average `Total voice` per site and `On Air Year` vs average `DAILY 4G DATA (GB)` per site, oldest year first.

All rules are in `RULES.md`.

## Files

| File | Purpose |
|---|---|
| `Robi_Live_Site_Aug_2026_Dashboard_v2.zip` | The dashboard. Unzip it and open the `.html` file in Chrome or Edge. Works offline |
| `Robi_Live_Site_Aug_2026_Dashboard_v2.html` | The same page, unzipped. GitHub shows a raw `.html` as plain text, so download the zip |
| `scripts/build_dashboard.py` | Reads the workbook and writes the page and the zip |
| `scripts/dashboard_template.html` | Page layout, charts and report |
| `RULES.md` | Filter, chart, sorting and data rules |
| `Robi Live Site_Aug_2026.xlsx` | Source workbook (uploaded) |

## Rebuild

```bash
python3 scripts/build_dashboard.py "Robi Live Site_Aug_2026.xlsx" -o Robi_Live_Site_Aug_2026_Dashboard_v2.html --version v2
```
