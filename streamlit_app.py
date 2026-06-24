import streamlit as st
import pandas as pd
import pydeck as pdk

TA_RED = "#CC0000"
TA_DARK = "#1B1B1B"

st.set_page_config(
    page_title="TA Site Map",
    page_icon=":material/local_gas_station:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS: hide Streamlit chrome, full-bleed layout ──────────────────────
st.markdown("""
<style>
  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .stAppDeployButton { display: none; }

  /* Remove all default padding so map goes edge-to-edge */
  .main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
  }
  section[data-testid="stMain"] > div { padding: 0 !important; }

  /* Floating top bar */
  .top-bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 1000;
    padding: 10px 12px 6px 12px;
    background: linear-gradient(to bottom, rgba(17,17,17,0.98) 70%, transparent);
    pointer-events: none;
  }
  .top-bar > * { pointer-events: auto; }

  /* App title */
  .app-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }
  .app-title .bar {
    width: 5px; height: 28px;
    background: #CC0000;
    border-radius: 3px;
    flex-shrink: 0;
  }
  .app-title .text {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.3px;
    line-height: 1.2;
  }
  .app-title .sub {
    font-size: 11px;
    color: #888;
    font-weight: 400;
  }

  /* Metric pills */
  .metrics-row {
    display: flex;
    gap: 6px;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }
  .metric-pill {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 12px;
    font-weight: 600;
    padding: 5px 10px;
    border-radius: 20px;
    color: #fff;
    white-space: nowrap;
  }
  .metric-pill.total { background: #2C2C2E; border: 1px solid #3A3A3C; }
  .metric-pill.coco  { background: rgba(204,0,0,0.25); border: 1px solid #CC0000; }
  .metric-pill.fran  { background: rgba(30,136,229,0.2); border: 1px solid #1E88E5; }

  /* Filter chips */
  .filter-chips {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    padding-bottom: 2px;
  }
  .filter-chips::-webkit-scrollbar { display: none; }

  /* Legend bar at bottom */
  .legend-bar {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    z-index: 1000;
    background: rgba(17,17,17,0.95);
    border-top: 1px solid #2C2C2E;
    padding: 8px 16px 12px 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 12px;
    color: #aaa;
  }
  .legend-dot {
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
  }
  .legend-hint {
    margin-left: auto;
    font-size: 11px;
    color: #555;
  }

  /* Streamlit widget overrides — filter chips style */
  div[data-testid="stSegmentedControl"] {
    background: transparent !important;
  }
  div[data-testid="stSegmentedControl"] button {
    background: #2C2C2E !important;
    color: #ccc !important;
    border: 1px solid #3A3A3C !important;
    border-radius: 20px !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
    min-height: 34px !important;
  }
  div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background: #CC0000 !important;
    color: #fff !important;
    border-color: #CC0000 !important;
  }

  /* Site list panel */
  .site-list-panel {
    background: #1C1C1E;
    border-radius: 16px 16px 0 0;
    padding: 16px;
    margin-top: 4px;
  }
  .site-row {
    display: flex;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #2C2C2E;
    gap: 12px;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  }
  .site-row:last-child { border-bottom: none; }
  .site-dot {
    width: 12px; height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .site-name {
    font-size: 14px;
    font-weight: 600;
    color: #fff;
    line-height: 1.3;
  }
  .site-meta {
    font-size: 12px;
    color: #888;
    margin-top: 1px;
  }
  .site-badge {
    margin-left: auto;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 10px;
    white-space: nowrap;
  }
  .badge-coco { background: rgba(204,0,0,0.2); color: #FF6B6B; border: 1px solid rgba(204,0,0,0.4); }
  .badge-fran { background: rgba(30,136,229,0.2); color: #64B5F6; border: 1px solid rgba(30,136,229,0.4); }
  .badge-other { background: rgba(158,158,158,0.2); color: #aaa; border: 1px solid rgba(158,158,158,0.3); }

  /* Search input */
  div[data-testid="stTextInput"] input {
    background: #2C2C2E !important;
    border: 1px solid #3A3A3C !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-size: 15px !important;
    padding: 10px 14px !important;
  }
  div[data-testid="stTextInput"] input::placeholder { color: #666 !important; }
  div[data-testid="stTextInput"] label { display: none !important; }

  /* Expander */
  div[data-testid="stExpander"] {
    background: #1C1C1E !important;
    border: 1px solid #2C2C2E !important;
    border-radius: 16px !important;
  }
  div[data-testid="stExpander"] summary {
    color: #fff !important;
    font-size: 15px !important;
    font-weight: 600 !important;
  }

  /* Map spacer — push content below fixed top bar */
  .map-spacer { height: 130px; }
  .bottom-spacer { height: 48px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_sites():
    return pd.read_csv("sites.csv")


df = load_sites()

# ── Session state defaults ─────────────────────────────────────────────────────
if "ownership" not in st.session_state:
    st.session_state.ownership = "All"

# ── Top bar: title + metrics + ownership filter ────────────────────────────────
st.markdown('<div class="map-spacer"></div>', unsafe_allow_html=True)

# Ownership filter (rendered first so it affects metrics)
ownership_filter = st.segmented_control(
    "Ownership",
    options=["All", "COCO", "Franchise"],
    default="All",
    key="ownership",
    label_visibility="collapsed",
)

if ownership_filter == "COCO":
    filtered = df[df["OWNERSHIP"] == "COCO"]
elif ownership_filter == "Franchise":
    filtered = df[df["OWNERSHIP"] == "Franchise"]
else:
    filtered = df

coco_n = len(filtered[filtered["OWNERSHIP"] == "COCO"])
fran_n = len(filtered[filtered["OWNERSHIP"] == "Franchise"])
total_n = len(filtered)

# Floating top bar HTML
st.markdown(f"""
<div class="top-bar">
  <div class="app-title">
    <div class="bar"></div>
    <div class="text">TravelCenters of America<br><span class="sub">Site Ownership Map</span></div>
  </div>
  <div class="metrics-row">
    <span class="metric-pill total">&#9679; {total_n} Sites</span>
    <span class="metric-pill coco">&#9679; {coco_n} COCO</span>
    <span class="metric-pill fran">&#9679; {fran_n} Franchise</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Map ────────────────────────────────────────────────────────────────────────
map_data = filtered.copy()
color_map = {
    "COCO": [204, 0, 0, 220],
    "Franchise": [30, 136, 229, 220],
    "Fo-Fo": [255, 152, 0, 220],
    "Other": [158, 158, 158, 200],
}
map_data["color"] = map_data["OWNERSHIP"].map(lambda x: color_map.get(x, [158, 158, 158, 200]))

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position=["LON", "LAT"],
    get_fill_color="color",
    get_radius=18000,
    radius_min_pixels=5,
    radius_max_pixels=18,
    pickable=True,
    auto_highlight=True,
    highlight_color=[255, 215, 0, 200],
)

tooltip = {
    "html": """
        <div style="font-family:-apple-system,BlinkMacSystemFont,sans-serif;padding:14px 16px;max-width:300px;min-width:220px;">
            <div style="font-weight:700;font-size:16px;margin-bottom:3px;color:#fff;">{LOCATION_NM}</div>
            <div style="font-size:11px;color:#888;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.6px;">
                Site {LOCATION_ID} &nbsp;·&nbsp; {BRAND_CD} &nbsp;·&nbsp;
                <span style="color:{OWNERSHIP_COLOR}">{OWNERSHIP}</span>
            </div>
            <div style="font-size:13px;line-height:1.8;border-top:1px solid #2C2C2E;padding-top:10px;">
                {ADDRESS_TXT}<br/>
                {CITY_TXT}, {STATE_TXT} {ZIP_CD}
            </div>
            <div style="font-size:12px;line-height:1.8;border-top:1px solid #2C2C2E;padding-top:8px;margin-top:8px;color:#aaa;">
                <span style="color:#666;">Gas:</span> {GAS_BRAND_TXT}<br/>
                <span style="color:#666;">Restaurant:</span> {FSR_NM}<br/>
                <span style="color:#666;">Region:</span> {REGION_TXT}
            </div>
        </div>
    """,
    "style": {
        "backgroundColor": "#1C1C1E",
        "color": "#ffffff",
        "borderRadius": "14px",
        "border": "1px solid #3A3A3C",
        "boxShadow": "0 8px 32px rgba(0,0,0,0.7)",
        "padding": "0",
    },
}

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=38.5,
            longitude=-96.0,
            zoom=3.5,
            pitch=0,
        ),
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v11",
    ),
    use_container_width=True,
    height=480,
)

