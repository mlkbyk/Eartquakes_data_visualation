import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 0. STREAMLIT ÇEKİRDEK AÇIK TEMA KONFİGÜRASYONU ---
os.makedirs(".streamlit", exist_ok=True)
config_path = os.path.join(".streamlit", "config.toml")
if not os.path.exists(config_path):
    with open(config_path, "w", encoding="utf-8") as f:
        f.write('[theme]\nbase="light"\nprimaryColor="#0284c7"\nbackgroundColor="#f4f7fb"\nsecondaryBackgroundColor="#ffffff"\ntextColor="#0f172a"\n')

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="SEISMOSCOPE | Earthquake Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- YARDIMCI FONKSİYON: KLASÖRLERDE DOSYA BULUCU ---
def find_file(filename):
    for root, dirs, files in os.walk("."):
        if filename in files:
            return os.path.join(root, filename)
    return None

# --- 2. VERİ YÜKLEME (prepare_data.py SÜTUNLARIYLA TAM UYUMLU) ---
@st.cache_data
def load_data():
    csv_path = find_file("earthquakes_dashboard_ready.csv")
    scored_path = find_file("ml_scored_events.csv")
    is_mock = False

    if csv_path:
        df = pd.read_csv(csv_path)
    elif scored_path:
        df = pd.read_csv(scored_path)
    else:
        is_mock = True
        np.random.seed(42)
        n = 1500
        df = pd.DataFrame({
            'time': pd.date_range('2023-02-01', '2024-05-31', periods=n),
            'latitude': np.random.uniform(-60, 70, n),
            'longitude': np.random.uniform(-180, 180, n),
            'depth': np.random.exponential(60, n).clip(1, 650).round(1),
            'mag': np.random.gamma(2.2, 1.1, n).clip(4.5, 7.8).round(1),
            'magType': np.random.choice(['mww', 'mb', 'mwr', 'ml', 'md'], n, p=[0.4, 0.35, 0.15, 0.05, 0.05]),
            'magError': np.random.gamma(2.0, 0.04, n).round(3),
            'place': ['Global Seismic Zone'] * n
        })

    # Zaman sütunları (prepare_data.py: 'event_date_utc' ve 'time')
    time_candidates = ['time', 'event_date_utc', 'date', 'datetime']
    time_col = next((c for c in time_candidates if c in df.columns), df.columns[0])
    df['time_parsed'] = pd.to_datetime(df[time_col], errors='coerce', utc=True)
    
    if 'event_date_utc' in df.columns:
        df['event_date_utc'] = pd.to_datetime(df['event_date_utc'], errors='coerce')
    else:
        df['event_date_utc'] = pd.to_datetime(df['time_parsed'].dt.strftime('%Y-%m-%d'))

    df['date_only'] = df['event_date_utc'].dt.date
    df['year_month'] = df['event_date_utc'].dt.strftime('%Y-%m')

    # Yarımküre sütunu (prepare_data.py: 'latitude_hemisphere')
    hem_candidates = ['latitude_hemisphere', 'hemisphere', 'ns_hemisphere']
    found_hem = next((c for c in hem_candidates if c in df.columns), None)
    if found_hem:
        df['hemisphere_col'] = df[found_hem].astype(str)
    else:
        df['hemisphere_col'] = np.where(df['latitude'] >= 0, 'Northern', 'Southern')

    # Büyüklük kategorisi (prepare_data.py: 'magnitude_band')
    mag_cat_candidates = ['magnitude_band', 'mag_category', 'magnitude_category']
    found_mag_cat = next((c for c in mag_cat_candidates if c in df.columns), None)
    if found_mag_cat:
        df['mag_cat_col'] = df[found_mag_cat].astype(str)
    else:
        df['mag_cat_col'] = pd.cut(
            df['mag'],
            bins=[-1, 4.999, 5.999, 6.999, 10],
            labels=['M4.5–4.9', 'M5.0–5.9', 'M6.0–6.9', 'M7.0+']
        ).astype(str)

    # Derinlik kategorisi (prepare_data.py: 'depth_category')
    depth_cat_candidates = ['depth_category', 'depth_cat', 'depth_class']
    found_depth_cat = next((c for c in depth_cat_candidates if c in df.columns), None)
    if found_depth_cat:
        df['depth_cat_col'] = df[found_depth_cat].astype(str)
    else:
        df['depth_cat_col'] = pd.cut(
            df['depth'],
            bins=[-10, 69.999, 299.999, 1000],
            labels=['Shallow (<70 km)', 'Intermediate (70–299 km)', 'Deep (>=300 km)']
        ).astype(str)

    # 10 km sabit derinlik bayrağı (prepare_data.py: 'depth_exactly_10km')
    if 'depth_exactly_10km' not in df.columns:
        df['depth_exactly_10km'] = (df['depth'] == 10.0).astype(str)

    return df, is_mock

df, is_mock = load_data()

# --- 3. SIDEBAR: GÖRÜNÜM TEMASI VE KÜRESEL FİLTRELER ---
st.sidebar.markdown("## 🌍 **SEISMOSCOPE**")
st.sidebar.caption("Global Seismic Intelligence & Visual Analytics")

ui_theme = st.sidebar.radio(
    "🎨 Ekran Teması:",
    ["☀️ Ferah Açık (Sunum Önerisi)", "🌌 Yumuşak Gece Mavisi"],
    index=0
)

is_light = ui_theme.startswith("☀️")

if is_light:
    bg_main = "#f4f7fb"
    bg_card = "#ffffff"
    bg_sidebar = "#ffffff"
    input_bg = "#f8fafc"
    text_primary = "#0f172a"
    text_secondary = "#475569"
    border_col = "#cbd5e1"
    accent_col = "#0284c7"
    map_tile = "carto-positron"
    globe_ocean = "#e0f2fe"
    globe_land = "#f8fafc"
    globe_border = "#94a3b8"
    color_scale_main = "Spectral_r"
else:
    bg_main = "#0f172a"
    bg_card = "#1e293b"
    bg_sidebar = "#1e293b"
    input_bg = "#334155"
    text_primary = "#f8fafc"
    text_secondary = "#cbd5e1"
    border_col = "#475569"
    accent_col = "#38bdf8"
    map_tile = "carto-darkmatter"
    globe_ocean = "#0f172a"
    globe_land = "#1e293b"
    globe_border = "#475569"
    color_scale_main = "Turbo"

# --- KAPSAMLI CSS ---
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{
        background-color: {bg_main} !important;
        border-bottom: none !important;
    }}
    .stApp {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
    }}
    .block-container {{
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {border_col} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_primary} !important;
    }}
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    input[type="text"],
    div[data-testid="stDateInput"] div {{
        background-color: {input_bg} !important;
        color: {text_primary} !important;
        border-color: {border_col} !important;
        border-radius: 8px !important;
    }}
    div[data-baseweb="popover"] div,
    ul[data-baseweb="menu"],
    li[role="option"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
    }}
    li[role="option"]:hover {{
        background-color: {input_bg} !important;
    }}
    span[data-baseweb="tag"] {{
        background-color: {accent_col} !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }}
    span[data-baseweb="tag"] span {{
        color: #ffffff !important;
    }}
    div[data-testid="stDownloadButton"] button {{
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25) !important;
    }}
    div[data-testid="stDownloadButton"] button * {{
        color: #ffffff !important;
    }}
    .hero-banner {{
        background: linear-gradient(135deg, {bg_card} 0%, {input_bg} 100%);
        border: 1px solid {border_col};
        border-left: 6px solid {accent_col};
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05);
    }}
    div[data-testid="metric-container"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_col} !important;
        border-top: 4px solid {accent_col} !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05) !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {text_primary} !important;
        font-weight: 800 !important;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {text_secondary} !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stPlotlyChart"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_col} !important;
        border-radius: 14px !important;
        padding: 10px !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05) !important;
    }}
    button[data-baseweb="tab"] {{
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        color: {text_secondary} !important;
        padding: 10px 16px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {accent_col} !important;
    }}
    .insight-box {{
        background-color: {bg_card};
        border: 1px solid {border_col};
        border-left: 5px solid #10b981;
        border-radius: 12px;
        padding: 14px 20px;
        margin-top: 10px;
        margin-bottom: 18px;
        color: {text_primary};
        font-size: 0.95rem;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    }}
    /* Üye 2 Bilimsel Açıklama Kartı */
    .sci-card {{
        background-color: {bg_card};
        border: 1px solid {border_col};
        border-top: 4px solid #0d9488;
        border-radius: 12px;
        padding: 16px;
        color: {text_primary};
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }}
    .sci-note {{
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px dashed {border_col};
        font-size: 0.88rem;
        color: {text_secondary};
    }}
    </style>
