import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Configuración de entorno
st.set_page_config(
    page_title="Agrovita · Inteligencia Agrícola",
    page_icon="🌱",
    layout="wide"
)

# Estilos CSS Profesionales y Layout Responsivo
st.markdown("""
<style>
    .stApp { background-color: #0D1B2A; color: #E0E0E0; }
    [data-testid="stSidebar"] { display: none; }

    /* Ajuste para evitar encimamiento en pantallas pequeñas (720p/Móvil) */
    [data-testid="column"] {
        min-width: 320px !important;
    }

    .dash-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0 6px 0;
        border-bottom: 1px solid #1E3A5F;
        margin-bottom: 14px;
    }
    .dash-title {
        font-size: 15px;
        font-weight: 600;
        color: #B0BEC5;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
        margin-bottom: 14px;
    }
    
    .kpi-card {
        background: #112233;
        border: 1px solid #1E3A5F;
        border-radius: 4px;
        padding: 10px 12px;
    }
    .kpi-label {
        font-size: 10px;
        color: #546E7A;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 20px;
        font-weight: 700;
        color: #E0E0E0;
    }
    .kpi-value.accent { color: #00E676; }

    .rec-banner {
        background: #0A2A1A;
        border-left: 3px solid #00E676;
        border-radius: 0 4px 4px 0;
        padding: 12px 16px;
        margin-bottom: 14px;
        font-size: 14px;
        color: #B0BEC5;
    }
    .rec-banner strong { color: #00E676; }

    .section-label {
        font-size: 10px;
        color: #90A4AE;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
        border-bottom: 1px solid #1E3A5F;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab-list"] { background: #112233; }
    .stTabs [aria-selected="true"] { color: #00E676 !important; border-bottom-color: #00E676 !important; }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Dataset de referencia técnica y financiera
datos_financieros = {
    "Tomate rojo (jitomate)": {"precio_ton": 10062.31, "costo_ha": 120000, "rendimiento": 74.79},
    "Fresa":                  {"precio_ton": 24706.56, "costo_ha": 85000,  "rendimiento": 43.90},
    "Pepino":                 {"precio_ton": 8035.89,  "costo_ha": 35000,  "rendimiento": 59.73},
    "Papaya":                 {"precio_ton": 6676.38,  "costo_ha": 40000,  "rendimiento": 55.99},
    "Papa":                   {"precio_ton": 9539.00,  "costo_ha": 45000,  "rendimiento": 32.71},
    "Cebolla":                {"precio_ton": 7306.00,  "costo_ha": 25000,  "rendimiento": 32.03},
    "Aguacate":               {"precio_ton": 20633.31, "costo_ha": 50000,  "rendimiento": 10.91},
    "Nopalitos":              {"precio_ton": 3569.46,  "costo_ha": 15000,  "rendimiento": 68.05},
    "Sandía":                 {"precio_ton": 4899.92,  "costo_ha": 20000,  "rendimiento": 32.88},
    "Zanahoria":              {"precio_ton": 3771.80,  "costo_ha": 30000,  "rendimiento": 31.05},
    "Brócoli":                {"precio_ton": 5000.00,  "costo_ha": 30000,  "rendimiento": 17.37},
    "Maíz grano":             {"precio_ton": 5685.58,  "costo_ha": 15000,  "rendimiento": 3.70},
    "Caña de azúcar":         {"precio_ton": 800.00,   "costo_ha": 25000,  "rendimiento": 64.94},
    "Melón":                  {"precio_ton": 5000.00,  "costo_ha": 25000,  "rendimiento": 29.97},
    "Lechuga":                {"precio_ton": 4500.00,  "costo_ha": 20000,  "rendimiento": 23.05},
}

compatibilidad = {
    "Húmedo / Cálido":        ["Tomate rojo (jitomate)", "Papaya", "Nopalitos", "Pepino", "Caña de azúcar"],
    "Húmedo / Templado":      ["Tomate rojo (jitomate)", "Fresa", "Pepino", "Brócoli", "Zanahoria"],
    "Húmedo / Frío":          ["Fresa", "Brócoli", "Papa", "Zanahoria", "Lechuga"],
    "Semi-húmedo / Cálido":   ["Tomate rojo (jitomate)", "Pepino", "Sandía", "Melón", "Nopalitos"],
    "Semi-húmedo / Templado": ["Tomate rojo (jitomate)", "Fresa", "Papa", "Cebolla", "Zanahoria"],
    "Semi-húmedo / Frío":     ["Papa", "Brócoli", "Zanahoria", "Lechuga", "Fresa"],
    "Seco / Cálido":          ["Nopalitos", "Sandía", "Melón", "Pepino", "Espárrago"],
    "Seco / Templado":        ["Nopalitos", "Sandía", "Cebolla", "Papa"],
}

PLOT_CONFIG = dict(
    paper_bgcolor="#0D1B2A",
    plot_bgcolor="#112233",
    font_color="#B0BEC5",
    margin=dict(t=40, b=30, l=10, r=10)
)

@st.cache_data
def load_data_engine():
    df_agro = pd.read_csv("data/processed/cultivos_2025.csv")
    df_clima = pd.read_csv("data/processed/clima_estados_2025.csv")
    df_agro = df_agro[df_agro["es_flor"] == False].copy()

    def get_climate_profile(row):
        h = "Húmedo" if row["precipitacion_anual_mm"] >= 1000 else "Semi-húmedo" if row["precipitacion_anual_mm"] >= 500 else "Seco"
        t = "Cálido" if row["temp_media_anual_c"] >= 24 else "Templado" if row["temp_media_anual_c"] >= 18 else "Frío"
        return f"{h} / {t}"

    df_clima["perfil"] = df_clima.apply(get_climate_profile, axis=1)
    
    m_rend = df_agro["rendimiento"].mean()
    m_risk = df_agro["tasa_siniestro_pct"].mean()
    
    def get_quadrant(row):
        if row["rendimiento"] > m_rend:
            return "Alta Producción / Bajo Riesgo" if row["tasa_siniestro_pct"] <= m_risk else "Alta Producción / Alto Riesgo"
        return "Baja Producción / Bajo Riesgo" if row["tasa_siniestro_pct"] <= m_risk else "Baja Producción / Alto Riesgo"

    df_agro["cuadrante"] = df_agro.apply(get_quadrant, axis=1)
    return df_agro, df_clima

df_agro, df_clima = load_data_engine()

# --- Interfaz Principal ---
st.markdown("""
<div class="dash-header">
    <div class="dash-title">Agrovita: Inteligencia para Diversificación de Cultivos</div>
    <div style="font-size:11px; color:#546E7A">URNC · EQUIPO 4 · 2026</div>
</div>
""", unsafe_allow_html=True)

col_f1, _ = st.columns([1.2, 3])
with col_f1:
    estado_sel = st.selectbox("Entidad Federativa", sorted(df_clima["estado"].tolist()))

# Lógica de Negocio: Cálculo de Rentabilidad
estado_info = df_clima[df_clima["estado"] == estado_sel].iloc[0]
perfil = estado_info["perfil"]
cultivos_viables = [c for c in compatibilidad.get(perfil, []) if c in datos_financieros]

maiz_data = datos_financieros["Maíz grano"]
maiz_margin = (maiz_data["precio_ton"] * maiz_data["rendimiento"]) - maiz_data["costo_ha"]

if cultivos_viables:
    mejor_opcion = max(cultivos_viables, key=lambda x: (datos_financieros[x]["precio_ton"] * datos_financieros[x]["rendimiento"]) - datos_financieros[x]["costo_ha"])
    fin_opcion = datos_financieros[mejor_opcion]
    utilidad = (fin_opcion["precio_ton"] * fin_opcion["rendimiento"]) - fin_opcion["costo_ha"]
    vol_vs_maiz = fin_opcion["rendimiento"] / maiz_data["rendimiento"]
else:
    mejor_opcion, utilidad, vol_vs_maiz = "Maíz grano", maiz_margin, 1.0

# KPIs Dinámicos
st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card"><div class="kpi-label">Perfil Climático</div><div class="kpi-value">{perfil}</div></div>
    <div class="kpi-card"><div class="kpi-label">Recomendación Primaria</div><div class="kpi-value accent">{mejor_opcion}</div></div>
    <div class="kpi-card"><div class="kpi-label">Ganancia Neta / Ha</div><div class="kpi-value accent">${utilidad:,.0f} MXN</div></div>
    <div class="kpi-card"><div class="kpi-label">Volumen vs Maíz</div><div class="kpi-value accent">{vol_vs_maiz:.1f}x Ton</div></div>
</div>
<div class="rec-banner">
    Análisis Estratégico: En <strong>{estado_sel}</strong>, la transición a <strong>{mejor_opcion}</strong> incrementa la utilidad proyectada a <strong>${utilidad:,.0f} MXN</strong> por ciclo hectárea.
</div>
""", unsafe_allow_html=True)

