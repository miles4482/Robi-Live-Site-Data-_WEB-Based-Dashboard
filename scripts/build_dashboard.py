#!/usr/bin/env python3
"""Build the District -> Thana On Air Year web dashboard from the Robi live site workbook.

Standard library only. Columns are found by their header text on row 1, so the
script keeps working if columns move in a later export.
"""
import argparse
import datetime
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
FIELDS = {
    "code": "Site Code",
    "name": "Site Name",
    "status": "Site Status",
    "type": "Site Type",
    "thana": "Thana",
    "district": "District",
    "date": "On Air Date",
    "year": "On Air Year",
    "data": "DAILY 4G DATA (GB)",
    "voice": "Total voice",
}
EXCEL_EPOCH = datetime.date(1899, 12, 30)
TEXT_DATE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})")
YEAR = re.compile(r"(\d{4})")


def col_letters(ref):
    return "".join(ch for ch in ref if ch.isalpha())


def read_shared_strings(book):
    strings = []
    if "xl/sharedStrings.xml" not in book.namelist():
        return strings
    with book.open("xl/sharedStrings.xml") as handle:
        for _, el in ET.iterparse(handle):
            if el.tag == NS + "si":
                strings.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
    return strings


def cell_value(cell, strings):
    kind = cell.get("t")
    if kind == "inlineStr":
        return "".join(t.text or "" for t in cell.iter(NS + "t"))
    node = cell.find(NS + "v")
    if node is None or node.text is None:
        return None
    raw = node.text
    if kind == "s":
        return strings[int(raw)]
    if kind in ("str", "e"):
        return raw
    if kind == "b":
        return raw == "1"
    try:
        return float(raw)
    except ValueError:
        return raw


def first_sheet_path(book):
    rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
    workbook = ET.fromstring(book.read("xl/workbook.xml"))
    first = workbook.find(f"{NS}sheets/{NS}sheet")
    rel_id = first.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    for rel in rels:
        if rel.get("Id") == rel_id:
            target = rel.get("Target").lstrip("/")
            return target if target.startswith("xl/") else "xl/" + target
    raise SystemExit("First worksheet not found in workbook")


def parse_date(value):
    """Return (ISO date or raw text, sortable key or None)."""
    if value is None or value == "":
        return "", None
    if isinstance(value, float):
        day = EXCEL_EPOCH + datetime.timedelta(days=int(value))
        return day.isoformat(), day.isoformat()
    text = str(value).strip()
    match = TEXT_DATE.match(text)
    if match:
        month, day, year = (int(part) for part in match.groups())
        try:
            parsed = datetime.date(year, month, day)
            return parsed.isoformat(), parsed.isoformat()
        except ValueError:
            pass
    return text, None


def parse_year(value):
    if value is None:
        return None
    match = YEAR.search(str(value))
    return int(match.group(1)) if match else None


def measure(value):
    if isinstance(value, float):
        return round(value, 2)
    if value is None or value == "":
        return None
    return str(value)


def read_sites(path):
    with zipfile.ZipFile(path) as book:
        strings = read_shared_strings(book)
        sheet = first_sheet_path(book)
        columns = {}
        rows = []
        with book.open(sheet) as handle:
            for _, el in ET.iterparse(handle):
                if el.tag != NS + "row":
                    continue
                values = {}
                for cell in el:
                    if cell.tag == NS + "c":
                        values[col_letters(cell.get("r"))] = cell_value(cell, strings)
                if not columns:
                    by_header = {str(v).strip(): k for k, v in values.items() if v is not None}
                    missing = [h for h in FIELDS.values() if h not in by_header]
                    if missing:
                        raise SystemExit(f"Missing columns on row 1: {missing}")
                    columns = {key: by_header[header] for key, header in FIELDS.items()}
                else:
                    rows.append({key: values.get(letter) for key, letter in columns.items()})
                el.clear()
    return rows


def display_name(variants):
    return variants.most_common(1)[0][0]


def build(rows):
    district_names = {}
    thana_names = {}
    grouped = {}
    stats = Counter()
    for row in rows:
        district = str(row["district"] or "").strip()
        thana = str(row["thana"] or "").strip()
        if not district or not thana:
            stats["no district or thana"] += 1
            continue
        dkey = district.casefold()
        tkey = (dkey, thana.casefold())
        district_names.setdefault(dkey, Counter())[district] += 1
        thana_names.setdefault(tkey, Counter())[thana] += 1
        year = parse_year(row["year"])
        date_text, date_key = parse_date(row["date"])
        voice = measure(row["voice"])
        data = measure(row["data"])
        charted = year is not None and isinstance(voice, float) and isinstance(data, float)
        stats["rows"] += 1
        stats["charted"] += charted
        stats["no year"] += year is None
        stats["voice not numeric"] += not isinstance(voice, float)
        stats["4G not numeric"] += not isinstance(data, float)
        site = {
            "row": [
                str(row["code"] or ""),
                str(row["name"] or ""),
                year,
                date_text,
                str(row["status"] or ""),
                str(row["type"] or ""),
                voice,
                data,
            ],
            "charted": charted,
            "sort": (
                not charted,
                year if year is not None else 9999,
                date_key or "9999-99-99",
                str(row["code"] or ""),
            ),
        }
        grouped.setdefault(dkey, {}).setdefault(tkey, []).append(site)

    districts = []
    for dkey in sorted(grouped, key=lambda key: display_name(district_names[key]).casefold()):
        thanas = []
        for tkey in sorted(grouped[dkey], key=lambda key: display_name(thana_names[key]).casefold()):
            sites = sorted(grouped[dkey][tkey], key=lambda site: site["sort"])
            thanas.append({
                "name": display_name(thana_names[tkey]),
                "charted": sum(site["charted"] for site in sites),
                "sites": [site["row"] for site in sites],
            })
        districts.append({"name": display_name(district_names[dkey]), "thanas": thanas})

    merged = {
        display_name(names): sorted(names)
        for names in list(district_names.values()) + list(thana_names.values())
        if len(names) > 1
    }
    return districts, stats, merged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True, help="HTML file to write")
    parser.add_argument("--version", default="v1")
    args = parser.parse_args()

    rows = read_sites(args.workbook)
    districts, stats, merged = build(rows)
    payload = {
        "source": args.workbook.name,
        "version": args.version,
        "fields": list(FIELDS.values()),
        "districts": districts,
    }
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = (Path(__file__).with_name("dashboard_template.html")).read_text(encoding="utf-8")
    html = template.replace("__VERSION__", args.version).replace("__DATA__", blob)
    args.output.write_text(html, encoding="utf-8")

    archive = args.output.with_suffix(".zip")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        bundle.write(args.output, args.output.name)

    thana_count = sum(len(d["thanas"]) for d in districts)
    print(f"Rows {stats['rows']:,} · districts {len(districts)} · thanas {thana_count}")
    print(f"On chart {stats['charted']:,} · no On Air Year {stats['no year']} · "
          f"Total voice not numeric {stats['voice not numeric']} · 4G not numeric {stats['4G not numeric']}")
    if stats["no district or thana"]:
        print(f"Skipped (no District or Thana): {stats['no district or thana']}")
    for shown, variants in merged.items():
        print(f"Merged spellings into '{shown}': {variants}")
    print(f"Wrote {args.output} ({args.output.stat().st_size / 1e6:.2f} MB) and {archive} "
          f"({archive.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
