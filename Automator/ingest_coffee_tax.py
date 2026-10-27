"""Pull German coffee tax (Kaffeesteuer) receipts from Destatis GENESIS and convert to implied consumption.

Source table 71211-0005: tax revenue, Germany, months, types of taxes prior to distribution (EUR 1000).
Implied bags = EUR 1000 * 1000 / 2.19 EUR/kg roasted * 1.19 green-equivalent / 60 kg.
"""
import csv
import sys
from pathlib import Path

from genesis import month, tablefile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Database" / "german_coffee_tax.csv"
TABLE = "71211-0005"
START_YEAR = 1999
TAX_RATE = 2.19          # EUR per kg roasted coffee
GREEN_FACTOR = 1.19      # roasted -> green equivalent
BAG_KG = 60


def parse(raw):
    rows = []
    for r in raw:
        if r["3_variable_attribute_label"] != "Coffee tax":
            continue
        v = r["value"].strip()
        if not v or not v.lstrip("-").isdigit():               # '...' = not yet published
            continue
        eur_k = int(v)
        bags = eur_k * 1000 / TAX_RATE * GREEN_FACTOR / BAG_KG
        rows.append({"date": month(r), "coffee_tax_eur_k": eur_k,
                     "roasted_t": round(eur_k * 1000 / TAX_RATE / 1000, 1), "bags_m": round(bags / 1e6, 4)})
    return sorted(rows, key=lambda x: x["date"])


def main():
    rows = parse(tablefile(TABLE, startyear=START_YEAR))
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
