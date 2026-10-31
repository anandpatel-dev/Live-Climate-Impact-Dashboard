from pathlib import Path
import sqlite3
import calendar

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------
# Climate Impact Dashboard
# Data: local SQLite DB populated by the project's data scripts
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "climate.db"
LOGO_FILE = BASE_DIR / "assets" / "climate_logo.png"

st.set_page_config(
    page_title="Climate Impact Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEXT = {
    "English": {
        "brand": "CLIMATE / INSIGHTS",
        "title": "Climate Impact Dashboard",
        "subtitle": "Explore historical weather, rainfall, air quality and forecasts across four Indian cities.",
        "nav": "WORKSPACE",
        "overview": "Overview",
        "trends": "Climate trends",
        "air": "Air quality",
        "forecast": "Forecast",
        "guide": "Insights & guide",
        "language": "Language / भाषा",
        "city": "City",
        "date": "Historical date range",
        "overview_kicker": "CITY SNAPSHOT",
        "selected_city": "Selected city",
        "max_temp": "Latest max temperature",
        "min_temp": "Latest min temperature",
        "rain_total": "Total rainfall · selected period",
        "aqi": "Latest US AQI",
        "temp_trend": "Temperature through time",
        "rain_monthly": "Monthly rainfall",
        "city_compare": "Compare cities",
        "air_snapshot": "Latest saved air-quality snapshot",
        "forecast_preview": "Forecast outlook",
        "high": "Maximum",
        "low": "Minimum",
        "rain": "Rainfall",
        "month": "Month",
        "temperature": "Temperature (°C)",
        "rain_mm": "Rainfall (mm)",
        "city_label": "City",
        "value": "Value",
        "pm25": "PM2.5 (µg/m³)",
        "pm10": "PM10 (µg/m³)",
        "us_aqi": "US AQI",
        "date_label": "Date",
        "no_history": "No historical weather data for this city and date range.",
        "no_air": "No saved air-quality record was found for this city.",
        "no_forecast": "No forecast rows were found for this city.",
        "data_note": "Weather history is daily data. Air quality is the latest saved snapshot, not a continuous historical series. Forecasts are model predictions.",
        "trends_intro": "Use the date filter in the sidebar to explore the selected period. Monthly charts aggregate the filtered daily records.",
        "monthly_temp": "Average temperature by month",
        "yearly_temp": "Yearly average temperature",
        "yearly_rain": "Yearly rainfall",
        "daily_table": "Historical records",
        "air_intro": "Particulate concentrations are shown in µg/m³. US AQI uses the United States scale; it is not India's official National AQI.",
        "air_city_compare": "Latest saved air-quality readings by city",
        "forecast_intro": "Forecast data is separate from historical observations and may not represent a live sensor reading.",
        "forecast_temp": "Forecast temperature",
        "forecast_rain": "Forecast precipitation",
        "forecast_table": "Forecast data",
        "guide_intro": "This dashboard combines historical weather, forecast data and saved air-quality snapshots to help explore climate patterns. It describes the data; it does not prove that one factor caused another.",
        "read_title": "How to read the charts",
        "read_1": "Temperature: the line chart compares daily maximum and minimum temperature in °C.",
        "read_2": "Rainfall: bars show precipitation in millimetres (mm). The selected-period total is the sum of daily precipitation in that range.",
        "read_3": "Monthly and yearly charts aggregate available historical records; they are useful for comparing patterns, not making a forecast.",
        "read_4": "Air quality: PM2.5 and PM10 are particle concentrations. US AQI is a US-scale index and must not be described as India's official AQI.",
        "filters_title": "How to use filters",
        "filters_text": "Choose a city and date range in the left sidebar. Weather charts and historical tables update to match. Air-quality cards use the latest saved record for the selected city.",
        "coverage_title": "Data coverage & limitations",
        "source": "Sources",
        "history": "Historical period",
        "cities": "Cities",
        "records": "Daily historical records",
        "air_records": "Saved air-quality records",
        "forecast_records": "Forecast rows",
        "limitations": "The historical weather table covers the dates stored in the local database. Air-quality snapshots are sparse, so do not interpret them as a historical trend. Missing values are shown as unavailable rather than invented.",
        "updated": "Data currently stored locally",
        "no_db": "Database not found",
        "load_error": "Could not load data",
        "rain_days": "Days with rain",
        "avg_max": "Average daily maximum",
        "avg_min": "Average daily minimum",
        "temp_range": "Temperature spread",
        "period": "Selected period",
        "insight": "Quick read",
        "insight_temp": "Average maximum temperature in the selected period",
        "insight_rain": "Rainiest month in the selected period",
        "insight_air": "Latest saved US AQI",
        "not_enough": "Not enough data to calculate this insight.",
        "empty_air": "No saved readings available.",
        "mm": "mm",
        "days": "days",
    },
    "हिन्दी": {
        "brand": "जलवायु / जानकारी",
        "title": "जलवायु प्रभाव डैशबोर्ड",
        "subtitle": "चार भारतीय शहरों के ऐतिहासिक मौसम, वर्षा, वायु गुणवत्ता और पूर्वानुमान देखें।",
        "nav": "मुख्य मेनू",
        "overview": "मुख्य जानकारी",
        "trends": "जलवायु के रुझान",
        "air": "वायु गुणवत्ता",
        "forecast": "मौसम पूर्वानुमान",
        "guide": "जानकारी और उपयोग-गाइड",
        "language": "Language / भाषा",
        "city": "शहर",
        "date": "ऐतिहासिक तारीख की अवधि",
        "overview_kicker": "शहर की झलक",
        "selected_city": "चुना गया शहर",
        "max_temp": "नवीनतम अधिकतम तापमान",
        "min_temp": "नवीनतम न्यूनतम तापमान",
        "rain_total": "चुनी अवधि की कुल वर्षा",
        "aqi": "नवीनतम US AQI",
        "temp_trend": "समय के साथ तापमान",
        "rain_monthly": "मासिक वर्षा",
        "city_compare": "शहरों की तुलना",
        "air_snapshot": "वायु गुणवत्ता की नवीनतम सेव की गई रीडिंग",
        "forecast_preview": "आने वाले दिनों का पूर्वानुमान",
        "high": "अधिकतम",
        "low": "न्यूनतम",
        "rain": "वर्षा",
        "month": "महीना",
        "temperature": "तापमान (°C)",
        "rain_mm": "वर्षा (mm)",
        "city_label": "शहर",
        "value": "मान",
        "pm25": "PM2.5 (µg/m³)",
        "pm10": "PM10 (µg/m³)",
        "us_aqi": "US AQI",
        "date_label": "तारीख",
        "no_history": "इस शहर और तारीख की अवधि के लिए ऐतिहासिक मौसम डेटा नहीं है।",
        "no_air": "इस शहर के लिए वायु गुणवत्ता की सेव की गई रीडिंग नहीं मिली।",
        "no_forecast": "इस शहर के लिए पूर्वानुमान डेटा नहीं मिला।",
        "data_note": "मौसम इतिहास दैनिक डेटा है। वायु गुणवत्ता केवल नवीनतम सेव की गई रीडिंग है, लगातार ऐतिहासिक श्रृंखला नहीं। पूर्वानुमान मॉडल का अनुमान है।",
        "trends_intro": "बाईं ओर शहर और तारीख की अवधि चुनें। मासिक चार्ट चुनी गई अवधि के दैनिक डेटा से बनाए जाते हैं।",
        "monthly_temp": "महीने के अनुसार औसत तापमान",
        "yearly_temp": "वर्ष के अनुसार औसत तापमान",
        "yearly_rain": "वर्ष के अनुसार वर्षा",
        "daily_table": "ऐतिहासिक रिकॉर्ड",
        "air_intro": "PM2.5 और PM10 हवा में कणों की मात्रा µg/m³ में हैं। US AQI अमेरिकी पैमाना है, भारत का आधिकारिक National AQI नहीं।",
        "air_city_compare": "शहरों के अनुसार नवीनतम सेव की गई वायु गुणवत्ता",
        "forecast_intro": "पूर्वानुमान ऐतिहासिक अवलोकनों से अलग है और लाइव सेंसर रीडिंग होना ज़रूरी नहीं।",
        "forecast_temp": "पूर्वानुमानित तापमान",
        "forecast_rain": "पूर्वानुमानित वर्षा",
        "forecast_table": "पूर्वानुमान डेटा",
        "guide_intro": "यह डैशबोर्ड ऐतिहासिक मौसम, पूर्वानुमान और सेव की गई वायु गुणवत्ता रीडिंग को एक जगह दिखाता है। यह डेटा में पैटर्न दिखाता है, किसी कारण-परिणाम को साबित नहीं करता।",
        "read_title": "चार्ट कैसे समझें",
        "read_1": "तापमान: लाइन चार्ट दैनिक अधिकतम और न्यूनतम तापमान °C में दिखाता है।",
        "read_2": "वर्षा: बार चार्ट वर्षा को मिलीमीटर (mm) में दिखाता है। चुनी अवधि का कुल दैनिक वर्षा का योग है।",
        "read_3": "मासिक और वार्षिक चार्ट उपलब्ध ऐतिहासिक रिकॉर्ड का सार हैं; ये पैटर्न की तुलना करते हैं, पूर्वानुमान नहीं देते।",
        "read_4": "वायु गुणवत्ता: PM2.5 और PM10 कणों की मात्रा हैं। US AQI को भारत का आधिकारिक AQI नहीं कहना चाहिए।",
        "filters_title": "फ़िल्टर कैसे उपयोग करें",
        "filters_text": "बाईं ओर शहर और तारीख की अवधि चुनें। मौसम के चार्ट और ऐतिहासिक तालिका बदलेंगे। वायु गुणवत्ता चुने गए शहर की नवीनतम सेव की गई रीडिंग दिखाती है।",
        "coverage_title": "डेटा की अवधि और सीमाएँ",
        "source": "डेटा स्रोत",
        "history": "ऐतिहासिक अवधि",
        "cities": "शहर",
        "records": "दैनिक ऐतिहासिक रिकॉर्ड",
        "air_records": "सेव की गई वायु गुणवत्ता रीडिंग",
        "forecast_records": "पूर्वानुमान पंक्तियाँ",
        "limitations": "ऐतिहासिक मौसम की अवधि स्थानीय डेटाबेस में मौजूद तारीखों पर निर्भर है। वायु गुणवत्ता की रीडिंग सीमित हैं, इसलिए उन्हें ऐतिहासिक रुझान न समझें। अनुपलब्ध मानों को गढ़ने के बजाय अनुपलब्ध दिखाया जाता है।",
        "updated": "स्थानीय रूप से सेव डेटा",
        "no_db": "डेटाबेस नहीं मिला",
        "load_error": "डेटा लोड नहीं हो सका",
        "rain_days": "बारिश वाले दिन",
        "avg_max": "औसत दैनिक अधिकतम",
        "avg_min": "औसत दैनिक न्यूनतम",
        "temp_range": "तापमान का अंतर",
        "period": "चुनी अवधि",
        "insight": "त्वरित जानकारी",
        "insight_temp": "चुनी अवधि का औसत अधिकतम तापमान",
        "insight_rain": "चुनी अवधि का सबसे बरसाती महीना",
        "insight_air": "नवीनतम सेव किया गया US AQI",
        "not_enough": "यह जानकारी निकालने के लिए पर्याप्त डेटा नहीं है।",
        "empty_air": "कोई सेव की गई रीडिंग उपलब्ध नहीं है।",
        "mm": "mm",
        "days": "दिन",
    },
}


