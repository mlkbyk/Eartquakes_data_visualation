import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 0. STREAMLIT ÇEKİRDEK AÇIK TEMA КОНFİGÜRASYONU (SİYAH KUTULARI KÖKTEN ÖNLER) ---
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

# --- 2. VERİ YÜKLEME ---
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
            'place': ['Global Seismic Zone'] * n
        })

    time_candidates = ['time', 'date', 'datetime', 'event_time', 'origin_time']
    time_col = next((c for c in time_candidates if c in df.columns), df.columns[0])
    df['time_parsed'] = pd.to_datetime(df[time_col], errors='coerce', utc=True)
    df['date_only'] = df['time_parsed'].dt.date
    df['year_month'] = df['time_parsed'].dt.strftime('%Y-%m')

    if 'magnitude' in df.columns and 'mag' not in df.columns:
        df['mag'] = df['magnitude']
    if 'lat' in df.columns and 'latitude' not in df.columns:
        df['latitude'] = df['lat']
    if 'lon' in df.columns and 'longitude' not in df.columns:
        df['longitude'] = df['lon']

    hem_candidates = ['hemisphere', 'ns_hemisphere', 'lat_hemisphere']
    found_hem = next((c for c in hem_candidates if c in df.columns), None)
    if found_hem:
        df['hemisphere_col'] = df[found_hem].astype(str)
    else:
        df['hemisphere_col'] = np.where(df['latitude'] >= 0, 'Northern', 'Southern')

    mag_cat_candidates = ['mag_category', 'magnitude_category', 'mag_cat', 'mag_class']
    found_mag_cat = next((c for c in mag_cat_candidates if c in df.columns), None)
    if found_mag_cat:
        df['mag_cat_col'] = df[found_mag_cat].astype(str)
    else:
        df['mag_cat_col'] = pd.cut(
            df['mag'],
            bins=[-1, 4.9, 5.9, 6.9, 10],
            labels=['Light (4.5-4.9)', 'Moderate (5.0-5.9)', 'Strong (6.0-6.9)', 'Major (7.0+)']
        ).astype(str)

    depth_cat_candidates = ['depth_category', 'depth_cat', 'depth_class']
    found_depth_cat = next((c for c in depth_cat_candidates if c in df.columns), None)
    if found_depth_cat:
        df['depth_cat_col'] = df[found_depth_cat].astype(str)
    else:
        df['depth_cat_col'] = pd.cut(
            df['depth'],
            bins=[-10, 70, 300, 1000],
            labels=['Shallow (<70 km)', 'Intermediate (70-300 km)', 'Deep (>300 km)']
        ).astype(str)

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

# --- TÜM SİYAH KUTULARI VE ÜST BARI DÜZELTEN KAPSAMLI CSS ---
st.markdown(f"""
    <style>
    /* Üstteki siyah Streamlit barını tamamen şeffaf/açık yapma */
    header[data-testid="stHeader"] {{
        background-color: {bg_main} !important;
        border-bottom: none !important;
    }}
    
    /* Ana arka plan */
    .stApp {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
    }}
    .block-container {{
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }}
    
    /* Sol Menü (Sidebar) tasarımı */
    section[data-testid="stSidebar"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {border_col} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_primary} !important;
    }}

    /* SİYAH KUTULARI BEYAZA ÇEVİREN KURAL: Selectbox, DateInput, Multiselect */
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
    
    /* Açılır menü (Dropdown) listesinin siyah arka planını beyaza çevirme */
    div[data-baseweb="popover"] div,
    ul[data-baseweb="menu"],
    li[role="option"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
    }}
    li[role="option"]:hover {{
        background-color: {input_bg} !important;
    }}

    /* Multiselect içindeki etiketler (Northern / Southern) */
    span[data-baseweb="tag"] {{
        background-color: {accent_col} !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }}
    span[data-baseweb="tag"] span {{
        color: #ffffff !important;
    }}

    /* İndirme Butonu (Siyahlığı giderip modern mavi butona çevirme) */
    div[data-testid="stDownloadButton"] button {{
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stDownloadButton"] button * {{
        color: #ffffff !important;
    }}
    div[data-testid="stDownloadButton"] button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.38) !important;
    }}

    /* Hero Başlık Kartı */
    .hero-banner {{
        background: linear-gradient(135deg, {bg_card} 0%, {input_bg} 100%);
        border: 1px solid {border_col};
        border-left: 6px solid {accent_col};
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05);
    }}

    /* KPI Kartları */
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

    /* Grafik Kart Çerçeveleri */
    div[data-testid="stPlotlyChart"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_col} !important;
        border-radius: 14px !important;
        padding: 10px !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05) !important;
    }}

    /* Sekme (Tab) Tasarımı */
    button[data-baseweb="tab"] {{
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        color: {text_secondary} !important;
        padding: 10px 16px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {accent_col} !important;
    }}

    /* Canlı Veri Özeti Kutusu */
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
    </style>
""", unsafe_allow_html=True)

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