""", unsafe_allow_html=True)

# Üye 2 Bilimsel Bilgi Kartı Bileşeni (preview_statistical.py -> show_insight)
def show_scientific_card(main_text: str, note_text: str):
    st.markdown(
        f"""
        <div class="sci-card">
            <h4 style="margin-top:0; color:{accent_col};">📖 Nasıl Okunmalı? (How to read)</h4>
            <div style="font-size:0.94rem; line-height:1.5;">{main_text}</div>
            <div class="sci-note">
                <b>🔬 Bilimsel Not (Scientific Note):</b><br>{note_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Harita Çizici Fonksiyon
def render_interactive_map(df_plot, lat_col, lon_col, color_col, size_col=None, hover_name=None, hover_data=None, zoom=1.3, center=None, height=550, color_scale=color_scale_main, discrete_seq=None, labels=None, title=None, animation_frame=None):
    use_new_api = hasattr(px, "scatter_map")
    plot_fn = px.scatter_map if use_new_api else px.scatter_mapbox
    
    fig = plot_fn(
        df_plot, lat=lat_col, lon=lon_col, color=color_col, size=size_col,
        size_max=18 if size_col else None,
        color_continuous_scale=color_scale if not discrete_seq else None,
        color_discrete_sequence=discrete_seq,
        hover_name=hover_name, hover_data=hover_data,
        zoom=zoom, center=center, height=height, labels=labels, title=title,
        animation_frame=animation_frame
    )
    
    layout_args = dict(
        margin={"r": 10, "t": 45 if title else 10, "l": 10, "b": 10},
        paper_bgcolor=bg_card,
        plot_bgcolor=bg_card,
        font=dict(color=text_primary)
    )
    if use_new_api:
        layout_args["map_style"] = map_tile
    else:
        layout_args["mapbox_style"] = map_tile
        
    fig.update_layout(**layout_args)
    fig.update_traces(marker=dict(opacity=0.82))
    return fig

# =========================================================================
# ÜYE 2 GRAFİK ÜRETİCİ FONKSİYONLARI (preview_statistical.py ENTEGRASYONU)
# =========================================================================
def build_u2_density_contour(data: pd.DataFrame, view_mode: str, is_binned: bool):
    d_plot = data.copy()
    if view_mode == "Focused View":
        d_plot = d_plot[(d_plot["mag"] <= 6.8) & (d_plot["depth"] <= 250)]
    
    if is_binned:
        # Detailed Bins: 0.05 magnitude x 10 km depth
        nbinsx = max(10, int((d_plot["mag"].max() - d_plot["mag"].min()) / 0.05)) if not d_plot.empty else 30
        nbinsy = max(10, int((d_plot["depth"].max() - d_plot["depth"].min()) / 10.0)) if not d_plot.empty else 30
        title_txt = f"Detaylı Histogram Yoğunluk Konturu (0.05 Mw × 10 km Bin) — {view_mode}"
    else:
        nbinsx, nbinsy = 28, 28
        title_txt = f"Genel Büyüklük × Derinlik Yoğunluk Konturu (Overview) — {view_mode}"

    fig = px.density_contour(
        d_plot, x="mag", y="depth", nbinsx=nbinsx, nbinsy=nbinsy,
        title=title_txt,
        labels={"mag": "Deprem Büyüklüğü (Mw)", "depth": "Derinlik (km)"}
    )
    fig.update_traces(contours_coloring="fill", contours_showlabels=True, colorscale="Tealgrn")
    fig.update_yaxes(autorange="reversed", title="Derinlik (km) [Yüzey Üstte]")
    fig.update_layout(height=470, paper_bgcolor=bg_card, plot_bgcolor=bg_card, font=dict(color=text_primary))
    return fig

def build_u2_violin_plot(data: pd.DataFrame, selected_methods: list):
    v_df = data[data["magType"].isin(selected_methods)].copy()
    v_df["magError"] = pd.to_numeric(v_df["magError"], errors="coerce")
    v_df = v_df.dropna(subset=["magError"])
    v_df = v_df[v_df["magError"] >= 0]

    fig = px.violin(
        v_df, x="magType", y="magError", color="magType",
        box=True, points="outliers",
        category_orders={"magType": selected_methods},
        title="Tahmin Yöntemlerine (magType) Göre Büyüklük Belirsizliği (magError) Dağılımı",
        labels={"magType": "Büyüklük Tahmin Yöntemi (magType)", "magError": "Büyüklük Hatası / Belirsizliği (magError)"},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(height=460, showlegend=False, paper_bgcolor=bg_card, plot_bgcolor=bg_card, font=dict(color=text_primary))
    return fig

def build_u2_calendar_heatmap(data: pd.DataFrame, year: int, visible_start, visible_end):
    start_yr = pd.Timestamp(year=year, month=1, day=1)
    end_yr = pd.Timestamp(year=year, month=12, day=31)
    all_days = pd.date_range(start_yr, end_yr, freq="D")

    yr_df = data[data["event_date_utc"].dt.year == year]
    daily_counts = yr_df.groupby(yr_df["event_date_utc"].dt.normalize()).size()

    cal_df = pd.DataFrame({"date": all_days})
    cal_df["count"] = cal_df["date"].map(daily_counts).fillna(0).astype(int)
    cal_df["in_range"] = (cal_df["date"].dt.date >= visible_start) & (cal_df["date"].dt.date <= visible_end)
    
    # Seçili aralık dışındaki günleri NaN yaparak gri gösterme
    cal_df["z_val"] = np.where(cal_df["in_range"], np.log1p(cal_df["count"]), np.nan)
    cal_df["weekday"] = cal_df["date"].dt.weekday  # 0=Mon, 6=Sun
    
    # Yılın ilk gününe göre hafta indeksi
    first_monday = start_yr - pd.Timedelta(days=start_yr.weekday())
    cal_df["week_idx"] = ((cal_df["date"] - first_monday).dt.days // 7)

    day_names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    max_week = int(cal_df["week_idx"].max()) + 1

    z_matrix = np.full((7, max_week), np.nan)
    text_matrix = np.full((7, max_week), "", dtype=object)

    for _, row in cal_df.iterrows():
        w = int(row["week_idx"])
        d = int(row["weekday"])
        z_matrix[d, w] = row["z_val"]
        d_str = row["date"].strftime("%d %b %Y")
        if row["in_range"]:
            text_matrix[d, w] = f"<b>{d_str} (UTC)</b><br>Deprem Sayısı: {row['count']:,}"
        else:
            text_matrix[d, w] = f"<b>{d_str}</b><br>Veri/Filtre Aralığı Dışında"

    # Ay başlangıç etiketleri
    month_ticks, month_labels = [], []
    for m in range(1, 13):
        m_date = pd.Timestamp(year=year, month=m, day=1)
        w_m = int((m_date - first_monday).days // 7)
        month_ticks.append(w_m)
        month_labels.append(m_date.strftime("%b"))

    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=list(range(max_week)),
        y=day_names,
        text=text_matrix,
        hoverinfo="text",
        colorscale="Teal",
        showscale=True,
        xgap=3,
        ygap=3,
        colorbar=dict(
            title="Günlük Olay<br>(Log Ölçek)",
            tickvals=[0, np.log1p(5), np.log1p(15), np.log1p(50), np.log1p(150)],
            ticktext=["0", "5", "15", "50", "150+"]
        )
    ))

    # 2023 yılında 6 Şubat gününü Kehribar (Amber) çerçeve ile işaretleme (Üye 2 özelliği)
    if year == 2023:
        feb6 = pd.Timestamp("2023-02-06")
        w_f6 = int((feb6 - first_monday).days // 7)
        d_f6 = feb6.weekday()
        fig.add_shape(
            type="rect",
            x0=w_f6 - 0.5, x1=w_f6 + 0.5,
            y0=d_f6 - 0.5, y1=d_f6 + 0.5,
            line=dict(color="#f59e0b", width=3.2),
        )
        fig.add_annotation(
            x=w_f6, y=d_f6, text="★ 6 Şub",
            showarrow=True, arrowhead=2, ax=0, ay=-28,
            font=dict(color="#d97706", size=11, family="Arial Black"),
            bgcolor=bg_card, bordercolor="#f59e0b"
        )

    fig.update_xaxes(tickmode="array", tickvals=month_ticks, ticktext=month_labels, showgrid=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_layout(
        title=f"{year} Yılı Günlük M4.5+ Deprem Aktivite Takvimi (UTC)",
        height=340,
        margin=dict(l=20, r=20, t=45, b=20),
        paper_bgcolor=bg_card,
        plot_bgcolor="#e2e8f0" if is_light else "#334155",
        font=dict(color=text_primary)
    )
    return fig

# --- SIDEBAR FİLTRELERİ ---
if not is_mock:
    st.sidebar.success(f"🟢 Veri Aktif: {len(df):,} olay × {len(df.columns)} sütun")

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Dinamik Filtreler")

preset = st.sidebar.selectbox(
    "⚡ Hızlı Sunum Senaryoları:",
    ["Tüm Küresel Kayıtlar (Varsayılan)", "Sadece Büyük Depremler (M ≥ 6.0)", "Sadece Sığ Depremler (< 70 km)", "Şubat 2023 Dönemi (Türkiye Odaklı)"]
)

valid_dates = df['date_only'].dropna()
min_date, max_date = valid_dates.min(), valid_dates.max()
min_mag, max_mag = float(df['mag'].min()), float(df['mag'].max())
min_depth, max_depth = float(df['depth'].min()), float(df['depth'].max())

default_dates = (min_date, max_date)
default_mag = (min_mag, max_mag)
default_depth = (min_depth, max_depth)

if preset == "Sadece Büyük Depremler (M ≥ 6.0)":
    default_mag = (6.0, max_mag)
elif preset == "Sadece Sığ Depremler (< 70 km)":
    default_depth = (min_depth, 70.0)
elif preset == "Şubat 2023 Dönemi (Türkiye Odaklı)":
    default_dates = (pd.to_datetime("2023-02-01").date(), pd.to_datetime("2023-02-28").date())

date_range = st.sidebar.date_input("📅 Tarih Aralığı (UTC)", value=default_dates, min_value=min_date, max_value=max_date)
mag_range = st.sidebar.slider("📈 Deprem Büyüklüğü (Mw)", min_mag, max_mag, default_mag, step=0.1)
depth_range = st.sidebar.slider("⬇️ Derinlik Aralığı (km)", min_depth, max_depth, default_depth, step=1.0)

hemispheres = st.sidebar.multiselect(
    "🌐 Yarımküre Seçimi",
    options=sorted(df['hemisphere_col'].dropna().unique()),
    default=sorted(df['hemisphere_col'].dropna().unique())
)

# Üye 2'nin özel bilimsel filtresi: 10 km sabit derinlik kontrolü
include_10km = st.sidebar.checkbox(
    "Tam 10 km kaydedilen derinlikleri dahil et (depth_exactly_10km)",
    value=True,
    help="USGS kayıtlarında derinliği tam hesaplanamayan sığ depremlere varsayılan olarak 10 km atanabilir."
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df['date_only'] >= start_date) & (df['date_only'] <= end_date) &
        (df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1]) &
        (df['depth'] >= depth_range[0]) & (df['depth'] <= depth_range[1]) &
        (df['hemisphere_col'].isin(hemispheres))
    ].copy()
else:
    filtered_df = df.copy()

if not include_10km:
    ten_km_mask = filtered_df["depth_exactly_10km"].astype(str).str.lower().eq("true")
    filtered_df = filtered_df.loc[~ten_km_mask].copy()

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Filtrelenen Veriyi İndir (CSV)",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name="seismoscope_filtered_export.csv",
    mime="text/csv",
    use_container_width=True
)

# --- 4. ANA EKRAN HERO BANNER & KPI KARTLARI ---
st.markdown(f"""
    <div class='hero-banner'>
        <h1 style='margin:0; font-size:2.1rem; color:{text_primary};'>🌍 SEISMOSCOPE — Küresel Deprem Analiz Platformu</h1>
        <p style='margin:6px 0 0 0; color:{text_secondary}; font-size:1.02rem;'>
            <b>USGS M4.5+ Küresel Sismik Veri Seti (1 Şubat 2023 – 31 Mayıs 2024)</b> &nbsp;|&nbsp; Coğrafi, İstatistiksel, Zamansal ve Makine Öğrenmesi Karar Destek Sistemi
        </p>
    </div>
""", unsafe_allow_html=True)

total_pct = (len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0
shallow_pct = (len(filtered_df[filtered_df['depth'] < 70]) / len(filtered_df) * 100) if not filtered_df.empty else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Seçili Deprem Kaydı", f"{len(filtered_df):,}", f"Küresel verinin %{total_pct:.1f}'i")
kpi2.metric("Maksimum Büyüklük", f"{filtered_df['mag'].max():.1f} Mw" if not filtered_df.empty else "0 Mw", "Pazarcık / Kahramanmaraş" if not filtered_df.empty and filtered_df['mag'].max() >= 7.8 else "Seçili Aralık Zirvesi")
kpi3.metric("Ortalama / Medyan Derinlik", f"{filtered_df['depth'].mean():.1f} km" if not filtered_df.empty else "0 km", f"Medyan: {filtered_df['depth'].median():.1f} km | %{shallow_pct:.1f} Sığ")
kpi4.metric("Güçlü Sarsıntılar (M ≥ 6.0)", f"{len(filtered_df[filtered_df['mag'] >= 6.0]):,}" if not filtered_df.empty else "0", f"{len(filtered_df[filtered_df['mag'] >= 7.0])} Major (≥7.0 Mw)")

if not filtered_df.empty:
    top_event = filtered_df.loc[filtered_df['mag'].idxmax()]
    top_place = top_event['place'] if 'place' in filtered_df.columns else "Bilinmiyor"
    dom_hem = filtered_df['hemisphere_col'].mode()[0]
    st.markdown(
        f"<div class='insight-box'>💡 <b>Canlı Veri Özeti:</b> Seçili filtrelerdeki en şiddetli sarsıntı <b>{top_event['mag']:.1f} Mw</b> büyüklüğüyle <b>{top_place}</b> bölgesinde kaydedilmiştir. Kayıtların <b>%{shallow_pct:.1f}</b>'i yüzeye yakın sığ depremlerden (<70 km) oluşurken en yoğun sismik hareketlilik <b>{dom_hem}</b> yarımkürededir.</div>",
        unsafe_allow_html=True
    )

# --- 5. NAVİGASYON (SEKMELER) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Coğrafi & Kategorik Analiz (Üye 1)", 
    "📈 İstatistiksel & Zamansal Analiz (Üye 2)", 
    "📊 Üye 3 Analizleri",
    "🤖 Makine Öğrenmesi (K-Means & DT)", 
    "🇹🇷 6 Şubat 2023 Türkiye & Dalga Simülatörü"
])

