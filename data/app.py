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

# ── Cargar datos ──────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df_cultivos = pd.read_csv(r"C:\Users\USER\Documents\PPFINAL\agricultural-diversification-pipeline\data\processed\cultivos_2025.csv")
    df_clima    = pd.read_csv(r"C:\Users\USER\Documents\PPFINAL\agricultural-diversification-pipeline\data\processed\clima_estados_2025.csv")
    df_agro     = df_cultivos[df_cultivos["es_flor"] == False].copy()

    # Clasificar perfiles climáticos
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

    # Clasificar cuadrantes
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
st.sidebar.caption("Datos: SIAP + CONAGUA 2025")
st.sidebar.caption("Universidad Rosario Castellanos — LCDN 2026")

# ════════════════════════════════════════════════════════════
# ENCABEZADO
# ════════════════════════════════════════════════════════════
st.title("🌽 Análisis de Diversificación Agrícola en México")
st.markdown(f"### Resultados para: **{estado_sel}**")
st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 1 — Perfil climático del estado
# ════════════════════════════════════════════════════════════
estado_data = df_clima[df_clima["estado"] == estado_sel].iloc[0]
perfil      = estado_data["perfil_climatico"]

st.subheader("🌤️ Perfil climático")
st.markdown(f"**Clasificación:** `{perfil}`")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Precipitación anual", f"{estado_data['precipitacion_anual_mm']:.1f} mm")
col2.metric("Temperatura media",   f"{estado_data['temp_media_anual_c']:.1f} °C")
col3.metric("Temperatura máxima",  f"{estado_data['temp_maxima_anual_c']:.1f} °C")
col4.metric("Temperatura mínima",  f"{estado_data['temp_minima_anual_c']:.1f} °C")

st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 2 — Cultivos recomendados
# ════════════════════════════════════════════════════════════
st.subheader("✅ Cultivos recomendados para este estado")

cultivos_rec = compatibilidad.get(perfil, [])
df_rec = df_agro[df_agro["cultivo"].isin(cultivos_rec)][
    ["cultivo", "rendimiento", "tasa_cosecha_pct", "tasa_siniestro_pct"]
].copy()
df_rec = df_rec.sort_values("rendimiento", ascending=False).reset_index(drop=True)
df_rec.index += 1

# Comparar vs maíz
maiz_rend = df_agro[df_agro["cultivo"] == "Maíz grano"]["rendimiento"].values[0]
df_rec["vs_maiz"] = (df_rec["rendimiento"] / maiz_rend).round(1).astype(str) + "x más"

df_rec.columns = ["Cultivo", "Rendimiento (ton/ha)", "Tasa cosecha (%)", "Tasa siniestro (%)", "vs Maíz"]
st.dataframe(df_rec, use_container_width=True)

st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 3 — Gráficas
# ════════════════════════════════════════════════════════════
st.subheader("📊 Análisis visual")

tab1, tab2, tab3 = st.tabs(["Rendimiento vs Maíz", "Mapa riesgo-rendimiento", "Clima del estado"])

# Tab 1 — Rendimiento
with tab1:
    cultivos_graf = cultivos_rec + ["Maíz grano"]
    df_bar = df_agro[df_agro["cultivo"].isin(cultivos_graf)].sort_values("rendimiento", ascending=True)
    df_bar["color"] = df_bar["cultivo"].apply(lambda x: "Maíz (referencia)" if x == "Maíz grano" else "Cultivo recomendado")

    fig1 = px.bar(
        df_bar, x="rendimiento", y="cultivo", color="color",
        color_discrete_map={"Maíz (referencia)": "#EF5350", "Cultivo recomendado": "#42A5F5"},
        labels={"rendimiento": "Rendimiento (ton/ha)", "cultivo": "Cultivo"},
        title=f"Rendimiento de cultivos recomendados vs Maíz — {estado_sel}",
        orientation="h"
    )
    fig1.update_layout(legend_title="")
    st.plotly_chart(fig1, use_container_width=True)

# Tab 2 — Dispersión
with tab2:
    colores_map = {
        "Alto rendimiento / Bajo riesgo":  "#42A5F5",
        "Alto rendimiento / Alto riesgo":  "#EF5350",
        "Bajo rendimiento / Bajo riesgo":  "#9E9E9E",
        "Bajo rendimiento / Alto riesgo":  "#FFA726"
    }

    fig2 = px.scatter(
        df_agro, x="tasa_siniestro_pct", y="rendimiento",
        color="cuadrante", hover_name="cultivo",
        color_discrete_map=colores_map,
        labels={
            "tasa_siniestro_pct": "Tasa de siniestro (%)",
            "rendimiento": "Rendimiento (ton/ha)",
            "cuadrante": "Cuadrante"
        },
        title="Mapa de riesgo-rendimiento — todos los cultivos"
    )

    # Resaltar recomendados
    df_highlight = df_agro[df_agro["cultivo"].isin(cultivos_rec)]
    fig2.add_scatter(
        x=df_highlight["tasa_siniestro_pct"],
        y=df_highlight["rendimiento"],
        mode="markers+text",
        marker=dict(size=14, color="green", symbol="star"),
        text=df_highlight["cultivo"],
        textposition="top center",
        name=f"Recomendados para {estado_sel}",
        textfont=dict(size=9)
    )
    st.plotly_chart(fig2, use_container_width=True)

# Tab 3 — Clima comparativo
with tab3:
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        name=estado_sel,
        x=["Precipitación (mm)", "Temp. media (°C)", "Temp. máxima (°C)", "Temp. mínima (°C)"],
        y=[
            estado_data["precipitacion_anual_mm"],
            estado_data["temp_media_anual_c"],
            estado_data["temp_maxima_anual_c"],
            estado_data["temp_minima_anual_c"]
        ],
        marker_color="#42A5F5"
    ))

    fig3.add_trace(go.Bar(
        name="Promedio nacional",
        x=["Precipitación (mm)", "Temp. media (°C)", "Temp. máxima (°C)", "Temp. mínima (°C)"],
        y=[
            df_clima["precipitacion_anual_mm"].mean(),
            df_clima["temp_media_anual_c"].mean(),
            df_clima["temp_maxima_anual_c"].mean(),
            df_clima["temp_minima_anual_c"].mean()
        ],
        marker_color="#9E9E9E"
    ))

    fig3.update_layout(
        barmode="group",
        title=f"Clima de {estado_sel} vs promedio nacional",
        legend_title=""
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ════════════════════════════════════════════════════════════
# SECCIÓN 4 — Conclusión
# ════════════════════════════════════════════════════════════
st.subheader("💡 Conclusión")
mejor = df_rec.iloc[0] if len(df_rec) > 0 else None
if mejor is not None:
    st.success(
        f"Para **{estado_sel}** con perfil **{perfil}**, "
        f"el cultivo más recomendado es **{mejor['Cultivo']}** "
        f"con un rendimiento de **{mejor['Rendimiento (ton/ha)']} ton/ha**, "
        f"que es **{mejor['vs Maíz']}** que el maíz grano."
    )
