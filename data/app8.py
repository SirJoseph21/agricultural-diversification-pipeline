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

# ── Configuración inicial ──────────────────────────────────────
st.set_page_config(
    page_title="Diversificación Agrícola · México",
    page_icon="🌱",
    layout="wide"
)

# ── CSS global — aspecto dashboard (CON OPTIMIZACIÓN ANDROID) ──
st.markdown("""
<style>
    .stApp { background-color: #0D1B2A; color: #E0E0E0; }
    [data-testid="stSidebar"] { display: none; }

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
    .dash-subtitle { font-size: 12px; color: #90A4AE; }

    .filter-label {
        font-size: 11px;
        color: #B0BEC5;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        white-space: nowrap;
        margin-bottom: 4px;
    }

    /* ── MAGIA ANDROID: auto-fit para que no se aplasten en móvil ── */
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
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 20px;
        font-weight: 700;
        color: #E0E0E0;
        line-height: 1.1;
    }
    .kpi-value.accent { color: #00E676; }
    .kpi-sub { font-size: 10px; color: #90A4AE; margin-top: 2px; }

    .rec-banner {
        background: #0A2A1A;
        border-left: 3px solid #00E676;
        border-radius: 0 4px 4px 0;
        padding: 12px 16px;
        margin-bottom: 14px;
        font-size: 14px;
        color: #B0BEC5;
    }
    .rec-banner strong { color: #00E676; font-size: 16px; }

    .section-label {
        font-size: 10px;
        color: #90A4AE;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
        border-bottom: 1px solid #1E3A5F;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #112233;
        border-bottom: 1px solid #1E3A5F;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 11px;
        color: #546E7A;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 8px 16px;
        border-radius: 0;
    }
    .stTabs [aria-selected="true"] {
        color: #00E676 !important;
        border-bottom: 2px solid #00E676 !important;
        background: transparent !important;
    }

    .dash-footer {
        font-size: 10px;
        color: #546E7A;
        border-top: 1px solid #1E3A5F;
        padding-top: 8px;
        margin-top: 16px;
    }

    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Datos financieros ─────────────────────────────────────────
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

PLOT_LAYOUT = dict(
    paper_bgcolor="#0D1B2A",
    plot_bgcolor="#112233",
    font_color="#B0BEC5",
    font_size=11,
    margin=dict(t=36, b=28, l=8, r=8),
    legend=dict(bgcolor="#0D1B2A", bordercolor="#1E3A5F", borderwidth=1, font_size=10),
)

# ── Cargar datos ──────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df_cultivos = pd.read_csv("data/processed/cultivos_2025.csv")
    df_clima    = pd.read_csv("data/processed/clima_estados_2025.csv")
    df_agro     = df_cultivos[df_cultivos["es_flor"] == False].copy()

    def clasificar_clima(row):
        humedad = "Húmedo" if row["precipitacion_anual_mm"] >= 1000 else \
                  "Semi-húmedo" if row["precipitacion_anual_mm"] >= 500 else "Seco"
        temp    = "Cálido" if row["temp_media_anual_c"] >= 24 else \
                  "Templado" if row["temp_media_anual_c"] >= 18 else "Frío"
        return f"{humedad} / {temp}"

    df_clima["perfil_climatico"] = df_clima.apply(clasificar_clima, axis=1)

    prom_rend      = df_agro["rendimiento"].mean()
    prom_siniestro = df_agro["tasa_siniestro_pct"].mean()

    def clasificar_cuadrante(row):
        alto_rend   = row["rendimiento"] > prom_rend
        bajo_riesgo = row["tasa_siniestro_pct"] <= prom_siniestro
        if   alto_rend and     bajo_riesgo: return "Alta producción / Bajo riesgo"
        elif alto_rend and not bajo_riesgo: return "Alta producción / Alto riesgo"
        elif not alto_rend and bajo_riesgo: return "Baja producción / Bajo riesgo"
        else:                               return "Baja producción / Alto riesgo"

    df_agro["cuadrante"] = df_agro.apply(clasificar_cuadrante, axis=1)
    return df_agro, df_clima

df_agro, df_clima = cargar_datos()

# ════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="dash-header">
  <div>
    <div class="dash-title">¿Qué puedo sembrar en mi estado?</div>
    <div class="dash-subtitle">Cultivos alternativos al maíz con mayor ganancia · SIAP / CONAGUA / SIACON 2024-2026</div>
  </div>
  <div class="dash-subtitle">Universidad Rosario Castellanos — LCDN · Equipo 4 · 2026</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# FILTRO HORIZONTAL
# ════════════════════════════════════════════════════════════
col_f1, col_f2 = st.columns([1, 4])
with col_f1:
    st.markdown('<div class="filter-label">Selecciona tu estado</div>', unsafe_allow_html=True)
    estado_sel = st.selectbox(
        "", sorted(df_clima["estado"].tolist()), label_visibility="collapsed"
    )

# ════════════════════════════════════════════════════════════
# DATOS DEL ESTADO
# ════════════════════════════════════════════════════════════
estado_data  = df_clima[df_clima["estado"] == estado_sel].iloc[0]
perfil       = estado_data["perfil_climatico"]
cultivos_rec = compatibilidad.get(perfil, [])
maiz_rend    = df_agro[df_agro["cultivo"] == "Maíz grano"]["rendimiento"].values[0]
maiz_margen  = (datos_financieros["Maíz grano"]["precio_ton"] *
                datos_financieros["Maíz grano"]["rendimiento"] -
                datos_financieros["Maíz grano"]["costo_ha"])

cultivos_con_margen = [c for c in cultivos_rec if c in datos_financieros]
if cultivos_con_margen:
    mejor_cultivo = max(
        cultivos_con_margen,
        key=lambda x: datos_financieros[x]["precio_ton"] * datos_financieros[x]["rendimiento"] - datos_financieros[x]["costo_ha"]
    )
    mejor_rend   = df_agro[df_agro["cultivo"] == mejor_cultivo]["rendimiento"].values[0]
    mejor_margen = (datos_financieros[mejor_cultivo]["precio_ton"] *
                    datos_financieros[mejor_cultivo]["rendimiento"] -
                    datos_financieros[mejor_cultivo]["costo_ha"])
    veces_maiz   = mejor_rend / maiz_rend
else:
    mejor_cultivo = "N/D"
    mejor_rend = mejor_margen = veces_maiz = 0

# ════════════════════════════════════════════════════════════
# KPI ROW — 4 indicadores clave
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">Tipo de clima</div>
    <div class="kpi-value" style="font-size:14px">{perfil}</div>
    <div class="kpi-sub">{estado_sel}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Mejor cultivo para sembrar</div>
    <div class="kpi-value accent" style="font-size:16px">{mejor_cultivo}</div>
    <div class="kpi-sub">recomendado para tu clima</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Ganancia estimada por hectárea</div>
    <div class="kpi-value accent">${mejor_margen:,.0f}</div>
    <div class="kpi-sub">pesos mexicanos</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Volumen vs Maíz</div>
    <div class="kpi-value accent">{veces_maiz:.1f}x</div>
    <div class="kpi-sub">toneladas por hectárea</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# BANNER DE RECOMENDACIÓN
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="rec-banner">
  Para <strong>{estado_sel}</strong> recomendamos cambiar a <strong>{mejor_cultivo}</strong> —
  puedes ganar <strong>${mejor_margen:,.0f} pesos libres por hectárea</strong>,
  produciendo un volumen <strong>{veces_maiz:.1f} veces mayor</strong> en toneladas comparado al maíz.
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL — tabla izquierda / gráficas derecha
# ════════════════════════════════════════════════════════════
col_tabla, col_graficas = st.columns([1, 2.5])

# Inicializamos df_rec vacío por seguridad
df_rec = pd.DataFrame() 

with col_tabla:
    st.markdown('<div class="section-label">Cultivos recomendados</div>', unsafe_allow_html=True)

    if cultivos_rec:
        df_rec = df_agro[df_agro["cultivo"].isin(cultivos_rec)][["cultivo", "rendimiento"]].copy()
        
        df_rec["costo_ha"] = df_rec["cultivo"].apply(
            lambda x: datos_financieros[x]["costo_ha"] if x in datos_financieros else None
        )
        df_rec["ganancia_ha"] = df_rec["cultivo"].apply(
            lambda x: (datos_financieros[x]["precio_ton"] * datos_financieros[x]["rendimiento"]) - datos_financieros[x]["costo_ha"]
            if x in datos_financieros else None
        )
        
        df_rec["vs_maiz"] = (df_rec["rendimiento"] / maiz_rend).round(1).astype(str) + "x"
        
        # ── LA MAGIA DE LA LIMPIEZA: Eliminamos cultivos sin datos financieros ──
        df_rec = df_rec.dropna(subset=["ganancia_ha"])
        
        if not df_rec.empty:
            # 1. Ordenamos por ganancia (el que más gana va arriba)
            df_rec = df_rec.sort_values("ganancia_ha", ascending=False).reset_index(drop=True)
            
            # 2. Formateo de moneda
            df_rec["costo_ha"] = df_rec["costo_ha"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/D")
            df_rec["ganancia_ha"] = df_rec["ganancia_ha"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/D")
            
            # 3. Magia del Ranking
            df_rec.insert(0, "Top", range(1, len(df_rec) + 1))
            df_rec["Top"] = df_rec["Top"].apply(lambda x: f"#{x}")
            
            # 4. Renombramos columnas
            df_rec.columns = ["Top", "Cultivo", "Producción (t/ha)", "Inversión/ha", "Ganancia/ha", "Vol. vs Maíz"]
            
            # 5. Imprimimos ocultando el índice del sistema
            st.dataframe(df_rec, use_container_width=True, height=230, hide_index=True)
        else:
            st.warning("No hay datos financieros registrados para este perfil climático.")
    else:
        st.warning("No hay datos financieros registrados para este perfil climático.")

    # ── Tabla de clima ──
    st.markdown('<div class="section-label" style="margin-top:12px">Clima de tu estado</div>', unsafe_allow_html=True)
    df_clima_tabla = pd.DataFrame({
        "Indicador": ["Lluvia anual", "Temp. media", "Temp. máxima", "Temp. mínima"],
        "Tu estado": [
            f"{estado_data['precipitacion_anual_mm']:.0f} mm",
            f"{estado_data['temp_media_anual_c']:.1f} °C",
            f"{estado_data['temp_maxima_anual_c']:.1f} °C",
            f"{estado_data['temp_minima_anual_c']:.1f} °C",
        ],
        "Promedio nacional": [
            f"{df_clima['precipitacion_anual_mm'].mean():.0f} mm",
            f"{df_clima['temp_media_anual_c'].mean():.1f} °C",
            f"{df_clima['temp_maxima_anual_c'].mean():.1f} °C",
            f"{df_clima['temp_minima_anual_c'].mean():.1f} °C",
        ]
    })
    st.dataframe(df_clima_tabla, use_container_width=True, height=180, hide_index=True)

with col_graficas:
    tab1, tab2, tab3 = st.tabs([
        "🌾 ¿Cuánto produce?",
        "💰 ¿Cuánto gana?",
        "⚠️ ¿Qué tan seguro es?"
    ])

    with tab1:
        st.caption("La barra roja es el maíz — todo lo que la supera produce más toneladas por hectárea.")
        cultivos_graf = cultivos_rec + ["Maíz grano"]
        df_bar = df_agro[df_agro["cultivo"].isin(cultivos_graf)].sort_values("rendimiento", ascending=True).copy()
        df_bar["color"] = df_bar["cultivo"].apply(
            lambda x: "Maíz (referencia)" if x == "Maíz grano" else "Cultivo recomendado"
        )
        fig1 = px.bar(
            df_bar, x="rendimiento", y="cultivo", color="color",
            color_discrete_map={"Maíz (referencia)": "#EF5350", "Cultivo recomendado": "#42A5F5"},
            labels={"rendimiento": "Producción (toneladas por hectárea)", "cultivo": ""},
            orientation="h", template="plotly_dark"
        )
        fig1.update_layout(**PLOT_LAYOUT, legend_title="")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.caption("Los cultivos a la derecha de la línea roja dejan más ganancia que el maíz.")
        cultivos_fin = [c for c in cultivos_rec if c in datos_financieros]
        df_fin_graf = pd.DataFrame([
            {"cultivo": c,
             "ganancia": datos_financieros[c]["precio_ton"] * datos_financieros[c]["rendimiento"] - datos_financieros[c]["costo_ha"]}
            for c in cultivos_fin
        ]).sort_values("ganancia", ascending=True)

        fig2 = px.bar(
            df_fin_graf, x="ganancia", y="cultivo",
            color_discrete_sequence=["#42A5F5"],
            labels={"ganancia": "Ganancia por hectárea (pesos)", "cultivo": ""},
            orientation="h", template="plotly_dark"
        )
        fig2.add_vline(x=maiz_margen, line_dash="dash", line_color="#EF5350", line_width=2,
                       annotation_text=f"Maíz: ${maiz_margen:,.0f}/ha",
                       annotation_position="top right", annotation_font_color="#EF5350")
        fig2.update_layout(**PLOT_LAYOUT, legend_title="")
        fig2.update_xaxes(tickformat="$,.0f")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.caption("Lo ideal está arriba a la izquierda: produce mucho y tiene bajo riesgo de perder la cosecha. Pasa el cursor sobre ⭐ para ver los cultivos recomendados.")
        colores_map = {
            "Alta producción / Bajo riesgo": "#42A5F5",
            "Alta producción / Alto riesgo": "#EF5350",
            "Baja producción / Bajo riesgo": "#546E7A",
            "Baja producción / Alto riesgo": "#FFA726"
        }
        fig3 = px.scatter(
            df_agro, x="tasa_siniestro_pct", y="rendimiento",
            color="cuadrante", hover_name="cultivo",
            color_discrete_map=colores_map,
            labels={
                "tasa_siniestro_pct": "Riesgo de perder la cosecha (%)",
                "rendimiento": "Producción (toneladas por hectárea)",
                "cuadrante": ""
            },
            template="plotly_dark"
        )
        prom_s = df_agro["tasa_siniestro_pct"].mean()
        prom_r = df_agro["rendimiento"].mean()
        fig3.add_vline(x=prom_s, line_dash="dot", line_color="#546E7A", line_width=1,
                       annotation_text=f"{prom_s:.1f}%", annotation_font_color="#546E7A", annotation_font_size=9)
        fig3.add_hline(y=prom_r, line_dash="dot", line_color="#546E7A", line_width=1,
                       annotation_text=f"{prom_r:.1f} t/ha", annotation_font_color="#546E7A", annotation_font_size=9)
        df_highlight = df_agro[df_agro["cultivo"].isin(cultivos_rec)]
        fig3.add_scatter(
            x=df_highlight["tasa_siniestro_pct"], y=df_highlight["rendimiento"],
            mode="markers",
            marker=dict(size=13, color="#00E676", symbol="star"),
            customdata=df_highlight[["cultivo"]],
            hovertemplate="<b>%{customdata[0]}</b><br>Riesgo: %{x:.1f}%<br>Producción: %{y:.1f} t/ha<extra></extra>",
            name="Recomendados"
        )
        fig3.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════
# BOTÓN DE DESCARGA — REPORTE PDF
# ════════════════════════════════════════════════════════════
def generar_reporte_pdf(estado, perfil, mejor_cultivo, mejor_margen, veces_maiz, maiz_margen, df_rec):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle("titulo", parent=styles["Title"],
                                   fontSize=18, textColor=colors.HexColor("#1B5E20"),
                                   spaceAfter=4)
    estilo_subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"],
                                      fontSize=10, textColor=colors.HexColor("#546E7A"),
                                      spaceAfter=16)
    estilo_seccion = ParagraphStyle("seccion", parent=styles["Heading2"],
                                    fontSize=12, textColor=colors.HexColor("#1B5E20"),
                                    spaceBefore=14, spaceAfter=6,
                                    borderPad=4)
    estilo_cuerpo = ParagraphStyle("cuerpo", parent=styles["Normal"],
                                   fontSize=11, leading=16, spaceAfter=6)
    estilo_destacado = ParagraphStyle("destacado", parent=styles["Normal"],
                                      fontSize=13, textColor=colors.HexColor("#1B5E20"),
                                      fontName="Helvetica-Bold", spaceAfter=8)
    estilo_nota = ParagraphStyle("nota", parent=styles["Normal"],
                                 fontSize=8, textColor=colors.HexColor("#888888"),
                                 spaceBefore=24)

    historia = []

    historia.append(Paragraph("Recomendación de Cultivos", estilo_titulo))
    historia.append(Paragraph(f"Diversificación Agrícola · {estado} · 2026", estilo_subtitulo))

    # Separador
    historia.append(Table([[""]], colWidths=[6.4*inch],
                           style=[("LINEBELOW", (0,0), (-1,-1), 1, colors.HexColor("#1B5E20"))]))
    historia.append(Spacer(1, 12))

    # Bloque principal
    historia.append(Paragraph("Resumen para el productor", estilo_seccion))
    historia.append(Paragraph(
        f"Su estado <b>{estado}</b> tiene un clima de tipo <b>{perfil}</b>. "
        f"Con base en ese clima, el cultivo que más ganancia le puede dejar es:",
        estilo_cuerpo
    ))
    historia.append(Paragraph(f"→ {mejor_cultivo}", estilo_destacado))
    historia.append(Paragraph(
        f"Sembrando <b>{mejor_cultivo}</b> puede ganar aproximadamente "
        f"<b>${mejor_margen:,.0f} pesos libres por hectárea</b>, "
        f"con un volumen de producción <b>{veces_maiz:.1f} veces mayor</b> al del maíz "
        f"(${maiz_margen:,.0f}/ha).",
        estilo_cuerpo
    ))

    historia.append(Spacer(1, 10))

    # Tabla de cultivos
    historia.append(Paragraph("Cultivos recomendados para su estado", estilo_seccion))
    
    if not df_rec.empty:
        historia.append(Paragraph(
            "En la siguiente tabla se muestran todos los cultivos que funcionan bien "
            "en su tipo de clima, priorizados por rentabilidad y requerimiento de capital:",
            estilo_cuerpo
        ))
        historia.append(Spacer(1, 6))

        tabla_datos = [["Top", "Cultivo", "Prod. (t/ha)", "Inv./ha", "Ganancia/ha", "vs Maíz"]]
        for _, row in df_rec.iterrows():
            tabla_datos.append([
                row["Top"],
                row["Cultivo"],
                str(row["Producción (t/ha)"]),
                row["Inversión/ha"],
                row["Ganancia/ha"],
                row["Vol. vs Maíz"]
            ])

        tabla = Table(tabla_datos, colWidths=[0.5*inch, 1.8*inch, 1.1*inch, 1.2*inch, 1.3*inch, 1.0*inch])
        tabla.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#1B5E20")),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0),  10),
            ("FONTSIZE",    (0, 1), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F1F8E9"), colors.white]),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#C8E6C9")),
            ("ALIGN",       (2, 0), (-1, -1), "CENTER"), # Alinear números al centro
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ROWHEIGHT",   (0, 0), (-1, -1), 22),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]))
        historia.append(tabla)
    else:
        historia.append(Paragraph(
            "Actualmente no hay un registro de cultivos viables financieramente para "
            "el perfil climatológico exacto de esta entidad.", estilo_cuerpo
        ))

    historia.append(Spacer(1, 10))

    # Clima
    historia.append(Paragraph("Condiciones climáticas de su estado", estilo_seccion))
    historia.append(Paragraph(
        f"Lluvia anual: <b>{estado_data['precipitacion_anual_mm']:.0f} mm</b> &nbsp;·&nbsp; "
        f"Temperatura media: <b>{estado_data['temp_media_anual_c']:.1f} °C</b> &nbsp;·&nbsp; "
        f"Máxima: <b>{estado_data['temp_maxima_anual_c']:.1f} °C</b> &nbsp;·&nbsp; "
        f"Mínima: <b>{estado_data['temp_minima_anual_c']:.1f} °C</b>",
        estilo_cuerpo
    ))

    # Nota al pie
    historia.append(Paragraph(
        "Fuentes: SIAP 2025-2026 · SIACON 2024 · CONAGUA 2025 · FIRA/SAGARPA (costos de referencia)  "
        "Universidad Rosario Castellanos — LCDN · Equipo 4 · 2026  "
        "Los valores de ganancia son estimaciones basadas en precios promedio de mercado.",
        estilo_nota
    ))

    doc.build(historia)
    buffer.seek(0)
    return buffer

st.divider()

col_btn, _ = st.columns([1, 3])
with col_btn:
    # Aseguramos que al exportar a PDF, tampoco haya nulos estorbando
    df_rec_pdf = df_rec.dropna(subset=["Ganancia/ha"]) if not df_rec.empty else df_rec
    
    pdf_buffer = generar_reporte_pdf(
        estado_sel, perfil, mejor_cultivo, mejor_margen,
        veces_maiz, maiz_margen, df_rec_pdf
    )
    st.download_button(
        label="Descargar resumen en PDF",
        data=pdf_buffer,
        file_name=f"recomendacion_{estado_sel.lower().replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# ════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="dash-footer">
  Fuentes: SIAP 2025-2026 · SIACON 2024 · CONAGUA 2025 · FIRA/SAGARPA (costos de referencia) &nbsp;·&nbsp;
  Universidad Rosario Castellanos — LCDN · Equipo 4 · 2026
</div>
""", unsafe_allow_html=True)