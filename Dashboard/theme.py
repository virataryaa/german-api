"""COT_ALL (Comprehensive COT) theme, copied from LSEG/COT_ALL/Dashboard/cot_app.py, plus the few classes this app adds."""
FONT_CSS = ("<style>@import url('https://fonts.googleapis.com/css2?"
            "family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');</style>")

COT_CSS = """
<style>
  :root { color-scheme: light !important; }
  html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background:#fafafa !important; color:#1a1a2e !important;
  }
  [data-testid="stSidebar"] { background:#f0f2f8 !important; border-right:1px solid #dfe3ee; color:#1a1a2e; }
  [data-testid="stSidebarUserContent"] { padding-top:1rem !important; }
  [data-testid="stHeader"]  { background:#fafafa !important; }
  .block-container { padding-top:3.2rem !important; max-width:1600px; }
  div[data-testid="stExpander"] {
    border:1px solid #dfe3ee !important; border-radius:10px !important; background:#ffffff;
  }
  h1, h2, h3, h4, h5, h6 { color:#0a2463 !important; }
  div[role="radiogroup"] { background:#eef0f6; padding:4px; border-radius:999px; gap:2px; display:inline-flex; flex-wrap:wrap; }
  div[role="radiogroup"] label { background:transparent !important; border-radius:999px !important; padding:4px 12px !important; margin:0 !important; }
  div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child { display:none; }
  div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size:12px !important; color:#5a6688 !important; }
  div[role="radiogroup"] label:has(input:checked) { background:#0a2463 !important; }
  div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color:#ffffff !important; font-weight:600; }
  hr { border:none !important; border-top:1px solid #dfe3ee !important; margin:.5rem 0 !important; }
  [data-testid="stRadio"] label { font-size:.82rem !important; }
  h1, h2, h3, h4, h5, h6 { color: #0a2463 !important; }

  /* Pill / segmented-control tabs */
  .stTabs [data-baseweb="tab-list"] { background:#eef0f6; padding:4px; border-radius:999px; gap:4px; display:inline-flex; width:fit-content; max-width:100%; }
  .stTabs [data-baseweb="tab"] { background:transparent !important; color:#5a6688 !important; border-radius:999px !important;
      padding:8px 20px !important; font-weight:600; border:none !important; margin:0 !important; height:auto !important; }
  .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span { font-size:0.85rem !important; font-weight:600 !important; color:inherit !important; }
  .stTabs [aria-selected="true"] { background:#0a2463 !important; color:#ffffff !important; }
  .stTabs [data-baseweb="tab-highlight"] { display:none !important; }
  .stTabs [data-baseweb="tab-border"] { display:none !important; }

  /* Radio as pill / segmented control */
  div[role="radiogroup"] { background:#eef0f6; padding:4px; border-radius:999px; gap:2px; display:inline-flex; flex-wrap:wrap; }
  div[role="radiogroup"] label { background:transparent !important; border-radius:999px !important; padding:4px 12px !important; margin:0 !important; }
  div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child { display:none; }
  div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size:12px !important; color:#5a6688 !important; }
  div[role="radiogroup"] label:has(input:checked) { background:#0a2463 !important; }
  div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color:#ffffff !important; font-weight:600; }

  /* Collapsed sections: same soft row tint as the section headers, lift on hover */
  div[data-testid="stExpander"] { border:1px solid rgba(43,74,138,.10) !important; border-radius:12px !important; box-shadow:none !important;
    background:#ffffff !important; overflow:hidden; margin-bottom:8px; transition:box-shadow .18s, border-color .18s; }
  div[data-testid="stExpander"] details { border:0 !important; }
  div[data-testid="stExpander"] summary { padding:10px 14px !important;
    background:linear-gradient(90deg, rgba(43,74,138,.07) 0%, rgba(43,74,138,.025) 55%, rgba(43,74,138,0) 100%) !important; transition:background .18s; }
  div[data-testid="stExpander"] summary p {
    font-family:Plus Jakarta Sans, sans-serif !important; font-size:13.5px !important; font-weight:700 !important; color:#0a2463 !important; }
  div[data-testid="stExpander"] summary svg { color:#5a6688 !important; fill:#5a6688 !important; }
  div[data-testid="stExpander"]:hover { border-color:rgba(43,74,138,.22) !important; box-shadow:0 6px 18px rgba(10,36,99,.08) !important; }
  div[data-testid="stExpander"] summary:hover { background:linear-gradient(90deg, rgba(43,74,138,.12) 0%, rgba(43,74,138,.04) 60%, rgba(43,74,138,0) 100%) !important; }
  div[data-testid="stExpander"] summary:focus, div[data-testid="stExpander"] summary:focus-visible { outline:none !important; box-shadow:none !important; }
  div[data-testid="stExpander"] details[open] > summary { border-bottom:1px solid rgba(43,74,138,.08); }
  [class*="st-key-feat_"] { background:linear-gradient(160deg, rgba(250,252,255,.98) 0%, rgba(238,243,251,.94) 55%, rgba(228,236,249,.92) 100%);
    border:1px solid rgba(255,255,255,.95); border-radius:20px; padding:18px 22px 14px; margin:14px 0 18px;
    box-shadow:0 0 0 1px rgba(43,74,138,.10), 0 14px 40px rgba(30,58,110,.12), inset 0 1px 0 #ffffff; }
  .feat-h { display:flex; align-items:center; justify-content:center; gap:10px; margin:2px 0 12px; }
  [class*="st-key-feat_"] [data-testid="stCaptionContainer"], [class*="st-key-feat_"] [data-testid="stMarkdownContainer"] > p { text-align:center; }
  [class*="st-key-feat_"] div[role="radiogroup"] { min-height:40px; align-items:center; flex-wrap:nowrap !important; }
  [class*="st-key-feat_"] [data-testid="stNumberInput"] [data-baseweb="input"] { border-radius:12px !important; background:#ffffff !important;
    border:1px solid rgba(43,74,138,.14) !important; box-shadow:0 1px 2px rgba(10,36,99,.05); }
  [class*="st-key-feat_"] [data-testid="stNumberInput"] input { background:#ffffff !important; font-weight:600; color:#0a2463; }
  .rl-wrap { display:flex; justify-content:center; overflow-x:auto; margin-top:6px; }
  .rl-wrap table { border-collapse:separate !important; border-spacing:0; background:#ffffff; border:1px solid rgba(43,74,138,.12) !important;
    border-radius:14px; overflow:hidden; box-shadow:0 1px 2px rgba(10,36,99,.04), 0 10px 28px rgba(10,36,99,.08);
    font-family:Plus Jakarta Sans, sans-serif; font-variant-numeric:tabular-nums; }
  .rl-wrap th, .rl-wrap td { border:0 !important; border-bottom:1px solid rgba(43,74,138,.07) !important; padding:8px 11px !important; white-space:nowrap; }
  .rl-wrap thead th { background:linear-gradient(180deg,#f7f9fd,#edf2fa) !important; color:#1e3a6e !important;
    font-family:Plus Jakarta Sans, sans-serif !important; font-size:10.5px !important; font-weight:700 !important; letter-spacing:.08em; text-transform:uppercase; }
  .rl-wrap th.row_heading { color:#1e3a6e !important; font-weight:600 !important; background:#fafbfe; }
  .rl-wrap tbody tr:hover td, .rl-wrap tbody tr:hover th { background:rgba(43,74,138,.05) !important; }
  .feat-t { font-family:Plus Jakarta Sans, sans-serif; font-size:17px; font-weight:800; color:#0a2463; letter-spacing:-.01em; }
  .feat-tag { font-family:Plus Jakarta Sans, sans-serif; font-size:10px; font-weight:700; letter-spacing:.14em; text-transform:uppercase;
    color:#1e3a6e; background:rgba(255,255,255,.75); border:1px solid rgba(43,74,138,.18); border-radius:999px; padding:2px 9px; }
  .pt-head { display:flex; align-items:center; gap:12px; margin:18px 0 10px; padding:9px 14px; border-radius:12px;
    background:linear-gradient(90deg, rgba(43,74,138,.09) 0%, rgba(43,74,138,.035) 55%, rgba(43,74,138,0) 100%);
    border:1px solid rgba(43,74,138,.08); }
  .pt-title { font-family:Plus Jakarta Sans, sans-serif; font-size:14.5px; font-weight:700; color:#0a2463; letter-spacing:-.005em; }
  .pt-sub { font-weight:500; color:#7a86a8; margin-left:6px; font-size:13px; }
  .pt-meta { margin-left:auto; display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end; }
  .pt-chip { font-family:Plus Jakarta Sans, sans-serif; font-size:11px; font-weight:600; color:#5a6688; background:#ffffff;
    border:1px solid rgba(43,74,138,.14); border-radius:999px; padding:2px 10px; white-space:nowrap; font-variant-numeric:tabular-nums; }
  .cot-h { font-family:Plus Jakarta Sans, sans-serif; font-size:12.5px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:#1e3a6e; margin:22px 0 8px 2px; text-align:center; }
  /* Sidebar radios: stacked pills, like Daily Miner's selector */
  [data-testid="stSidebar"] div[role="radiogroup"] { border-radius:22px; padding:4px; gap:3px; background:#e6eaf3; }
  [data-testid="stSidebar"] div[role="radiogroup"] label { padding:6px 14px !important; }

  /* Dropdowns and multiselect: white controls, navy tags, soft pop-up */
  [data-baseweb="select"] > div { background:#ffffff !important; color:#1a1a2e !important; border-color:#dfe3ee !important; border-radius:10px !important; }
  [data-baseweb="select"] > div:focus-within { border-color:#0a2463 !important; box-shadow:0 0 0 3px rgba(10,36,99,.12) !important; }
  span[data-baseweb="tag"], span[data-baseweb="tag"] div, span[data-baseweb="tag"] span { background-color:#0a2463 !important; color:#ffffff !important; }
  span[data-baseweb="tag"] svg { fill:#ffffff !important; }
  [data-baseweb="popover"] [data-baseweb="menu"] { background:#ffffff !important; border-radius:10px !important; box-shadow:0 10px 28px rgba(10,36,99,.14) !important; }
  [data-baseweb="popover"] [data-baseweb="menu"] li, [data-baseweb="popover"] [data-baseweb="menu"] li * { color:#1a1a2e !important; }
  [data-baseweb="popover"] [data-baseweb="menu"] li:hover { background:#eef0f6 !important; }
  [data-testid="stSidebar"] input, [data-testid="stSidebar"] [data-baseweb="input"] { background:#ffffff !important; border-radius:10px !important; }

  /* Sidebar title (hero) */
  .sb-title { font-family:Plus Jakarta Sans, sans-serif; font-size:1.5rem; font-weight:600; color:#0a2463 !important; margin-bottom:2px; }
  .sb-caption { font-size:11px; color:#7a86a8 !important; margin-bottom:16px; line-height:1.4; }
  /* Sidebar polish: serif title with italic accent, small-caps labels, airy spacing, clean Rollex list */
  [data-testid="stSidebarUserContent"] { padding:1.6rem 1.35rem 2rem !important; }
  [data-testid="stSidebar"] .sb-title { font-family:Plus Jakarta Sans, sans-serif !important; font-size:1.12rem !important; font-weight:800 !important;
    text-transform:none !important; letter-spacing:-.01em; line-height:1.2; color:#0a2463 !important; margin:0 0 12px; white-space:nowrap; }
  .sb-rule { height:1px; background:rgba(43,74,138,.12); margin:0 0 20px; }
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, .sb-lbl {
    font-family:Plus Jakarta Sans, sans-serif !important; font-size:10.5px !important; font-weight:700 !important;
    letter-spacing:.14em !important; text-transform:uppercase; color:#7a86a8 !important; margin:0 0 6px 2px; }
  [data-testid="stSidebar"] .st-key-hist_decimal_toggle [data-testid="stWidgetLabel"] p { text-transform:none; letter-spacing:.01em !important; font-size:.8rem !important; color:#1e3a6e !important; }
  .sb-note { font-family:Plus Jakarta Sans, sans-serif; font-size:11px; color:#8a94a8; letter-spacing:.02em; margin:2px 0 8px 4px; font-variant-numeric:tabular-nums; }
  [data-testid="stSidebar"] hr { border-top:1px solid rgba(43,74,138,.10) !important; margin:1.1rem 0 !important; }
  [data-testid="stSidebar"] [data-testid="stElementContainer"] { margin-bottom:2px; }
  .sb-rx { width:100%; border-collapse:separate; border-spacing:0; font-family:Plus Jakarta Sans, sans-serif; font-size:12px;
    background:rgba(255,255,255,.55); border:1px solid rgba(255,255,255,.9); border-radius:12px; overflow:hidden;
    box-shadow:0 1px 2px rgba(10,36,99,.05), inset 0 1px 0 rgba(255,255,255,.9); }
  .sb-rx td { border:0 !important; border-bottom:1px solid rgba(43,74,138,.07) !important; padding:5px 12px; }
  .sb-rx tr:last-child td { border-bottom:0 !important; }
  .sb-rx td.c { font-weight:700; color:#1e3a6e; letter-spacing:.04em; width:46px; }
  .sb-rx td.d { color:#5a6688; text-align:right; font-variant-numeric:tabular-nums; }
  /* Main-area widget labels ("Include Index in spec legs?" etc.) */
  [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
    font-family:Plus Jakarta Sans, sans-serif !important; font-size:12.5px !important; font-weight:600 !important;
    color:#1e3a6e !important; letter-spacing:.01em; }
  [data-testid="stMain"] [data-testid="stCheckbox"] label p { font-family:Plus Jakarta Sans, sans-serif !important; font-weight:600 !important; color:#1e3a6e !important; }

  /* ── Ice theme, same as Daily Miner: fonts, glass sidebar, glass pill tracks, glass dropdowns, icy tables ── */
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"], [data-testid="stAppViewContainer"], .stMarkdown, button, input, textarea {
    font-family:Plus Jakarta Sans, sans-serif !important; -webkit-font-smoothing:antialiased; }
  .stTabs [data-baseweb="tab"] p, div[role="radiogroup"] label p, [data-testid="stCaptionContainer"] {
    font-family:Plus Jakarta Sans, sans-serif !important; letter-spacing:.01em; }
  [data-testid="stSidebar"] { background:linear-gradient(160deg, rgba(246,248,253,.92) 0%, rgba(233,238,248,.88) 55%, rgba(240,236,246,.9) 100%) !important;
    -webkit-backdrop-filter:blur(24px) saturate(160%); backdrop-filter:blur(24px) saturate(160%);
    border-right:1px solid rgba(255,255,255,.75) !important; box-shadow:inset -1px 0 0 rgba(10,36,99,.06), 6px 0 28px rgba(10,36,99,.06); }
  .sb-title { font-family:Plus Jakarta Sans, sans-serif; }
  /* pill tracks (tabs, radios): frosted glass, navy gradient pick, soft hover */
  div[role="radiogroup"], .stTabs [data-baseweb="tab-list"] {
    background:linear-gradient(160deg, rgba(250,252,255,.97), rgba(236,242,251,.93) 60%, rgba(229,237,249,.9)) !important;
    border:1px solid rgba(43,74,138,.14) !important; box-shadow:0 4px 16px rgba(30,58,110,.07), inset 0 1px 0 rgba(255,255,255,.95) !important; }
  div[role="radiogroup"] label:has(input:checked), .stTabs [aria-selected="true"] {
    background:linear-gradient(180deg, #2b4a8a, #1e3a6e) !important; color:#ffffff !important;
    box-shadow:0 2px 8px rgba(30,58,110,.28), inset 0 1px 0 rgba(255,255,255,.18) !important; }
  div[role="radiogroup"] label, .stTabs [data-baseweb="tab"] { transition:background .15s, transform .15s; }
  div[role="radiogroup"] label:not(:has(input:checked)):hover, .stTabs [data-baseweb="tab"]:not([aria-selected="true"]):hover { background:rgba(43,74,138,.07) !important; transform:translateY(-1px); }
  /* dropdowns: glass pill, lift on hover, burgundy focus ring + caret */
  [data-testid="stMain"] [data-baseweb="select"], [data-testid="stSidebar"] [data-baseweb="select"] { background:transparent !important; box-shadow:none !important; }
  [data-baseweb="select"] > div { background:linear-gradient(180deg, rgba(255,255,255,.78), rgba(238,242,250,.62)) !important;
    -webkit-backdrop-filter:blur(14px) saturate(170%); backdrop-filter:blur(14px) saturate(170%);
    border:1px solid rgba(255,255,255,.9) !important; border-radius:999px !important; min-height:34px;
    box-shadow:0 1px 2px rgba(10,36,99,.06), 0 6px 18px rgba(10,36,99,.08), inset 0 1px 0 rgba(255,255,255,.95); transition:box-shadow .18s, transform .18s; }
  [data-baseweb="select"] > div:hover { box-shadow:0 0 0 3px rgba(10,36,99,.07), 0 8px 22px rgba(10,36,99,.14), inset 0 1px 0 rgba(255,255,255,.95); transform:translateY(-1px); }
  [data-baseweb="select"] > div:focus-within { box-shadow:0 0 0 3px rgba(123,30,58,.16), 0 8px 22px rgba(10,36,99,.14) !important; }
  [data-baseweb="select"] svg { fill:#7b1e3a !important; }
  [data-baseweb="select"] > div:has([data-baseweb="tag"]) { border-radius:16px !important; padding:4px 6px !important; }
  [data-baseweb="tag"] { height:24px !important; margin:2px 3px !important; border-radius:8px !important; }
  [data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul {
    background:rgba(255,255,255,.82) !important; -webkit-backdrop-filter:blur(18px) saturate(170%); backdrop-filter:blur(18px) saturate(170%);
    border:1px solid rgba(255,255,255,.9) !important; border-radius:14px !important; box-shadow:0 14px 40px rgba(10,36,99,.18) !important; }
  [data-baseweb="popover"] li:hover { background:rgba(43,74,138,.07) !important; }
  [data-baseweb="popover"] li[aria-selected="true"] { background:rgba(123,30,58,.10) !important; }
  /* cards and buttons */
  div[data-testid="stExpander"] { background:#ffffff; border:1px solid #e3e7f0 !important; border-radius:14px !important; box-shadow:0 1px 3px rgba(10,36,99,.06); }
  [data-testid="stMain"] [data-testid="stPlotlyChart"] { background:#ffffff; border:1px solid rgba(43,74,138,.10);
    border-radius:18px; padding:6px 8px; overflow:hidden; box-shadow:0 1px 2px rgba(10,36,99,.04), 0 4px 14px rgba(30,58,110,.06), inset 0 1px 0 #ffffff;
    transition:box-shadow .2s; }
  [data-testid="stMain"] [data-testid="stPlotlyChart"] > div, [data-testid="stMain"] [data-testid="stPlotlyChart"] .js-plotly-plot,
  [data-testid="stMain"] [data-testid="stPlotlyChart"] .main-svg { border-radius:16px; }
  [data-testid="stMain"] [data-testid="stPlotlyChart"]:hover { box-shadow:0 1px 2px rgba(10,36,99,.05), 0 8px 20px rgba(30,58,110,.09), inset 0 1px 0 #ffffff; }
  .stButton > button, .stDownloadButton > button { border-radius:999px; border:1px solid rgba(43,74,138,.18); background:linear-gradient(180deg,#ffffff,#eef2fa);
    color:#0a2463; font-weight:600; box-shadow:0 1px 2px rgba(10,36,99,.06); transition:box-shadow .18s, transform .18s; }
  .stButton > button:hover, .stDownloadButton > button:hover { transform:translateY(-1px); box-shadow:0 8px 20px rgba(10,36,99,.14); border-color:rgba(43,74,138,.35); color:#0a2463; }
  /* icy tables: frosted card, pale gradient headers (colour bands keep their own colour), zebra rows, soft hover */
  [data-testid="stMain"] div:has(> table.rtbl) { border:1px solid rgba(43,74,138,.12); border-radius:14px; background:#ffffff; }
  [data-testid="stMain"] div:has(> table.rtbl) { box-shadow:0 1px 2px rgba(10,36,99,.04), 0 8px 24px rgba(10,36,99,.06); }
</style>
"""

