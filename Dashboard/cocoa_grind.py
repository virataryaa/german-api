"""Cocoa grind: Germany's quarterly cocoa bean grind (BDSI, via the Cocoa Grind project), crop year Oct-Sep."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (H, AXIS, GREEN, GREY, NAVY, OTHER_C, RED, TEAL, UNITS, base, card_head, hero, load_grind, pct, show,
                    table, unit_picker, yoy_cell)

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
Q_LABEL = {"Q1": "Oct–Dec", "Q2": "Jan–Mar", "Q3": "Apr–Jun", "Q4": "Jul–Sep"}


def sidebar():
    st.markdown("<div class='sb-lbl'>Grind</div>", unsafe_allow_html=True)
    return (unit_picker("gr_unit", "cocoa"),)


def render(unit):
    f, fmt, suf = UNITS[unit]
    g = load_grind()
    piv = g.pivot_table(index="crop_year", columns="quarter", values="grind_t").reindex(columns=QUARTERS)
    piv = piv.loc[sorted(piv.index, key=lambda c: (int(c[:2]) + 50) % 100)]
    cys = list(piv.index)
    cur, prev = cys[-1], cys[-2]
    last_q = piv.loc[cur].last_valid_index()

    hero("German cocoa grind", f" · {unit}", [f"Latest {cur} {last_q} ({Q_LABEL[last_q]})"])

    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        card_head("Grind by quarter")
        fig = go.Figure()
        show_years = cys[-4:]
        for i, y in enumerate(show_years):
            fig.add_bar(x=[Q_LABEL[q] for q in QUARTERS], y=piv.loc[y] * f, name=y,
                        marker_color=NAVY if y == cur else [OTHER_C, "#9fb0d6", TEAL][i % 3],
                        hovertemplate=f"{y} %{{x}}: %{{y:{fmt}}} {suf}<extra></extra>")
        ref = [c for c in cys if c < cur][-5:]
        fig.add_scatter(x=[Q_LABEL[q] for q in QUARTERS], y=piv.loc[ref].mean() * f, name="5y avg", mode="lines+markers",
                        line=dict(color=GREY, dash="dot", width=1.6), marker=dict(size=5))
        lo = float(piv.loc[show_years].min().min()) * f
        show(base(fig, H, barmode="group", bargap=0.25, bargroupgap=0.05, unified=False,
                  yaxis=dict(tickformat=fmt, range=[lo * 0.85, None])), "gr_q")

    s = pd.Series([piv.loc[c, q] for c in cys for q in QUARTERS], index=[f"{c} {q}" for c in cys for q in QUARTERS]).dropna()
    with r, st.container(border=True):
        card_head("Rolling 4 quarters")
        roll = s.rolling(4).sum().dropna() * f
        fig = go.Figure(go.Scatter(x=roll.index, y=roll.values, mode="lines+markers", line=dict(color=NAVY, width=2.2),
                                   marker=dict(size=4), hovertemplate=f"%{{x}}: %{{y:{fmt}}} {suf}<extra></extra>"))
        show(base(fig, H, legend=None, xaxis=dict(tickangle=-45, tickfont=dict(size=9, color=AXIS), nticks=12),
                  yaxis=dict(tickformat=fmt)), "gr_roll")

    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        card_head("Change vs same quarter a year earlier")
        yoy = (s / s.shift(4) - 1).dropna().iloc[-12:] * 100
        fig = go.Figure(go.Bar(x=yoy.index, y=yoy.values, marker_color=[GREEN if v >= 0 else RED for v in yoy.values],
                               text=[f"{v:+.1f}%" for v in yoy.values], textposition="outside", textfont=dict(size=9, color=AXIS),
                               cliponaxis=False, hovertemplate="%{x}: %{y:+.1f}%<extra></extra>"))
        show(base(fig, H, legend=None, unified=False, bargap=0.35, xaxis=dict(tickangle=-45, tickfont=dict(size=9, color=AXIS)),
                  yaxis=dict(ticksuffix="%")), "gr_yoy")

    with r, st.container(border=True):
        card_head("Grind table")
        rows = []
        for i, c in enumerate(cys[::-1]):
            r_ = piv.loc[c]
            full = r_.notna().all()
            tot = r_.sum() if full else None
            j = cys.index(c)
            p_ = piv.loc[cys[j - 1]] if j else None
            tot_p = p_.sum() if j and p_.notna().all() else None
            rows.append([(c, "n")] + [("" if pd.isna(v) else format(v * f, fmt), "") for v in r_]
                        + [(format(tot * f, fmt) if tot else "", "b"),
                           yoy_cell(pct(tot, tot_p) if tot and tot_p else float("nan"))])
        table(["Crop year"] + [f"{q} {Q_LABEL[q]}" for q in QUARTERS] + ["Total", "YoY"], rows)
