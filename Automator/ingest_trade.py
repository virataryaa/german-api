"""German coffee and cocoa foreign trade from Destatis GENESIS (statistic 51000), monthly from 2006.

products: 51000-0014 (HS-8, Germany total) -> Database/german_trade_products.csv / german_cocoa_products.csv
          one row per month x HS code: imports / exports in t, EUR 1000, USD 1000.
origins:  51000-0018 (HS-8 x partner country), green coffee / cocoa beans only
          -> Database/german_trade_origins.csv / german_cocoa_origins.csv (zero rows dropped).
Also copies Germany's quarterly cocoa grind from the Cocoa Grind project -> Database/german_cocoa_grind.csv.
The origin tables are big, so after the first run only the last two years are re-pulled and merged.
"""
import csv
import datetime as dt
import sys
from pathlib import Path

from genesis import month, num, tablefile

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "Database"
GRIND_SRC = ROOT.parent / "Cocoa Grind" / "Database" / "cocoa_grind.csv"
START_YEAR = 2006
CHOC = ["WA18061015", "WA18061020", "WA18061030", "WA18061090", "WA18062010", "WA18062030", "WA18062050", "WA18062070",
        "WA18062080", "WA18062095", "WA18063100", "WA18063210", "WA18063290", "WA18069011", "WA18069019", "WA18069031",
        "WA18069039", "WA18069050", "WA18069060", "WA18069070", "WA18069090"]
COMMODITIES = {
    "coffee": dict(products={"WA09011100": "Green", "WA09011200": "Green decaf", "WA09012100": "Roasted",
                             "WA09012200": "Roasted decaf", "WA21011100": "Soluble"},
                   origin_codes=["WA09011100", "WA09011200"],
                   out_products=DB / "german_trade_products.csv", out_origins=DB / "german_trade_origins.csv"),
    "cocoa": dict(products={"WA18010000": "Beans", "WA18031000": "Paste", "WA18032000": "Paste", "WA18040000": "Butter",
                            "WA18050000": "Powder", **{c: "Chocolate" for c in CHOC}},
                  origin_codes=["WA18010000"],
                  out_products=DB / "german_cocoa_products.csv", out_origins=DB / "german_cocoa_origins.csv"),
}
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


def col_of(raw, var, part):
    """Name of the flat-file column holding `part` (attribute_code / attribute_label) of variable `var`."""
    return next(c for c in raw[0] if c.endswith("_variable_code") and raw[0][c] == var).replace("_code", f"_{part}")


def write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def products(cfg):
    names = cfg["products"]
    raw = tablefile("51000-0014", startyear=START_YEAR, classifyingvariable1="WAM8",
                    classifyingkey1=",".join(names), contents=",".join(FIELDS))
    data = collect(raw, [col_of(raw, "WAM8", "attribute_code")])
    rows = [[d, hs[2:], names[hs]] + [v.get(c, 0.0) for c in COLS]
            for (d, hs), v in sorted(data.items()) if len(v) == len(COLS)]
    write(cfg["out_products"], ["date", "hs", "product"] + COLS, rows)
    print(f"products: {len(rows)} rows {rows[0][0][:7]} -> {rows[-1][0][:7]} -> {cfg['out_products'].name}")


def origins(cfg):
    out, names = cfg["out_origins"], cfg["products"]
    this_year = dt.date.today().year
    keep = []
    first = START_YEAR
    if out.exists():                                        # incremental: keep history, re-pull the last 2 years
        first = this_year - 1
        with open(out, encoding="utf-8") as fh:
            rd = csv.reader(fh)
            next(rd)
            keep = [r for r in rd if int(r[0][:4]) < first]
    new = []
    for y0 in range(first, this_year + 1, CHUNK):
        y1 = min(y0 + CHUNK - 1, this_year)
        raw = tablefile("51000-0018", startyear=y0, endyear=y1, classifyingvariable1="WAM8",
                        classifyingkey1=",".join(cfg["origin_codes"]), contents=",".join(FIELDS))
        if not raw:
            continue
        ctry, hs = col_of(raw, "STLAH", "attribute_label"), col_of(raw, "WAM8", "attribute_code")
        for (d, country, code), v in sorted(collect(raw, [ctry, hs]).items()):
            vals = [v.get(c, 0.0) for c in COLS]
            if any(vals):
                new.append([d, country, code[2:], names[code]] + vals)
        print(f"origins {y0}-{y1}: {len(new)} rows so far")
    if not new:
        sys.exit("No origin rows returned")
    write(out, ["date", "country", "hs", "product"] + COLS, keep + new)
    print(f"origins: {len(keep) + len(new)} rows -> {out.name}")


def grind():
    """Germany's quarterly cocoa grind (tonnes, Oct-Sep crop year, Q1 = Oct-Dec) from the Cocoa Grind project."""
    if not GRIND_SRC.exists():
        print(f"grind: {GRIND_SRC} not found, kept the existing copy")
        return
    with open(GRIND_SRC, encoding="utf-8") as fh:
        rows = [[r["crop_year"], r["quarter"], r["German"]] for r in csv.DictReader(fh) if r.get("German")]
    write(DB / "german_cocoa_grind.csv", ["crop_year", "quarter", "grind_t"], rows)
    print(f"grind: {len(rows)} quarters to {rows[-1][0]} {rows[-1][1]}")


if __name__ == "__main__":
    which = sys.argv[1:] or list(COMMODITIES)
    for name in which:
        print(f"== {name}")
        products(COMMODITIES[name])
        origins(COMMODITIES[name])
    if "cocoa" in which:
        grind()
