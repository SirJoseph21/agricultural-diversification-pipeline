import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Configuración de la página ────────────────────────────────
st.set_page_config(
    page_title="Diversificación Agrícola México",
    page_icon="🌱",
    layout="wide"
)

# ── Datos financieros por cultivo ─────────────────────────────
# Precios: SIACON 2024 | Costos: referencia FIRA/SAGARPA
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

# ── Compatibilidad clima-cultivo ──────────────────────────────
compatibilidad = {
    "Húmedo / Cálido":       ["Tomate rojo (jitomate)", "Papaya", "Nopalitos", "Pepino", "Caña de azúcar"],
    "Húmedo / Templado":     ["Tomate rojo (jitomate)", "Fresa", "Pepino", "Brócoli", "Zanahoria"],
    "Húmedo / Frío":         ["Fresa", "Brócoli", "Papa", "Zanahoria", "Lechuga"],
    "Semi-húmedo / Cálido":  ["Tomate rojo (jitomate)", "Pepino", "Sandía", "Melón", "Nopalitos"],
    "Semi-húmedo / Templado":["Tomate rojo (jitomate)", "Fresa", "Papa", "Cebolla", "Zanahoria"],
    "Semi-húmedo / Frío":    ["Papa", "Brócoli", "Zanahoria", "Lechuga", "Fresa"],
    "Seco / Cálido":         ["Nopalitos", "Sandía", "Melón", "Pepino", "Espárrago"],
    "Seco / Templado":       ["Nopalitos", "Espárrago", "Sandía", "Cebolla", "Papa"],
}

# ── Cargar datos ──────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df_cultivos = pd.read_csv("data/processed/cultivos_2025.csv")
    df_clima    = pd.read_csv("data/processed/clima_estados_2025.csv")
    df_agro     = df_cultivos[df_cultivos["es_flor"] == False].copy()

    def clasificar_clima(row):
        if row["precipitacion_anual_mm"] >= 1000:
            humedad = "Húmedo"
        elif row["precipitacion_anual_mm"] >= 500:
            humedad = "Semi-húmedo"
        else:
            humedad = "Seco"
        if row["temp_media_anual_c"] >= 24:
            temp = "Cálido"
        elif row["temp_media_anual_c"] >= 18:
            temp = "Templado"
        else:
            temp = "Frío"
        return f"{humedad} / {temp}"

    df_clima["perfil_climatico"] = df_clima.apply(clasificar_clima, axis=1)

    prom_rend      = df_agro["rendimiento"].mean()
    prom_siniestro = df_agro["tasa_siniestro_pct"].mean()

    def clasificar_cuadrante(row):
        alto_rend   = row["rendimiento"] > prom_rend
        bajo_riesgo = row["tasa_siniestro_pct"] <= prom_siniestro
        if alto_rend and bajo_riesgo:
            return "Alto rendimiento / Bajo riesgo"
        elif alto_rend and not bajo_riesgo:
            return "Alto rendimiento / Alto riesgo"
        elif not alto_rend and bajo_riesgo:
            return "Bajo rendimiento / Bajo riesgo"
        else:
            return "Bajo rendimiento / Alto riesgo"

    df_agro["cuadrante"] = df_agro.apply(clasificar_cuadrante, axis=1)
    return df_agro, df_clima

df_agro, df_clima = cargar_datos()

# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Mexico.svg/320px-Flag_of_Mexico.svg.png", width=80)
st.sidebar.title("🌱 Diversificación Agrícola")
st.sidebar.markdown("Sistema de recomendación de cultivos basado en datos del SIAP y CONAGUA 2025.")
st.sidebar.divider()

estado_sel = st.sidebar.selectbox(
    "Selecciona tu estado:",
    sorted(df_clima["estado"].tolist())
)

st.sidebar.divider()
st.sidebar.caption("Precios: SIACON 2024")
st.sidebar.caption("Producción: SIAP 2025-2026")
st.sidebar.caption("Clima: CONAGUA 2025")
st.sidebar.caption("Universidad Rosario Castellanos — LCDN 2026")