# ==========================================
# SEKME 1: ÜYE 1 GRAFİKLERİ (MAP, SANKEY, SUNBURST)
# ==========================================
with tab1:
    if filtered_df.empty:
        st.warning("⚠️ Seçilen filtre kriterlerine uygun deprem kaydı bulunamadı.")
    else:
        col_title, col_mode = st.columns([2, 2])
        with col_title:
            st.subheader("1. Küresel Deprem Dağılım Haritası (Geographic Map)")
        with col_mode:
            map_mode = st.radio(
                "Harita Görünüm Modu:",
                ["🗺️ 2B İnteraktif Harita (Zoom)", "🌐 3B İnteraktif Küre", "🎬 Zaman Animasyonu (Aylık Akış)"],
                horizontal=True
            )
        
        plot_df = filtered_df.copy()
        plot_df['size_mag'] = ((plot_df['mag'] - 4.2).clip(lower=0.25) ** 2.15).round(2)
        
        hover_cols = {
            'mag': ':.1f', 'depth': ':.1f', 'date_only': True,
            'latitude': ':.2f', 'longitude': ':.2f',
            'mag_cat_col': True, 'depth_cat_col': True, 'size_mag': False
        }
        hover_title = 'place' if 'place' in plot_df.columns else None
        label_map = {"mag": "Büyüklük (Mw)", "depth": "Derinlik (km)", "date_only": "Tarih", "mag_cat_col": "Büyüklük Bandı", "depth_cat_col": "Derinlik Kat.", "year_month": "Dönem"}

        if map_mode == "🗺️ 2B İnteraktif Harita (Zoom)":
            fig_map = render_interactive_map(
                plot_df, lat_col="latitude", lon_col="longitude", color_col="mag", size_col="size_mag",
                hover_name=hover_title, hover_data=hover_cols, zoom=1.35, height=550, color_scale=color_scale_main, labels=label_map
            )
        elif map_mode == "🌐 3B İnteraktif Küre":
            fig_map = px.scatter_geo(
                plot_df, lat="latitude", lon="longitude", color="mag", size="size_mag",
                size_max=18, opacity=0.85, projection="orthographic", color_continuous_scale=color_scale_main,
                hover_name=hover_title, hover_data=hover_cols, height=550, labels=label_map
            )
            fig_map.update_geos(
                bgcolor=bg_card, showland=True, landcolor=globe_land,
                showocean=True, oceancolor=globe_ocean,
                showcountries=True, countrycolor=globe_border,
                showcoastlines=True, coastlinecolor=globe_border
            )
            fig_map.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, paper_bgcolor=bg_card, font=dict(color=text_primary))
        else:
            anim_df = plot_df.sort_values('year_month')
            fig_map = render_interactive_map(
                anim_df, lat_col="latitude", lon_col="longitude", color_col="mag", size_col="size_mag",
                hover_name=hover_title, hover_data=hover_cols, zoom=1.3, height=590, color_scale=color_scale_main,
                labels=label_map, animation_frame="year_month"
            )

        st.plotly_chart(fig_map, use_container_width=True)

        col_sankey, col_sunburst = st.columns(2)

        with col_sankey:
            st.subheader("2. Kategorisel Akış (Sankey Diagram)")
            st.caption("Akış Yönü: Magnitude Band ➔ Depth Category ➔ Hemisphere")
            
            s1 = filtered_df.groupby(['mag_cat_col', 'depth_cat_col']).size().reset_index(name='count')
            s1.columns = ['source', 'target', 'value']
            s2 = filtered_df.groupby(['depth_cat_col', 'hemisphere_col']).size().reset_index(name='count')
            s2.columns = ['source', 'target', 'value']
            links = pd.concat([s1, s2], axis=0)
            links = links[links['value'] > 0]

            unique_nodes = list(pd.unique(links[['source', 'target']].values.ravel('K')))
            node_map = {node: idx for idx, node in enumerate(unique_nodes)}

            palette = {
                '4.5': ('#0ea5e9', 'rgba(14, 165, 233, 0.35)'),
                'Light': ('#0ea5e9', 'rgba(14, 165, 233, 0.35)'),
                '5.0': ('#eab308', 'rgba(234, 179, 8, 0.42)'),
                'Moderate': ('#eab308', 'rgba(234, 179, 8, 0.42)'),
                '6.0': ('#f97316', 'rgba(249, 115, 22, 0.50)'),
                'Strong': ('#f97316', 'rgba(249, 115, 22, 0.50)'),
                '7.0': ('#e11d48', 'rgba(225, 29, 72, 0.65)'),
                'Major': ('#e11d48', 'rgba(225, 29, 72, 0.65)'),
                'Shallow': ('#10b981', 'rgba(16, 185, 129, 0.35)'),
                'Intermediate': ('#8b5cf6', 'rgba(139, 92, 246, 0.35)'),
                'Deep': ('#6366f1', 'rgba(99, 102, 241, 0.42)'),
                'Northern': ('#14b8a6', 'rgba(20, 184, 166, 0.35)'),
                'Southern': ('#ec4899', 'rgba(236, 72, 153, 0.35)')
            }

            def get_node_color(label):
                for k, v in palette.items():
                    if k.lower() in str(label).lower():
                        return v[0]
                return "#0284c7"

            def get_link_color(src_label):
                for k, v in palette.items():
                    if k.lower() in str(src_label).lower():
                        return v[1]
                return "rgba(2, 132, 199, 0.32)"

            fig_sankey = go.Figure(data=[go.Sankey(
                textfont=dict(color=text_primary, size=12, family="Arial"),
                node=dict(
                    pad=20, thickness=22,
                    line=dict(color=bg_card, width=1.5),
                    label=unique_nodes,
                    color=[get_node_color(n) for n in unique_nodes],
                    hovertemplate="<b>%{label}</b><br>Toplam Akış: %{value:,} deprem<extra></extra>"
                ),
                link=dict(
                    source=links['source'].map(node_map),
                    target=links['target'].map(node_map),
                    value=links['value'],
                    color=[get_link_color(s) for s in links['source']],
                    hovertemplate="<b>%{source.label} ➔ %{target.label}</b><br>Deprem Sayısı: %{value:,}<extra></extra>"
                )
            )])
            fig_sankey.update_layout(height=490, margin=dict(l=15, r=15, t=20, b=15), paper_bgcolor=bg_card, font=dict(color=text_primary, size=12))
            st.plotly_chart(fig_sankey, use_container_width=True)

        with col_sunburst:
            st.subheader("3. Hiyerarşik Dağılım (Sunburst Diagram)")
            st.caption("Hiyerarşi: Hemisphere (İç) ➔ Magnitude Band (Orta) ➔ Depth Category (Dış)")
            
            fig_sunburst = px.sunburst(
                filtered_df,
                path=['hemisphere_col', 'mag_cat_col', 'depth_cat_col'],
                color='mag',
                color_continuous_scale=color_scale_main,
                height=490,
                labels={'mag': 'Ort. Büyüklük (Mw)'}
            )
            fig_sunburst.update_traces(
                hovertemplate="<b>%{label}</b><br>Kayıt Sayısı: %{value:,} deprem<br>Ortalama Büyüklük: %{color:.2f} Mw<br>Üst Kategori Oranı: %{percentParent:.1%}<extra></extra>",
                insidetextorientation='radial'
            )
            fig_sunburst.update_layout(margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor=bg_card, font=dict(color=text_primary))
            st.plotly_chart(fig_sunburst, use_container_width=True)