@st.cache_data(ttl=60)
def load_table(table_name: str) -> pd.DataFrame:
    allowed = {"historical_weather", "weather_forecast", "air_quality"}
    if table_name not in allowed:
        raise ValueError("Unsupported table")
    with sqlite3.connect(DB_FILE) as connection:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)


def fmt(value, decimals=1, suffix=""):
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):,.{decimals}f}{suffix}"


def safe_numeric(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def month_name(month_num, language):
    names_en = [calendar.month_name[i] for i in range(1, 13)]
    names_hi = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
                "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
    return (names_hi if language == "हिन्दी" else names_en)[int(month_num) - 1]


# ---------------------------- STYLE ----------------------------
st.markdown(
    """
    <style>
    :root { --ink:#17352f; --muted:#687d77; --teal:#0f766e; --green:#39835f; --line:#e0e9e4; --paper:#f6f8f6; }
    .stApp { background:#f3f6f4; color:var(--ink); }
    [data-testid="stMainBlockContainer"] { max-width:1600px !important; }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] { align-items:stretch; }
    [data-testid="stPlotlyChart"] { background:#fff; border:1px solid #e1e9e4; border-radius:16px; padding:.45rem .45rem .15rem; box-shadow:0 4px 18px rgba(23,53,47,.035); }
    [data-testid="stMetric"] { transition:transform .15s ease, box-shadow .15s ease; }
    [data-testid="stMetric"]:hover { transform:translateY(-2px); box-shadow:0 8px 22px rgba(23,53,47,.08); }
    [data-testid="stHeader"] { background:rgba(246,248,246,.94); }
    .block-container, [data-testid="stMainBlockContainer"] { max-width:100% !important; width:100% !important; padding-top:1.35rem !important; padding-left:2rem !important; padding-right:2rem !important; padding-bottom:3rem !important; }
    section[data-testid="stMain"] > div { max-width:100% !important; }
    [data-testid="stAppViewContainer"] > .main { width:100% !important; }
    [data-testid="stHorizontalBlock"] { gap:1.1rem; }
    [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"] { background:#ffffff; border:1px solid #e0e9e4; border-radius:14px; padding:.35rem; }
    [data-testid="stDataFrame"] { background:#ffffff; }
    h1,h2,h3 { color:var(--ink); letter-spacing:-.025em; }
    h1 { font-size:2.15rem !important; font-weight:800 !important; }
    h2 { font-size:1.38rem !important; font-weight:760 !important; }
    h3 { font-size:1.05rem !important; font-weight:720 !important; }
    p, label { color:#3e5851; }
    [data-testid="stSidebar"] { background:#17352f; border-right:1px solid #244a41; }
    [data-testid="stSidebar"] * { color:#f4f8f5; }
    [data-testid="stSidebar"] [data-baseweb="select"] div { color:#17352f !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.22rem .15rem; }
    .eyebrow { color:#0f766e; font-size:.7rem; font-weight:850; letter-spacing:.15em; text-transform:uppercase; margin-bottom:.35rem; }
    .hero { background:linear-gradient(115deg,#17352f 0%,#205b50 58%,#0f8b83 100%); color:white; border-radius:22px; padding:1.8rem 2rem; margin:.2rem 0 1.25rem; box-shadow:0 12px 30px rgba(23,53,47,.12); border:1px solid rgba(255,255,255,.12); }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color:#e0e9e4 !important; border-radius:18px !important; background:#fff; padding:1rem; }
    .hero h1 { color:white !important; margin:.15rem 0 .4rem; }
    .hero p { color:#d9eee6; margin:0; font-size:1rem; }
    .hero .eyebrow { color:#a7e4c8; }
    .hero-row { display:flex; align-items:center; gap:1rem; }
    .hero-logo { width:64px; height:64px; flex:0 0 64px; background:#ffffff; border-radius:16px; padding:7px; object-fit:contain; }
    .hero-copy { min-width:0; }
    .status-strip { display:flex; flex-wrap:wrap; gap:.55rem; margin:.55rem 0 1.1rem; clear:both; }
    .status-chip { background:#e7f3ed; color:#245d49; border:1px solid #d3e8dc; padding:.38rem .72rem; border-radius:999px; font-size:.78rem; font-weight:650; }
    div[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:16px; padding:1rem 1.1rem; box-shadow:0 5px 18px rgba(23,53,47,.035); min-height:112px; }
    div[data-testid="stMetricLabel"] { color:var(--muted); font-weight:650; }
    div[data-testid="stMetricValue"] { color:var(--ink); font-weight:820; }
    div[data-testid="stMetricDelta"] { font-size:.8rem; }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:13px; overflow:hidden; }
    [data-testid="stTabs"] button { font-weight:650; }
    .note { color:var(--muted); font-size:.84rem; }
    .small-pill { display:inline-block; border-radius:999px; padding:.28rem .65rem; background:#dff3e8; color:#205b50; font-size:.78rem; font-weight:700; }
    .stButton > button { border-radius:10px; font-weight:700; border:1px solid #cbded3; }
    .stButton > button[kind="primary"] { background:#0f766e; border-color:#0f766e; }
    hr { border-color:var(--line); }
    @media (max-width: 700px) { .hero { padding:1.15rem; } .hero-logo { width:48px;height:48px;flex-basis:48px; } h1 {font-size:1.7rem!important;} }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------- SIDEBAR ----------------------------
if LOGO_FILE.exists():
    st.sidebar.image(str(LOGO_FILE), width=154)
else:
    st.sidebar.markdown("🌿 **Climate Insights**")
st.sidebar.markdown('<div style="font-size:.68rem;letter-spacing:.15em;color:#a7e4c8!important;font-weight:800">CLIMATE ANALYTICS</div>', unsafe_allow_html=True)
if st.sidebar.button("↻ Reload saved data", width="stretch", key="sidebar_reload_saved_data", help="Reload data currently saved in the local SQLite database. This does not call the weather APIs."):
    st.cache_data.clear()
    st.rerun()
language = st.sidebar.selectbox("Language / भाषा", ["English", "हिन्दी"])
t = TEXT[language]
page = st.sidebar.radio(
    t["nav"],
    [t["overview"], t["trends"], t["air"], t["forecast"], t["guide"]],
)
st.sidebar.divider()

if not DB_FILE.exists():
    st.error(f"{t['no_db']}: {DB_FILE}")
    st.stop()

try:
    historical = load_table("historical_weather")
    forecast = load_table("weather_forecast")
    air_quality = load_table("air_quality")
except Exception as error:
    st.error(f"{t['load_error']}: {error}")
    st.stop()

if historical.empty:
    st.error(t["no_history"])
    st.stop()

if "date" not in historical.columns or "city" not in historical.columns:
    st.error("The historical_weather table is missing required columns: date and/or city.")
    st.stop()
historical["date"] = pd.to_datetime(historical["date"], errors="coerce")
historical = historical.dropna(subset=["date"]).copy()
if historical.empty:
    st.error("The historical_weather table has no valid dates. Check the historical data ingestion script.")
    st.stop()
historical["city"] = historical["city"].astype(str)
historical = safe_numeric(historical, ["max_temperature_c", "min_temperature_c", "precipitation_mm"])

if "date" in forecast.columns:
    forecast["date"] = pd.to_datetime(forecast["date"], errors="coerce")
forecast["city"] = forecast["city"].astype(str) if "city" in forecast.columns else pd.Series(dtype=str)
forecast = safe_numeric(forecast, ["max_temperature_c", "min_temperature_c", "precipitation_mm"])

if "observation_time" in air_quality.columns:
    air_quality["observation_time"] = pd.to_datetime(air_quality["observation_time"], errors="coerce")
air_quality["city"] = air_quality["city"].astype(str) if "city" in air_quality.columns else pd.Series(dtype=str)
air_quality = safe_numeric(air_quality, ["pm2_5_ug_m3", "pm10_ug_m3", "us_aqi"])

cities = sorted(historical["city"].dropna().unique().tolist())
st.sidebar.markdown(f"**{t['city']}**")
selected_city = st.sidebar.selectbox(t["city"], cities)
min_date = historical["date"].min().date()
max_date = historical["date"].max().date()
selected_dates = st.sidebar.date_input(
    t["date"], value=(min_date, max_date), min_value=min_date, max_value=max_date,
    format="YYYY-MM-DD",
)
if isinstance(selected_dates, (tuple, list)):
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = selected_dates
if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")
    st.stop()

# Show the true date coverage found in the loaded historical table, not hardcoded dates.
latest_air_fetch = None
if "fetched_at_utc" in air_quality.columns and not air_quality.empty:
    parsed_fetch = pd.to_datetime(air_quality["fetched_at_utc"], errors="coerce", utc=True).dropna()
    if not parsed_fetch.empty:
        latest_air_fetch = parsed_fetch.max().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(
    '<div class="status-strip">'
    + f'<span class="status-chip">Historical coverage: {min_date} — {max_date}</span>'
    + f'<span class="status-chip">Cities in history: {len(cities)}</span>'
    + (f'<span class="status-chip">Last air-quality fetch: {latest_air_fetch}</span>' if latest_air_fetch else '<span class="status-chip">Air-quality fetch time unavailable</span>')
    + '</div>',
    unsafe_allow_html=True,
)

history_all_cities = historical[
    historical["date"].dt.date.between(start_date, end_date)
].copy()
city_history = history_all_cities[history_all_cities["city"] == selected_city].sort_values("date").copy()
city_air = air_quality[air_quality["city"] == selected_city].sort_values("observation_time" if "observation_time" in air_quality.columns else "city").copy()
city_forecast = forecast[forecast["city"] == selected_city].sort_values("date").copy() if "date" in forecast.columns else forecast.iloc[0:0].copy()

def chart_ready(df, cols, index="date"):
    valid = [c for c in cols if c in df.columns]
    if df.empty or not valid:
        return pd.DataFrame()
    result = df.set_index(index)[valid].copy()
    return result


# Plotly helpers: consistent, readable, presentation-quality charts.
def _polish_figure(fig, height=360):
    fig.update_layout(
        template="plotly_white", height=height, autosize=True,
        margin=dict(l=12, r=18, t=24, b=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#334e48"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    bgcolor="rgba(255,255,255,0)", title_text=""),
        hoverlabel=dict(bgcolor="#17352f", font_color="#ffffff", bordercolor="#17352f"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#dce7e1", ticks="outside", tickcolor="#dce7e1")
    fig.update_yaxes(showgrid=True, gridcolor="#edf2ef", zeroline=False, linecolor="#dce7e1")
    return fig


def render_line_chart(frame, height=360, y_title=None):
    if frame is None or frame.empty:
        st.info("No data available for this chart.")
        return
    data = frame.reset_index()
    x_col = data.columns[0]
    value_cols = list(data.columns[1:])
    if not value_cols:
        st.info("No numeric values available for this chart.")
        return
    # Convert the x-axis to dates only when every value parses successfully.
    # pandas no longer supports errors="ignore" in to_datetime; categorical
    # month labels must remain strings rather than triggering a parsing error.
    if not pd.api.types.is_numeric_dtype(data[x_col]):
        parsed_x = pd.to_datetime(data[x_col], errors="coerce")
        if parsed_x.notna().all():
            data[x_col] = parsed_x
    fig = px.line(data, x=x_col, y=value_cols, markers=False,
                  color_discrete_sequence=["#0f766e", "#5aa6d1", "#7ba66b", "#e0a458"])
    for trace in fig.data:
        trace.update(line=dict(width=2.6), connectgaps=False)
    fig.update_layout(hovermode="x unified", xaxis_title=None, yaxis_title=y_title)
    fig.update_traces(hovertemplate="%{x|%d %b %Y}<br>%{fullData.name}: %{y:.1f}<extra></extra>")
    st.plotly_chart(_polish_figure(fig, height), width="stretch", config={"displayModeBar": False, "responsive": True})


def render_bar_chart(frame, height=340, y_title=None):
    if frame is None or frame.empty:
        st.info("No data available for this chart.")
        return
    data = frame.reset_index()
    x_col = data.columns[0]
    value_cols = list(data.columns[1:])
    if not value_cols:
        st.info("No numeric values available for this chart.")
        return
    if len(value_cols) > 1:
        fig = px.bar(data, x=x_col, y=value_cols, barmode="group",
                     color_discrete_sequence=["#0f766e", "#8fc5e8", "#82a879", "#e0a458"])
    else:
        fig = px.bar(data, x=x_col, y=value_cols[0],
                     color_discrete_sequence=["#168477"])
        fig.update_traces(marker_line_width=0, opacity=0.94,
                          hovertemplate="%{x}<br>%{y:,.1f}<extra></extra>")
    fig.update_layout(xaxis_title=None, yaxis_title=y_title, bargap=0.28)
    st.plotly_chart(_polish_figure(fig, height), width="stretch", config={"displayModeBar": False, "responsive": True})

# ---------------------------- HERO ----------------------------
hero = st.container(border=True)
with hero:
    hero_logo, hero_text = st.columns([0.12, 0.88], vertical_alignment="center", gap="large")
    with hero_logo:
        if LOGO_FILE.exists():
            st.image(str(LOGO_FILE), width=100)
        else:
            st.markdown("🌿")
    with hero_text:
        st.markdown(f'<div class="eyebrow">{t["brand"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<h1 style="margin:0 0 .35rem 0;color:#17352f">{t["title"]}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin:0;color:#536b64;font-size:1.02rem">{t["subtitle"]}</p>', unsafe_allow_html=True)

# ---------------------------- OVERVIEW ----------------------------
if page == t["overview"]:
    st.markdown(f'<div class="eyebrow">{t["overview_kicker"]}</div>', unsafe_allow_html=True)
    st.subheader(f"{selected_city} · {start_date} — {end_date}")
    if not city_history.empty:
        latest = city_history.iloc[-1]
        avg_max = city_history["max_temperature_c"].mean()
        avg_min = city_history["min_temperature_c"].mean()
        rain_total = city_history["precipitation_mm"].sum()
        rain_days = int((city_history["precipitation_mm"].fillna(0) > 0).sum())
    else:
        latest = pd.Series(dtype=object)
        avg_max = avg_min = rain_total = float("nan")
        rain_days = 0
    city_air_latest = city_air.iloc[-1] if not city_air.empty else pd.Series(dtype=object)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t["max_temp"], fmt(latest.get("max_temperature_c"), 1, " °C"), help=t["data_note"])
    m2.metric(t["min_temp"], fmt(latest.get("min_temperature_c"), 1, " °C"), help=t["data_note"])
    m3.metric(t["rain_total"], fmt(rain_total, 1, " mm"), help=t["data_note"])
    m4.metric(t["aqi"], fmt(city_air_latest.get("us_aqi"), 0), help=t["data_note"])
    st.caption(t["data_note"])

    left, right = st.columns([1.65, 1])
    with left:
        st.subheader(t["temp_trend"])
        if city_history.empty:
            st.info(t["no_history"])
        else:
            temp = city_history.set_index("date")[["max_temperature_c", "min_temperature_c"]].rename(
                columns={"max_temperature_c": t["high"] + " (°C)", "min_temperature_c": t["low"] + " (°C)"}
            )
            render_line_chart(temp, height=330)
    with right:
        st.subheader(t["rain_monthly"])
        if city_history.empty:
            st.info(t["no_history"])
        else:
            monthly_rain = city_history.assign(month=city_history["date"].dt.to_period("M").dt.to_timestamp()).groupby("month")["precipitation_mm"].sum().to_frame(t["rain_mm"])
            render_bar_chart(monthly_rain, height=330)

    st.divider()
    st.subheader(t["city_compare"])
    if not history_all_cities.empty:
        compare = history_all_cities.groupby("city").agg(
            average_max=("max_temperature_c", "mean"),
            average_min=("min_temperature_c", "mean"),
            total_rain=("precipitation_mm", "sum"),
        ).reset_index().rename(columns={
            "city": t["city_label"],
            "average_max": t["high"] + " (°C)",
            "average_min": t["low"] + " (°C)",
            "total_rain": t["rain_mm"],
        })
        st.caption(t["period"] + f": {start_date} — {end_date}")
        st.dataframe(compare, width="stretch", hide_index=True)
        compare_chart = compare.set_index(t["city_label"])[[t["high"] + " (°C)", t["low"] + " (°C)"]]
        render_bar_chart(compare_chart, height=280)
    else:
        st.info(t["no_history"])

    st.divider()
    air_left, air_right = st.columns([1, 1])
    with air_left:
        st.subheader(t["air_snapshot"])
        if not city_air.empty:
            display_cols = [c for c in ["observation_time", "pm2_5_ug_m3", "pm10_ug_m3", "us_aqi"] if c in city_air.columns]
            air_display = city_air[display_cols].tail(1).rename(columns={
                "observation_time": t["date_label"],
                "pm2_5_ug_m3": t["pm25"],
                "pm10_ug_m3": t["pm10"],
                "us_aqi": t["us_aqi"],
            })
            st.dataframe(air_display, width="stretch", hide_index=True)
        else:
            st.info(t["no_air"])
    with air_right:
        st.subheader(t["forecast_preview"])
        if not city_forecast.empty:
            fc = city_forecast.head(7).copy()
            fc = fc[[c for c in ["date", "max_temperature_c", "min_temperature_c", "precipitation_mm"] if c in fc.columns]].rename(columns={
                "date": t["date_label"],
                "max_temperature_c": t["high"] + " (°C)",
                "min_temperature_c": t["low"] + " (°C)",
                "precipitation_mm": t["rain_mm"],
            })
            st.dataframe(fc, width="stretch", hide_index=True)
        else:
            st.info(t["no_forecast"])

# ---------------------------- CLIMATE TRENDS ----------------------------
elif page == t["trends"]:
    st.subheader(t["trends"] + f" · {selected_city}")
    st.write(t["trends_intro"])
    if city_history.empty:
        st.info(t["no_history"])
    else:
        tab1, tab2, tab3 = st.tabs([t["temp_trend"], t["rain_monthly"], t["daily_table"]])
        with tab1:
            temp = city_history.set_index("date")[["max_temperature_c", "min_temperature_c"]].rename(
                columns={"max_temperature_c": t["high"] + " (°C)", "min_temperature_c": t["low"] + " (°C)"}
            )
            render_line_chart(temp, height=400)
            monthly = city_history.assign(month=city_history["date"].dt.month).groupby("month").agg(
                max_temperature_c=("max_temperature_c", "mean"),
                min_temperature_c=("min_temperature_c", "mean"),
            ).reindex(range(1, 13)).dropna(how="all").reset_index()
            if not monthly.empty:
                monthly["Month"] = monthly["month"].map(lambda m: month_name(m, language))
                monthly = monthly.set_index("Month")[["max_temperature_c", "min_temperature_c"]].rename(
                    columns={"max_temperature_c": t["high"] + " (°C)", "min_temperature_c": t["low"] + " (°C)"}
                )
                st.subheader(t["monthly_temp"])
                render_line_chart(monthly, height=300)
            yearly = city_history.assign(year=city_history["date"].dt.year).groupby("year").agg(
                max_temperature_c=("max_temperature_c", "mean"),
                min_temperature_c=("min_temperature_c", "mean"),
            ).rename(columns={"max_temperature_c": t["high"] + " (°C)", "min_temperature_c": t["low"] + " (°C)"})
            st.subheader(t["yearly_temp"])
            render_bar_chart(yearly, height=300)
        with tab2:
            monthly_rain = city_history.assign(month=city_history["date"].dt.to_period("M").dt.to_timestamp()).groupby("month")["precipitation_mm"].sum().to_frame(t["rain_mm"])
            render_bar_chart(monthly_rain, height=400)
            yearly_rain = city_history.assign(year=city_history["date"].dt.year).groupby("year")["precipitation_mm"].sum().to_frame(t["rain_mm"])
            st.subheader(t["yearly_rain"])
            render_bar_chart(yearly_rain, height=300)
            st.metric(t["rain_days"], f"{int((city_history['precipitation_mm'].fillna(0) > 0).sum())} {t['days']}")
        with tab3:
            display = city_history.sort_values("date", ascending=False).rename(columns={
                "date": t["date_label"],
                "max_temperature_c": t["high"] + " (°C)",
                "min_temperature_c": t["low"] + " (°C)",
                "precipitation_mm": t["rain_mm"],
            })
            st.dataframe(display, width="stretch", hide_index=True)
    st.caption(t["data_note"])

# ---------------------------- AIR QUALITY ----------------------------
elif page == t["air"]:
    st.subheader(t["air"] + f" · {selected_city}")
    st.write(t["air_intro"])
    if city_air.empty:
        st.info(t["no_air"])
    else:
        latest_air = city_air.iloc[-1]
        a1, a2, a3 = st.columns(3)
        a1.metric(t["pm25"], fmt(latest_air.get("pm2_5_ug_m3"), 1))
        a2.metric(t["pm10"], fmt(latest_air.get("pm10_ug_m3"), 1))
        a3.metric(t["us_aqi"], fmt(latest_air.get("us_aqi"), 0))
        if "observation_time" in city_air.columns:
            st.caption(t["date_label"] + ": " + str(latest_air.get("observation_time")))
        st.subheader(t["air_city_compare"])
        latest_by_city = air_quality.sort_values("observation_time" if "observation_time" in air_quality.columns else "city").groupby("city", as_index=False).tail(1)
        available = [c for c in ["pm2_5_ug_m3", "pm10_ug_m3"] if c in latest_by_city.columns]
        if available:
            air_chart = latest_by_city.set_index("city")[available].rename(columns={
                "pm2_5_ug_m3": "PM2.5 (µg/m³)",
                "pm10_ug_m3": "PM10 (µg/m³)",
            })
            render_bar_chart(air_chart, height=350)
        if "us_aqi" in latest_by_city.columns:
            aqi_chart = latest_by_city.set_index("city")[["us_aqi"]].rename(columns={"us_aqi": "US AQI"})
            render_bar_chart(aqi_chart, height=300)
        display_cols = [c for c in ["city", "observation_time", "pm2_5_ug_m3", "pm10_ug_m3", "us_aqi"] if c in latest_by_city.columns]
        st.dataframe(latest_by_city[display_cols].rename(columns={
            "city": t["city_label"], "observation_time": t["date_label"],
            "pm2_5_ug_m3": t["pm25"], "pm10_ug_m3": t["pm10"], "us_aqi": t["us_aqi"]
        }), width="stretch", hide_index=True)
    st.caption(t["data_note"])

# ---------------------------- FORECAST ----------------------------
elif page == t["forecast"]:
    st.subheader(t["forecast"] + f" · {selected_city}")
    st.write(t["forecast_intro"])
    if city_forecast.empty:
        st.info(t["no_forecast"])
    else:
        fc = city_forecast.dropna(subset=["date"]).sort_values("date").head(14).copy()
        if not fc.empty:
            fc["date"] = pd.to_datetime(fc["date"])
            temp_cols = [c for c in ["max_temperature_c", "min_temperature_c"] if c in fc.columns]
            if temp_cols:
                temp_chart = fc.set_index("date")[temp_cols].rename(columns={
                    "max_temperature_c": t["high"] + " (°C)",
                    "min_temperature_c": t["low"] + " (°C)",
                })
                st.subheader(t["forecast_temp"])
                render_line_chart(temp_chart, height=350)
            if "precipitation_mm" in fc.columns:
                st.subheader(t["forecast_rain"])
                render_bar_chart(fc.set_index("date")[["precipitation_mm"]].rename(columns={"precipitation_mm": t["rain_mm"]}), height=280)
            st.subheader(t["forecast_table"])
            display = fc[[c for c in ["date", "max_temperature_c", "min_temperature_c", "precipitation_mm"] if c in fc.columns]].rename(columns={
                "date": t["date_label"],
                "max_temperature_c": t["high"] + " (°C)",
                "min_temperature_c": t["low"] + " (°C)",
                "precipitation_mm": t["rain_mm"],
            })
            st.dataframe(display, width="stretch", hide_index=True)
    st.caption(t["data_note"])

# ---------------------------- INSIGHTS & GUIDE ----------------------------
elif page == t["guide"]:
    st.subheader(t["guide"])
    st.write(t["guide_intro"])
    if not city_history.empty:
        st.markdown(f'<div class="eyebrow">{t["insight"]}</div>', unsafe_allow_html=True)
        i1, i2, i3 = st.columns(3)
        i1.metric(t["insight_temp"], fmt(city_history["max_temperature_c"].mean(), 1, " °C"))
        monthly_rain = city_history.assign(month=city_history["date"].dt.to_period("M")).groupby("month")["precipitation_mm"].sum()
        if not monthly_rain.empty and monthly_rain.notna().any():
            rainiest = monthly_rain.idxmax()
            i2.metric(t["insight_rain"], f"{month_name(rainiest.month, language)} {rainiest.year}")
        else:
            i2.metric(t["insight_rain"], "—")
        latest_air = city_air.iloc[-1] if not city_air.empty else pd.Series(dtype=object)
        i3.metric(t["insight_air"], fmt(latest_air.get("us_aqi"), 0))
    else:
        st.info(t["not_enough"])

    st.divider()
    st.subheader(t["read_title"])
    st.markdown(f"- {t['read_1']}\n- {t['read_2']}\n- {t['read_3']}\n- {t['read_4']}")
    st.subheader(t["filters_title"])
    st.write(t["filters_text"])
    st.subheader(t["coverage_title"])
    hist_start = historical["date"].min().date()
    hist_end = historical["date"].max().date()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t["history"], f"{hist_start} – {hist_end}")
    c2.metric(t["cities"], str(historical["city"].nunique()))
    c3.metric(t["records"], f"{len(historical):,}")
    c4.metric(t["air_records"], f"{len(air_quality):,}")
    st.write(f"**{t['source']}:** Open-Meteo Historical Archive, Open-Meteo Forecast data stored in the project database, and Open-Meteo Air Quality API.")
    st.info(t["limitations"])

st.divider()
st.caption("Climate Impact Dashboard · Python · Streamlit · Pandas · SQLite | Data is shown from the local database; automatic API scheduling is configured separately.")
