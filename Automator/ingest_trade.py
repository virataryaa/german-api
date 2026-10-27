"""German coffee foreign trade from Destatis GENESIS (statistic 51000), monthly from 2006.

products: 51000-0014 (HS-8, Germany total) -> Database/german_trade_products.csv
          one row per month x HS code: imports / exports in t, EUR 1000, USD 1000.
origins:  51000-0018 (HS-8 x partner country), green coffee only -> Database/german_trade_origins.csv
          one row per month x country x HS code (zero rows dropped).
The origin table is big, so after the first run only the last two years are re-pulled and merged.
"""
import csv
import datetime as dt
import sys
from pathlib import Path

from genesis import month, num, tablefile

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "Database"
OUT_PRODUCTS = DB / "german_trade_products.csv"
OUT_ORIGINS = DB / "german_trade_origins.csv"
START_YEAR = 2006
PRODUCTS = {"WA09011100": "Green", "WA09011200": "Green decaf", "WA09012100": "Roasted",
            "WA09012200": "Roasted decaf", "WA21011100": "Soluble"}
GREEN = ["WA09011100", "WA09011200"]
FIELDS = {"GEWE": "imp_t", "WERTE": "imp_eur_k", "WERTES": "imp_usd_k",
          "GEWA": "exp_t", "WERTA": "exp_eur_k", "WERTAS": "exp_usd_k"}
COLS = list(FIELDS.values())
CHUNK = 2                # years per origin request


def collect(raw, key_cols):
    """Flat rows -> {(date, *keys): {field: value}}. Months not yet published ('...') are skipped."""
    out = {}
    for r in raw:
        f = FIELDS.get(r["value_variable_code"])
        v = num(r["value"])
        if f is None or v is None:
            continue
        k = (month(r),) + tuple(r[c] for c in key_cols)
        out.setdefault(k, {})[f] = v
    return out


def write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def products():
    raw = tablefile("51000-0014", startyear=START_YEAR, classifyingvariable1="WAM8",
                    classifyingkey1=",".join(PRODUCTS), contents=",".join(FIELDS))
    hs_col = next(c for c in raw[0] if c.endswith("_variable_code") and raw[0][c] == "WAM8").replace("_code", "_attribute_code")
    data = collect(raw, [hs_col])
    rows = [[d, hs[2:], PRODUCTS[hs]] + [v.get(c, 0.0) for c in COLS]
            for (d, hs), v in sorted(data.items()) if len(v) == len(COLS)]
    write(OUT_PRODUCTS, ["date", "hs", "product"] + COLS, rows)
    print(f"products: {len(rows)} rows {rows[0][0][:7]} -> {rows[-1][0][:7]}")


def origins():
    this_year = dt.date.today().year
    keep = []
    first = START_YEAR
    if OUT_ORIGINS.exists():                                # incremental: keep history, re-pull the last 2 years
        first = this_year - 1
        with open(OUT_ORIGINS, encoding="utf-8") as fh:
            rd = csv.reader(fh)
            next(rd)
            keep = [r for r in rd if int(r[0][:4]) < first]
    new = []
    for y0 in range(first, this_year + 1, CHUNK):
        y1 = min(y0 + CHUNK - 1, this_year)
        raw = tablefile("51000-0018", startyear=y0, endyear=y1, classifyingvariable1="WAM8",
                        classifyingkey1=",".join(GREEN), contents=",".join(FIELDS))
        if not raw:
            continue
        cols = raw[0]
        ctry = next(c for c in cols if c.endswith("_variable_code") and cols[c] == "STLAH").replace("_code", "_attribute_label")
        hs = next(c for c in cols if c.endswith("_variable_code") and cols[c] == "WAM8").replace("_code", "_attribute_code")
        for (d, country, code), v in sorted(collect(raw, [ctry, hs]).items()):
            vals = [v.get(c, 0.0) for c in COLS]
            if any(vals):
                new.append([d, country, code[2:], PRODUCTS[code]] + vals)
        print(f"origins {y0}-{y1}: {len(new)} rows so far")
    if not new:
        sys.exit("No origin rows returned")
    write(OUT_ORIGINS, ["date", "country", "hs", "product"] + COLS, keep + new)
    print(f"origins: {len(keep) + len(new)} rows -> {OUT_ORIGINS}")


if __name__ == "__main__":
    products()
    origins()
