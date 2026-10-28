"""Cocoa trade balance: German imports and exports of beans, paste, butter, powder and chocolate (51000-0014),
in bean equivalent (ICCO: paste x1.25, butter x1.33, powder x1.18, chocolate ~x0.4)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (H, AMBER, AXIS, CBE, MONTHS, NAVY, RED, SERIES, TEAL, UNITS, WINE, base, card_head, hero,
                    latest_month, load_products, show, table, unit_picker)

PRODUCTS = list(CBE)


def sidebar():
    st.markdown("<div class='sb-lbl'>Trade balance</div>", unsafe_allow_html=True)
    unit = unit_picker("ctb_unit", "cocoa")
    since = st.radio("History from", ["2010", "2016", "2020"], index=1, horizontal=True, key="ctb_since")
    return unit, since


def render(unit, since):
    f, fmt, suf = UNITS[unit]
    p = load_products("cocoa").copy()
    last = latest_month(p)
    p = p[p["date"] <= last]
    p["imp"], p["exp"] = p["imp_t"] * p["gbe"], p["exp_t"] * p["gbe"]
    imp = p.pivot_table(index="date", columns="product", values="imp", aggfunc="sum").reindex(columns=PRODUCTS).fillna(0)
    exp = p.pivot_table(index="date", columns="product", values="exp", aggfunc="sum").reindex(columns=PRODUCTS).fillna(0)
    i12, e12 = imp.iloc[-12:].sum(), exp.iloc[-12:].sum()

    hero("Cocoa trade balance", f" · bean equivalent · {unit}", [f"Latest {last:%b %Y}"])

    l, r = st.columns([1, 1.35], gap="small")
    with l, st.container(border=True):
        card_head(f"In and out, 12m to {last:%b %Y}")
        steps = [(f"{k} in", i12[k]) for k in PRODUCTS] + [(f"{k} out", -e12[k]) for k in PRODUCTS]
        x = [a for a, _ in steps] + ["Net"]
        y = [v * f for _, v in steps] + [0]
        fig = go.Figure(go.Waterfall(x=x, y=y, measure=["relative"] * len(steps) + ["total"],
                                     connector=dict(line=dict(color="rgba(10,36,99,.25)", width=1)),
                                     increasing=dict(marker=dict(color=TEAL)), decreasing=dict(marker=dict(color=RED)),
                                     totals=dict(marker=dict(color=NAVY)), hovertemplate=f"%{{x}}: %{{y:{fmt}}} {suf}<extra></extra>"))
        show(base(fig, H, legend=None, unified=False, xaxis=dict(tickfont=dict(size=9, color=AXIS), tickangle=-45),
                  yaxis=dict(tickformat=fmt)), "ctb_wf")

    with r, st.container(border=True):
        h, c = st.columns([1.2, 2], vertical_alignment="center")
        with h:
            card_head("Flows by product")
        with c:
            prod = st.radio("Product", PRODUCTS, horizontal=True, key="tb_prod_cocoa", label_visibility="collapsed")
        q = p[p["product"] == prod].set_index("date").loc[since:]
        fig = go.Figure()
        fig.add_bar(x=q.index, y=q["imp_t"] * f, name="Imports", marker_color=TEAL, hovertemplate=f"Imports: %{{y:{fmt}}}<extra></extra>")
        fig.add_bar(x=q.index, y=-q["exp_t"] * f, name="Exports", marker_color=WINE, hovertemplate=f"Exports: %{{y:{fmt}}}<extra></extra>")
        net = (q["imp_t"] - q["exp_t"]) * f
        fig.add_scatter(x=q.index, y=net.rolling(12).mean(), name="Net, 12m avg", mode="lines", line=dict(color=NAVY, width=2),
                        hovertemplate=f"Net 12m avg: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, H, barmode="relative", bargap=0.1, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "ctb_prod")

    with st.container(border=True):
        card_head("Net imports by product, 12m rolling, bean equivalent")
        net = (imp - exp).rolling(12).sum().loc[since:] * f
        fig = go.Figure()
        for i, k in enumerate(PRODUCTS):
            fig.add_scatter(x=net.index, y=net[k], name=k, mode="lines", line=dict(color=SERIES[i], width=2),
                            hovertemplate=f"{k}: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, 280, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "ctb_net")

    with st.container(border=True):
        cm = (last.month - 10) % 12 + 1
        card_head(f"Crop-year balance, bean equivalent (latest = Oct–{MONTHS[cm - 1]})")
        y = imp.add_prefix("i_").join(exp.add_prefix("e_"))
        y["cy"] = [f"{(d.year - (d.month < 10)) % 100:02d}/{(d.year - (d.month < 10) + 1) % 100:02d}" for d in y.index]
        t = y.groupby("cy").sum().iloc[-10:]
        t["net"] = t[[f"i_{k}" for k in PRODUCTS]].sum(axis=1) - t[[f"e_{k}" for k in PRODUCTS]].sum(axis=1)
        cols = [(f"i_{k}", f"{k} in") for k in PRODUCTS] + [(f"e_{k}", f"{k} out") for k in PRODUCTS] + [("net", "Net")]
        rows = [[(cy, "n")] + [(format(r_[c] * f, fmt), "b" if c == "net" else "") for c, _ in cols] for cy, r_ in t.iloc[::-1].iterrows()]
        table(["Crop year"] + [lbl for _, lbl in cols], rows)
