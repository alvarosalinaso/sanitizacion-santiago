# Sanitización Comuna de Santiago

Interactive visualization of 87 sanitization request points in Santiago, Chile.

## Overview

This project visualizes georeferenced sanitization requests collected for the Comuna de Santiago. The data originates from a KML file exported from Google My Maps ("Mapa de Sanitización Comuna de Santiago") and was transformed into a structured CSV for analysis.

The application is an interactive Dash dashboard featuring:

- A map with all 87 request points plotted geographically
- Distribution analysis by type (bar chart, pie chart, street frequency)
- Geographic density analysis (lat/lon histograms, scatter plot)
- A filterable data table

## Data Types

| Type | Description |
|------|-------------|
| Cité | Cité-style housing complexes |
| Pasaje | Passageways / alleys |
| Edificio | Buildings / apartment blocks |
| Domicilio | Individual residences |
| Calle | Street-level requests |
| Otro | Other / unclassified |

## How to Run

```bash
pip install -r requirements.txt
python dashboard.py
```

The dashboard will be available at `http://localhost:8054`.

## Tech Stack

- **Python** — core language
- **pandas** — data loading and manipulation
- **Plotly** — interactive visualizations
- **Dash** — web application framework

## Project Structure

```
sanitizacion-santiago/
├── dashboard.py              # Main Dash application
├── requirements.txt          # Python dependencies
├── .gitignore
├── README.md
├── data/
│   └── raw/
│       └── sanitization_points.csv
└── tests/
    └── test_dashboard.py
```

## Data Source

Data extracted from a KML file created in Google My Maps: **"Mapa de Sanitización Comuna de Santiago"**. The KML was parsed and converted to CSV with columns: `name`, `description`, `lat`, `lon`, `type`.