# ════════════════════════════════════════════════════════════
# ENCABEZADO
# ════════════════════════════════════════════════════════════
st.title("Diversificación Agrícola en México")
st.markdown(f"Resultados para: **{estado_sel}**")
st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 1 — Perfil climático del estado
# ════════════════════════════════════════════════════════════
estado_data = df_clima[df_clima["estado"] == estado_sel].iloc[0]
perfil      = estado_data["perfil_climatico"]

st.subheader("Perfil climático")
st.markdown(f"**Clasificación:** `{perfil}`")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Precipitación anual", f"{estado_data['precipitacion_anual_mm']:.1f} mm")
col2.metric("Temperatura media",   f"{estado_data['temp_media_anual_c']:.1f} °C")
col3.metric("Temperatura máxima",  f"{estado_data['temp_maxima_anual_c']:.1f} °C")
col4.metric("Temperatura mínima",  f"{estado_data['temp_minima_anual_c']:.1f} °C")

st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 2 — Datos base para el resto de la página
# ════════════════════════════════════════════════════════════
cultivos_rec = compatibilidad.get(perfil, [])
df_rec = df_agro[df_agro["cultivo"].isin(cultivos_rec)][
    ["cultivo", "rendimiento", "tasa_cosecha_pct", "tasa_siniestro_pct"]
].copy()

# Agregar datos financieros
df_rec["ingreso_bruto_ha"] = df_rec["cultivo"].apply(
    lambda x: datos_financieros[x]["precio_ton"] * datos_financieros[x]["rendimiento"]
    if x in datos_financieros else None
)
df_rec["costo_ha"] = df_rec["cultivo"].apply(
    lambda x: datos_financieros[x]["costo_ha"]
    if x in datos_financieros else None
)
df_rec["margen_ha"] = (df_rec["ingreso_bruto_ha"] - df_rec["costo_ha"]).round(0)

# Comparar vs maíz
maiz_rend = df_agro[df_agro["cultivo"] == "Maíz grano"]["rendimiento"].values[0]
df_rec["vs_maiz"] = (df_rec["rendimiento"] / maiz_rend).round(1).astype(str) + "x más"

# Ordenar por margen
df_rec = df_rec.sort_values("margen_ha", ascending=False).reset_index(drop=True)
df_rec.index += 1

# ════════════════════════════════════════════════════════════
# CONCLUSIÓN — arriba para que sea lo primero que se lea
# ════════════════════════════════════════════════════════════
cultivos_con_margen = [c for c in cultivos_rec if c in datos_financieros]
if cultivos_con_margen:
    mejor_cultivo = max(
        cultivos_con_margen,
        key=lambda x: datos_financieros[x]["precio_ton"] * datos_financieros[x]["rendimiento"] - datos_financieros[x]["costo_ha"]
    )
    mejor_rend   = df_agro[df_agro["cultivo"] == mejor_cultivo]["rendimiento"].values[0]
    mejor_margen = datos_financieros[mejor_cultivo]["precio_ton"] * datos_financieros[mejor_cultivo]["rendimiento"] - datos_financieros[mejor_cultivo]["costo_ha"]
    veces_maiz   = mejor_rend / maiz_rend

    st.success(
        f"✅ **Recomendación para {estado_sel}:** Cambia a **{mejor_cultivo}** — "
        f"genera **${mejor_margen:,.0f} por hectárea** ({veces_maiz:.1f}x más que el maíz)."
    )

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Mejor cultivo", mejor_cultivo)
    mc2.metric("Margen estimado/ha", f"${mejor_margen:,.0f}")
    mc3.metric("vs Maíz", f"{veces_maiz:.1f}x más rentable")
else:
    st.info(f"Para **{estado_sel}** con perfil **{perfil}**, consulta la tabla de cultivos recomendados.")

st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 3 — Tabla simplificada
# ════════════════════════════════════════════════════════════
st.subheader("Cultivos recomendados para este estado")
st.caption("Ordenados de mayor a menor rentabilidad estimada por hectárea.")

