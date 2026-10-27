"""Trade balance: imports, re-exports and net imports in green-bean equivalent (roasted x1.19, soluble x2.6)
against coffee-tax consumption. Net imports minus consumption = implied stock change."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (AMBER, AXIS, GBE, NAVY, RED, TEAL, UNITS, base, card_head, fmt_u, hero, kpis, latest_month,
                    load_products, load_tax, pct, show, signed)


def render(unit):
    f, fmt, suf = UNITS[unit]
    p = load_products().copy()
    last = min(latest_month(p), load_tax().index.max())
    p = p[p["date"] <= last]
    p["kind"] = p["product"].str.replace(" decaf", "")                      # Green / Roasted / Soluble
    p["imp"], p["exp"] = p["imp_t"] * p["gbe"], p["exp_t"] * p["gbe"]
    m = p.groupby("date")[["imp", "exp"]].sum()
    m["net"] = m["imp"] - m["exp"]
    m["cons"] = load_tax()["cons_t"].reindex(m.index)
    m["gap"] = m["net"] - m["cons"]
    s, sp = m.iloc[-12:].sum(), m.iloc[-24:-12].sum()

    hero("Trade balance", f" · green-bean equivalent · {unit} · last 12 months", [f"To {last:%b %Y}", "Roasted ×1.19 · Soluble ×2.6"])
    kpis([
        ("Imports", fmt_u(s["imp"], unit), f"{signed(pct(s['imp'], sp['imp']))} YoY", pct(s["imp"], sp["imp"])),
        ("Re-exports", fmt_u(s["exp"], unit), f"{s['exp'] / s['imp'] * 100:.0f}% of imports", None),
        ("Net imports", fmt_u(s["net"], unit), f"{signed(pct(s['net'], sp['net']))} YoY", pct(s["net"], sp["net"])),
        ("Consumption", fmt_u(s["cons"], unit), f"{signed(pct(s['cons'], sp['cons']))} YoY", pct(s["cons"], sp["cons"])),
        ("Implied stock change", fmt_u(s["gap"], unit), "build" if s["gap"] >= 0 else "draw", s["gap"]),
    ])

    l, r = st.columns([1, 1.3], gap="medium")
    with l, st.container(border=True):
        card_head("From imports to stock change", f"12 months to {last:%b %Y}")
        k12 = p[p["date"] > last - pd.DateOffset(months=12)].groupby("kind")[["imp", "exp"]].sum()
        steps = [(f"{k} in", k12.loc[k, "imp"]) for k in ["Green", "Roasted", "Soluble"]] + \
                [(f"{k} out", -k12.loc[k, "exp"]) for k in ["Green", "Roasted", "Soluble"]]
        x = [a for a, _ in steps] + ["Net imports", "Consumption", "Stock change"]
        y = [v * f for _, v in steps] + [0, -s["cons"] * f, 0]
        fig = go.Figure(go.Waterfall(x=x, y=y, measure=["relative"] * 6 + ["total", "relative", "total"],
                                     connector=dict(line=dict(color="rgba(10,36,99,.2)", width=1)),
                                     increasing=dict(marker=dict(color=TEAL)), decreasing=dict(marker=dict(color=RED)),
                                     totals=dict(marker=dict(color=NAVY)), hovertemplate=f"%{{x}}: %{{y:{fmt}}} {suf}<extra></extra>"))
        show(base(fig, 400, legend=None, unified=False, xaxis=dict(tickfont=dict(size=9.5, color=AXIS)), yaxis=dict(tickformat=fmt)), "tb_wf")
    with r, st.container(border=True):
        card_head("Net imports vs consumption", "12-month rolling · the gap between the lines is the implied stock change")
        roll = m[["net", "cons"]].rolling(12).sum().loc["2010-01-01":] * f
        fig = go.Figure()
        fig.add_scatter(x=roll.index, y=roll["net"], name="Net imports", mode="lines", line=dict(color=NAVY, width=2.2))
        fig.add_scatter(x=roll.index, y=roll["cons"], name="Consumption", mode="lines", line=dict(color=AMBER, width=2.2))
        show(base(fig, 400, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "tb_roll")
    st.caption("Consumption is the coffee-tax proxy; the gap also carries conversion-factor and tax-timing error, so read it as a direction.")
