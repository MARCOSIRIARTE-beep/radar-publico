"""RADAR PÚBLICO — prototipo de observatorio de servicios públicos."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).resolve().parent
CSV = BASE / "RADAR_PUBLICO_sanidad_2024_2025.csv"

st.set_page_config(page_title="RADAR PÚBLICO", page_icon="📡", layout="wide")
st.title("📡 RADAR PÚBLICO")
st.caption("Observatorio experimental de indicadores de servicios públicos · Versión 0.2")
st.info("Las alertas identifican cambios que merecen revisión; no demuestran por sí solas deterioro, anomalía estadística ni causalidad.")

@st.cache_data
def cargar_datos():
    datos = pd.read_csv(CSV, encoding="utf-8-sig")
    requeridas = {"sector", "territorio", "especialidad", "valor_2024", "valor_2025", "fuente_2024", "fuente_2025"}
    faltantes = requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas en el CSV: {', '.join(sorted(faltantes))}")
    for campo in ["valor_2024", "valor_2025"]:
        datos[campo] = pd.to_numeric(datos[campo], errors="coerce")
    datos = datos.dropna(subset=["valor_2024", "valor_2025"]).copy()
    datos["variacion_dias"] = datos["valor_2025"] - datos["valor_2024"]
    datos["variacion_porcentual"] = (datos["variacion_dias"] / datos["valor_2024"].replace(0, float("nan"))) * 100
    return datos

df = cargar_datos()
with st.sidebar:
    st.header("Filtros y criterios")
    sector = st.selectbox("Sector", ["Sanidad", "Correos (próximamente)", "Trenes (próximamente)"])
    st.subheader("Umbrales provisionales")
    alta_dias = st.number_input("Alerta alta · mínimo de días", min_value=1, max_value=365, value=20)
    alta_pct = st.number_input("Alerta alta · mínimo porcentual", min_value=1, max_value=500, value=15)
    media_dias = st.number_input("Alerta media · mínimo de días", min_value=1, max_value=365, value=10)
    media_pct = st.number_input("Alerta media · mínimo porcentual", min_value=1, max_value=500, value=10)
    st.caption("Una alerta exige superar ambos umbrales del nivel correspondiente.")

if sector != "Sanidad":
    st.warning("Este sector está previsto en el proyecto, pero todavía no dispone de una base de datos validada.")
    st.stop()

territorios = sorted(df["territorio"].unique().tolist())
especialidades = sorted(df["especialidad"].unique().tolist())
col_a, col_b = st.columns(2)
with col_a:
    elegidos_territorios = st.multiselect("Comunidades y ciudades autónomas", territorios, default=territorios)
with col_b:
    elegidas_especialidades = st.multiselect("Especialidades", especialidades, default=especialidades)

vista = df[df["territorio"].isin(elegidos_territorios) & df["especialidad"].isin(elegidas_especialidades)].copy()

def clasificar(fila):
    d, p = fila["variacion_dias"], fila["variacion_porcentual"]
    if pd.isna(p):
        return "SIN DATOS SUFICIENTES"
    if d >= alta_dias and p >= alta_pct:
        return "ALTA"
    if d >= media_dias and p >= media_pct:
        return "MEDIA"
    return "SIN ALERTA"

vista["nivel"] = vista.apply(clasificar, axis=1)
alertas = vista[vista["nivel"].isin(["ALTA", "MEDIA"])].copy()
alertas["orden"] = alertas["nivel"].map({"ALTA": 0, "MEDIA": 1})
alertas = alertas.sort_values(["orden", "variacion_dias"], ascending=[True, False])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Comparaciones", len(vista))
k2.metric("Alertas altas", (vista["nivel"] == "ALTA").sum())
k3.metric("Alertas medias", (vista["nivel"] == "MEDIA").sum())
k4.metric("Territorios seleccionados", vista["territorio"].nunique())

pestana1, pestana2, pestana3 = st.tabs(["🚨 Alertas", "📊 Comparador", "📚 Metodología"])
with pestana1:
    st.subheader("Casos para revisión periodística")
    if alertas.empty:
        st.success("Ninguna comparación supera los umbrales seleccionados.")
    else:
        columnas = ["nivel", "territorio", "especialidad", "valor_2024", "valor_2025", "variacion_dias", "variacion_porcentual"]
        st.dataframe(alertas[columnas], hide_index=True, use_container_width=True,
                     column_config={"valor_2024": "Días 2024", "valor_2025": "Días 2025", "variacion_dias": "Cambio (días)", "variacion_porcentual": st.column_config.NumberColumn("Cambio (%)", format="%.1f")})
        st.download_button("Descargar alertas filtradas (CSV)", data=alertas.drop(columns=["orden"]).to_csv(index=False).encode("utf-8-sig"), file_name="radar_publico_alertas_filtradas.csv", mime="text/csv")
        seleccion = st.selectbox("Examinar una alerta", alertas.index.tolist(), format_func=lambda i: f"{alertas.loc[i, 'nivel']} · {alertas.loc[i, 'territorio']} · {alertas.loc[i, 'especialidad']}")
        caso = alertas.loc[seleccion]
        st.markdown(f"**{caso['territorio']} — {caso['especialidad']}**")
        st.write(f"La espera media pasó de **{caso['valor_2024']:.0f} días** (diciembre de 2024) a **{caso['valor_2025']:.0f} días** (diciembre de 2025): **{caso['variacion_dias']:+.0f} días** ({caso['variacion_porcentual']:+.1f}%).")
        st.write("**Fuentes:**", caso["fuente_2024"], "y", caso["fuente_2025"])
        st.warning("Estado: pendiente de verificación editorial. Revisar cambios metodológicos, número de pacientes y contexto antes de publicar.")
with pestana2:
    st.subheader("Comparación interanual")
    if vista.empty:
        st.info("Selecciona al menos un territorio y una especialidad.")
    else:
        graf = vista.melt(id_vars=["territorio", "especialidad"], value_vars=["valor_2024", "valor_2025"], var_name="Año", value_name="Días")
        graf["Año"] = graf["Año"].map({"valor_2024": "2024", "valor_2025": "2025"})
        graf["Serie"] = graf["territorio"] + " · " + graf["especialidad"]
        if graf["Serie"].nunique() > 25:
            st.info("Para visualizar mejor el gráfico, selecciona hasta 25 combinaciones de territorio y especialidad.")
        else:
            fig = px.bar(graf, x="Serie", y="Días", color="Año", barmode="group", title="Tiempo medio de espera quirúrgica")
            fig.update_layout(xaxis_title="Territorio y especialidad", yaxis_title="Días de espera")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(vista[["territorio", "especialidad", "valor_2024", "valor_2025", "variacion_dias", "variacion_porcentual", "nivel"]], hide_index=True, use_container_width=True)
with pestana3:
    st.markdown("""### Fuentes y alcance
- Ministerio de Sanidad, Sistema de Información sobre Listas de Espera del SNS (SISLE-SNS), **31 de diciembre de 2024 y 31 de diciembre de 2025**, tablas de tiempos medios de espera por especialidad y territorio, página 4 de cada documento.
- Cada fila corresponde a **una especialidad en un territorio**, no a la media quirúrgica total.
- Los cambios se calculan como `días_2025 − días_2024` y el porcentaje como `100 × cambio / días_2024`.
- Los umbrales son **experimentales y configurables**; no son criterios oficiales ni un contraste estadístico.
- Con solo dos cortes anuales **no puede estimarse una anomalía histórica**. Tampoco se deducen causas de las variaciones.
- Los valores ausentes se excluyen de los cálculos y no se convierten en ceros.

### Próximas iteraciones
1. Incorporar más años y controles de comparabilidad.
2. Validar series de calidad postal (CNMC) y ferrocarril antes de activar esos módulos.
3. Incorporar resúmenes asistidos por IA con citas verificables, nunca como fuente autónoma.
""")
st.divider()
st.caption("RADAR PÚBLICO · Prototipo de investigación y docencia. Ninguna alerta equivale a una noticia verificada.")
