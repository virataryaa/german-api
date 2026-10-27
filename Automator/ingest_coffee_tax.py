"""Pull German coffee tax (Kaffeesteuer) receipts from Destatis GENESIS and convert to implied consumption.

Source table 71211-0005: tax revenue, Germany, months, types of taxes prior to distribution (EUR 1000).
Implied bags = EUR 1000 * 1000 / 2.19 EUR/kg roasted * 1.19 green-equivalent / 60 kg.
Token: env GENESIS_TOKEN or Automator/genesis_token.txt (gitignored).
"""
import csv
import io
import os
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Database" / "german_coffee_tax.csv"
URL = "https://genesis.destatis.de/genesisWS/rest/2020/data/tablefile"
TABLE = "71211-0005"
START_YEAR = 1999
TAX_RATE = 2.19          # EUR per kg roasted coffee
GREEN_FACTOR = 1.19      # roasted -> green equivalent
BAG_KG = 60


def token():
    t = os.environ.get("GENESIS_TOKEN")
    if t:
        return t.strip()
    f = Path(__file__).resolve().parent / "genesis_token.txt"
    if f.exists():
        return f.read_text().strip()
    sys.exit("No GENESIS token: set GENESIS_TOKEN or create Automator/genesis_token.txt")


def fetch():
    body = urllib.parse.urlencode({"name": TABLE, "area": "all", "format": "ffcsv", "compress": "false",
                                   "startyear": START_YEAR, "language": "en"}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "username": token(), "password": "", "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=600) as r:
        raw = r.read()
    if raw[:2] == b"PK":                                    # API returns the flat file zipped
        z = zipfile.ZipFile(io.BytesIO(raw))
        raw = z.read(z.namelist()[0])
    text = raw.decode("utf-8-sig")
    if not text.startswith("statistics_code"):
        sys.exit(f"Unexpected response from GENESIS:\n{text[:500]}")
    return text


def parse(text):
    rows = []
    for r in csv.DictReader(io.StringIO(text), delimiter=";"):
        if r["3_variable_attribute_label"] != "Coffee tax":
            continue
        v = r["value"].strip()
        if not v or not v.lstrip("-").isdigit():               # '...' = not yet published
            continue
        eur_k = int(v)
        month = int(r["1_variable_attribute_code"].replace("MONAT", ""))
        bags = eur_k * 1000 / TAX_RATE * GREEN_FACTOR / BAG_KG
        rows.append({"date": f"{r['time']}-{month:02d}-01", "coffee_tax_eur_k": eur_k,
                     "roasted_t": round(eur_k * 1000 / TAX_RATE / 1000, 1), "bags_m": round(bags / 1e6, 4)})
    return sorted(rows, key=lambda x: x["date"])


def main():
    rows = parse(fetch())
    if not rows:
        sys.exit("No coffee tax rows found")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} months {rows[0]['date'][:7]} -> {rows[-1]['date'][:7]} | latest {rows[-1]['bags_m']:.3f} M bags -> {OUT}")


if __name__ == "__main__":
    main()
