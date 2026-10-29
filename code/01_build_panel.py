"""Build the quarterly and fiscal-year panels for Afghanistan and Iraq.

Inputs (data/raw/, from 00_get_data.py):
  contractor-census/contractor_census_headcounts.csv
  contractor-injury-claims/dba_claims_by_country_year.csv
  crs/R44116_2021-02-22.pdf
  dcas/dcas_deaths_by_incident_country_fy.csv
  approx/afghanistan_troops_fy2018_2020_approx.csv

Outputs (data/clean/):
  troops_quarterly_crs.csv       troop levels parsed from CRS R44116 Tables 1 and 3
  check_crs_vs_census.csv        CRS contractor totals compared with the census, quarter by quarter
  contractors_quarterly.csv      census rows used (Afghanistan, Iraq)
  panel_fy.csv                   one row per country and fiscal year
"""
import csv, os, re, sys
from collections import defaultdict

import pdfplumber

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
CLEAN = os.path.join(ROOT, "data", "clean")
os.makedirs(CLEAN, exist_ok=True)


def num(s):
    return int(s.replace(",", ""))


# ---------- 1. Troop levels from CRS R44116 ----------
pdf = pdfplumber.open(os.path.join(RAW, "crs", "R44116_2021-02-22.pdf"))
# Table 1 (Afghanistan) is on PDF pages 10-11; Table 3 (Iraq, Iraq and Syria) on pages 16-17.
TABLE_PAGES = {"Afghanistan": [10, 11], "Iraq": [16, 17]}
row_re = re.compile(r"^\s*Q([1-4]) FY(\d{4})\s+(.*)$", re.M)
troops = []
for country, pages in TABLE_PAGES.items():
    for pg in pages:
        text = pdf.pages[pg - 1].extract_text()
        for q, fy, rest in row_re.findall(text):
            rest = rest.strip()
            m = re.match(r"^(Not Available\w?|—|Up to [\d,]+\w?|[\d,]+\w?)\s+(No Data Available|[\d,]+)\s+(No Data Available|[\d,]+)\s+(?:([\d,]+)(\w)?|([\d,]+) \(est\.\))$", rest)
            if not m:
                sys.exit(f"Could not parse CRS row: {country} Q{q} FY{fy}: {rest!r}")
            t_raw, us_c, fh_c, tot, tot_flag, tot_est = m.groups()
            note, value = "", ""
            if t_raw.startswith("Not Available"):
                note = "not available (DoD stopped publishing troop numbers)"
            elif t_raw == "—":
                note = "no figure (after the end of the U.S. military mission)"
            elif t_raw.startswith("Up to"):
                note = "force management level (an upper limit, not a count)"
                value = re.sub(r"\D", "", t_raw.replace("Up to", ""))
                # strip the footnote letter that pdfplumber joins to the number
                value = str(num(re.match(r"Up to ([\d,]+)", t_raw).group(1)))
            else:
                value = str(num(re.match(r"([\d,]+)", t_raw).group(1)))
                note = "Boots on the Ground"
                if re.search(r"\d[a-z]$", t_raw):
                    note += f" (CRS footnote {t_raw[-1]})"
            troops.append({
                "country": country, "fiscal_year": int(fy), "quarter": int(q),
                "troops": value, "troops_note": note,
                "crs_us_contractors": "" if us_c.startswith("No") else num(us_c),
                "crs_foreign_and_host_contractors": "" if fh_c.startswith("No") else num(fh_c),
                "crs_total_contractors": num(tot) if tot else num(tot_est),
                "crs_total_flag": (tot_flag or "") + (" estimate" if tot_est else ""),
            })
troops.sort(key=lambda r: (r["country"], r["fiscal_year"], r["quarter"]))
# Every quarter from Q4 FY2007 to Q4 FY2020 should appear exactly once per country
# (Iraq has no row for Q2-Q4 FY2014 in CRS's table).
seen = defaultdict(int)
for r in troops:
    seen[(r["country"], r["fiscal_year"], r["quarter"])] += 1