date_range = st.sidebar.date_input("📅 Tarih Aralığı", value=default_dates, min_value=min_date, max_value=max_date)
mag_range = st.sidebar.slider("📈 Deprem Büyüklüğü (Mw)", min_mag, max_mag, default_mag, step=0.1)
depth_range = st.sidebar.slider("⬇️ Derinlik Aralığı (km)", min_depth, max_depth, default_depth, step=1.0)

hemispheres = st.sidebar.multiselect(
    "🌐 Yarımküre Seçimi",
    options=sorted(df['hemisphere_col'].dropna().unique()),
    default=sorted(df['hemisphere_col'].dropna().unique())
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df['date_only'] >= start_date) & (df['date_only'] <= end_date) &
        (df['mag'] >= mag_range[0]) & (df['mag'] <= mag_range[1]) &
        (df['depth'] >= depth_range[0]) & (df['depth'] <= depth_range[1]) &
        (df['hemisphere_col'].isin(hemispheres))
    ]
else:
    filtered_df = df.copy()

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
            <b>USGS M4.5+ Küresel Sismik Veri Seti (1 Şubat 2023 – 31 Mayıs 2024)</b> &nbsp;|&nbsp; İnteraktif Görselleştirme, Coğrafi Analiz ve Karar Destek Sistemi
        </p>
    </div>
