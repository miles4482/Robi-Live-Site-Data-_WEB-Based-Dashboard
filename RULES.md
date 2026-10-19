# Dashboard rules — v8

Source: `Robi Live Site_Aug_2026.xlsx`, first sheet. Columns are found by their header text on row 1, not by letter.

## Page

One web page, no Excel output. A single self-contained HTML file (charts drawn on canvas, no internet libraries), delivered as a zip because GitHub shows a raw `.html` as plain text.

- Left panel: **District** filter (column `District`, A to Z, with site counts). Choosing a district opens the **district chart** and lists that district at the top of the thana list (navy row), then every **Thana** (column `Thana`, A to Z, numbered). Click the district row for the district chart, or a thana for that thana. A search box narrows the thanas; the district row stays pinned. Previous / Next steps through the district row and the listed thanas.
- Two charts beside each other:
  1. `On Air Year` (X) vs `Total voice` (Y), titled `Total voice(Erl) vs On Air Year`, left Y axis `Total Voice, Erl` (the sum). The right Y axis is **Site count**, drawn as bars. This secondary axis is only on the voice chart.
  2. `On Air Year` (X) vs `DAILY 4G DATA (GB)` (Y), titled `DAILY 4G DATA (GB) vs  On Air Year`, Y axis `Daily 4G Data volume, GB` (the sum). No site-count axis.
  3. Below those two, one full-width line chart: `On Air Year` (X) vs `Cumulative site count` (Y). The line is the running total of sites on the chart, oldest year first. It is a line, not bars. A missing year is skipped because it adds no sites. Each point is labeled with that running total.
- The site-count bars on the voice chart are labeled with that year's site count. The voice line and the 4G line are not labeled.
- Report under the charts: site-count chips, then **per site Total voice (Erl)** and **per site data volume (GB)**. A thana view shows that thana's two averages and the district's two averages. The district view shows the district's two averages. Under the chips: a **By On Air Year** table of the yearly sums, and the site table. The site table keeps each site's own voice and data.
- Each table has an **Export** button. It downloads a CSV of that table for the district or thana on screen (every row, including sites with no On Air Year or `#N/A`). Excel opens the file. Numbers have no thousands separator.
- The URL hash is `#District` for the district chart and `#District/Thana` for a thana.

## Chart rules

- **One point per On Air Year.** The line is the sum of the sites on air in that year. Total voice and DAILY 4G DATA both use the sum. The voice chart also draws the site count as bars on a right-hand axis. The data chart has no secondary axis.
- **Oldest first (A to Z).** Years run 2013, 2014, 2015, and so on.
- Both charts use the same years. Hovering a point highlights that year in the year table and the sites of that year in the site table.
- The year table shows Sites, the sum of Total voice (Erl), and the sum of DAILY 4G DATA (GB). The last row is **Total**.
- Line: smoothed, dark teal `#156082`, 3 px, with a marker on every year. Smoothing never overshoots the data (monotone curve), so it does not invent negative or peak values. Every year is labeled.
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
python3 scripts/build_dashboard.py "Robi Live Site_Aug_2026.xlsx" -o Robi_Live_Site_Aug_2026_Dashboard_v8.html --version v8
```

Python 3 standard library only. Writes the `.html` and the `.zip` next to it. For a new month, upload the new workbook, run the same command with the new file name and the next version, and keep these rules.
