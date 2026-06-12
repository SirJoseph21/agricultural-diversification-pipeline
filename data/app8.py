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

st.set_page_config(
    page_title="Diversificación Agrícola · México",
    page_icon="🌱",
    layout="wide"
)

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

    .kpi-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
        margin-bottom: 14px;
    }

    [data-testid="stDataFrame"] {
        overflow-x: auto !important;
    }
    [data-testid="stDataFrame"] > div {
        min-width: 580px;
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

st.markdown("""
<div class="dash-header">
  <div>
    <div class="dash-title">¿Qué puedo sembrar en mi estado?</div>
    <div class="dash-subtitle">Cultivos alternativos al maíz con mayor ganancia · SIAP / CONAGUA / SIACON 2024-2026</div>
  </div>
  <div class="dash-subtitle">Universidad Rosario Castellanos — LCDN · Equipo 4 · 2026</div>
</div>
""", unsafe_allow_html=True)

col_f1, col_f2 = st.columns([1, 4])
with col_f1:
    st.markdown('<div class="filter-label">Selecciona tu estado</div>', unsafe_allow_html=True)
    estado_sel = st.selectbox(
        "", sorted(df_clima["estado"].tolist()), label_visibility="collapsed"
    )

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

st.markdown(f"""
<div class="rec-banner">
  Para <strong>{estado_sel}</strong> recomendamos cambiar a <strong>{mejor_cultivo}</strong> —
  puedes ganar <strong>${mejor_margen:,.0f} pesos libres por hectárea</strong>,
  produciendo un volumen <strong>{veces_maiz:.1f} veces mayor</strong> en toneladas comparado al maíz.
</div>
""", unsafe_allow_html=True)

col_tabla, col_graficas = st.columns([1.4, 2.6])
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
        df_rec = df_rec.dropna(subset=["ganancia_ha"])
        
        if not df_rec.empty:
            df_rec = df_rec.sort_values("ganancia_ha", ascending=False).reset_index(drop=True)
            df_rec["costo_ha"] = df_rec["costo_ha"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/D")
            df_rec["ganancia_ha"] = df_rec["ganancia_ha"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/D")
            
            df_rec.insert(0, "Top", range(1, len(df_rec) + 1))
            df_rec["Top"] = df_rec["Top"].apply(lambda x: f"#{x}")
            df_rec.columns = ["#", "Cultivo", "t/ha", "Inv/ha", "Gan/ha", "vs Maíz"]
            
            st.dataframe(
                df_rec,
                width="stretch",
                height=230,
                hide_index=True,
                column_config={
                    "#": st.column_config.TextColumn(width="small"),
                    "Cultivo": st.column_config.TextColumn(width="medium"),
                    "t/ha": st.column_config.TextColumn(width="small"),
                    "Inv/ha": st.column_config.TextColumn(width="small"),
                    "Gan/ha": st.column_config.TextColumn(width="small"),
                    "vs Maíz": st.column_config.TextColumn(width="small"),
                }
            )
        else:
            st.warning("No hay datos financieros registrados para este perfil climático.")
    else:
        st.warning("No hay datos financieros registrados para este perfil climático.")

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
    st.dataframe(df_clima_tabla, width="stretch", height=180, hide_index=True)

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

def generar_reporte_pdf(estado, perfil, mejor_cultivo, mejor_margen, veces_maiz, maiz_margen, df_rec):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            leftMargin=0.8*inch, rightMargin=0.8*inch,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()

    color_primario = colors.HexColor("#0A2540")   
    color_secundario = colors.HexColor("#1976D2") 
    color_gris = colors.HexColor("#546E7A")       
    color_fondo_fila = colors.HexColor("#F0F4F8") 
    color_borde = colors.HexColor("#CFD8DC")      

    estilo_titulo = ParagraphStyle("titulo", parent=styles["Title"],
                                   fontSize=18, textColor=color_primario,
                                   spaceAfter=4)
    estilo_subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"],
                                      fontSize=10, textColor=color_gris,
                                      spaceAfter=16)
    estilo_seccion = ParagraphStyle("seccion", parent=styles["Heading2"],
                                    fontSize=12, textColor=color_secundario,
                                    spaceBefore=14, spaceAfter=6,
                                    borderPad=4)
    estilo_cuerpo = ParagraphStyle("cuerpo", parent=styles["Normal"],
                                   fontSize=11, leading=16, spaceAfter=6)
    estilo_destacado = ParagraphStyle("destacado", parent=styles["Normal"],
                                      fontSize=13, textColor=color_primario,
                                      fontName="Helvetica-Bold", spaceAfter=8)
    estilo_nota = ParagraphStyle("nota", parent=styles["Normal"],
                                 fontSize=8, textColor=colors.HexColor("#888888"),
                                 spaceBefore=24)

    historia = []

    historia.append(Paragraph("Reporte de Inteligencia Agrícola", estilo_titulo))
    historia.append(Paragraph(f"Análisis de Diversificación · {estado} · 2026", estilo_subtitulo))

    historia.append(Table([[""]], colWidths=[6.4*inch],
                           style=[("LINEBELOW", (0,0), (-1,-1), 1.5, color_secundario)]))
    historia.append(Spacer(1, 12))

    historia.append(Paragraph("Resumen Ejecutivo para el Productor", estilo_seccion))
    historia.append(Paragraph(
        f"La entidad federativa de <b>{estado}</b> presenta un perfil climatológico <b>{perfil}</b>. "
        f"De acuerdo con nuestro modelo financiero, el cultivo más rentable es:",
        estilo_cuerpo
    ))
    historia.append(Paragraph(f"→ {mejor_cultivo}", estilo_destacado))
    historia.append(Paragraph(
        f"La transición hacia <b>{mejor_cultivo}</b> proyecta una utilidad de "
        f"<b>${mejor_margen:,.0f} MXN libres por hectárea</b>. Esto representa "
        f"un volumen de producción <b>{veces_maiz:.1f} veces mayor</b> en contraste con el maíz tradicional "
        f"(${maiz_margen:,.0f}/ha).",
        estilo_cuerpo
    ))

    historia.append(Spacer(1, 10))

    historia.append(Paragraph("Ranking de Rentabilidad y Capital", estilo_seccion))
    
    if not df_rec.empty:
        historia.append(Paragraph(
            "Alternativas agrícolas viables para la región, ordenadas por margen de ganancia:",
            estilo_cuerpo
        ))
        historia.append(Spacer(1, 6))

        tabla_datos = [["Top", "Cultivo", "Prod. (t/ha)", "Inv./ha", "Ganancia/ha", "vs Maíz"]]
        for _, row in df_rec.iterrows():
            tabla_datos.append([
                row["#"],
                row["Cultivo"],
                str(row["t/ha"]),
                row["Inv/ha"],
                row["Gan/ha"],
                row["vs Maíz"]
            ])

        tabla = Table(tabla_datos, colWidths=[0.5*inch, 1.8*inch, 1.1*inch, 1.2*inch, 1.3*inch, 1.0*inch])
        tabla.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  color_primario),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0),  10),
            ("FONTSIZE",    (0, 1), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [color_fondo_fila, colors.white]),
            ("GRID",        (0, 0), (-1, -1), 0.5, color_borde),
            ("ALIGN",       (2, 0), (-1, -1), "CENTER"), 
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

    historia.append(Paragraph("Parámetros Climatológicos (Promedio Anual)", estilo_seccion))
    historia.append(Paragraph(
        f"Precipitación: <b>{estado_data['precipitacion_anual_mm']:.0f} mm</b> &nbsp;·&nbsp; "
        f"Temp. Media: <b>{estado_data['temp_media_anual_c']:.1f} °C</b> &nbsp;·&nbsp; "
        f"Máxima: <b>{estado_data['temp_maxima_anual_c']:.1f} °C</b> &nbsp;·&nbsp; "
        f"Mínima: <b>{estado_data['temp_minima_anual_c']:.1f} °C</b>",
        estilo_cuerpo
    ))

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
    df_rec_pdf = df_rec.dropna(subset=["Gan/ha"]) if not df_rec.empty else df_rec
    
    pdf_buffer = generar_reporte_pdf(
        estado_sel, perfil, mejor_cultivo, mejor_margen,
        veces_maiz, maiz_margen, df_rec_pdf
    )
    st.download_button(
        label="Descargar resumen en PDF",
        data=pdf_buffer,
        file_name=f"recomendacion_{estado_sel.lower().replace(' ', '_')}.pdf",
        mime="application/pdf",
        width="stretch"
    )

st.markdown("""
<div class="dash-footer">
  Fuentes: SIAP 2025-2026 · SIACON 2024 · CONAGUA 2025 · FIRA/SAGARPA (costos de referencia) &nbsp;·&nbsp;
  Universidad Rosario Castellanos — LCDN · Equipo 4 · 2026
</div>
""", unsafe_allow_html=True)