assert all(v == 1 for v in seen.values()), "duplicate CRS rows"
with open(os.path.join(CLEAN, "troops_quarterly_crs.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(troops[0]))
    w.writeheader()
    w.writerows(troops)

# ---------- 2. Census rows ----------
census = [r for r in csv.DictReader(open(os.path.join(RAW, "contractor-census", "contractor_census_headcounts.csv")))]
cq = {}
for r in census:
    area = r["area"]
    country = {"Afghanistan": "Afghanistan", "Iraq": "Iraq", "Iraq and Syria": "Iraq and Syria"}.get(area)
    if not country:
        continue
    key = (country, int(r["fiscal_year"]), int(r["fiscal_quarter"]))
    assert key not in cq, key
    cq[key] = {k: int(r[k]) for k in ("total", "us_citizens", "third_country_nationals", "local_nationals")}
    cq[key]["note"] = r["note"]
with open(os.path.join(CLEAN, "contractors_quarterly.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["country", "fiscal_year", "quarter", "total", "us_citizens", "third_country_nationals", "local_nationals", "parts_sum", "note"])
    for k in sorted(cq):
        v = cq[k]
        w.writerow([*k, v["total"], v["us_citizens"], v["third_country_nationals"], v["local_nationals"],
                    v["us_citizens"] + v["third_country_nationals"] + v["local_nationals"], v["note"]])

# ---------- 3. Check CRS contractor totals against the census ----------
checks = []
for r in troops:
    key = (r["country"], r["fiscal_year"], r["quarter"])
    alt = ("Iraq and Syria", r["fiscal_year"], r["quarter"]) if r["country"] == "Iraq" else None
    c = cq.get(key) or (cq.get(alt) if alt else None)
    if c is None:
        checks.append([*key, r["crs_total_contractors"], "", "", "census has no row (CRS covers quarters before FY2008 Q3, or an estimate)"])
        continue
    diff = r["crs_total_contractors"] - c["total"]
    us_diff = (r["crs_us_contractors"] - c["us_citizens"]) if r["crs_us_contractors"] != "" else ""
    checks.append([*key, r["crs_total_contractors"], c["total"], diff, f"U.S. citizens differ by {us_diff}" if us_diff not in ("", 0) else ""])
with open(os.path.join(CLEAN, "check_crs_vs_census.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["country", "fiscal_year", "quarter", "crs_total", "census_total", "difference", "comment"])
    w.writerows(checks)
mismatch = [c for c in checks if c[5] not in ("", 0)]
print(f"CRS vs census: {len(checks)} quarters, {len(mismatch)} with a different total")
for c in mismatch:
    print("   ", c)

# ---------- 4. Fiscal-year panel ----------
tq = {(r["country"], r["fiscal_year"], r["quarter"]): r for r in troops}
approx = {(int(r["fiscal_year"]), int(r["quarter"])): r for r in csv.DictReader(open(os.path.join(RAW, "approx", "afghanistan_troops_fy2018_2020_approx.csv")))}

dcas = defaultdict(lambda: defaultdict(int))
for r in csv.DictReader(open(os.path.join(RAW, "dcas", "dcas_deaths_by_incident_country_fy.csv"))):
    code = {"AF": "Afghanistan", "IZ": "Iraq", "SY": "Syria"}.get(r["incident_geo_code"])
    if code:
        dcas[(code, int(r["fiscal_year"]))][r["type"]] += int(r["deaths"])

dba = {}
pending = {}
known_total = defaultdict(int)
for r in csv.DictReader(open(os.path.join(RAW, "contractor-injury-claims", "dba_claims_by_country_year.csv"))):
    fy = int(r["fiscal_year"])
    d = r["death"].strip()
    if r["country"] == "NATION PENDING":
        pending[fy] = int(d) if d else None
        continue
    if d:
        known_total[fy] += int(d)
    if r["country"] in ("AFGHANISTAN", "IRAQ"):
        dba[(r["country"].title(), fy)] = int(d) if d else None


def mean(xs):
    return sum(xs) / len(xs)


rows = []
for country, years in (("Afghanistan", range(2009, 2022)), ("Iraq", range(2009, 2022))):
    for fy in years:
        qs = [1, 2, 3, 4]
        cen_key = lambda q: (country, fy, q) if (country, fy, q) in cq else ("Iraq and Syria", fy, q)
        cen = [cq[cen_key(q)] for q in qs if cen_key(q) in cq]
        n_cq = len(cen)
        # A quarter with zero contractors (Afghanistan Q4 FY2021, after the withdrawal) is a real zero.
        P_C = mean([c["total"] for c in cen]) if cen else None
        parts = [c["us_citizens"] + c["third_country_nationals"] + c["local_nationals"] for c in cen]
        sum_parts = sum(parts)
        sh = lambda k: (sum(c[k] for c in cen) / sum_parts) if sum_parts else None
        P_US = mean([c["us_citizens"] for c in cen]) if cen else None
        P_TCN = mean([c["third_country_nationals"] for c in cen]) if cen else None
        P_LN = mean([c["local_nationals"] for c in cen]) if cen else None
        census_area = sorted({cen_key(q)[0] for q in qs if cen_key(q) in cq})
        # troops
        t_vals = [tq.get((country, fy, q), {}).get("troops", "") for q in qs]
        t_notes = [tq.get((country, fy, q), {}).get("troops_note", "") for q in qs]
        official = all(v != "" and n.startswith("Boots") for v, n in zip(t_vals, t_notes))
        P_M = mean([int(v) for v in t_vals]) if official else None
        P_M_lo = P_M_hi = None
        troop_basis = "Boots on the Ground (CRS R44116)" if official else ""
        if not official and country == "Afghanistan" and fy in (2018, 2019, 2020):
            a = [approx[(fy, q)] for q in qs]
            P_M = mean([int(x["troops_central"]) for x in a])
            P_M_lo = mean([int(x["troops_low"]) for x in a])
            P_M_hi = mean([int(x["troops_high"]) for x in a])
            troop_basis = "approximate (official figures quoted in CRS R45122)"
        dm = dcas.get((country, fy), {})
        D_M = dm.get("hostile", 0) + dm.get("non-hostile", 0)
        D_M_h = dm.get("hostile", 0)
        D_C = dba.get((country, fy))
        rows.append({
            "country": country, "fiscal_year": fy,
            "census_area": "+".join(census_area), "census_quarters": n_cq,
            "contractors": round(P_C, 1) if P_C is not None else "",
            "contractors_us": round(P_US, 1) if P_US is not None else "",
            "contractors_tcn": round(P_TCN, 1) if P_TCN is not None else "",
            "contractors_local": round(P_LN, 1) if P_LN is not None else "",
            "share_us": round(sh("us_citizens"), 6) if cen else "",
            "share_tcn": round(sh("third_country_nationals"), 6) if cen else "",
            "share_local": round(sh("local_nationals"), 6) if cen else "",
            "troops": round(P_M, 1) if P_M is not None else "",
            "troops_low": round(P_M_lo, 1) if P_M_lo is not None else "",
            "troops_high": round(P_M_hi, 1) if P_M_hi is not None else "",
            "troop_basis": troop_basis,
            "military_deaths": D_M, "military_deaths_hostile": D_M_h,
            "contractor_deaths_dba": "" if D_C is None else D_C,
            "dba_nation_pending_deaths": "" if pending.get(fy) is None else pending[fy],
            "dba_known_nation_deaths_all_countries": known_total[fy],
        })
with open(os.path.join(CLEAN, "panel_fy.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("panel rows:", len(rows))
for r in rows:
    print(r["country"], r["fiscal_year"], r["census_area"], r["census_quarters"], r["contractors"], r["troops"], r["troop_basis"][:12],
          "deaths M/C:", r["military_deaths"], r["contractor_deaths_dba"])
