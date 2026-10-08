"""RADAR PÚBLICO v0.1: alertas reproducibles sobre esperas quirúrgicas."""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / 'RADAR_PUBLICO_sanidad_2024_2025.csv'
SALIDA = BASE / 'RADAR_PUBLICO_alertas_sanidad.csv'

def clasificar(dias, porcentaje):
    if dias >= 20 and porcentaje >= 15:
        return 'ALTA'
    if dias >= 10 and porcentaje >= 10:
        return 'MEDIA'
    return 'SIN ALERTA'

with ENTRADA.open(encoding='utf-8-sig', newline='') as f:
    datos = list(csv.DictReader(f))

alertas = []
for fila in datos:
    previo = int(fila['valor_2024'])
    actual = int(fila['valor_2025'])
    cambio = actual - previo
    porcentaje = (cambio / previo * 100) if previo else None
    if porcentaje is None:
        continue
    nivel = clasificar(cambio, porcentaje)
    if nivel == 'SIN ALERTA':
        continue
    alertas.append({
        'nivel': nivel,
        'sector': fila['sector'],
        'territorio': fila['territorio'],
        'especialidad': fila['especialidad'],
        'dias_2024': previo,
        'dias_2025': actual,
        'variacion_dias': cambio,
        'variacion_porcentual': f'{porcentaje:.2f}',
        'fuente_2024': fila['fuente_2024'],
        'fuente_2025': fila['fuente_2025'],
        'estado': 'PENDIENTE DE VERIFICACIÓN',
        'nota': 'Cambio interanual; no acredita anomalía estadística ni causalidad.'
    })
alertas.sort(key=lambda r: (0 if r['nivel'] == 'ALTA' else 1, -r['variacion_dias']))
with SALIDA.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(alertas[0]) if alertas else ['nivel'])
    writer.writeheader()
    writer.writerows(alertas)
print('Registros analizados:', len(datos))
print('Alertas altas:', sum(a['nivel']=='ALTA' for a in alertas))
print('Alertas medias:', sum(a['nivel']=='MEDIA' for a in alertas))
print('Archivo generado:', SALIDA)
for a in alertas[:6]:
    print(a['nivel'], a['territorio'], a['especialidad'], a['variacion_dias'], 'días', a['variacion_porcentual']+'%')
