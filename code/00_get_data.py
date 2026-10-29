"""Download every input and save it, with checksums, in data/raw/.

Sources:
  1. contractor-census v1.0.0 (Zenodo 10.5281/zenodo.23736051): the DoD quarterly contractor census.
  2. contractor-injury-claims v1.0.0 (Zenodo 10.5281/zenodo.23746799): Defense Base Act claims by nation and fiscal year.
  3. us-guard-spending v1.0.0 (Zenodo 10.5281/zenodo.23750993): federal guard-service (S206) contract actions.
  4. CRS report R44116 (22 February 2021), from EveryCRSReport.com: troop levels.
  5. DCAS names-of-fallen records for OEF, OFS, OIF, OND and OIR. Only counts are kept; names are not saved.

Run: python code/00_get_data.py
"""
import csv, datetime, hashlib, io, json, os, ssl, sys, time, urllib.request, zipfile
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (research replication script)"}
# Certificates come from the system's default store; set SSL_CERT_FILE to use another CA bundle.
CTX = ssl.create_default_context()


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, context=CTX, timeout=180) as r:
                return r.read()
        except Exception as e:  # network hiccups: retry, then fail loudly
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def md5(b):
    return hashlib.md5(b).hexdigest()


log = []

# ---- 1-3: Zenodo releases of the three data projects ----
ZENODO = [
    ("contractor-census", "23736051", "Affnann/contractor-census-v1.0.0.zip", "5fcaac90b693829351b2e9d2b4507034",
     ["data/clean/contractor_census_headcounts.csv"]),
    ("contractor-injury-claims", "23746799", "Affnann/contractor-injury-claims-v1.0.0.zip", "5003cb1326f1da68aab5163dc5ffb045",
     ["data/clean/dba_claims_by_country_year.csv", "data/clean/dba_claims_year_totals.csv",
      "data/clean/dba_claims_cumulative_2001_2024.csv"]),
    ("us-guard-spending", "23750993", "Affnann/us-guard-spending-v1.0.0.zip", "24102445ea67e02004eccbd1d9df32fb",
     ["data/clean/s206_transactions.csv.gz"]),
]
for name, rec, key, want_md5, members in ZENODO:
    url = f"https://zenodo.org/api/records/{rec}/files/{key}/content"
    blob = get(url)
    got = md5(blob)
    if got != want_md5:
        sys.exit(f"{name}: checksum {got} does not match Zenodo's {want_md5}")
    z = zipfile.ZipFile(io.BytesIO(blob))
    outdir = os.path.join(RAW, name)
    os.makedirs(outdir, exist_ok=True)
    for m in members:
        hits = [n for n in z.namelist() if n.endswith("/" + m)]
        assert len(hits) == 1, (name, m, hits)
        data = z.read(hits[0])
        with open(os.path.join(outdir, os.path.basename(m)), "wb") as f:
            f.write(data)
        log.append((f"{name}/{os.path.basename(m)}", f"Zenodo record {rec}, {key} (zip md5 {want_md5})", md5(data)))

# ---- 4: CRS R44116, February 22, 2021 version ----
CRS_URL = "https://www.everycrsreport.com/files/2021-02-22_R44116_bbc1c6b0768dab9e0d49372e55cf6083408b4049.pdf"
crs = get(CRS_URL)
os.makedirs(os.path.join(RAW, "crs"), exist_ok=True)
with open(os.path.join(RAW, "crs", "R44116_2021-02-22.pdf"), "wb") as f:
    f.write(crs)
log.append(("crs/R44116_2021-02-22.pdf", CRS_URL, md5(crs)))

# ---- 5: DCAS: count deaths by operation, incident country, fiscal year and hostile/non-hostile ----
counts = Counter()
meta = []
for op in ["oef", "ofs", "oif", "ond", "oir"]:
    url = f"https://dcas.dmdc.osd.mil/dcas/api/report/wia/fallenByName/{op}"
    d = json.loads(get(url))
    rows = d["data"]["tableData"]
    nodate = 0
    for r in rows:
        dod = r.get("date_of_death")
        if not dod:
            nodate += 1
            continue
        y, m, _ = (int(x) for x in dod.split("/"))
        fy = y + 1 if m >= 10 else y
        hostile = "hostile" if r.get("hostile") == "HOSTILE" else "non-hostile"
        counts[(op.upper(), r.get("incident_Geographic_Code") or "", fy, hostile)] += 1
    meta.append({"operation": op.upper(), "records": len(rows), "records_without_date": nodate,
                 "dcas_extraction_date": d["data"].get("extractionDate", ""), "url": url})
os.makedirs(os.path.join(RAW, "dcas"), exist_ok=True)
with open(os.path.join(RAW, "dcas", "dcas_deaths_by_incident_country_fy.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["operation", "incident_geo_code", "fiscal_year", "type", "deaths"])
    for k in sorted(counts):
        w.writerow([*k, counts[k]])
with open(os.path.join(RAW, "dcas", "dcas_download_notes.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(meta[0]))
    w.writeheader()
    w.writerows(meta)

with open(os.path.join(RAW, "download_log.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["file", "source", "md5", "downloaded_utc"])
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    for row in log:
        w.writerow([*row, now])
print("done:", len(log), "files plus DCAS counts;", sum(counts.values()), "dated DCAS records")
for m in meta:
    print(m)
