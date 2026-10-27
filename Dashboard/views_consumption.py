"""Consumption: coffee-tax implied German consumption (green-bean equivalent), coffee year Oct-Sep."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (AMBER, GREY, MONTHS, NAVY, UNITS, base, card_head, fmt_u, hero, kpis, load_tax, pct, show, signed,
                    table, yoy_cell)


def render(unit):
    f, fmt, suf = UNITS[unit]
    t = load_tax()["cons_t"]
    last = t.index.max()
    d = t.to_frame("v")
    y0 = d.index.year - (d.index.month < 10)
    d["cy"] = [f"{y % 100:02d}/{(y + 1) % 100:02d}" for y in y0]
    d["cm"] = (d.index.month - 10) % 12 + 1
    piv = d.pivot_table(index="cy", columns="cm", values="v").reindex(columns=range(1, 13))
    piv = piv.loc[sorted(piv.index, key=lambda c: (int(c[:2]) + 50) % 100)]          # '99/00' before '00/01'
    cys = list(piv.index)
    cur, prev = cys[-1], cys[-2]
    cm = int(d["cm"].iloc[-1])
    cut = f"Oct–{MONTHS[cm - 1]}"
    ytd = piv.loc[:, :cm].sum(axis=1)

    hero("Implied coffee consumption", f" · green-bean equivalent · {unit}", [f"Latest {last:%b %Y}", "Coffee tax / €2.19 per kg × 1.19"])

    s12, p12 = t.iloc[-12:].sum(), t.iloc[-24:-12].sum()
    m_ly = t.get(last - pd.DateOffset(years=1))
    items = [
        (f"{last:%b %Y}", fmt_u(t.iloc[-1], unit), f"{signed(pct(t.iloc[-1], m_ly))} vs {last.year - 1}", pct(t.iloc[-1], m_ly)),
        (f"{cur} " + ("full year" if cm == 12 else f"to date ({cut})"), fmt_u(ytd[cur], unit),
         f"{signed(pct(ytd[cur], ytd[prev]))} vs {prev}", pct(ytd[cur], ytd[prev])),
    ]
    if cm < 12:                                                  # at Sep the coffee year and the last 12m are the same number
        items.append(("Last 12 months", fmt_u(s12, unit), f"{signed(pct(s12, p12))} vs prior 12m", pct(s12, p12)))
    kpis(items)

    l, r = st.columns(2, gap="medium")
    with l, st.container(border=True):
        ref = cys[-6:-1]
        card_head("Monthly, by coffee year", f"{cur} vs {prev} · dotted = average {ref[0]}–{ref[-1]}")
        fig = go.Figure()
        fig.add_scatter(x=MONTHS, y=piv.loc[ref].mean() * f, name="5y avg", mode="lines", line=dict(color=GREY, dash="dot", width=1.6))
        fig.add_scatter(x=MONTHS, y=piv.loc[prev] * f, name=prev, mode="lines", line=dict(color=AMBER, width=2))
        fig.add_scatter(x=MONTHS, y=piv.loc[cur] * f, name=cur, mode="lines+markers", line=dict(color=NAVY, width=2.6), marker=dict(size=5))
        show(base(fig, 360, yaxis=dict(tickformat=fmt)), "co_seas")
    with r, st.container(border=True):
        card_head("12-month rolling total", "Trailing 12-month sum, the trend without the monthly tax-timing noise")
        roll = t.rolling(12).sum().dropna() * f
        fig = go.Figure(go.Scatter(x=roll.index, y=roll.values, mode="lines", line=dict(color=NAVY, width=2), name="12m"))
        show(base(fig, 360, legend=None, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "co_roll")

    with st.container(border=True):
        card_head("Coffee-year table", f"{unit} · totals only for complete years · YTD = {cut}")
        rows = []
        for c in cys[::-1][:10]:
            r_ = piv.loc[c]
            full = r_.notna().all()
            tot = r_.sum() if full else None
            i = cys.index(c)
            tot_p = piv.loc[cys[i - 1]].sum() if i and full else None
            rows.append([(c, "n")] + [("" if pd.isna(v) else format(v * f, fmt), "") for v in r_]
                        + [(format(tot * f, fmt) if tot else "", "b"), yoy_cell(pct(tot, tot_p) if tot and tot_p else float("nan")),
                           (format(ytd[c] * f, fmt), ""), yoy_cell(pct(ytd[c], ytd[cys[i - 1]]) if i else float("nan"))])
        table(["Coffee year"] + MONTHS + ["Total", "YoY", "YTD", "YTD YoY"], rows)
