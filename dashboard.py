"""Dash Dashboard: Sanitización Comuna de Santiago — Mondrian / De Stijl."""

from pathlib import Path
from typing import Any

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html, no_update

app = dash.Dash(
    __name__,
    title="Sanitización Santiago",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

RED = "#cc0000"
BLUE = "#0033cc"
YELLOW = "#ffcc00"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#e0e0e0"

TYPE_COLORS: dict[str, str] = {
    "Cité": RED, "Pasaje": BLUE, "Edificio": YELLOW,
    "Domicilio": RED, "Calle": BLUE, "Otro": YELLOW,
}

DATA_PATH = Path(__file__).parent / "data" / "raw" / "sanitization_points.csv"

MONDRIAN_BORDER = f"5px solid {BLACK}"

BLOCK_STYLE: dict[str, Any] = {
    "border": MONDRIAN_BORDER,
    "padding": "0",
}

CARD_BODY: dict[str, Any] = {
    "padding": "20px",
}


def load_data() -> pd.DataFrame:
    """Load and validate sanitization points data."""
    if not DATA_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(DATA_PATH)
    # Data validation
    required_cols = {"name", "description", "lat", "lon", "type"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"[WARN] Missing columns: {missing}")
        return pd.DataFrame()
    # Validate lat/lon bounds for Santiago
    lat_ok = df["lat"].between(-33.55, -33.35).all()
    lon_ok = df["lon"].between(-70.8, -70.55).all()
    if not lat_ok or not lon_ok:
        print("[WARN] Coordinates outside Santiago bounds")
    # Validate types
    valid_types = {"Pasaje", "Edificio", "Domicilio", "Calle", "Otro"}
    invalid = set(df["type"].unique()) - valid_types
    if invalid:
        print(f"[WARN] Invalid types found: {invalid}")
    return df


# Lazy load - DATA is loaded on first access via get_data()
_DATA: pd.DataFrame | None = None


def get_data() -> pd.DataFrame:
    """Get data with lazy loading."""
    global _DATA
    if _DATA is None:
        _DATA = load_data()
    return _DATA


def stat_block(value, label, bg_color):
    return html.Div(
        style={
            **BLOCK_STYLE,
            "backgroundColor": bg_color,
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
            "minWidth": "120px",
            "minHeight": "90px",
        },
        children=[
            html.Div(str(value), style={
                "fontSize": "2rem", "fontWeight": "bold",
                "color": BLACK if bg_color == YELLOW else WHITE,
                "fontFamily": "'Segoe UI', system-ui, sans-serif",
            }),
            html.Div(label, style={
                "fontSize": "0.75rem", "fontWeight": "300", "textTransform": "uppercase",
                "letterSpacing": "0.1em",
                "color": BLACK if bg_color == YELLOW else WHITE,
                "fontFamily": "'Segoe UI', system-ui, sans-serif",
                "marginTop": "2px",
            }),
        ],
    )


def mondrian_title(text):
    return html.H3(text, style={
        "fontSize": "0.9rem", "fontWeight": "bold", "textTransform": "uppercase",
        "letterSpacing": "0.15em", "margin": "0 0 12px 0",
        "paddingBottom": "10px", "borderBottom": f"2px solid {BLACK}",
        "color": BLACK, "fontFamily": "'Segoe UI', system-ui, sans-serif",
    })


BAUHAUS_POSTER_SVG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='90' viewBox='0 0 1200 90'%3E"
    "%3Crect width='1200' height='90' fill='%23ffffff'/%3E"
    "%3Ccircle cx='80' cy='45' r='30' fill='%23cc0000'/%3E"
    "%3Crect x='150' y='15' width='60' height='60' fill='%230033cc'/%3E"
    "%3Cpolygon points='250,75 280,15 310,75' fill='%23ffcc00' stroke='%23000000' stroke-width='4'/%3E"
    "%3Cg stroke='%23000000' stroke-width='2' opacity='0.12'%3E"
    "%3Cline x1='0' y1='22' x2='1200' y2='22'/%3E%3Cline x1='0' y1='45' x2='1200' y2='45'/%3E%3Cline x1='0' y1='68' x2='1200' y2='68'/%3E"
    "%3C/g%3E%3Ccircle cx='1050' cy='45' r='10' fill='%23000000'/%3E"
    "%3Ccircle cx='1080' cy='45' r='10' fill='%23cc0000'/%3E"
    "%3Ccircle cx='1110' cy='45' r='10' fill='%230033cc'/%3E"
    "%3C/svg%3E"
)


