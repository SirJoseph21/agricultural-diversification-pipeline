import pandas as pd
from io import StringIO

# ── Ruta base del proyecto ──────────────────────────────────────
BASE = r"C:\Users\USER\Documents\PPFINAL\agricultural-diversification-pipeline"
RAW  = BASE + r"\data\dataraw"
PROC = BASE + r"\data\processed"

# ── PARTE 1: SIAP ───────────────────────────────────────────────
with open(RAW + r"\Avance de Siembras y Cosechas.xls", "r", encoding="latin-1") as f:
    contenido = f.read()

# Corregir encoding corrupto antes de parsear
contenido = contenido.encode("latin-1").decode("utf-8", errors="replace")

tablas = pd.read_html(StringIO(contenido))
df_siap = tablas[1].copy()

df_siap.columns = ["id", "entidad", "sup_sembrada_ha", "sup_cosechada_ha", "sup_siniestrada_ha"]
df_siap = df_siap[df_siap["entidad"] != "Total"].copy()
df_siap = df_siap.drop(columns=["id"])
df_siap["entidad"] = df_siap["entidad"].replace("México", "Estado de México")
df_siap["tasa_cosecha_pct"]   = (df_siap["sup_cosechada_ha"]  / df_siap["sup_sembrada_ha"] * 100).round(2)
df_siap["tasa_siniestro_pct"] = (df_siap["sup_siniestrada_ha"] / df_siap["sup_sembrada_ha"] * 100).round(4)

print("SIAP cargado:", df_siap.shape)
print(df_siap.head())

# ── PARTE 2: CONAGUA ────────────────────────────────────────────
df_precip   = pd.read_csv(RAW + r"\precipitacion_2025.csv", encoding="utf-8")
df_t_media  = pd.read_csv(RAW + r"\temp_media_2025.csv",    encoding="utf-8")
df_t_maxima = pd.read_csv(RAW + r"\temp_maxima_2025.csv",   encoding="utf-8")
df_t_minima = pd.read_csv(RAW + r"\temp_minima_2025.csv",   encoding="utf-8")

for df in [df_precip, df_t_media, df_t_maxima, df_t_minima]:
    df.rename(columns={df.columns[0]: "entidad"}, inplace=True)

df_precip   = df_precip[df_precip["entidad"]   != "Nacional"][["entidad", "anual"]].rename(columns={"anual": "precipitacion_anual_mm"})
df_t_media  = df_t_media[df_t_media["entidad"]  != "Nacional"][["entidad", "anual"]].rename(columns={"anual": "temp_media_anual_c"})
df_t_maxima = df_t_maxima[df_t_maxima["entidad"] != "Nacional"][["entidad", "anual"]].rename(columns={"anual": "temp_maxima_anual_c"})
df_t_minima = df_t_minima[df_t_minima["entidad"] != "Nacional"][["entidad", "anual"]].rename(columns={"anual": "temp_minima_anual_c"})

print("\nClima cargado:", df_precip.shape)

# Diccionario de corrección de nombres para que coincidan con el SIAP
nombres = {
    "Ciudad de Mexico":  "Ciudad de México",
    "Estado de Mexico":  "Estado de México",
    "Michoacan":         "Michoacán",
    "Nuevo Leon":        "Nuevo León",
    "Queretaro":         "Querétaro",
    "San Luis Potosi":   "San Luis Potosí",
    "Yucatan":           "Yucatán"
}

df_precip["entidad"]   = df_precip["entidad"].replace(nombres)
df_t_media["entidad"]  = df_t_media["entidad"].replace(nombres)
df_t_maxima["entidad"] = df_t_maxima["entidad"].replace(nombres)
df_t_minima["entidad"] = df_t_minima["entidad"].replace(nombres)

# ── PARTE 3: JOIN ───────────────────────────────────────────────
df_clima = df_precip.merge(df_t_media,  on="entidad", how="inner")
df_clima = df_clima.merge(df_t_maxima, on="entidad", how="inner")
df_clima = df_clima.merge(df_t_minima, on="entidad", how="inner")

df_final = df_siap.merge(df_clima, on="entidad", how="left")

print("\nDataset final:", df_final.shape)
print(df_final.head())

sin_clima = df_final[df_final["precipitacion_anual_mm"].isna()]["entidad"].tolist()
if sin_clima:
    print("\n[AVISO] Sin datos climáticos:", sin_clima)

# ── PARTE 4: GUARDAR ────────────────────────────────────────────
import os
os.makedirs(PROC, exist_ok=True)
df_final.to_csv(PROC + r"\dataset_agricola_clima.csv", index=False)
print("\n[OK] Guardado en:", PROC + r"\dataset_agricola_clima.csv")