# Classes used by this app's pages (card heads, KPI tiles, compact tables), in the COT type scale.
APP_CSS = """
<style>
  .card-desc { font-family:Plus Jakarta Sans, sans-serif; color:#7a86a8; font-size:12px; margin:-2px 0 8px; line-height:1.35; }
  .chart-head, .card-title { font-family:Plus Jakarta Sans, sans-serif; color:#0a2463; font-weight:700; font-size:14.5px; margin-bottom:2px; }
  [data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
    background:#ffffff; border:1px solid rgba(43,74,138,.10) !important; border-radius:18px;
    box-shadow:0 1px 2px rgba(10,36,99,.04), 0 4px 14px rgba(30,58,110,.06); }
  [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPlotlyChart"] { border:0 !important; box-shadow:none !important; padding:0 !important; }
  .kpis { display:flex; flex-wrap:wrap; gap:8px; margin:4px 0 14px; }
  .kpi { background:rgba(10,36,99,.045); border:1px solid rgba(10,36,99,.14); border-radius:10px; padding:8px 16px; min-width:140px;
         display:flex; flex-direction:column; font-family:Plus Jakarta Sans, sans-serif; }
  .kpi .l { font-size:10px; color:#7a86a8; text-transform:uppercase; letter-spacing:.08em; margin-bottom:3px; font-weight:700; }
  .kpi .v { font-size:16px; font-weight:800; color:#0a2463; font-variant-numeric:tabular-nums; }
  .kpi .s { font-size:11px; color:#7a86a8; margin-top:1px; }
  .kpi .up { color:#1f9d6f; font-weight:700; } .kpi .dn { color:#c94a4a; font-weight:700; }
  .gt { border-collapse:separate; border-spacing:0; font-family:Plus Jakarta Sans, sans-serif; font-size:11.5px; font-variant-numeric:tabular-nums;
        background:#ffffff; border:1px solid rgba(43,74,138,.12); border-radius:12px; overflow:hidden; margin:0 auto; }
  .gt th { background:linear-gradient(180deg,#f7f9fd,#edf2fa); color:#1e3a6e; font-size:10px; font-weight:700; letter-spacing:.06em;
           text-transform:uppercase; padding:6px 9px; white-space:nowrap; text-align:center; }
  .gt td { padding:3px 9px; border-bottom:1px solid rgba(43,74,138,.07); text-align:right; white-space:nowrap; color:#1a1a2e; }
  .gt td.n { text-align:left; font-weight:600; color:#0a2463; background:#fafbfe; }
  .gt td.b { font-weight:700; } .gt td.up { color:#1f9d6f; font-weight:700; } .gt td.dn { color:#c94a4a; font-weight:700; }
  .gt tr.tot td { border-top:1.5px solid rgba(43,74,138,.25); font-weight:700; background:#f5f8fc; }
  .tbl-scroll { overflow-x:auto; }
  /* Summary: last sidebar pill and its page cards in a soft wine shade, set apart from the data pages */
  .st-key-nav div[role="radiogroup"] label:last-child { margin-top:10px; position:relative; }
  .st-key-nav div[role="radiogroup"] label:last-child::before { content:""; position:absolute; left:12px; right:12px; top:-7px; height:1px; background:rgba(123,30,58,.18); }
  .st-key-nav div[role="radiogroup"] label:last-child div[data-testid="stMarkdownContainer"] p { color:#7b1e3a !important; font-weight:600; }
  .st-key-nav div[role="radiogroup"] label:last-child:has(input:checked) { background:linear-gradient(180deg,#9a2a4c,#7b1e3a) !important; }
  .st-key-nav div[role="radiogroup"] label:last-child:has(input:checked) div[data-testid="stMarkdownContainer"] p { color:#ffffff !important; }
  [class*="st-key-sum_"] { background:linear-gradient(160deg,#fdf8f9,#f8eef1) !important; border:1px solid rgba(123,30,58,.14) !important;
    border-radius:18px !important; padding:14px 18px 10px !important; box-shadow:0 4px 14px rgba(123,30,58,.06) !important; }
  [class*="st-key-sum_"] .chart-head { color:#7b1e3a !important; }
  .sb-foot { font-family:Plus Jakarta Sans, sans-serif; font-size:11px; color:#8a94a8; line-height:1.5; margin-top:14px; }
</style>
"""