# --- Contenedor Lateral (Ajuste de ratio para pantallas 768p) ---
col_left, col_right = st.columns([1.3, 2])

with col_left:
    st.markdown('<div class="section-label">Ranking de Rentabilidad</div>', unsafe_allow_html=True)
    if cultivos_viables:
        df_rank = pd.DataFrame([
            {"Cultivo": c, 
             "Ganancia/Ha": (datos_financieros[c]["precio_ton"] * datos_financieros[c]["rendimiento"]) - datos_financieros[c]["costo_ha"],
             "vs Maíz": f"{(datos_financieros[c]['rendimiento'] / maiz_data['rendimiento']):.1f}x"} 
            for c in cultivos_viables
        ]).sort_values("Ganancia/Ha", ascending=False).reset_index(drop=True)
        
        df_rank.insert(0, "Rank", range(1, len(df_rank)+1))
        df_rank["Rank"] = df_rank["Rank"].apply(lambda x: f"#{x}")
        df_rank["Ganancia/Ha"] = df_rank["Ganancia/Ha"].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(df_rank, use_container_width=True, hide_index=True, height=250)

    st.markdown('<div class="section-label">Variables Climáticas (CONAGUA)</div>', unsafe_allow_html=True)
    df_env = pd.DataFrame({
        "Variable": ["Precipitación Anual", "Temp. Media", "Máxima Abs."],
        "Valor": [f"{estado_info['precipitacion_anual_mm']:.0f} mm", f"{estado_info['temp_media_anual_c']:.1f} °C", f"{estado_info['temp_maxima_anual_c']:.1f} °C"]
    })
    st.table(df_env)

