# Dashboard rules — v1

Source: `Robi Live Site_Aug_2026.xlsx`, first sheet. Columns are found by their header text on row 1, not by letter.

## Page

One web page, no Excel output. A single self-contained HTML file (charts drawn on canvas, no internet libraries), delivered as a zip because GitHub shows a raw `.html` as plain text.

- Left panel: **District** filter (column `District`, A to Z, with site counts). Choosing a district lists every **Thana** of that district (column `Thana`, A to Z, numbered, with site count and On Air Year span). A search box narrows the thana list. Previous / Next step through the listed thanas.
- Clicking a thana draws **two charts beside each other** in one window:
  1. `On Air Year` (X) vs `Total voice` (Y), titled `Total voice(Erl) vs On Air Year`, Y axis `Total voice, Erl`.
  2. `On Air Year` (X) vs `DAILY 4G DATA (GB)` (Y), titled `DAILY 4G DATA (GB) vs  On Air Year`, Y axis `DAILY 4G DATA (GB)`.
- Report under the charts: KPI chips (sites, sites on chart, oldest and newest year, sum and average per site of both measures), a **By On Air Year** table (sites and sums per year), and the **site table** of that thana.
- The URL hash is `#District/Thana`, so a thana view can be bookmarked or shared.

## Chart rules

- **One point per site**, the same as the reference Excel chart. The X label of each point is that site's `On Air Year` (for example `Y 2015`), so a year repeats once per site.
- **Oldest first (A to Z).** Sites are sorted by `On Air Year` ascending. Within the same year, by `On Air Date` ascending, then by `Site Code`.
- Both charts use the same site order, so point *n* is the same site in both charts and is row *n* of the site table. Hovering a point (or a table row) highlights that site in both charts.
- Line: smoothed, dark teal `#156082`, 3 px, matching the reference. Smoothing never overshoots the data (monotone curve), so it does not invent negative or peak values. Markers are drawn only when a thana has 25 sites or fewer. When there are too many sites to label every point, X labels are thinned so they stay readable; every point is still plotted.
- Y axis starts at 0, about five gridlines, labels with one decimal (`2500.0`).

## Data handling

- A site is **on the chart** when it has an `On Air Year` and a number in both `Total voice` and `DAILY 4G DATA (GB)`. In this file 19,786 of 19,880 sites qualify.
- Not on the chart, but listed (grey, No. `—`) at the bottom of the site table: 56 sites with no `On Air Year` (51 `Configured (N On air)`, 5 `Lock/Down`) and 43 sites whose `Total voice` and `DAILY 4G DATA (GB)` are `#N/A`. They are never plotted as zero.
- All site statuses are kept. Values are the workbook values, rounded to 2 decimals.
- `On Air Date` is shown as `YYYY-MM-DD`. It is stored as text (`M/D/YYYY`) on most rows and as an Excel date on the rest; both are read. The X axis uses `On Air Year` as written in the workbook, even where it differs from the year of `On Air Date` (1,780 rows).
- District and thana names that differ only by letter case are merged and shown with the most common spelling: `Cox'S Bazar` (597) and `Cox's Bazar` (2) are one district, `Cox'S Bazar Sadar` and `Cox's Bazar Sadar` are one thana. That gives 64 districts and 548 thanas.
- A thana is identified by district + thana, because some thana names exist in more than one district (Kotwali in Chittagong, Dhaka and Jessore; Kaliganj in four districts).
- Only these fields are written into the page: Site Code, Site Name, Site Status, Site Type, Thana, District, On Air Date, On Air Year, DAILY 4G DATA (GB), Total voice. Address, latitude and longitude are not published.

## Build

```bash
python3 scripts/build_dashboard.py "Robi Live Site_Aug_2026.xlsx" -o Robi_Live_Site_Aug_2026_Dashboard_v1.html --version v1
```

Python 3 standard library only. Writes the `.html` and the `.zip` next to it. For a new month, upload the new workbook, run the same command with the new file name and the next version, and keep these rules.