# =========================================================================
# SEKME 2: ÜYE 2 — İSTATİSTİKSEL VE ZAMANSAL ANALİZ (preview_statistical.py)
# =========================================================================
with tab2:
    st.subheader("📈 İstatistiksel ve Zamansal Analiz (Üye 2 — Statistical & Temporal Lead)")
    st.caption("Büyüklük × Derinlik yoğunluk konturları, ölçüm yöntemi belirsizlik dağılımı (Violin Plot) ve günlük sismik aktivite takvimi (Calendar Heatmap).")

    if filtered_df.empty:
        st.warning("⚠️ Seçilen filtre kriterlerine uygun deprem kaydı bulunamadı.")
    else:
        u2_choices = [
            "1. Density Contour (Büyüklük × Derinlik Yoğunluğu)",
            "2. Violin Plot (Yöntemlere Göre Ölçüm Belirsizliği)",
            "3. Calendar Heatmap (Günlük Deprem Aktivite Takvimi)"
        ]
        chosen_u2 = st.radio("İncelenecek Görselleştirmeyi Seçin:", u2_choices, horizontal=True)
        st.markdown("---")

        # --- ÜYE 2 GÖRSELLEŞTİRME 1: DENSITY CONTOUR ---
        if chosen_u2.startswith("1."):
            h_col, c_col = st.columns([3, 1])
            with h_col:
                st.markdown("#### Magnitude × Depth Density Contour")
                st.caption("Farklı histogram kutu genişlikleri (bin widths) kullanarak aynı deprem verisinin iki tamamlayıcı görünümü.")
            with c_col:
                contour_view = st.selectbox("Görünüm Aralığı (Chart range):", ["Focused View", "Full Range"])

            ov_tab, det_tab = st.tabs(["Overview Contours (Genel Kontur)", "Detailed Bins (0.05 Mw × 10 km)"])

            with ov_tab:
                ch_col, nt_col = st.columns([3.4, 1.3], gap="large")
                with ch_col:
                    fig_ov = build_u2_density_contour(filtered_df, contour_view, is_binned=False)
                    st.plotly_chart(fig_ov, use_container_width=True, key="u2_dens_ov")
                with nt_col:
                    show_scientific_card(
                        "Otomatik seçilen kutu aralıkları (bins), genel büyüklük-derinlik yoğunlaşma örüntüsünü gösterir. Bu bir KDE tahmini değil, histogram konturudur.",
                        "Tam 10 km olarak kaydedilen bazı derinlikler varsayılan atanmış değerler olabilir. Yorumlamadan önce sol menüdeki 'Tam 10 km' onay kutusunu kapatıp açarak karşılaştırın."
                    )

            with det_tab:
                ch_col2, nt_col2 = st.columns([3.4, 1.3], gap="large")
                with ch_col2:
                    fig_det = build_u2_density_contour(filtered_df, contour_view, is_binned=True)
                    st.plotly_chart(fig_det, use_container_width=True, key="u2_dens_det")
                with nt_col2:
                    show_scientific_card(
                        "Sabit ince aralıklar (0.05 büyüklük × 10 km derinlik) yerel yoğunlaşmaları ortaya çıkarır. Renk ölçeği sayıları genel görünümle doğrudan kıyaslanmamalıdır.",
                        "Özellikle 10 km derinlik çizgisindeki yatay yoğunlaşma sismolojik kataloglama standartlarından kaynaklanır."
                    )

        # --- ÜYE 2 GÖRSELLEŞTİRME 2: VIOLIN PLOT ---
        elif chosen_u2.startswith("2."):
            st.markdown("#### Magnitude Uncertainty by Estimation Method (Violin Plot)")
            st.caption("Deprem büyüklüğü tahmin yöntemleri (`magType`) arasında raporlanan büyüklük belirsizliğini (`magError`) karşılaştırın.")

            if "magError" not in filtered_df.columns or "magType" not in filtered_df.columns:
                st.info("Veri setinde `magType` veya `magError` sütunu bulunamadı.")
            else:
                method_counts = filtered_df.dropna(subset=["magError"])["magType"].value_counts()
                available_methods = method_counts[method_counts >= 30].index.tolist()

                if not available_methods:
                    available_methods = method_counts.index.tolist()

                selected_methods = st.multiselect(
                    "Büyüklük Tahmin Yöntemleri (En az 30 geçerli kayıt içerenler):",
                    options=available_methods,
                    default=available_methods
                )

                violin_data = filtered_df.loc[
                    filtered_df["magType"].isin(selected_methods),
                    ["magType", "magError"]
                ].copy()
                violin_data["magError"] = pd.to_numeric(violin_data["magError"], errors="coerce")
                violin_data = violin_data.dropna(subset=["magError"])
                violin_data = violin_data[violin_data["magError"] >= 0]

                v1, v2, v3 = st.columns(3)
                v1.metric("Geçerli Ölçüm Sayısı", f"{len(violin_data):,}")
                v2.metric("Seçili Yöntem Sayısı", f"{len(selected_methods)}")
                v3.metric("Medyan Belirsizlik (magError)", f"{violin_data['magError'].median():.3f}" if not violin_data.empty else "—")

                ch_col, nt_col = st.columns([3.4, 1.3], gap="large")
                with ch_col:
                    if violin_data.empty:
                        st.info("Seçilen kriterlere uygun geçerli ölçüm bulunamadı.")
                    else:
                        fig_vio = build_u2_violin_plot(filtered_df, selected_methods)
                        st.plotly_chart(fig_vio, use_container_width=True, key="u2_violin")
                with nt_col:
                    show_scientific_card(
                        "Her bir keman (violin) bir yöntemin belirsizlik dağılımını temsil eder. Geniş bölümler daha yüksek yoğunluğu, içteki kutu ise çeyreklikleri (IQR) ve medyanı gösterir.",
                        "Farklı büyüklük yöntemleri farklı sismik koşullar altında kullanılır. Raporlanan hatanın küçük olması tek başına o yöntemin daha doğru olduğunu kanıtlamaz."
                    )

                if not violin_data.empty:
                    st.markdown("##### 📋 İstatistiksel Özet Tablosu (Statistical Summary)")
                    summary_df = (
                        violin_data.groupby("magType")["magError"]
                        .agg(Records="size", Median="median", Mean="mean", Std_Dev="std")
                        .reindex(selected_methods)
                        .round(3)
                        .reset_index()
                        .rename(columns={"magType": "Method (Yöntem)", "Std_Dev": "Std. dev."})
                    )
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # --- ÜYE 2 GÖRSELLEŞTİRME 3: CALENDAR HEATMAP ---
        elif chosen_u2.startswith("3."):
            st.markdown("#### Daily Earthquake Activity Calendar (Günlük Deprem Takvimi)")
            st.caption("Günlük M4.5+ deprem sayılarını UTC tarihlerine göre inceleyin. 2023 görünümünde 6 Şubat kehribar (amber) çerçeve ile işaretlenmiştir.")

            y_col, s_col = st.columns([1, 2])
            with y_col:
                avail_years = sorted(df["event_date_utc"].dt.year.dropna().unique().astype(int))
                cal_year = st.selectbox("Takvim Yılı (Calendar year):", options=avail_years, index=0)
            with s_col:
                geo_scope = st.selectbox(
                    "Coğrafi Kapsam (Geographic scope):",
                    ["Global (Tüm Dünya)", "6 Feb epicentral region (35–40°N, 34–41°E)"],
                    help="Yaklaşık 6 Şubat bölgesi dikdörtgen koordinat filtresi: 35–40°K, 34–41°D."
                )

            cal_data = filtered_df.copy()
            if not geo_scope.startswith("Global"):
                cal_data = cal_data.loc[
                    cal_data["latitude"].between(35, 40) & cal_data["longitude"].between(34, 41)
                ].copy()

            vis_start, vis_end = (date_range if len(date_range) == 2 else (min_date, max_date))
            year_data = cal_data[cal_data["event_date_utc"].dt.year == int(cal_year)]
            daily_series = year_data.groupby(year_data["event_date_utc"].dt.normalize()).size()

            max_day_cnt = int(daily_series.max()) if not daily_series.empty else 0
            feb6_cnt = int(daily_series.get(pd.Timestamp("2023-02-06"), 0))

            c1, c2, c3 = st.columns(3)
            c1.metric(f"{cal_year} Yılındaki Olay Sayısı", f"{len(year_data):,}")
            c2.metric("Günlük Zirve Kayıt (Peak Daily)", f"{max_day_cnt:,}")
            if int(cal_year) == 2023:
                c3.metric("6 Şubat 2023 (UTC) Kayıt Sayısı", f"{feb6_cnt:,}")
            else:
                c3.metric("Deprem Kaydedilen Gün Sayısı", f"{len(daily_series):,}")

            ch_col, nt_col = st.columns([3.4, 1.3], gap="large")
            with ch_col:
                fig_cal = build_u2_calendar_heatmap(cal_data, int(cal_year), vis_start, vis_end)
                st.plotly_chart(fig_cal, use_container_width=True, key="u2_cal")
            with nt_col:
                show_scientific_card(
                    "Her kutucuk bir UTC gününü temsil eder. Koyu turkuaz tonları daha fazla M4.5+ depremi gösterir. Kesin sayı için kutucukların üzerine gelebilirsiniz.",
                    "2023 görünümünde kehribar çerçeve 6 Şubat'ı işaretler. Renkler log(1 + sayı) ölçeğini kullanır. Bölgesel seçenek yaklaşık koordinatları baz alır."
                )

            if not daily_series.empty:
                st.markdown("##### 🏆 En Aktif 5 Gün (Most Active Days)")
                top_days = (
                    daily_series.sort_values(ascending=False)
                    .head(5)
                    .rename_axis("UTC Tarih")
                    .reset_index(name="Kaydedilen Deprem Sayısı (M4.5+)")
                )
                top_days["UTC Tarih"] = top_days["UTC Tarih"].dt.strftime("%d %b %Y")
                st.dataframe(top_days, use_container_width=True, hide_index=True)