with col_right:
    t1, t2, t3 = st.tabs(["Rendimiento", "Finanzas", "Riesgo"])
    
    with t1:
        c_list = cultivos_viables + ["Maíz grano"]
        df_v1 = df_agro[df_agro["cultivo"].isin(c_list)].sort_values("rendimiento")
        fig1 = px.bar(df_v1, x="rendimiento", y="cultivo", orientation='h', template="plotly_dark",
                     color_discrete_sequence=["#1976D2"])
        fig1.update_layout(**PLOT_CONFIG)
        st.plotly_chart(fig1, use_container_width=True)

    with t2:
        df_v2 = pd.DataFrame([{"c": c, "util": (datos_financieros[c]["precio_ton"] * datos_financieros[c]["rendimiento"]) - datos_financieros[c]["costo_ha"]} for c in cultivos_viables])
        fig2 = px.bar(df_v2, x="util", y="c", template="plotly_dark", color_discrete_sequence=["#00E676"])
        fig2.add_vline(x=maiz_margin, line_dash="dash", line_color="#EF5350")
        fig2.update_layout(**PLOT_CONFIG)
        st.plotly_chart(fig2, use_container_width=True)

    with t3:
        fig3 = px.scatter(df_agro, x="tasa_siniestro_pct", y="rendimiento", color="cuadrante",
                         hover_name="cultivo", template="plotly_dark")
        fig3.update_layout(**PLOT_CONFIG)
        st.plotly_chart(fig3, use_container_width=True)

# --- Generador de PDF (Tema McKinsey / Azul Corporativo) ---
def generate_corporate_pdf(estado, perfil, mejor, util, vol, df_rank):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=0.7*inch, rightMargin=0.7*inch, topMargin=0.7*inch)
    styles = getSampleStyleSheet()
    
    c_navy = colors.HexColor("#0A2540")
    c_blue = colors.HexColor("#1976D2")
    
    s_title = ParagraphStyle("T", parent=styles["Title"], fontSize=20, textColor=c_navy, spaceAfter=10)
    s_body = ParagraphStyle("B", parent=styles["Normal"], fontSize=11, leading=14)
    s_sec = ParagraphStyle("S", parent=styles["Heading2"], fontSize=13, textColor=c_blue, spaceBefore=15)

    elements = [
        Paragraph("Reporte de Inteligencia Agrícola", s_title),
        Paragraph(f"Análisis Técnico-Financiero · {estado} · 2026", styles["Normal"]),
        Spacer(1, 15),
        Paragraph("Resumen Ejecutivo", s_sec),
        Paragraph(f"Bajo un perfil climático <b>{perfil}</b>, se identifica a <b>{mejor}</b> como el activo biológico de mayor viabilidad. "
                  f"La proyección de utilidad neta se estima en <b>${util:,.0f} MXN/Ha</b>, con una eficiencia productiva <b>{vol:.1f} veces superior</b> al maíz.", s_body),
        Spacer(1, 15),
        Paragraph("Comparativa de Rentabilidad", s_sec)
    ]

    if not df_rank.empty:
        data = [df_rank.columns.tolist()] + df_rank.values.tolist()
        t = Table(data, colWidths=[0.6*inch, 2.2*inch, 1.5*inch, 1.2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.white])
        ]))
        elements.append(t)

    elements.append(Paragraph("<br/><br/><i>Fuentes: SIAP, CONAGUA, FIRA. Análisis generado por Agrovita URNC.</i>", styles["Italic"]))
    doc.build(elements)
    buf.seek(0)
    return buf

st.divider()
if st.download_button("Exportar Dictamen Técnico (PDF)", 
                      data=generate_corporate_pdf(estado_sel, perfil, mejor_opcion, utilidad, vol_vs_maiz, df_rank if cultivos_viables else pd.DataFrame()), 
                      file_name=f"Dictamen_{estado_sel}.pdf", mime="application/pdf"):
    st.success("Reporte generado exitosamente.")

st.markdown('<div style="text-align:center; font-size:10px; color:#546E7A; padding-top:20px">URNC · Licenciatura en Ciencia de Datos para Negocios · 2026</div>', unsafe_allow_html=True)