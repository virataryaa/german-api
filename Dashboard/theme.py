"""Shared look, copied from Cecafe Daily app.py (base CSS + ICE glacier theme)."""
BASE_CSS = """
<style>
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main { background: #fafafa !important; }
[data-testid="stHeader"] { background: #fafafa !important; }
[data-testid="stSidebar"] { background: #f0f2f8 !important; border-right: 1px solid #dfe3ee; }
h1, h2, h3, h4, h5, h6 { color: #0a2463 !important; }
body, .main { color: #1a1a2e; }
[data-testid="stSidebar"] { color: #1a1a2e; }
.block-container { padding-top: 2.2rem; }

/* Pill / segmented-control tabs */
.stTabs [data-baseweb="tab-list"] { background: #eef0f6; padding: 4px; border-radius: 999px; gap: 4px; display: inline-flex; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #5a6688 !important; border-radius: 999px !important;
                               padding: 8px 20px !important; font-weight: 600; border: none !important; }
.stTabs [aria-selected="true"] { background: #0a2463 !important; color: #ffffff !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Radio as pill/segmented control */
div[role="radiogroup"] { background: #eef0f6; padding: 4px; border-radius: 999px; gap: 2px; display: inline-flex; flex-wrap: wrap; }
div[role="radiogroup"] label { background: transparent !important; border-radius: 999px !important; padding: 4px 12px !important; margin: 0 !important; }
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child { display: none; }
div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 12px !important; color: #5a6688; }
div[role="radiogroup"] label:has(input:checked) { background: #0a2463 !important; }
div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; font-weight: 600; }

/* Selects: white bg, dark text */
[data-baseweb="popover"] [data-baseweb="menu"] { background: #ffffff !important; }
[data-baseweb="popover"] [data-baseweb="menu"] li,
[data-baseweb="popover"] [data-baseweb="menu"] li * { color: #1a1a2e !important; }
[data-baseweb="select"] { background: #ffffff !important; }
[data-baseweb="select"] > div { background: #ffffff !important; color: #1a1a2e !important; }

.card-desc { color: #5a6688; font-size: 0.82rem; margin-top: -6px; margin-bottom: 10px; }
.chart-head { color: #0a2463; font-weight: 600; font-size: 0.95rem; margin-bottom: 0; }
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
    background: #ffffff; border: 1px solid #e3e7f0 !important; border-radius: 12px;
    box-shadow: 0 1px 3px rgba(10,36,99,0.06); }
/* Section selector in the sidebar: large stacked pills, as in Daily Miner */
[data-testid="stSidebarUserContent"] { padding-top: 1rem !important; }
[data-testid="stSidebar"] div[role="radiogroup"] { display: flex; flex-direction: column; align-items: stretch; width: 100%; border-radius: 22px; padding: 5px; gap: 3px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding: 8px 18px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; }
/* Daily & Monthly Entry (first sidebar pill) and its sub-tabs: dark orange when selected */
[data-testid="stSidebar"] div[role="radiogroup"] label:first-of-type:has(input:checked),
.st-key-entry_nav div[role="radiogroup"] label:has(input:checked) { background: #c2410c !important; }
.sb-label { font-size: 11px; color: #7a86a8; text-transform: uppercase; letter-spacing: .06em; margin: 6px 0 4px; }
.st-key-nav div[role="radiogroup"] label { padding: 7px 18px !important; }
.st-key-monthsel { display: flex; justify-content: flex-end; }
.st-key-monthsel [data-baseweb="select"] { min-width: 210px; max-width: 250px; margin-left: auto; }
.st-key-monthsel [data-baseweb="select"] > div { border-radius: 999px !important; border: 1.5px solid #0a2463 !important;
    background: #ffffff !important; box-shadow: 0 1px 5px rgba(10,36,99,0.14); min-height: 40px; padding-left: 8px; }
.st-key-monthsel [data-baseweb="select"] div, .st-key-monthsel [data-baseweb="select"] span { color: #0a2463 !important; font-weight: 600; }
.st-key-monthsel [data-baseweb="select"] svg { fill: #0a2463 !important; }
.st-key-nav div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 14px !important; }
.page-title { color: #0a2463; font-weight: 700; font-size: 1.25rem; margin: 0 0 6px 0; }
.card-title { color: #0a2463; font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.pill { display: inline-block; background: #e6e9f2; color: #0a2463; font-size: 11px; font-weight: 600;
        padding: 1px 8px; border-radius: 999px; margin-left: 6px; vertical-align: middle; }
.grid-head { color: #0a2463; font-weight: 600; font-size: 0.85rem; padding: 3px 8px; background: #e6e9f2; border-radius: 6px 6px 0 0; margin-bottom: 2px; display: inline-block; }

/* Sidebar title + small stats */
.sb-title { font-family: Plus Jakarta Sans, sans-serif; font-size: 1.5rem; font-weight: 600; color: #0a2463; margin-bottom: 2px; }
.sb-caption { font-size: 11px; color: #7a86a8; margin-bottom: 16px; line-height: 1.4; }
.filter-stat { font-size: 12px; color: #5a6688 !important; line-height: 1.7; margin-bottom: 14px; }
.filter-stat b { color: #0a2463 !important; font-size: 13px; }

/* Compact Excel-style tables */
.dtab { width: auto; border-collapse: collapse; font-size: 11.5px; line-height: 1.15; background: #ffffff; }
.dtab th { text-align: center; padding: 2px 8px; font-weight: 600; white-space: nowrap; }
.dtab .g1 { background: #ffffff; color: #1a1a2e; border: 1px solid #dfe3ee; }
.dtab .g2 { background: #dfe5f1; color: #0a2463; border: 1px solid #dfe3ee; }
.dtab .g3 { background: #e3f1ee; color: #0a2463; border: 1px solid #dfe3ee; }
.dtab .sub th { background: #0a2463; color: #ffffff; }
.dtab td { text-align: right; padding: 1px 8px; border-bottom: 1px solid #eef0f6; white-space: nowrap; color: #1a1a2e; }
.dtab td.dt { text-align: center; background: #f0f2f8; }
.dtab td.b { font-weight: 700; background: #f6f7fb; }
.dtab-lg { font-size: 13px; }
.dtab-lg th { padding: 3px 9px; }
.dtab-lg td { padding: 2px 9px; }
.dtab td.avgc { background: #e3f1ee; color: #0a2463; font-style: italic; }
.dtab td.early { color: #6f7895; background: #f4f5f8; font-weight: 400; font-style: italic; }
.tab-note { font-size: 11px; color: #7a86a8; margin-top: 4px; }
.dtab td.ts { font-size: 10.5px; font-style: italic; color: #7a86a8; text-align: left; }
</style>
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
[data-testid="stSidebar"] { background: linear-gradient(160deg, rgba(246,248,253,.92) 0%, rgba(233,238,248,.88) 55%, rgba(240,236,246,.9) 100%) !important;
  -webkit-backdrop-filter: blur(24px) saturate(160%); backdrop-filter: blur(24px) saturate(160%);
  border-right: 1px solid rgba(255,255,255,.75) !important; box-shadow: inset -1px 0 0 rgba(10,36,99,.06), 6px 0 28px rgba(10,36,99,.06); }
div[role="radiogroup"], .stTabs [data-baseweb="tab-list"] { background: linear-gradient(160deg, rgba(250,252,255,.97), rgba(236,242,251,.93) 60%, rgba(229,237,249,.9)) !important;
  border: 1px solid rgba(43,74,138,.14) !important; box-shadow: 0 4px 16px rgba(30,58,110,.07), inset 0 1px 0 rgba(255,255,255,.95) !important; }
div[role="radiogroup"] label:has(input:checked), .stTabs [aria-selected="true"] { background: linear-gradient(180deg, #2b4a8a, #1e3a6e) !important;
  box-shadow: 0 2px 8px rgba(30,58,110,.28), inset 0 1px 0 rgba(255,255,255,.18) !important; }
div[role="radiogroup"] label:not(:has(input:checked)):hover { background: rgba(43,74,138,.07) !important; }
[data-testid="stMain"] [data-testid="stPlotlyChart"] { background: #ffffff; border: 1px solid rgba(43,74,138,.12); border-radius: 16px; padding: 6px 8px;
  box-shadow: 0 6px 22px rgba(30,58,110,.07), inset 0 1px 0 rgba(255,255,255,.95); }
.dtab, .tbl-wrap { border: 1px solid rgba(43,74,138,.14) !important; border-radius: 12px; background: #ffffff !important; box-shadow: none !important; }
.tbl-wrap { overflow-x: auto; margin-bottom: 12px !important; }          /* stays inside its card */
[class*="st-key-mc_card_"], [class*="st-key-dx_card_"] { padding-bottom: 12px !important; border-color: rgba(43,74,138,.12) !important;
  box-shadow: 0 6px 22px rgba(30,58,110,.07) !important; }
.dtab { border-collapse: separate !important; border-spacing: 0; }
.dtab .sub th { background: linear-gradient(180deg, #2b4a8a, #1e3a6e) !important; color: #ffffff !important; }
.dtab .g2 { background: #e6edf8 !important; } .dtab .g3 { background: #e8f2f6 !important; }
.dtab .g1, .dtab .g2, .dtab .g3 { border-color: rgba(43,74,138,.10) !important; }
.dtab td { border-bottom-color: rgba(43,74,138,.07) !important; }
.dtab tr:nth-child(even) td:not(.dt):not(.b):not(.avgc):not(.early) { background: #f8fafd; }
.dtab td.dt { background: #f1f5fb !important; } .dtab td.b { background: #eef3fa !important; }
.tbl th { background: linear-gradient(180deg, #f3f7fd, #e7eef9) !important; color: #1e3a6e !important; }
.tbl td { border-bottom-color: rgba(43,74,138,.07) !important; } .tbl td.lbl { background: #f5f8fc !important; border-right-color: rgba(43,74,138,.10) !important; }
.tbl tr:nth-child(even) td:not(.lbl) { background: #f9fbfe; }
.grid-head { background: linear-gradient(160deg, rgba(250,252,255,.97), rgba(232,239,250,.92)) !important; border: 1px solid rgba(43,74,138,.12);
  border-bottom: 0; color: #1e3a6e !important; border-radius: 10px 10px 0 0 !important; }
.card-desc, .tbl th, .dtab th, .grid-head, [data-testid="stCaptionContainer"], [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
div[role="radiogroup"] label p, .stTabs [data-baseweb="tab"] p { font-family: Plus Jakarta Sans, sans-serif !important; letter-spacing: .01em; }
/* ── Ice theme completion (matches COT Comprehensive / Futures OI / TDM Comprehensive) ── */
[data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] > style:only-child) { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; pointer-events: none; }
[data-testid="stHeader"] button, [data-testid="stHeader"] a, [data-testid="stToolbar"] { pointer-events: auto; }
html, body, [class*="css"], [data-testid="stAppViewContainer"], .stMarkdown, button, input, textarea {
  font-family: Plus Jakarta Sans, sans-serif !important; -webkit-font-smoothing: antialiased; }
.page-title, .card-title, .chart-head, .mc-sec, .dx-sec, .mc-hero-t, .dx-hero-t, [data-testid="stWidgetLabel"] p {
  font-family: Plus Jakarta Sans, sans-serif !important; }
/* dropdowns: glass pill, lift on hover, wine focus ring + caret; frosted menus */
[data-baseweb="select"] { background: transparent !important; box-shadow: none !important; }
[data-baseweb="select"] > div { background: linear-gradient(180deg, rgba(255,255,255,.78), rgba(238,242,250,.62)) !important;
  -webkit-backdrop-filter: blur(14px) saturate(170%); backdrop-filter: blur(14px) saturate(170%);
  border: 1px solid rgba(255,255,255,.9) !important; border-radius: 999px !important; min-height: 34px;
  box-shadow: 0 1px 2px rgba(10,36,99,.06), 0 6px 18px rgba(10,36,99,.08), inset 0 1px 0 rgba(255,255,255,.95); transition: box-shadow .18s, transform .18s; }
[data-baseweb="select"] > div:hover { box-shadow: 0 0 0 3px rgba(10,36,99,.07), 0 8px 22px rgba(10,36,99,.14), inset 0 1px 0 rgba(255,255,255,.95); transform: translateY(-1px); }
[data-baseweb="select"] > div:focus-within { box-shadow: 0 0 0 3px rgba(123,30,58,.16), 0 8px 22px rgba(10,36,99,.14) !important; }
[data-baseweb="select"] svg { fill: #7b1e3a !important; }
.st-key-monthsel [data-baseweb="select"] > div { border: 1px solid rgba(43,74,138,.22) !important; min-height: 40px; }
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul {
  background: rgba(255,255,255,.82) !important; -webkit-backdrop-filter: blur(18px) saturate(170%); backdrop-filter: blur(18px) saturate(170%);
  border: 1px solid rgba(255,255,255,.9) !important; border-radius: 14px !important; box-shadow: 0 14px 40px rgba(10,36,99,.18) !important; }
[data-baseweb="popover"] li:hover { background: rgba(43,74,138,.07) !important; }
/* vertical option lists inside popovers: a plain menu, not a pill track */
[data-testid="stPopoverBody"] div[role="radiogroup"] { background: none !important; border: none !important; box-shadow: none !important;
  border-radius: 0 !important; padding: 0 !important; display: flex !important; flex-direction: column; gap: 2px; width: 100%; }
[data-testid="stPopoverBody"] div[role="radiogroup"] label { width: 100%; border-radius: 8px !important; padding: 5px 10px !important; }
[data-testid="stPopoverBody"] div[role="radiogroup"] label:has(input:checked) { background: rgba(43,74,138,.09) !important; box-shadow: none !important; }
[data-testid="stPopoverBody"] div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #0a2463 !important; font-weight: 700; }
/* pill rows lift on hover; charts/cards/buttons/expanders */
div[role="radiogroup"] label { transition: background .15s, transform .15s; }
div[role="radiogroup"] label:not(:has(input:checked)):hover { transform: translateY(-1px); }
[data-testid="stMain"] [data-testid="stPlotlyChart"] { overflow: hidden; transition: box-shadow .2s; }
[data-testid="stMain"] [data-testid="stPlotlyChart"] .main-svg { border-radius: 14px; }
[data-testid="stMain"] [data-testid="stPlotlyChart"]:hover { box-shadow: 0 1px 2px rgba(10,36,99,.05), 0 10px 26px rgba(30,58,110,.10), inset 0 1px 0 #ffffff; }
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) { border-radius: 18px !important;
  border-color: rgba(43,74,138,.10) !important; box-shadow: 0 1px 2px rgba(10,36,99,.04), 0 8px 24px rgba(30,58,110,.06) !important; }
.st-key-mc_filters, .st-key-dx_filters { border: 1px solid rgba(43,74,138,.10) !important; border-radius: 18px !important;
  box-shadow: 0 1px 2px rgba(10,36,99,.04), 0 10px 30px rgba(30,58,110,.08), inset 0 1px 0 #ffffff !important; }
.stButton > button, .stDownloadButton > button { border-radius: 999px !important; transition: box-shadow .18s, transform .18s; }
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(10,36,99,.12) !important; }
div[data-testid="stExpander"] { border: 1px solid rgba(43,74,138,.10) !important; border-radius: 14px !important; box-shadow: 0 1px 3px rgba(10,36,99,.06); background: #ffffff; }
/* headings: section heads minimal + centred on a royal-grey wash bar; chart/card titles navy, compact */
.mc-rule, .dx-rule { border-top: none !important; margin: 18px 0 0 !important; }
.mc-sec, .dx-sec { display: block; text-align: center; padding: 7px 14px; border-radius: 10px; margin: 6px 0 8px !important;
  background: linear-gradient(90deg, rgba(92,104,136,0) 0%, rgba(92,104,136,.12) 22%, rgba(92,104,136,.12) 78%, rgba(92,104,136,0) 100%);
  font-size: 12.5px !important; font-weight: 700 !important; letter-spacing: .12em !important; text-transform: uppercase; color: #3b4663 !important; }
.page-title { font-size: 1.15rem !important; letter-spacing: -.01em; }
.card-title, .chart-head { font-size: 14px !important; font-weight: 700 !important; color: #0a2463 !important; letter-spacing: -.005em; }
.card-desc { color: #7a86a8 !important; font-size: 12px !important; }
/* one header style for every chart and table title (chart-head, card-title, grid-head): centred, small caps-lock
   with wide tracking on a compact royal-grey wash bar; the note under a title is centred too */
.chart-head, .card-title, .grid-head { display: block !important; text-align: center; text-transform: uppercase; font-size: 12px !important;
  font-weight: 700 !important; letter-spacing: .14em !important; color: #1e3a6e !important; margin: 4px 0 4px !important; padding: 4px 12px !important;
  border: none !important; border-radius: 8px !important; box-shadow: none !important;
  background: linear-gradient(90deg, rgba(92,104,136,0) 0%, rgba(92,104,136,.11) 20%, rgba(92,104,136,.11) 80%, rgba(92,104,136,0) 100%) !important; }
.card-title .pill { letter-spacing: .04em; text-transform: none; }
.chart-head + .card-desc, .card-title + .card-desc, .tbl-head .card-desc { text-align: center; margin-top: 0 !important; }
.pill { background: rgba(43,74,138,.08) !important; border: 1px solid rgba(43,74,138,.14); color: #1e3a6e !important; }
/* icy tables: pale gradient sub-header instead of solid navy; tidy group bands */
.dtab .sub th { background: linear-gradient(180deg, #f7f9fd, #e8eef9) !important; color: #1e3a6e !important; font-weight: 700 !important;
  font-size: .92em; letter-spacing: .06em; text-transform: uppercase; border-bottom: 1px solid rgba(43,74,138,.18) !important; padding-top: 5px; padding-bottom: 5px; }
.dtab td.dt { color: #1e3a6e; font-weight: 600; }
.dtab tbody tr:hover td, .tbl tbody tr:hover td { background-color: rgba(43,74,138,.06) !important; }
.tbl-wrap, .dtab { box-shadow: 0 1px 2px rgba(10,36,99,.04), 0 8px 24px rgba(10,36,99,.06) !important; }
.tbl th { font-weight: 700 !important; letter-spacing: .06em; text-transform: uppercase; font-size: .9em; border-bottom: 1px solid rgba(43,74,138,.18) !important; }
/* ── Sidebar nav (same as Daily Miner): clean vertical menu, soft navy pick, amber first item ── */
.sb-title { font-family: Plus Jakarta Sans, sans-serif; font-size: 1.9rem; font-weight: 600; color: #0a2463; }
.sb-tag { font-family: Plus Jakarta Sans, sans-serif; font-size: 11.5px; color: #8a94a8; letter-spacing: .04em; margin: -4px 0 22px 2px; }
.st-key-sb_nav div[role="radiogroup"] { background: none !important; border: 0 !important; box-shadow: none !important; padding: 0 !important;
  display: flex !important; flex-direction: column; gap: 4px; width: 100%; -webkit-backdrop-filter: none !important; backdrop-filter: none !important; }
.st-key-sb_nav div[role="radiogroup"] label { border-radius: 12px !important; padding: 10px 16px !important; width: 100%; transition: background .15s, transform .15s; }
.st-key-sb_nav div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
  font-family: Plus Jakarta Sans, sans-serif !important; font-size: 14.5px !important; font-weight: 600 !important; color: #4a5578 !important; }
.st-key-sb_nav div[role="radiogroup"] label:not(:has(input:checked)):hover { background: rgba(43,74,138,.07) !important; transform: translateX(2px); }
.st-key-sb_nav div[role="radiogroup"] label:has(input:checked) { background: linear-gradient(135deg, #2b4a8a, #1e3a6e) !important;
  box-shadow: 0 6px 16px rgba(30,58,110,.25), inset 0 1px 0 rgba(255,255,255,.18) !important; }
.st-key-sb_nav div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; }
.st-key-sb_nav div[role="radiogroup"] label:first-child { margin-bottom: 8px; position: relative; }
.st-key-sb_nav div[role="radiogroup"] label:first-child::after { content: ""; position: absolute; left: 14px; right: 14px; bottom: -7px; height: 1px; background: rgba(43,74,138,.10); }
.st-key-sb_nav div[role="radiogroup"] label:first-child div[data-testid="stMarkdownContainer"] p { color: #d9701a !important; }
.st-key-sb_nav div[role="radiogroup"] label:first-child:has(input:checked) { background: linear-gradient(135deg, #f0923a, #d9701a) !important;
  box-shadow: 0 6px 16px rgba(217,112,26,.30), inset 0 1px 0 rgba(255,255,255,.25) !important; }
.st-key-sb_nav div[role="radiogroup"] label:first-child:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; }
</style>"""
