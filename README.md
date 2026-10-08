# RADAR PÚBLICO · Prototipo web v0.2

Aplicación de análisis de listas de espera quirúrgica del SNS, basada en datos de diciembre de 2024 y 2025.

## Cómo ejecutarla

1. Instala Python 3.10 o posterior.
2. Descomprime este paquete y abre una terminal dentro de la carpeta `RADAR_PUBLICO_APP`.
3. Ejecuta `python -m pip install -r requirements.txt`.
4. Ejecuta `python -m streamlit run app.py`.
5. Abre la dirección local que muestre la terminal (habitualmente `http://localhost:8501`).

No necesitas claves API ni cuentas externas. Funciona con el CSV incluido.

## Qué permite hacer

- Filtrar territorios y especialidades.
- Configurar los umbrales de alerta alta y media.
- Comparar los días de espera de 2024 y 2025 con gráficos.
- Revisar las fuentes y exportar alertas a CSV.
- Consultar las limitaciones metodológicas.

## Qué no hace todavía

- No detecta anomalías estadísticas con series largas.
- No ofrece diagnósticos causales ni publica noticias automáticamente.
- No incluye todavía datos validados de Correos y trenes.
- No utiliza todavía un modelo generativo de IA. La siguiente iteración añadirá esa capa.

## Fuentes

Ministerio de Sanidad, SISLE-SNS, tablas de tiempos medios de espera por especialidad y comunidad autónoma, página 4 de los informes de 31-12-2024 y 31-12-2025. Los documentos originales pueden adjuntarse a la memoria del TFM.