# Formatear margen para tabla
df_rec_tabla = df_rec[["cultivo", "rendimiento", "margen_ha", "vs_maiz"]].copy()
df_rec_tabla["margen_ha"] = df_rec_tabla["margen_ha"].apply(
    lambda x: f"${x:,.0f}" if pd.notna(x) else "N/D"
)
df_rec_tabla.columns = ["Cultivo", "Rendimiento (ton/ha)", "Margen/ha", "vs Maíz"]
st.dataframe(df_rec_tabla, use_container_width=True)

st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 4 — Gráficas
# ════════════════════════════════════════════════════════════
st.subheader("Análisis visual")

tab1, tab2, tab3, tab4 = st.tabs([
    "🌾 Rendimiento vs Maíz",
    "💰 Análisis financiero",
    "⚠️ Riesgo-Rendimiento",
    "🌡️ Clima del estado"
])

# Tab 1 — Rendimiento
with tab1:
    st.caption("La barra roja es el maíz — todo lo que la supera produce más toneladas por hectárea.")
    cultivos_graf = cultivos_rec + ["Maíz grano"]
    df_bar = df_agro[df_agro["cultivo"].isin(cultivos_graf)].sort_values("rendimiento", ascending=True)
    df_bar["color"] = df_bar["cultivo"].apply(
        lambda x: "Maíz (referencia)" if x == "Maíz grano" else "Cultivo recomendado"
    )
    fig1 = px.bar(
        df_bar, x="rendimiento", y="cultivo", color="color",
        color_discrete_map={"Maíz (referencia)": "#EF5350", "Cultivo recomendado": "#42A5F5"},
        labels={"rendimiento": "Rendimiento (ton/ha)", "cultivo": "Cultivo"},
        title=f"Rendimiento de cultivos recomendados vs Maíz — {estado_sel}",
        orientation="h",
        template="plotly_dark"
    )
    fig1.update_layout(legend_title="", paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A")
    st.plotly_chart(fig1, use_container_width=True)

# Tab 2 — Análisis financiero
with tab2:
    st.caption("Los cultivos a la derecha de la línea roja son más rentables que el maíz.")
    cultivos_fin = [c for c in cultivos_rec if c in datos_financieros]

    df_fin_graf = pd.DataFrame([
        {
            "cultivo": c,
            "margen":  datos_financieros[c]["precio_ton"] * datos_financieros[c]["rendimiento"] - datos_financieros[c]["costo_ha"],
        }
        for c in cultivos_fin if c in datos_financieros
    ])

    df_fin_graf = df_fin_graf.sort_values("margen", ascending=True)

    fig2 = px.bar(
        df_fin_graf, x="margen", y="cultivo",
        color_discrete_sequence=["#66BB6A"],
        labels={"margen": "Margen bruto ($/ha)", "cultivo": "Cultivo"},
        title=f"Margen bruto por hectárea — {estado_sel}",
        orientation="h",
        template="plotly_dark"
    )
    maiz_margen = datos_financieros["Maíz grano"]["precio_ton"] * datos_financieros["Maíz grano"]["rendimiento"] - datos_financieros["Maíz grano"]["costo_ha"]
    fig2.add_vline(
        x=maiz_margen,
        line_dash="dash",
        line_color="#EF5350",
        line_width=2,
        annotation_text=f"Maíz: ${maiz_margen:,.0f}/ha",
        annotation_position="top right",
        annotation_font_color="#EF5350"
    )
    fig2.update_layout(legend_title="", paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A")
    fig2.update_xaxes(tickformat="$,.0f")
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("Precios: SIACON 2024 | Costos: referencia FIRA/SAGARPA")

# Tab 3 — Dispersión
with tab3:
    st.caption("Lo ideal está arriba a la izquierda: alto rendimiento, baja probabilidad de siniestro. Pasa el cursor sobre ⭐ para ver los cultivos recomendados para tu estado.")
    colores_map = {
        "Alto rendimiento / Bajo riesgo":  "#42A5F5",
        "Alto rendimiento / Alto riesgo":  "#EF5350",
        "Bajo rendimiento / Bajo riesgo":  "#9E9E9E",
        "Bajo rendimiento / Alto riesgo":  "#FFA726"
    }
    fig3 = px.scatter(
        df_agro, x="tasa_siniestro_pct", y="rendimiento",
        color="cuadrante", hover_name="cultivo",
        color_discrete_map=colores_map,
        labels={
            "tasa_siniestro_pct": "Probabilidad de siniestro (%)",
            "rendimiento": "Rendimiento (ton/ha)",
            "cuadrante": "Cuadrante"
        },
        title="Mapa de riesgo-rendimiento — todos los cultivos",
        template="plotly_dark"
    )
    prom_siniestro_graf = df_agro["tasa_siniestro_pct"].mean()
    prom_rend_graf      = df_agro["rendimiento"].mean()
    fig3.add_vline(
        x=prom_siniestro_graf, line_dash="dot", line_color="white", line_width=1,
        annotation_text=f"Riesgo promedio: {prom_siniestro_graf:.1f}%",
        annotation_position="top right", annotation_font_color="white", annotation_font_size=10
    )
    fig3.add_hline(
        y=prom_rend_graf, line_dash="dot", line_color="white", line_width=1,
        annotation_text=f"Rendimiento promedio: {prom_rend_graf:.1f} t/ha",
        annotation_position="top right", annotation_font_color="white", annotation_font_size=10
    )
    df_highlight = df_agro[df_agro["cultivo"].isin(cultivos_rec)]
    fig3.add_scatter(
        x=df_highlight["tasa_siniestro_pct"],
        y=df_highlight["rendimiento"],
        mode="markers",
        marker=dict(size=14, color="#00E676", symbol="star"),
        customdata=df_highlight[["cultivo"]],
        hovertemplate="<b>%{customdata[0]}</b><br>Siniestro: %{x:.1f}%<br>Rendimiento: %{y:.1f} t/ha<extra></extra>",
        name=f"Recomendados para {estado_sel}"
    )
    fig3.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A")
    st.plotly_chart(fig3, use_container_width=True)

# Tab 4 — Clima comparativo
with tab4:
    st.caption("Condiciones climáticas de tu estado vs el promedio nacional.")
    from plotly.subplots import make_subplots

    fig4 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Precipitación anual (mm)", "Temperaturas (°C)")
    )

    # Precipitación
    fig4.add_trace(go.Bar(
        name=estado_sel,
        x=["Precipitación (mm)"],
        y=[estado_data["precipitacion_anual_mm"]],
        marker_color="#42A5F5",
        showlegend=True
    ), row=1, col=1)
    fig4.add_trace(go.Bar(
        name="Promedio nacional",
        x=["Precipitación (mm)"],
        y=[df_clima["precipitacion_anual_mm"].mean()],
        marker_color="#9E9E9E",
        showlegend=True
    ), row=1, col=1)

    # Temperaturas
    temp_labels = ["Media", "Máxima", "Mínima"]
    temp_estado  = [estado_data["temp_media_anual_c"], estado_data["temp_maxima_anual_c"], estado_data["temp_minima_anual_c"]]
    temp_nacional = [df_clima["temp_media_anual_c"].mean(), df_clima["temp_maxima_anual_c"].mean(), df_clima["temp_minima_anual_c"].mean()]

    fig4.add_trace(go.Bar(
        name=estado_sel,
        x=temp_labels, y=temp_estado,
        marker_color="#42A5F5",
        showlegend=False
    ), row=1, col=2)
    fig4.add_trace(go.Bar(
        name="Promedio nacional",
        x=temp_labels, y=temp_nacional,
        marker_color="#9E9E9E",
        showlegend=False
    ), row=1, col=2)

    fig4.update_layout(
        barmode="group",
        title_text=f"Clima de {estado_sel} vs promedio nacional",
        legend_title="",
        template="plotly_dark",
        paper_bgcolor="#0D1B2A",
        plot_bgcolor="#0D1B2A"
    )
    fig4.update_yaxes(title_text="mm", row=1, col=1)
    fig4.update_yaxes(title_text="°C", row=1, col=2)

    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.markdown(
    "Fuentes: SIAP 2025-2026 · SIACON 2024 · CONAGUA 2025 · FIRA/SAGARPA (costos de referencia)  \n"
    "Universidad Ricardo Castellanos — LCDN · Equipo 5 · 2026"
)