# ==========================================
# SEKME 3: ÜYE 3 ENTEGRASYON ALANI
# ==========================================
with tab3:
    st.subheader("📊 Üye 3 Analiz Grafikleri")
    st.info("Üye 3'ün kodları geldiğinde tıpkı Üye 2'de olduğu gibi doğrudan bu sekmeye entegre edilecektir.")

# ==========================================
# SEKME 4: GERÇEK ML EĞİTİM SONUÇLARI
# ==========================================
with tab4:
    st.subheader("🤖 SEISMOSCOPE — Makine Öğrenmesi Model Sonuçları")
    st.info("📌 **Metodolojik Not:** Bu modeller geçmişte kaydedilmiş sismik olayların örüntülerini inceler; gelecekteki depremlerin zamanı, konumu veya büyüklüğünü tahmin etmez.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("K-Means Küme Sayısı", "K = 7", "Silhouette: 0.287")
    m2.metric("DT Balanced Accuracy", "%78.7", "+%45.4 vs Baseline (%33.3)")
    m3.metric("DT Macro F1 Skoru", "0.625", "Kronolojik Test: 1,978 Olay")
    m4.metric("DT Overall Accuracy", "%69.8", "Eğitim/Test: 7,911 / 1,978")
    
    st.markdown("---")
    ml_left, ml_right = st.columns(2)
    
    with ml_left:
        st.markdown("#### 1. Model 1 — K-Means Clustering (Gözetimsiz Öğrenme)")
        st.markdown("""
        * **Özellik Uzayı:** Jeodezik birim küre koordinatları (`geo_x/y/z`), `mag` ve `log1p(depth)` (`StandardScaler` ile ölçeklendi).
        * **Küme Seçimi:** `K = 7` küme, 1.500 örneklem üzerinde **0.287** Silhouette skoru ile belirlendi.
        """)
        
        cluster_sizes = pd.DataFrame({
            'Küme': ['Küme 0', 'Küme 1', 'Küme 2', 'Küme 3', 'Küme 4', 'Küme 5', 'Küme 6'],
            'Olay Sayısı': [645, 751, 1315, 1587, 1236, 3235, 1120]
        })
        fig_clusters = px.bar(
            cluster_sizes, x='Küme', y='Olay Sayısı', color='Olay Sayısı',
            text='Olay Sayısı', color_continuous_scale='Tealgrn',
            title="K-Means (K=7) Küme Boyutları Dağılımı (Toplam: 9,889 Olay)",
            height=380
        )
        fig_clusters.update_traces(textposition='outside')
        fig_clusters.update_layout(paper_bgcolor=bg_card, plot_bgcolor=bg_card, font=dict(color=text_primary))
        st.plotly_chart(fig_clusters, use_container_width=True)
        
        cluster_prof_path = find_file("cluster_profiles.csv")
        if cluster_prof_path:
            with st.expander("📋 Küme Profilleri Tablosunu Aç (cluster_profiles.csv)"):
                st.dataframe(pd.read_csv(cluster_prof_path), use_container_width=True)

    with ml_right:
        st.markdown("#### 2. Model 2 — Decision Tree Classification (`depth_category`)")
        st.markdown("""
        * **Hedef:** `depth_category` (Sığ / Orta / Derin). Veri sızıntısını önlemek için `depth` sütunu girdi olarak **kullanılmamıştır**.
        * **Neden Balanced Accuracy?** Çoğunluk sınıfı baseline modeli tüm depremlere "Sığ" diyerek %77.6 sıradan doğruluk alır ancak orta/derin depremleri hiç yakalayamaz (Balanced Acc: **%33.3**). Karar ağacımız ise **%78.7 Balanced Accuracy** ile tüm derinlik sınıflarını dengeli biçimde ayrıştırır.
        """)
        
        comp_df = pd.DataFrame({
            'Metrik': ['Balanced Accuracy (%)', 'Overall Accuracy (%)', 'Macro F1 (x100)'],
            'Decision Tree (Modelimiz)': [78.7, 69.8, 62.5],
            'Majority Baseline': [33.3, 77.6, 29.1]
        })
        fig_comp = px.bar(
            comp_df, x='Metrik', y=['Decision Tree (Modelimiz)', 'Majority Baseline'],
            barmode='group', text_auto='.1f',
            title="Decision Tree vs. Baseline Performans Karşılaştırması",
            height=380, color_discrete_sequence=['#0284c7', '#94a3b8']
        )
        fig_comp.update_layout(paper_bgcolor=bg_card, plot_bgcolor=bg_card, font=dict(color=text_primary), yaxis_title="Skor (%)")
        st.plotly_chart(fig_comp, use_container_width=True)

        with st.expander("🧪 Deneysel Model: Decision Tree Regression (Neden Elendi?)"):
            st.markdown("""
            * **Hedef:** Deprem büyüklüğü (`mag`) tahmini.
            * **Sonuç:** Kronolojik test `MAE: 0.2643` (Sabit ortalama baseline `MAE: 0.2605`), `R²: -0.0251`.
            * **Bilimsel Karar:** Baseline modelden daha düşük performans gösterdiği için şeffaflık ilkesi gereği elenmiş ve raporlanmıştır.
            """)

    scored_events_path = find_file("ml_scored_events.csv")
    if scored_events_path:
        st.markdown("---")
        st.markdown("#### 🌐 K-Means Kümelerinin Küresel Harita Üzerindeki Dağılımı (`ml_scored_events.csv`)")
        scored_df = pd.read_csv(scored_events_path)
        cluster_col = next((c for c in ['cluster', 'kmeans_cluster', 'cluster_id'] if c in scored_df.columns), None)
        if cluster_col:
            scored_df[cluster_col] = "Küme " + scored_df[cluster_col].astype(str)
            fig_ml_map = render_interactive_map(
                scored_df, lat_col="latitude", lon_col="longitude", color_col=cluster_col,
                hover_data=['mag', 'depth'], zoom=1.25, height=480,
                discrete_seq=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig_ml_map, use_container_width=True)

# ==========================================
# SEKME 5: 6 ŞUBAT 2023 TÜRKİYE ÖZEL ANALİZİ & DALGA SİMÜLATÖRÜ
# ==========================================
with tab5:
    st.subheader("🇹🇷 6 Şubat 2023 Kahramanmaraş Depremleri Özel İncelemesi")
    st.markdown("Doğu Anadolu Fay Hattı üzerinde meydana gelen **7.8 Mw (Pazarcık)** ve **7.5 Mw (Elbistan)** ana şokları ile artçı sarsıntıların mekansal-zamansal analizi ve sismik dalga yayılım simülasyonu.")
    
    tr_df = df[
        (df['latitude'] >= 35.5) & (df['latitude'] <= 42.5) &
        (df['longitude'] >= 25.5) & (df['longitude'] <= 45.0)
    ].copy()
    
    if tr_df.empty:
        st.warning("Veri setinde Türkiye koordinat aralığında kayıt bulunamadı.")
    else:
        tr_k1, tr_k2, tr_k3, tr_k4 = st.columns(4)
        tr_k1.metric("Türkiye Bölgesi Kayıt", f"{len(tr_df):,} deprem")
        tr_k2.metric("Ana Şok (Maksimum)", f"{tr_df['mag'].max():.1f} Mw", "6 Şubat 2023 - 01:17 UTC")
        tr_k3.metric("Ortalama Derinlik", f"{tr_df['depth'].mean():.1f} km", "Yüzeye Yakın / Sığ Kırılma")
        tr_k4.metric("Güçlü Sarsıntılar (M ≥ 6.0)", f"{len(tr_df[tr_df['mag'] >= 6.0]):,}")
        
        focus_spot = st.radio(
            "🎯 Harita Kamera Odağı (Sunum Kısa Yolu):",
            ["Genel Deprem Bölgesi", "Pazarcık Ana Şok (7.8 Mw)", "Elbistan İkinci Ana Şok (7.5 Mw)", "Hatay / Antakya Kırığı (6.3 Mw)"],
            horizontal=True
        )
        focus_coords = {
            "Genel Deprem Bölgesi": (37.5, 37.0, 5.8),
            "Pazarcık Ana Şok (7.8 Mw)": (37.226, 37.014, 8.0),
            "Elbistan İkinci Ana Şok (7.5 Mw)": (38.024, 37.203, 8.0),
            "Hatay / Antakya Kırığı (6.3 Mw)": (36.126, 36.026, 8.0)
        }
        c_lat, c_lon, c_zoom = focus_coords[focus_spot]

        col_tr_map, col_tr_time = st.columns([3, 2])
        
        with col_tr_map:
            tr_df['size_mag'] = ((tr_df['mag'] - 4.0).clip(lower=0.3) ** 2.2).round(2)
            fig_tr_map = render_interactive_map(
                tr_df, lat_col="latitude", lon_col="longitude", color_col="mag", size_col="size_mag",
                hover_name="place" if "place" in tr_df.columns else None,
                hover_data={'mag': ':.1f', 'depth': ':.1f', 'date_only': True, 'size_mag': False},
                zoom=c_zoom, center={"lat": c_lat, "lon": c_lon}, height=470, color_scale="YlOrRd",
                title="Doğu Anadolu Fay Hattı Kırılma Zonu ve Artçı Dağılımı"
            )
            st.plotly_chart(fig_tr_map, use_container_width=True)
            
        with col_tr_time:
            fig_tr_timeline = px.scatter(
                tr_df.sort_values('time_parsed'), x="time_parsed", y="mag",
                color="depth", size="size_mag",
                color_continuous_scale="Plasma",
                hover_name="place" if "place" in tr_df.columns else None,
                title="Zaman İçinde Büyüklük (Mw) ve Derinlik (km) Evrimi",
                labels={"time_parsed": "Tarih", "mag": "Büyüklük (Mw)", "depth": "Derinlik (km)"},
                height=470
            )
            fig_tr_timeline.update_layout(paper_bgcolor=bg_card, plot_bgcolor=bg_card, font=dict(color=text_primary))
            st.plotly_chart(fig_tr_timeline, use_container_width=True)

        # SİSMİK DALGA YAYILIM VE ETKİ ALANI SİMÜLATÖRÜ
        st.markdown("---")
        st.subheader("🌊 Sismik Dalga Yayılım ve Etki Alanı Simülatörü (Kaç Saniyede Kaç KM?)")
        st.caption("Sismik kabuk modeline göre Birincil **P-Dalgası (~6.0 km/sn)** ve Yıkıcı **S-Dalgası (~3.5 km/sn)** hızlarıyla depremin saniye saniye kapsadığı coğrafi alan ve illere ulaşma süresi.")

        sim_col1, sim_col2 = st.columns([1, 2])
        with sim_col1:
            sim_event = st.selectbox(
                "📌 Simüle Edilecek Deprem Merkez Üssü:",
                [
                    "Pazarcık Ana Şok (7.8 Mw - Derinlik: 10.0 km)",
                    "Elbistan İkinci Ana Şok (7.5 Mw - Derinlik: 7.4 km)",
                    "Hatay / Yayladağı (6.3 Mw - Derinlik: 16.0 km)"
                ]
            )
        with sim_col2:
            elapsed_sec = st.slider(
                "⏱️ Kırılma Anından İtibaren Geçen Süre (Saniye):",
                min_value=5, max_value=110, value=40, step=5
            )

        event_params = {
            "Pazarcık Ana Şok (7.8 Mw - Derinlik: 10.0 km)": (37.226, 37.014, 10.0, 7.8),
            "Elbistan İkinci Ana Şok (7.5 Mw - Derinlik: 7.4 km)": (38.024, 37.203, 7.4, 7.5),
            "Hatay / Yayladağı (6.3 Mw - Derinlik: 16.0 km)": (36.126, 36.026, 16.0, 6.3)
        }
        ep_lat, ep_lon, ep_depth, ep_mag = event_params[sim_event]

        v_p, v_s = 6.0, 3.5
        hypo_p = v_p * elapsed_sec
        hypo_s = v_s * elapsed_sec
        r_p_km = float(np.sqrt(max(0.0, hypo_p**2 - ep_depth**2)))
        r_s_km = float(np.sqrt(max(0.0, hypo_s**2 - ep_depth**2)))
        area_s_km2 = np.pi * (r_s_km ** 2)
        area_p_km2 = np.pi * (r_p_km ** 2)

        cities = [
            ("Kahramanmaraş", 37.575, 36.922),
            ("Gaziantep", 37.066, 37.378),
            ("Osmaniye", 37.074, 36.246),
            ("Adıyaman", 37.764, 38.278),
            ("Kilis", 36.718, 37.121),
            ("Hatay (Antakya)", 36.202, 36.160),
            ("Malatya", 38.355, 38.309),
            ("Adana", 37.000, 35.321),
            ("Şanlıurfa", 37.159, 38.796),
            ("Mersin", 36.812, 34.641),
            ("Diyarbakır", 37.914, 40.230),
            ("Kayseri", 38.731, 35.478)
        ]

        def haversine_km(lat1, lon1, lat2, lon2):
            R = 6371.0
            phi1, phi2 = np.radians(lat1), np.radians(lat2)
            dphi = np.radians(lat2 - lat1)
            dlambda = np.radians(lon2 - lon1)
            a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0)**2
            return 2 * R * np.arcsin(np.sqrt(a))

        city_rows = []
        for c_name, c_lat_i, c_lon_i in cities:
            epi_dist = haversine_km(ep_lat, ep_lon, c_lat_i, c_lon_i)
            hypo_dist = np.sqrt(epi_dist**2 + ep_depth**2)
            t_p = hypo_dist / v_p
            t_s = hypo_dist / v_s
            if elapsed_sec >= t_s:
                status = "🔴 Yıkıcı S-Dalgası Ulaştı"
            elif elapsed_sec >= t_p:
                status = "🟠 Öncü P-Dalgası Ulaştı"
            else:
                status = "🟢 Henüz Ulaşmadı"
            city_rows.append({
                "Şehir": c_name,
                "lat": c_lat_i,
                "lon": c_lon_i,
                "Merkez Üssüne Mesafe (km)": round(epi_dist, 1),
                "P-Dalgası Varış (sn)": round(t_p, 1),
                "Yıkıcı S-Dalgası Varış (sn)": round(t_s, 1),
                "Erken Uyarı Süresi (S-P Farkı sn)": round(t_s - t_p, 1),
                "Anlık Durum": status
            })
        city_df = pd.DataFrame(city_rows).sort_values("Merkez Üssüne Mesafe (km)")
        hit_cities_count = len(city_df[city_df["Anlık Durum"] == "🔴 Yıkıcı S-Dalgası Ulaştı"])

        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric(f"{elapsed_sec}. Saniyede Yıkıcı Dalga Yarıçapı", f"{r_s_km:,.1f} km", "S-Dalgası (3.5 km/sn)")
        sk2.metric(f"{elapsed_sec}. Saniyede Sarsılan Toplam Alan", f"{area_s_km2:,.0f} km²", f"P-Dalgası Alanı: {area_p_km2:,.0f} km²")
        sk3.metric("Öncü P-Dalgası Yarıçapı", f"{r_p_km:,.1f} km", "Birincil Dalga (6.0 km/sn)")
        sk4.metric("Sarsıntının Ulaştığı İl Merkezleri", f"{hit_cities_count} / {len(cities)} İl", f"t = {elapsed_sec} saniye")

        def make_wave_ring(lat_c, lon_c, radius_km, n_pts=100):
            angles = np.linspace(0, 2 * np.pi, n_pts)
            d_lat = (radius_km / 111.32) * np.cos(angles)
            d_lon = (radius_km / (111.32 * np.cos(np.radians(lat_c)))) * np.sin(angles)
            return lat_c + d_lat, lon_c + d_lon

        col_wave_map, col_wave_chart = st.columns([3, 2])

        with col_wave_map:
            s_lats, s_lons = make_wave_ring(ep_lat, ep_lon, r_s_km)
            p_lats, p_lons = make_wave_ring(ep_lat, ep_lon, r_p_km)

            ring_df = pd.DataFrame({
                'lat': np.concatenate([p_lats, s_lats]),
                'lon': np.concatenate([p_lons, s_lons]),
                'Dalga Tipi': [f'Öncü P-Dalgası Cephesi ({r_p_km:.0f} km)'] * len(p_lats) + [f'Yıkıcı S-Dalgası Cephesi ({r_s_km:.0f} km)'] * len(s_lats)
            })

            use_new_api = hasattr(px, "line_map")
            line_fn = px.line_map if use_new_api else px.line_mapbox

            fig_wave = line_fn(
                ring_df, lat="lat", lon="lon", color="Dalga Tipi",
                color_discrete_sequence=["#0284c7", "#e11d48"],
                zoom=5.7, center={"lat": ep_lat, "lon": ep_lon}, height=480,
                title=f"t = {elapsed_sec}. Saniyede Sismik Dalga Cepheleri ve Etkilenen Şehirler"
            )
            fig_wave.update_traces(line=dict(width=3.5))

            scatter_fn = px.scatter_map if use_new_api else px.scatter_mapbox
            fig_cities = scatter_fn(
                city_df, lat="lat", lon="lon", color="Anlık Durum",
                hover_name="Şehir",
                hover_data={"Merkez Üssüne Mesafe (km)": True, "Yıkıcı S-Dalgası Varış (sn)": True, "lat": False, "lon": False},
                color_discrete_map={
                    "🔴 Yıkıcı S-Dalgası Ulaştı": "#e11d48",
                    "🟠 Öncü P-Dalgası Ulaştı": "#f59e0b",
                    "🟢 Henüz Ulaşmadı": "#10b981"
                }
            )
            fig_cities.update_traces(marker=dict(size=13))
            for trace in fig_cities.data:
                fig_wave.add_trace(trace)

            layout_wave = dict(
                margin={"r": 10, "t": 45, "l": 10, "b": 10},
                paper_bgcolor=bg_card,
                font=dict(color=text_primary),
                legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)" if is_light else "rgba(30,41,59,0.8)")
            )
            if use_new_api:
                layout_wave["map_style"] = map_tile
            else:
                layout_wave["mapbox_style"] = map_tile
            fig_wave.update_layout(**layout_wave)
            st.plotly_chart(fig_wave, use_container_width=True)

        with col_wave_chart:
            fig_arr = px.bar(
                city_df.sort_values("Merkez Üssüne Mesafe (km)", ascending=True),
                y="Şehir", x=["P-Dalgası Varış (sn)", "Yıkıcı S-Dalgası Varış (sn)"],
                barmode="group", orientation="h",
                title="İllere Göre Dalga Varış Süresi (Saniye)",
                color_discrete_sequence=["#0284c7", "#e11d48"],
                height=480
            )
            fig_arr.add_vline(
                x=elapsed_sec, line_width=2.5, line_dash="dash", line_color="#10b981",
                annotation_text=f"Seçili An: {elapsed_sec} sn", annotation_position="top right"
            )
            fig_arr.update_layout(
                paper_bgcolor=bg_card, plot_bgcolor=bg_card, font=dict(color=text_primary),
                xaxis_title="Varış Süresi (Saniye)", yaxis_title="",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_arr, use_container_width=True)

        with st.expander("📊 İl İl Mesafe (km), Varış Süresi (sn) ve Erken Uyarı Farkı Tablosu", expanded=True):
            st.dataframe(
                city_df.drop(columns=["lat", "lon"]),
                use_container_width=True,
                hide_index=True
            )

        ref_feb6_path = find_file("kahramanmaras_6feb_major_events_reference.csv")
        if ref_feb6_path:
            with st.expander("📌 6 Şubat 2023 Ana Şok ve Önemli Artçı Referans Kayıtları"):
                ref_df = pd.read_csv(ref_feb6_path)
                st.dataframe(ref_df, use_container_width=True)