""", unsafe_allow_html=True)

total_pct = (len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0
shallow_pct = (len(filtered_df[filtered_df['depth'] < 70]) / len(filtered_df) * 100) if not filtered_df.empty else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Toplam Deprem Kaydı", f"{len(filtered_df):,}", f"Küresel verinin %{total_pct:.1f}'i")
kpi2.metric("Maksimum Büyüklük", f"{filtered_df['mag'].max():.1f} Mw" if not filtered_df.empty else "0 Mw", "Pazarcık / Kahramanmaraş" if not filtered_df.empty and filtered_df['mag'].max() >= 7.8 else "Seçili Aralık Zirvesi")
kpi3.metric("Ortalama Derinlik", f"{filtered_df['depth'].mean():.1f} km" if not filtered_df.empty else "0 km", f"%{shallow_pct:.1f} Sığ (<70 km)")
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
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Coğrafi ve Kategorik Analiz (Üye 1)", 
    "📊 Üye 2 & Üye 3 Analizleri", 
    "🤖 Makine Öğrenmesi Sonuçları (K-Means & DT)", 
    "🇹🇷 6 Şubat 2023 Türkiye Özel Analizi"
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
        label_map = {"mag": "Büyüklük (Mw)", "depth": "Derinlik (km)", "date_only": "Tarih", "mag_cat_col": "Büyüklük Kat.", "depth_cat_col": "Derinlik Kat.", "year_month": "Dönem"}

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

        # --- SANKEY & SUNBURST ---
        col_sankey, col_sunburst = st.columns(2)

        with col_sankey:
            st.subheader("2. Kategorisel Akış (Sankey Diagram)")
            st.caption("Akış Yönü: Magnitude Category ➔ Depth Category ➔ Hemisphere")
            
            s1 = filtered_df.groupby(['mag_cat_col', 'depth_cat_col']).size().reset_index(name='count')
            s1.columns = ['source', 'target', 'value']
            s2 = filtered_df.groupby(['depth_cat_col', 'hemisphere_col']).size().reset_index(name='count')
            s2.columns = ['source', 'target', 'value']
            links = pd.concat([s1, s2], axis=0)
            links = links[links['value'] > 0]

            unique_nodes = list(pd.unique(links[['source', 'target']].values.ravel('K')))
            node_map = {node: idx for idx, node in enumerate(unique_nodes)}

            palette = {
                'Light': ('#0ea5e9', 'rgba(14, 165, 233, 0.35)'),
                'Moderate': ('#eab308', 'rgba(234, 179, 8, 0.42)'),
                'Strong': ('#f97316', 'rgba(249, 115, 22, 0.50)'),
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
            st.caption("Hiyerarşi: Hemisphere (İç) ➔ Magnitude Category (Orta) ➔ Depth Category (Dış)")
            
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

# ==========================================
# SEKME 2: ÜYE 2 & ÜYE 3 ENTEGRASYON ALANI
# ==========================================
with tab2:
    st.subheader("📊 Üye 2 ve Üye 3 Analiz Grafikleri")
    st.info("Üye 2 ve Üye 3 grafik kodlarını tamamladığında sol menüdeki ortak `filtered_df` verisiyle bu sekmeye entegre edilecektir.")

# ==========================================
# SEKME 3: GERÇEK ML EĞİTİM SONUÇLARI
# ==========================================
with tab3:
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
# SEKME 4: 6 ŞUBAT 2023 TÜRKİYE ÖZEL ANALİZİ & DALGA SİMÜLATÖRÜ
# ==========================================
with tab4:
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

        # =========================================================================
        # YENİ BÖLÜM: SİSMİK DALGA YAYILIM VE ETKİ ALANI SİMÜLATÖRÜ (KAÇ KM / KAÇ SN)
        # =========================================================================
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
                min_value=5, max_value=110, value=40, step=5,
                help="Kaydırıcıyı hareket ettirerek seçilen saniyede deprem dalgalarının kaç km yarıçapa ve hangi şehirlere ulaştığını inceleyin."
            )

        event_params = {
            "Pazarcık Ana Şok (7.8 Mw - Derinlik: 10.0 km)": (37.226, 37.014, 10.0, 7.8),
            "Elbistan İkinci Ana Şok (7.5 Mw - Derinlik: 7.4 km)": (38.024, 37.203, 7.4, 7.5),
            "Hatay / Yayladağı (6.3 Mw - Derinlik: 16.0 km)": (36.126, 36.026, 16.0, 6.3)
        }
        ep_lat, ep_lon, ep_depth, ep_mag = event_params[sim_event]

        # Dalga hızları (km/s) ve hiposantr derinliğini hesaba katan yüzey yarıçapı
        v_p, v_s = 6.0, 3.5
        hypo_p = v_p * elapsed_sec
        hypo_s = v_s * elapsed_sec
        r_p_km = float(np.sqrt(max(0.0, hypo_p**2 - ep_depth**2)))
        r_s_km = float(np.sqrt(max(0.0, hypo_s**2 - ep_depth**2)))
        area_s_km2 = np.pi * (r_s_km ** 2)
        area_p_km2 = np.pi * (r_p_km ** 2)

        # Çevre iller ve koordinatları
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

        # Haversine mesafe hesabı
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

        # Simülasyon KPI Kartları
        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric(f"{elapsed_sec}. Saniyede Yıkıcı Dalga Yarıçapı", f"{r_s_km:,.1f} km", "S-Dalgası (3.5 km/sn)")
        sk2.metric(f"{elapsed_sec}. Saniyede Sarsılan Toplam Alan", f"{area_s_km2:,.0f} km²", f"P-Dalgası Alanı: {area_p_km2:,.0f} km²")
        sk3.metric("Öncü P-Dalgası Yarıçapı", f"{r_p_km:,.1f} km", "Birincil Dalga (6.0 km/sn)")
        sk4.metric("Sarsıntının Ulaştığı İl Merkezleri", f"{hit_cities_count} / {len(cities)} İl", f"t = {elapsed_sec} saniye")

        # Harita üzerinde jeodezik çember (dalga halkası) koordinatları üretici
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

            # Şehir noktalarını haritaya ekleme
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
            # Seçili saniyeyi dikey kesikli çizgi olarak gösterme
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