# ── Legend bar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="legend-bar">
  <span><span class="legend-dot" style="background:#CC0000;"></span>COCO</span>
  <span><span class="legend-dot" style="background:#1E88E5;"></span>Franchise</span>
  <span><span class="legend-dot" style="background:#9E9E9E;"></span>Other</span>
  <span class="legend-hint">Tap a site for details</span>
</div>
<div class="bottom-spacer"></div>
""", unsafe_allow_html=True)

# ── Site list ──────────────────────────────────────────────────────────────────
with st.expander(f"Browse all sites  ({total_n})", expanded=False):
    search = st.text_input("Search", placeholder="Search by name, city, or state...")

    display = filtered
    if search:
        q = search.lower()
        display = filtered[
            filtered["LOCATION_NM"].str.lower().str.contains(q, na=False)
            | filtered["CITY_TXT"].str.lower().str.contains(q, na=False)
            | filtered["STATE_TXT"].str.lower().str.contains(q, na=False)
        ]

    badge_class = {"COCO": "badge-coco", "Franchise": "badge-fran"}

    rows_html = ""
    for _, row in display.sort_values("STATE_TXT").iterrows():
        bc = badge_class.get(row["OWNERSHIP"], "badge-other")
        dot_color = "#CC0000" if row["OWNERSHIP"] == "COCO" else "#1E88E5" if row["OWNERSHIP"] == "Franchise" else "#9E9E9E"
        restaurant = row["FSR_NM"] if pd.notna(row["FSR_NM"]) and str(row["FSR_NM"]).strip() else ""
        meta = f"{row['CITY_TXT']}, {row['STATE_TXT']}"
        if restaurant:
            meta += f" · {restaurant}"
        rows_html += f"""
        <div class="site-row">
          <div class="site-dot" style="background:{dot_color};"></div>
          <div>
            <div class="site-name">{row['LOCATION_NM']}</div>
            <div class="site-meta">{meta}</div>
          </div>
          <span class="site-badge {bc}">{row['OWNERSHIP']}</span>
        </div>"""

    st.markdown(f'<div class="site-list-panel">{rows_html}</div>', unsafe_allow_html=True)
