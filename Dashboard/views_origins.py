"""Origins: German green coffee / cocoa bean imports by country of origin (51000-0018), crop year Oct-Sep."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (H, COMMS, AMBER, AXIS, EUROPE, GREEN, GREY, MONTHS, NAVY, OTHER_C, RED, SERIES, TEAL, UNITS, base,
                    card_head, cy_ytd, hero, load_origins, latest_month, pct, rgba, show, table, unit_picker,
                    yoy_cell)


def sidebar(comm="coffee"):
    st.markdown("<div class='sb-lbl'>Origins</div>", unsafe_allow_html=True)
    unit = unit_picker("or_unit", comm)
    top_n = st.radio("Top origins", [5, 8, 10], index=1, horizontal=True, key="or_top")
    decaf = comm != "coffee" or st.radio("Green coffee", ["Incl. decaf", "Excl. decaf"], horizontal=True, key="or_decaf") == "Incl. decaf"
    eu = st.radio("European re-shipments", ["Show", "Hide"], horizontal=True, key="or_eu")
    return comm, unit, top_n, decaf, eu == "Show"


def render(comm, unit, top_n, decaf, eu):
    d = load_origins(comm)
    d = d if decaf else d[d["product"] == COMMS[comm]["main"]]
    if not eu:
        d = d[~d["country"].isin(EUROPE)]
    f, fmt, suf = UNITS[unit]
    latest = latest_month(d)
    d = d[d["date"] <= latest]
    cur_cy = d.loc[d["date"] == latest, "cy"].iloc[0]
    cys = sorted(d["cy"].unique())
    prev_cy = cys[cys.index(cur_cy) - 1]

    ytd_c, cm_now = cy_ytd(d, "imp_t", latest)
    cut = f"Oct–{MONTHS[cm_now - 1]}"
    by_c = d[d["cm"] <= cm_now].groupby(["cy", "country"])["imp_t"].sum()
    cur, prev = by_c.loc[cur_cy], by_c.loc[prev_cy]
    tops = cur.sort_values(ascending=False).index[:top_n].tolist()
    colors = {c: SERIES[i % len(SERIES)] for i, c in enumerate(tops)}

    hero(f"{COMMS[comm]['item']} imports by origin", f" · crop year Oct–Sep · {unit}",
         [f"Latest {latest:%b %Y}"])

    tot_c, tot_p = cur.sum(), prev.sum()

    # ── Row 1: monthly stack | CYTD by origin ──
    l, r = st.columns([1.55, 1], gap="small")
    with l, st.container(border=True):
        card_head("Monthly imports by origin")
        w = d[d["date"] > latest - pd.DateOffset(months=36)].copy()
        w["grp"] = np.where(w["country"].isin(tops), w["country"], "Other")
        p = w.pivot_table(index="date", columns="grp", values="imp_t", aggfunc="sum").fillna(0) * f
        fig = go.Figure()
        for c in tops + ["Other"]:
            if c in p:
                fig.add_bar(x=p.index, y=p[c], name=c, marker_color=colors.get(c, OTHER_C),
                            hovertemplate=f"{c}: %{{y:{fmt}}} {suf}<extra></extra>")
        tot = p.sum(axis=1)
        fig.add_scatter(x=tot.index, y=tot.rolling(12).mean(), name="12m avg", mode="lines",
                        line=dict(color=INK_DARK, width=1.6, dash="dot"), hovertemplate=f"12m avg: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, H, barmode="stack", bargap=0.18, xaxis=dict(dtick="M3", tickformat="%b-%y",
                                                                      range=[p.index[0] - pd.Timedelta(days=20), p.index[-1] + pd.Timedelta(days=20)]),
                  yaxis=dict(tickformat=fmt, title=dict(text=suf, font=dict(size=10)))), "or_stack")

    with r, st.container(border=True):
        card_head(f"CYTD by origin, {cut}")
        both = pd.DataFrame({"cur": cur, "prev": prev}).fillna(0)
        both = both.loc[both["cur"].sort_values(ascending=False).index[:10]]
        fig = go.Figure()
        fig.add_bar(x=both.index, y=both["prev"] * f, name=prev_cy, marker_color=OTHER_C,
                    hovertemplate=f"%{{x}} {prev_cy}: %{{y:{fmt}}} {suf}<extra></extra>")
        fig.add_bar(x=both.index, y=both["cur"] * f, name=cur_cy, marker_color=NAVY,
                    hovertemplate=f"%{{x}} {cur_cy}: %{{y:{fmt}}} {suf}<extra></extra>")
        for c, row in both.iterrows():
            ch = pct(row["cur"], row["prev"])
            if pd.notna(ch) and np.isfinite(ch):
                fig.add_annotation(x=c, y=max(row["cur"], row["prev"]) * f, text=f"{ch:+.0f}%", showarrow=False,
                                   yanchor="bottom", yshift=2, font=dict(size=9.5, color=GREEN if ch >= 0 else RED))
        show(base(fig, H, barmode="group", bargap=0.28, bargroupgap=0.06, unified=False,
                  xaxis=dict(tickfont=dict(size=9.5, color=AXIS), tickangle=-30), yaxis=dict(tickformat=fmt)), "or_ytd")

    # ── Row 2: origin mix | 12m rolling ──
    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        card_head("Origin mix by crop year")
        cy_tot = d.groupby(["cy", "country"])["imp_t"].sum().unstack(fill_value=0)
        cy_tot = cy_tot.loc[cys[-12:]]
        mix = cy_tot.div(cy_tot.sum(axis=1), axis=0) * 100
        fig = go.Figure()
        for c in tops:
            fig.add_bar(x=mix.index, y=mix[c], name=c, marker_color=colors[c], hovertemplate=f"{c}: %{{y:.1f}}%<extra></extra>")
        other = 100 - mix[tops].sum(axis=1)
        fig.add_bar(x=mix.index, y=other, name="Other", marker_color=OTHER_C, hovertemplate="Other: %{y:.1f}%<extra></extra>")
        show(base(fig, H, barmode="stack", bargap=0.25, yaxis=dict(ticksuffix="%", range=[0, 100])), "or_mix")

    with r, st.container(border=True):
        card_head("12-month rolling imports, top 5")
        m = d.groupby(["date", "country"])["imp_t"].sum().unstack(fill_value=0).sort_index()
        roll = m.rolling(12).sum().loc["2010-01-01":] * f
        fig = go.Figure()
        for c in tops[:5]:
            fig.add_scatter(x=roll.index, y=roll[c], name=c, mode="lines", line=dict(color=colors[c], width=2),
                            hovertemplate=f"{c}: %{{y:{fmt}}} {suf}<extra></extra>")
        show(base(fig, H, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "or_roll")

    # ── Row 3: single-origin drill-down ──
    with st.container(border=True):
        h, s = st.columns([3, 1], vertical_alignment="center")
        with s:
            pick = st.selectbox("Origin", cur.sort_values(ascending=False).index.tolist(), key="or_pick", label_visibility="collapsed")
        with h:
            card_head(f"{pick}: seasonality and pace")
        o = d[d["country"] == pick].pivot_table(index="cy", columns="cm", values="imp_t", aggfunc="sum").reindex(columns=range(1, 13))
        o = o.reindex(cys).fillna(0)
        o.loc[cur_cy, [m_ for m_ in range(1, 13) if m_ > cm_now]] = np.nan
        ref = [c for c in cys if c < cur_cy][-5:]
        a, b = st.columns(2, gap="small")
        with a:
            fig = go.Figure()
            rb = o.loc[ref] * f
            fig.add_scatter(x=MONTHS, y=rb.max(), mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip")
            fig.add_scatter(x=MONTHS, y=rb.min(), mode="lines", line=dict(width=0), fill="tonexty", fillcolor=rgba(TEAL, 0.14),
                            name="L5Y range", hoverinfo="skip")
            fig.add_scatter(x=MONTHS, y=rb.mean(), name="L5Y avg", mode="lines", line=dict(color=AXIS, dash="dot", width=1.5),
                            hovertemplate=f"Avg: %{{y:{fmt}}}<extra></extra>")
            fig.add_scatter(x=MONTHS, y=o.loc[prev_cy] * f, name=prev_cy, mode="lines", line=dict(color=RED, width=2),
                            hovertemplate=f"{prev_cy}: %{{y:{fmt}}}<extra></extra>")
            fig.add_scatter(x=MONTHS, y=o.loc[cur_cy] * f, name=cur_cy, mode="lines+markers", line=dict(color=NAVY, width=3),
                            marker=dict(size=5), hovertemplate=f"{cur_cy}: %{{y:{fmt}}}<extra></extra>")
            show(base(fig, H, yaxis=dict(tickformat=fmt, title=dict(text=suf, font=dict(size=10)))), "or_seas")
        with b:
            cum = o.cumsum(axis=1) * f
            fig = go.Figure()
            for i, c in enumerate(cys[-6:]):
                is_cur, is_prev = c == cur_cy, c == prev_cy
                fig.add_scatter(x=MONTHS, y=cum.loc[c], name=c, mode="lines",
                                line=dict(color=NAVY if is_cur else RED if is_prev else [GREY, AMBER, GREEN, TEAL][i % 4],
                                          width=3 if is_cur else 2 if is_prev else 1.2),
                                hovertemplate=f"{c}: %{{y:{fmt}}}<extra></extra>")
            show(base(fig, H, yaxis=dict(tickformat=fmt)), "or_cum")

    # ── Table ──
    with st.container(border=True):
        card_head("Imports by origin and crop year")
        full = [c for c in cys if c < cur_cy][-6:]
        yt = d.groupby(["cy", "country"])["imp_t"].sum().unstack(fill_value=0)
        rows_n = cur.sort_values(ascending=False).index[:15].tolist()
        def v(x):
            return format(x * f, fmt)
        rows = []
        for c in rows_n:
            rows.append([(c, "n")] + [(v(yt.loc[y].get(c, 0)), "") for y in full]
                        + [(v(prev.get(c, 0)), ""), (v(cur.get(c, 0)), "b"), yoy_cell(pct(cur.get(c, 0), prev.get(c, np.nan))),
                           (f"{cur.get(c, 0) / tot_c * 100:.1f}%", "")])
        rest_c, rest_p = tot_c - cur[rows_n].sum(), tot_p - prev.reindex(rows_n).fillna(0).sum()
        rows.append([("Other", "n")] + [(v(yt.loc[y].sum() - yt.loc[y].reindex(rows_n).fillna(0).sum()), "") for y in full]
                    + [(v(rest_p), ""), (v(rest_c), "b"), yoy_cell(pct(rest_c, rest_p)), (f"{rest_c / tot_c * 100:.1f}%", "")])
        tot = [("Total", "n")] + [(v(yt.loc[y].sum()), "") for y in full] + [(v(tot_p), ""), (v(tot_c), "b"),
                                                                             yoy_cell(pct(tot_c, tot_p)), ("100%", "")]
        table(["Origin"] + full + [f"{prev_cy} {cut}", f"{cur_cy} {cut}", "YoY", "Share"], rows, tot)


INK_DARK = "#1a1a2e"