def sparkline(values, color=RED):
    if not values or len(values) < 2:
        return html.Div(style={"height": "34px"})
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=list(values), mode="lines",
        line={"color": color, "width": 3, "shape": "spline"},
        fill="tozeroy", hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False}, yaxis={"visible": False}, height=34,
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "34px"})


def insight_card(question, answer, accent=RED):
    return html.Div(
        style={**BLOCK_STYLE, "borderLeft": f"8px solid {accent}", "padding": "14px 16px", "backgroundColor": WHITE, "marginBottom": "12px"},
        children=[
            html.Div(question, style={"fontWeight": "800", "textTransform": "uppercase", "fontSize": "0.72rem", "letterSpacing": "0.08em"}),
            html.Div(answer, style={"marginTop": "4px", "fontSize": "0.88rem", "lineHeight": "1.5"}),
        ],
    )


app.layout = html.Div(
    style={
        "backgroundColor": WHITE, "minHeight": "100vh",
        "fontFamily": "'Segoe UI', system-ui, sans-serif", "color": BLACK,
        "margin": "0", "padding": "0",
    },
    children=[
        html.Div(
            style={
                "backgroundColor": BLACK, "padding": "30px 20px",
                "textAlign": "center",
                "borderBottom": MONDRIAN_BORDER,
            },
            children=[
                html.H1("SANITIZACIÓN SANTIAGO", style={
                    "fontSize": "1.8rem", "fontWeight": "300", "color": WHITE,
                    "margin": "0", "letterSpacing": "0.25em", "textTransform": "uppercase",
                    "fontFamily": "'Segoe UI', system-ui, sans-serif",
                }),
                html.P("Mapa de solicitudes de sanitización — Datos georeferenciados", style={
                    "color": GRAY, "marginTop": "8px", "fontSize": "0.8rem",
                    "letterSpacing": "0.1em", "fontWeight": "300",
                }),
            ],
        ),
        html.Div(style={
            "backgroundImage": f"url(\"{BAUHAUS_POSTER_SVG}\")",
            "backgroundSize": "cover", "backgroundPosition": "center",
            "height": "90px", "borderBottom": MONDRIAN_BORDER,
        }),
        html.Div(style={
            "display": "flex", "gap": "0", "padding": "0",
            "flexWrap": "wrap", "borderBottom": MONDRIAN_BORDER,
        }, children=[
            html.Div(style={
                "flex": "3", "minWidth": "250px", "borderRight": MONDRIAN_BORDER,
                "padding": "18px 20px", "backgroundColor": WHITE,
            }, children=[
                html.Label("Filtrar por tipo", style={
                    "color": BLACK, "fontSize": "0.75rem", "textTransform": "uppercase",
                    "letterSpacing": "0.1em", "fontWeight": "bold",
                }),
                dcc.Checklist(
                    id="filter-type",
                    options=[{"label": f" {t}", "value": t} for t in get_data()["type"].unique()] if not get_data().empty else [],
                    value=get_data()["type"].unique().tolist() if not get_data().empty else [],
                    inline=True,
                    style={"color": BLACK, "marginTop": "6px"},
                    inputStyle={"marginRight": "4px", "accentColor": RED},
                ),
            ]),
            html.Div(style={
                "flex": "2", "minWidth": "200px", "padding": "18px 20px",
                "backgroundColor": WHITE,
            }, children=[
                html.Label("Buscar por nombre", style={
                    "color": BLACK, "fontSize": "0.75rem", "textTransform": "uppercase",
                    "letterSpacing": "0.1em", "fontWeight": "bold",
                }),
                dcc.Dropdown(
                    id="filter-name",
                    options=[{"label": n, "value": n} for n in get_data()["name"].tolist()] if not get_data().empty else [],
                    multi=True,
                    placeholder="Seleccionar...",
                    style={"backgroundColor": WHITE},
                ),
            ]),
        ]),
        dcc.Tabs(
            id="tabs", value="map",
            style={"backgroundColor": WHITE, "borderBottom": MONDRIAN_BORDER},
            children=[
                dcc.Tab(label="Mapa", value="map", style={
                    "backgroundColor": WHITE, "color": BLACK, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }, selected_style={
                    "backgroundColor": RED, "color": WHITE, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }),
                dcc.Tab(label="Distribución", value="dist", style={
                    "backgroundColor": WHITE, "color": BLACK, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }, selected_style={
                    "backgroundColor": RED, "color": WHITE, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }),
                dcc.Tab(label="Análisis", value="analysis", style={
                    "backgroundColor": WHITE, "color": BLACK, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }, selected_style={
                    "backgroundColor": RED, "color": WHITE, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }),
                dcc.Tab(label="Datos", value="data", style={
                    "backgroundColor": WHITE, "color": BLACK, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }, selected_style={
                    "backgroundColor": RED, "color": WHITE, "border": MONDRIAN_BORDER,
                    "fontWeight": "bold", "textTransform": "uppercase", "letterSpacing": "0.1em",
                    "fontSize": "0.8rem",
                }),
            ],
        ),
        html.Div(id="tab-content", style={"maxWidth": "1200px", "margin": "0 auto", "padding": "0"}),
    ],
)


