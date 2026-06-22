import streamlit as st
import pandas as pd
import pydeck as pdk

TA_RED = "#CC0000"
TA_DARK = "#1B1B1B"

st.set_page_config(
    page_title="TravelCenters of America | Site Map",
    page_icon=":material/local_gas_station:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(f"""
<div style="background: {TA_DARK}; padding: 16px 24px; border-radius: 8px; margin-bottom: 16px; display: flex; align-items: center; gap: 16px;">
    <div style="background: {TA_RED}; width: 8px; height: 40px; border-radius: 4px;"></div>
    <div>
        <div style="font-size: 22px; font-weight: 700; color: white; letter-spacing: -0.5px;">TravelCenters of America</div>
        <div style="font-size: 13px; color: #aaa; margin-top: 2px;">Site Ownership Map &middot; COCO vs Franchise</div>
    </div>
</div>
""", unsafe_allow_html=True)


@st.cache_data
def load_sites():
    return pd.read_csv("sites.csv")


df = load_sites()

ownership_filter = st.segmented_control(
    "Filter by ownership",
    options=["All", "COCO", "Franchise"],
    default="All",
)

if ownership_filter == "COCO":
    filtered = df[df["OWNERSHIP"] == "COCO"]
elif ownership_filter == "Franchise":
    filtered = df[df["OWNERSHIP"] == "Franchise"]
else:
    filtered = df

with st.popover("More filters", use_container_width=True):
    brands = sorted(filtered["BRAND_CD"].dropna().unique().tolist())
    selected_brands = st.multiselect("Brand", brands, default=brands)

    states = sorted(filtered["STATE_TXT"].dropna().unique().tolist())
    selected_states = st.multiselect("State", states, default=states)

    filtered = filtered[
        (filtered["BRAND_CD"].isin(selected_brands))
        & (filtered["STATE_TXT"].isin(selected_states))
    ]

coco_n = len(filtered[filtered["OWNERSHIP"] == "COCO"])
fran_n = len(filtered[filtered["OWNERSHIP"] == "Franchise"])

col1, col2, col3 = st.columns(3)
col1.metric("Total", len(filtered), border=True)
col2.metric("COCO", coco_n, border=True)
col3.metric("Franchise", fran_n, border=True)

map_data = filtered.copy()
color_map = {
    "COCO": [204, 0, 0],
    "Franchise": [30, 136, 229],
    "Other": [158, 158, 158],
}
map_data["color"] = map_data["OWNERSHIP"].map(color_map)

view_state = pdk.ViewState(
    latitude=38.5,
    longitude=-96.0,
    zoom=3.5,
    pitch=0,
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position=["LON", "LAT"],
    get_fill_color="color",
    get_radius=15000,
    pickable=True,
    auto_highlight=True,
    highlight_color=[255, 215, 0, 180],
)

tooltip = {
    "html": """
        <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 12px 14px; max-width: 280px;">
            <div style="font-weight: 700; font-size: 15px; margin-bottom: 2px;">{LOCATION_NM}</div>
            <div style="font-size: 11px; color: #aaa; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">Site {LOCATION_ID} &middot; {OWNERSHIP} &middot; {BRAND_CD}</div>
            <div style="font-size: 12px; line-height: 1.7; border-top: 1px solid #333; padding-top: 8px;">
                {ADDRESS_TXT}<br/>
                {CITY_TXT}, {STATE_TXT} {ZIP_CD}<br/>
                <span style="color: #aaa;">Region:</span> {REGION_TXT} &middot; {DISTRICT_TXT}
            </div>
            <div style="font-size: 12px; line-height: 1.7; border-top: 1px solid #333; padding-top: 8px; margin-top: 8px;">
                <span style="color: #aaa;">Gas:</span> {GAS_BRAND_TXT}<br/>
                <span style="color: #aaa;">Restaurant:</span> {FSR_NM}
            </div>
        </div>
    """,
    "style": {
        "backgroundColor": "#111111",
        "color": "#ffffff",
        "border-radius": "10px",
        "border": "1px solid #333",
        "padding": "0",
        "box-shadow": "0 4px 20px rgba(0,0,0,0.5)",
    },
}

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="road",
    ),
    use_container_width=True,
    height=520,
)

st.markdown(f"""
<div style="display: flex; gap: 16px; align-items: center; padding: 8px 0; font-size: 12px; color: #888;">
    <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{TA_RED};margin-right:4px;"></span>COCO</span>
    <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#1E88E5;margin-right:4px;"></span>Franchise</span>
    <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#9E9E9E;margin-right:4px;"></span>Other</span>
    <span style="margin-left: auto;">Tap a site for details</span>
</div>
""", unsafe_allow_html=True)

with st.expander(f"Site list ({len(filtered)})", expanded=False):
    search = st.text_input("Search", placeholder="Site name or city...", label_visibility="collapsed")
    display = filtered
    if search:
        search_lower = search.lower()
        display = filtered[
            filtered["LOCATION_NM"].str.lower().str.contains(search_lower, na=False)
            | filtered["CITY_TXT"].str.lower().str.contains(search_lower, na=False)
        ]

    st.dataframe(
        display[["LOCATION_ID", "LOCATION_NM", "BRAND_CD", "OWNERSHIP",
                 "CITY_TXT", "STATE_TXT", "FSR_NM", "GAS_BRAND_TXT"]].reset_index(drop=True),
        hide_index=True,
        column_config={
            "LOCATION_ID": st.column_config.NumberColumn("Site #", format="%d"),
            "LOCATION_NM": "Name",
            "BRAND_CD": "Brand",
            "OWNERSHIP": "Type",
            "CITY_TXT": "City",
            "STATE_TXT": "State",
            "FSR_NM": "Restaurant",
            "GAS_BRAND_TXT": "Gas Brand",
        },
    )
