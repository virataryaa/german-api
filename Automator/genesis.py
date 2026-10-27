"""Destatis GENESIS-Online REST client: POST only, token in the `username` header with an empty password.
Token: env GENESIS_TOKEN or Automator/genesis_token.txt (gitignored)."""
import csv
import io
import os
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

URL = "https://genesis.destatis.de/genesisWS/rest/2020/data/tablefile"


def token():
    t = os.environ.get("GENESIS_TOKEN")
    if t:
        return t.strip()
    f = Path(__file__).resolve().parent / "genesis_token.txt"
    if f.exists():
        return f.read_text().strip()
    sys.exit("No GENESIS token: set GENESIS_TOKEN or create Automator/genesis_token.txt")


def tablefile(name, **params):
    """One table as flat-file CSV rows (list of dicts). Extra params go straight to the API
    (startyear, endyear, classifyingvariable1, classifyingkey1, contents ...)."""
    body = urllib.parse.urlencode({"name": name, "area": "all", "format": "ffcsv", "compress": "false",
                                   "language": "en", **params}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "username": token(), "password": "", "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=900) as r:
        raw = r.read()
    if raw[:2] == b"PK":                                    # the flat file comes zipped
        z = zipfile.ZipFile(io.BytesIO(raw))
        raw = z.read(z.namelist()[0])
    text = raw.decode("utf-8-sig")
    if not text.startswith("statistics_code"):
        sys.exit(f"Unexpected response from GENESIS for {name}:\n{text[:500]}")
    return list(csv.DictReader(io.StringIO(text), delimiter=";"))


def num(v):
    """'123.4' -> 123.4; '-' (zero / nothing to report) -> 0.0; '...' / '.' / 'x' (not available) -> None."""
    v = (v or "").strip()
    if v == "-":
        return 0.0
    try:
        return float(v)
    except ValueError:
        return None


def month(r):
    """Flat-file row -> 'YYYY-MM-01'."""
    return f"{r['time']}-{int(r['1_variable_attribute_code'].replace('MONAT', '')):02d}-01"