def _filter_data(types, names):
    data = get_data()
    if data.empty:
        return data
    df = data[data["type"].isin(types)]
    if names:
        df = df[df["name"].isin(names)]
    return df


@callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("filter-type", "value"),
    Input("filter-name", "value"),
)
def render_tab(tab, types, names):
    if get_data().empty:
        return _error_block("No hay datos disponibles")
    df = _filter_data(types or [], names or [])
    if df.empty:
        return _error_block("No hay puntos que coincidan con los filtros")
    funcs = {"map": map_tab, "dist": dist_tab, "analysis": analysis_tab, "data": data_tab}
    return funcs.get(tab, map_tab)(df)


def _error_block(msg):
    return html.Div(style={
        **BLOCK_STYLE, "backgroundColor": RED,
        "padding": "60px 20px", "textAlign": "center",
    }, children=[
        html.P(msg, style={"color": WHITE, "fontSize": "1rem", "fontWeight": "300",
                           "letterSpacing": "0.1em", "margin": "0"}),
    ])


def map_tab(df):
    total = len(df)
    fig = px.scatter_mapbox(
        df, lat="lat", lon="lon", color="type",
        hover_name="name", hover_data=["description", "type"],
        center={"lat": -33.45, "lon": -70.66}, zoom=12,
        mapbox_style="carto-positron",
        color_discrete_map=TYPE_COLORS,
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]}<br>Tipo: %{customdata[1]}<br>%{lat:.4f}°, %{lon:.4f}°<extra></extra>",
    )
    fig.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=600, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(bgcolor=WHITE, bordercolor=BLACK, borderwidth=2,
                    font=dict(color=BLACK, size=11)),
    )
    by_type = df["type"].value_counts()
    top_type = by_type.index[0] if len(by_type) else "—"
    count_block = stat_block(total, "puntos", RED)
    insights = html.Div(style={**BLOCK_STYLE, "backgroundColor": WHITE, "padding": "16px 18px", "marginBottom": "0"}, children=[
        mondrian_title("Key Insights"),
        insight_card("¿Problema?", f"{total} solicitudes dispersas sin priorización visible por tipo ni calle.", RED),
        insight_card("¿Metodología?", f"Georreferenciación validada + top tipo '{top_type}' ({by_type.iloc[0] if len(by_type) else 0} casos) para focalizar cuadrillas.", BLUE),
        insight_card("¿Decisión?", "Asignar rutas por calle frecuente y tipo dominante; clic en barras de Distribución para filtrar.", YELLOW),
        sparkline(by_type.values.tolist(), RED),
    ])
    return html.Div(children=[
        insights,
        html.Div(style={"display": "flex", "gap": "0", "flexWrap": "wrap"}, children=[
        html.Div(style={**BLOCK_STYLE, "flex": "3", "minWidth": "300px", "backgroundColor": RED}, children=[
            html.Div(CARD_BODY, children=[
                mondrian_title("Mapa de Sanitización"),
                dcc.Graph(figure=fig, style={"margin": "0"}),
            ]),
        ]),
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "140px", "backgroundColor": WHITE,
                         "display": "flex", "flexDirection": "column"}, children=[
            count_block,
            html.Div(style={**BLOCK_STYLE, "backgroundColor": BLUE, "flex": "1",
                             "display": "flex", "alignItems": "center", "justifyContent": "center",
                             "minHeight": "90px"}, children=[
                html.Div(f"{len(df['type'].unique())} tipos", style={
                    "color": WHITE, "fontSize": "1.5rem", "fontWeight": "bold",
                    "fontFamily": "'Segoe UI', system-ui, sans-serif",
                }),
            ]),
            html.Div(style={**BLOCK_STYLE, "backgroundColor": YELLOW, "flex": "1",
                             "display": "flex", "alignItems": "center", "justifyContent": "center",
                             "minHeight": "90px"}, children=[
                html.Div(f"{df['lat'].mean():.4f}°", style={
                    "color": BLACK, "fontSize": "1.5rem", "fontWeight": "bold",
                    "fontFamily": "'Segoe UI', system-ui, sans-serif",
                }),
            ]),
        ]),
        ]),
    ])


