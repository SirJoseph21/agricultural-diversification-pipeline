# Análisis de Producción Agrícola + Clima México 🌽🌡️

Proyecto de ciencia de datos para identificar cultivos con potencial de diversificación en México, cruzando datos de producción agrícola del SIAP con datos climáticos de CONAGUA 2025.

Desarrollado como parte del Problema Prototípico de la Licenciatura en Ciencias de Datos para Negocios — Universidad Rosario Castellanos, Semestre 2026-1.

---

## Pregunta central

> ¿Qué cultivos tienen mejor potencial para diversificar la producción agrícola en México considerando rendimiento, riesgo de pérdida y condiciones climáticas por estado?

---

## Hallazgos principales

- El maíz grano ocupa el lugar **46 de 60** en rendimiento, con solo 3.52 ton/ha
- El promedio nacional de rendimiento es **21.18 ton/ha**, 6 veces más que el maíz
- **5 cultivos alternativos** superan al maíz en rendimiento, tasa de cosecha y siniestro
- El jitomate rinde **19.5x más** que el maíz con menor riesgo de pérdida
- Se identificaron **7 perfiles climáticos** en los 32 estados para cruzar con cultivos compatibles

---

## Estructura del proyecto

```
agricultural-diversification-pipeline/
│
├── data/
│   ├── dataraw/          ← archivos originales (SIAP + CONAGUA)
│   └── processed/        ← datasets limpios generados por el ETL
│
├── notebooks/            ← análisis exploratorio en Python
│
├── etl/                  ← scripts de extracción y transformación
│
├── sql/                  ← esquema y scripts de base de datos
│
└── docs/                 ← gráficas e informe ejecutivo
```

---

## Stack tecnológico

| Herramienta | Uso |
|---|---|
| Python + pandas | ETL y análisis |
| MySQL | Base de datos relacional |
| Matplotlib | Visualizaciones |
| Google Colab | Entorno de análisis |
| Git + GitHub | Control de versiones |
| Notion | Documentación del proyecto |

---

## Fuentes de datos

| Fuente | Descripción | Descarga |
|---|---|---|
| SIAP — SADER | Avance de siembras y cosechas 2025-2026, 64 cultivos | Manual (formulario dinámico) |
| CONAGUA — SMN | Precipitación y temperatura por entidad federativa 2025 | Manual (PDF) |

> **Nota técnica:** El archivo XLS del SIAP es internamente HTML. Se usa `pd.read_html` con `StringIO` para parsearlo. El scraping automático no fue posible por el formulario dinámico del sitio.

---

## Pipeline ETL

```
SIAP (.xls HTML)  ──┐
                    ├── ETL (Python/pandas) ── MySQL ── Análisis (Colab)
CONAGUA (4 CSVs) ──┘
```

1. Extracción: lectura del XLS del SIAP y 4 CSVs de clima
2. Transformación: limpieza, normalización de nombres, cálculo de métricas
3. Carga: 2 CSVs procesados + base de datos MySQL con 3 tablas

---

## Base de datos

3 tablas en MySQL (`agricola_clima`):

- `categoria_cultivo` — 7 categorías de cultivos
- `cultivos` — 64 cultivos con métricas de producción 2025
- `estados` — 32 estados con variables climáticas anuales 2025

---

## Resultados del análisis

### Top 5 cultivos recomendados para diversificación

| Cultivo | Rendimiento (ton/ha) | vs Maíz | Siniestro |
|---|---|---|---|
| Tomate rojo (jitomate) | 68.68 | 19.5x más | 0.65% |
| Nopalitos | 64.57 | 18.3x más | 0.00% |
| Papaya | 53.54 | 15.2x más | 0.00% |
| Pepino | 45.84 | 13.0x más | 0.24% |
| Fresa | 41.85 | 11.9x más | 0.40% |

### Perfiles climáticos identificados

| Perfil | Estados |
|---|---|
| Semi-húmedo / Templado | 10 estados (Jalisco, Guanajuato, Michoacán...) |
| Húmedo / Cálido | 8 estados (Chiapas, Guerrero, Tabasco...) |
| Seco / Templado | 5 estados (Chihuahua, Coahuila, Sonora...) |

---

## Próximos pasos

- [ ] Dashboard interactivo en Streamlit
- [ ] Visualizaciones ejecutivas en Power BI
- [ ] Migración del pipeline a AWS (S3 + RDS + Glue)

---

## Equipo

Proyecto desarrollado en equipo para la LCDN — Universidad Rosario Castellanos.

- Ingeniería de datos y análisis técnico
- Análisis financiero (Contabilidad Financiera)
- Análisis de riesgo (Probabilidad)
- Modelado matemático (Cálculo Integral)

---

## Referencias

- SADER. (2024). *Estadística de producción agrícola: Datos abiertos*. Gobierno de México.
- CONAGUA — SMN. (2025). *Precipitación y temperatura por entidad federativa*. Gobierno de México.
- Equipo Diverfarming. (2019). *¿Cuáles son los beneficios económicos de la diversificación de cultivos?* Universidad de Córdoba.
