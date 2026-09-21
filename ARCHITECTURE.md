# Arquitectura — sanitizacion-santiago

## Visión general
Dashboard de puntos de sanitización en Santiago (87 registros). Visualización Mapbox con estilo Mondrian. Datos sensibles (referencias COVID-19) en repo público.

## Componentes principales

### Datos
- `data/raw/sanitization_points.csv` — 87 puntos (name, description, lat, lon, type)
  - Types: Pasaje, Edificio, Domicilio, Calle, Otro
  - Incluye referencias a "Covid-19" en descripciones

### Dashboard
- `dashboard.py` — Dash app single-file:
  - Carga CSV al importar (módulo level: `df = pd.read_csv(...)`)
  - Mapbox scatter plot con 87 puntos
  - Filtros por tipo
  - Sidebar con stats
  - Estilo visual "Mondrian" (colores primarios, grillas)

## Flujo de datos
```
sanitization_points.csv → dashboard.py (carga en import) → Mapbox
```

## Despliegue
- Render: `gunicorn dashboard:server` (ver `render.yaml`)
- **Problema**: `df` cargado a nivel módulo — imposible testear con datos mock

## Tests
- `tests/test_dashboard.py` — Validación datos: row_count, columns, types, bounds lat/lon
- `tests/test_data_integrity.py` — Tests adicionales de integridad
- CI: pytest + coverage + ruff (Python 3.10, 3.11, 3.12)

## Seguridad
- Datos con referencias COVID-19 en repo público
- Coordenadas exactas de domicilios/pasajes
- Revisar si requiere anonimización

## Problemas conocidos
- `dashboard.py` carga datos a nivel módulo
- `State` importado pero no usado
- Regex de street extraction falla en "10 de Julio"
- `yaxis2` referenciado pero no existe en chart