def dist_tab(df):
    tipo_counts = df["type"].value_counts()

    total = len(df)
    fig_bar = px.bar(
        x=tipo_counts.index, y=tipo_counts.values,
        color=tipo_counts.index, color_discrete_map=TYPE_COLORS,
        labels={"x": "Tipo", "y": "Cantidad"},
        title="Puntos por Tipo — clic una barra para filtrar",
    )
    fig_bar.update_traces(
        hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<br>%{y:.0%} de " + str(total) + "<extra></extra>",
        marker_line_width=2, marker_line_color=BLACK,
    )
    fig_bar.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=380, showlegend=False, bargap=0.3,
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
    )

    fig_pie = px.pie(
        values=tipo_counts.values, names=tipo_counts.index,
        color=tipo_counts.index, color_discrete_map=TYPE_COLORS,
    )
    fig_pie.update_traces(
        marker=dict(line=dict(color=WHITE, width=2)),
        textfont_size=12,
    )
    fig_pie.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=380, showlegend=True,
        legend=dict(bgcolor=WHITE, bordercolor=BLACK, borderwidth=2,
                    font=dict(color=BLACK, size=11)),
    )

    df_copy = df.copy()
    # Regex mejorada: captura nombres de calles que pueden empezar con números (ej. "10 de Julio")
    # Incluye: letras, números, espacios, y caracteres comunes en nombres de calles chilenos
    df_copy["street"] = df_copy["name"].str.extract(r"^([A-Za-z0-9áéíóúñü\s\.\-]+)")
    df_copy["street"] = df_copy["street"].str.strip()
    street_counts = df_copy["street"].dropna().value_counts().head(15)
    fig_streets = px.bar(
        x=street_counts.values, y=street_counts.index, orientation="h",
        color_discrete_sequence=[BLUE],
    )
    fig_streets.update_traces(marker_line_width=0)
    fig_streets.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=500, showlegend=False,
yaxis={"categoryorder": "total ascending"},
    xaxis=dict(showgrid=False),
    )

    return html.Div(children=[
        html.Div(id="dist-crossfilter-output", style={"fontWeight": "800", "padding": "10px 20px", "borderBottom": MONDRIAN_BORDER}),
        html.Div(style={"display": "flex", "gap": "0", "flexWrap": "wrap"}, children=[
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px", "backgroundColor": WHITE}, children=[
            html.Div(CARD_BODY, children=[
                mondrian_title("Puntos por Tipo"),
                dcc.Graph(id="dist-type-bar", figure=fig_bar),
            ]),
        ]),
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px", "backgroundColor": BLUE}, children=[
            html.Div(CARD_BODY, children=[
                mondrian_title("Distribución por Tipo"),
                dcc.Graph(figure=fig_pie),
            ]),
        ]),
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px", "backgroundColor": WHITE}, children=[
            html.Div(CARD_BODY, children=[
                mondrian_title("Calles Más Frecuentes"),
                dcc.Graph(figure=fig_streets),
            ]),
        ]),
        ]),
    ])


@callback(
    Output("dist-crossfilter-output", "children"),
    Input("dist-type-bar", "clickData"),
    prevent_initial_call=True,
)
def dist_crossfilter(click):
    if not click:
        return no_update
    t = click["points"][0].get("x", "?")
    return f"Tipo seleccionado: {t} — usa el filtro superior para aislarlo en Mapa y Análisis."


def analysis_tab(df):
    fig_lat = px.histogram(
        df, x="lat", nbins=20,
        color_discrete_sequence=[RED],
    )
    fig_lat.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=320, title="Distribución de Latitud",
        xaxis=dict(title="Latitud", showgrid=False),
        yaxis=dict(title="Cantidad", showgrid=False),
    )

    fig_lon = px.histogram(
        df, x="lon", nbins=20,
        color_discrete_sequence=[BLUE],
    )
    fig_lon.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=320, title="Distribución de Longitud",
        xaxis=dict(title="Longitud", showgrid=False),
        yaxis=dict(title="Cantidad", showgrid=False),
    )

    fig_scatter = px.scatter(
        df, x="lon", y="lat",
        color="type", color_discrete_map=TYPE_COLORS,
    )
    fig_scatter.update_traces(marker=dict(size=8, line=dict(width=1, color=BLACK)))
    fig_scatter.update_layout(
        template="plotly_white", paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        height=450, title="Mapa de Densidad",
        xaxis=dict(title="Longitud", showgrid=False),
        yaxis=dict(title="Latitud", showgrid=False),
        legend=dict(bgcolor=WHITE, bordercolor=BLACK, borderwidth=2,
                    font=dict(color=BLACK, size=11)),
    )

    return html.Div(style={"display": "flex", "gap": "0", "flexWrap": "wrap"}, children=[
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px", "backgroundColor": WHITE}, children=[
            html.Div(CARD_BODY, children=[
                mondrian_title("Distribución Geográfica"),
                dcc.Graph(figure=fig_lat),
                dcc.Graph(figure=fig_lon),
            ]),
        ]),
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px", "backgroundColor": YELLOW}, children=[
            html.Div(CARD_BODY, children=[
                mondrian_title("Mapa de Densidad"),
                dcc.Graph(figure=fig_scatter),
            ]),
        ]),
    ])


def data_tab(df):
    from dash import dash_table
    return html.Div(style={
        **BLOCK_STYLE, "backgroundColor": WHITE, "padding": "20px",
    }, children=[
        mondrian_title(f"Todos los Registros ({len(df)} puntos)"),
        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in ["name", "description", "lat", "lon", "type"]],
            sort_action="native", page_size=20, filter_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": BLACK, "color": WHITE,
                "fontWeight": "bold", "textTransform": "uppercase",
                "letterSpacing": "0.08em", "fontSize": "0.8rem",
                "border": f"2px solid {BLACK}",
            },
            style_cell={
                "backgroundColor": WHITE, "color": BLACK,
                "border": f"2px solid {BLACK}", "padding": "10px 12px",
                "textAlign": "left", "fontFamily": "'Segoe UI', system-ui, sans-serif",
                "fontSize": "0.85rem",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": GRAY},
            ],
        ),
    ])


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8054)))
