"""Dash Dashboard: Sanitización Comuna de Santiago — Data-Art Poster Edition."""

from pathlib import Path
from typing import Any

import os

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

FONT_UI = "'Inter','Segoe UI',system-ui,sans-serif"
FONT_DATA = "'JetBrains Mono',Consolas,'Courier New',monospace"

BG = "#0a0e14"
CARD = "#11161f"
HAIRLINE = "1px solid rgba(255,255,255,0.08)"
TEXT = "#e8edf2"
MUTED = "#8b94a3"
RED = "#f472b6"
BLUE = "#54a0ff"
YELLOW = "#fbbf24"
GREEN = "#34d399"
CYAN = "#22d3ee"

TYPE_COLORS: dict[str, str] = {
    "Cité": RED, "Pasaje": BLUE, "Edificio": YELLOW,
    "Domicilio": CYAN, "Calle": GREEN, "Otro": "#a78bfa",
}

DATA_PATH = Path(__file__).parent / "data" / "raw" / "sanitization_points.csv"

BLOCK_STYLE: dict[str, Any] = {
    "border": HAIRLINE,
    "borderRadius": "14px",
    "padding": "0",
    "backgroundColor": CARD,
}

CARD_BODY: dict[str, Any] = {
    "padding": "20px",
}

CHART_TEMPLATE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter,Segoe UI,sans-serif", color="#e8edf2", size=13),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)",
               title=dict(font=dict(size=13)), tickfont=dict(family="JetBrains Mono,monospace", size=12)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)",
               title=dict(font=dict(size=13)), tickfont=dict(family="JetBrains Mono,monospace", size=12)),
    legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
)

DATA_CANVAS_SVG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='110' viewBox='0 0 1200 110'%3E"
    "%3Crect width='1200' height='110' fill='%230a0e14'/%3E"
    "%3Cg fill='%2322d3ee' opacity='0.16'%3E"
    + "".join(f"%3Ccircle cx='{x}' cy='{y}' r='2'/%3E" for x in range(30, 1200, 60) for y in range(20, 110, 30)) +
    "%3C/g%3E%3Cg fill='none' stroke='%23f472b6' stroke-width='2' opacity='0.7'%3E"
    "%3Cpath d='M0,85 Q200,40 400,65 T800,35 T1200,60'/%3E%3C/g%3E"
    "%3Cg fill='%23fbbf24' opacity='0.9'%3E"
    "%3Ccircle cx='150' cy='50' r='5'/%3E%3Ccircle cx='450' cy='75' r='4'/%3E%3Ccircle cx='750' cy='40' r='6'/%3E%3Ccircle cx='1020' cy='65' r='5'/%3E"
    "%3C/g%3E%3C/svg%3E"
)


def load_data() -> pd.DataFrame:
    """Load and validate sanitization points data."""
    if not DATA_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(DATA_PATH)
    required_cols = {"name", "description", "lat", "lon", "type"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"[WARN] Missing columns: {missing}")
        return pd.DataFrame()
    lat_ok = df["lat"].between(-33.55, -33.35).all()
    lon_ok = df["lon"].between(-70.8, -70.55).all()
    if not lat_ok or not lon_ok:
        print("[WARN] Coordinates outside Santiago bounds")
    valid_types = {"Pasaje", "Edificio", "Domicilio", "Calle", "Otro"}
    invalid = set(df["type"].unique()) - valid_types
    if invalid:
        print(f"[WARN] Invalid types found: {invalid}")
    return df


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
            "borderTop": f"3px solid {bg_color}",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center",
            "minWidth": "120px",
            "minHeight": "90px",
        },
        children=[
            html.Div(str(value), style={
                "fontSize": "2rem", "fontWeight": "800",
                "color": TEXT,
                "fontFamily": FONT_DATA,
            }),
            html.Div(label, style={
                "fontSize": "0.75rem", "fontWeight": "600",
                "letterSpacing": "0.08em",
                "color": MUTED,
                "fontFamily": FONT_UI,
                "marginTop": "2px",
            }),
        ],
    )


def mondrian_title(text):
    return html.Div(children=[
        html.H3(text, style={
            "fontSize": "1.05rem", "fontWeight": "700",
            "margin": "0 0 4px 0",
            "color": TEXT, "fontFamily": FONT_UI,
        }),
        html.Div("insights · metodología · decisión", style={
            "color": MUTED, "fontSize": "0.75rem",
            "fontFamily": FONT_DATA, "marginBottom": "12px",
        }),
    ])


def sparkline(values, color=RED):
    if not values or len(values) < 2:
        return html.Div(style={"height": "34px"})
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=list(values), mode="lines",
        line={"color": color, "width": 2.5, "shape": "spline"},
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
        style={**BLOCK_STYLE, "borderLeft": f"3px solid {accent}", "padding": "14px 16px", "marginBottom": "12px"},
        children=[
            html.Div(question, style={"fontWeight": "700", "fontSize": "0.75rem", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": accent, "fontFamily": FONT_UI}),
            html.Div(answer, style={"marginTop": "4px", "color": TEXT, "lineHeight": "1.55", "fontSize": "0.92rem"}),
        ],
    )


app.layout = html.Div(
    style={
        "backgroundColor": BG, "minHeight": "100vh",
        "fontFamily": FONT_UI, "color": TEXT,
        "margin": "0", "padding": "0",
    },
    children=[
        html.Div(
            style={
                "padding": "36px 20px 28px 20px",
                "textAlign": "center",
                "borderBottom": "1px solid rgba(255,255,255,0.08)",
            },
            children=[
                html.Div(
                    "PORTFOLIO · DATA ART",
                    style={"display": "inlineBlock", "color": CYAN, "fontWeight": "700", "letterSpacing": "0.28em", "fontSize": "0.7rem", "fontFamily": FONT_DATA, "padding": "6px 0", "marginBottom": "10px", "borderBottom": "1px solid rgba(34,211,238,0.4)"},
                ),
                html.H1("Sanitización Santiago", style={
                    "fontSize": "2.2rem", "fontWeight": "800", "color": TEXT,
                    "margin": "0", "letterSpacing": "-0.01em",
                }),
                html.P("Mapa de solicitudes de sanitización — Datos georeferenciados", style={
                    "color": MUTED, "marginTop": "8px", "fontSize": "0.95rem",
                    "fontFamily": FONT_DATA,
                }),
            ],
        ),
        html.Div(style={
            "backgroundImage": f"url(\"{DATA_CANVAS_SVG}\")",
            "backgroundSize": "cover", "backgroundPosition": "center",
            "height": "110px", "borderBottom": "1px solid rgba(255,255,255,0.08)",
        }),
        html.Div(style={
            "display": "flex", "gap": "14px", "padding": "18px 20px",
            "flexWrap": "wrap", "borderBottom": "1px solid rgba(255,255,255,0.08)",
            "maxWidth": "1200px", "margin": "0 auto",
        }, children=[
            html.Div(style={
                "flex": "3", "minWidth": "250px",
                "padding": "16px 18px", "backgroundColor": CARD,
                "border": "1px solid rgba(255,255,255,0.08)", "borderRadius": "12px",
            }, children=[
                html.Label("Filtrar por tipo", style={
                    "color": MUTED, "fontSize": "0.75rem",
                    "letterSpacing": "0.08em", "fontWeight": "700",
                }),
                dcc.Checklist(
                    id="filter-type",
                    options=[{"label": f" {t}", "value": t} for t in get_data()["type"].unique()] if not get_data().empty else [],
                    value=get_data()["type"].unique().tolist() if not get_data().empty else [],
                    inline=True,
                    style={"color": TEXT, "marginTop": "6px"},
                    inputStyle={"marginRight": "4px", "accentColor": CYAN},
                ),
            ]),
            html.Div(style={
                "flex": "2", "minWidth": "200px", "padding": "16px 18px",
                "backgroundColor": CARD,
                "border": "1px solid rgba(255,255,255,0.08)", "borderRadius": "12px",
            }, children=[
                html.Label("Buscar por nombre", style={
                    "color": MUTED, "fontSize": "0.75rem",
                    "letterSpacing": "0.08em", "fontWeight": "700",
                }),
                dcc.Dropdown(
                    id="filter-name",
                    options=[{"label": n, "value": n} for n in get_data()["name"].tolist()] if not get_data().empty else [],
                    multi=True,
                    placeholder="Seleccionar...",
                    style={"backgroundColor": BG, "color": TEXT},
                ),
            ]),
        ]),
        dcc.Tabs(
            id="tabs", value="map",
            style={"backgroundColor": "transparent", "borderBottom": "1px solid rgba(255,255,255,0.08)"},
            children=[
                dcc.Tab(label="Mapa", value="map", style={
                    "backgroundColor": "transparent", "color": MUTED, "border": "none",
                    "borderBottom": "2px solid transparent",
                    "fontWeight": "600", "fontSize": "0.85rem", "padding": "14px 20px",
                }, selected_style={
                    "backgroundColor": "transparent", "color": TEXT, "border": "none",
                    "borderBottom": "2px solid #22d3ee",
                    "fontWeight": "700", "fontSize": "0.85rem", "padding": "14px 20px",
                }),
                dcc.Tab(label="Distribución", value="dist", style={
                    "backgroundColor": "transparent", "color": MUTED, "border": "none",
                    "borderBottom": "2px solid transparent",
                    "fontWeight": "600", "fontSize": "0.85rem", "padding": "14px 20px",
                }, selected_style={
                    "backgroundColor": "transparent", "color": TEXT, "border": "none",
                    "borderBottom": "2px solid #22d3ee",
                    "fontWeight": "700", "fontSize": "0.85rem", "padding": "14px 20px",
                }),
                dcc.Tab(label="Análisis", value="analysis", style={
                    "backgroundColor": "transparent", "color": MUTED, "border": "none",
                    "borderBottom": "2px solid transparent",
                    "fontWeight": "600", "fontSize": "0.85rem", "padding": "14px 20px",
                }, selected_style={
                    "backgroundColor": "transparent", "color": TEXT, "border": "none",
                    "borderBottom": "2px solid #22d3ee",
                    "fontWeight": "700", "fontSize": "0.85rem", "padding": "14px 20px",
                }),
                dcc.Tab(label="Datos", value="data", style={
                    "backgroundColor": "transparent", "color": MUTED, "border": "none",
                    "borderBottom": "2px solid transparent",
                    "fontWeight": "600", "fontSize": "0.85rem", "padding": "14px 20px",
                }, selected_style={
                    "backgroundColor": "transparent", "color": TEXT, "border": "none",
                    "borderBottom": "2px solid #22d3ee",
                    "fontWeight": "700", "fontSize": "0.85rem", "padding": "14px 20px",
                }),
            ],
        ),
        html.Div(id="tab-content", style={"maxWidth": "1200px", "margin": "0 auto", "padding": "24px 20px"}),
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
        **BLOCK_STYLE, "backgroundColor": "#2a0e18",
        "padding": "60px 20px", "textAlign": "center",
    }, children=[
        html.P(msg, style={"color": TEXT, "fontSize": "1rem",
                           "letterSpacing": "0.05em", "margin": "0"}),
    ])


def map_tab(df):
    total = len(df)
    fig = px.scatter_map(
        df, lat="lat", lon="lon", color="type",
        hover_name="name", hover_data=["description", "type"],
        center={"lat": -33.45, "lon": -70.66}, zoom=12,
        map_style="carto-darkmatter",
        color_discrete_map=TYPE_COLORS,
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]}<br>Tipo: %{customdata[1]}<br>%{lat:.4f}°, %{lon:.4f}°<extra></extra>",
    )
    fig.update_layout(
        **CHART_TEMPLATE, height=600, margin=dict(t=10, b=10, l=10, r=10),
    )
    fig.update_layout(legend=dict(bgcolor="rgba(10,14,20,0.8)", font=dict(color=TEXT, size=11)))
    by_type = df["type"].value_counts()
    top_type = by_type.index[0] if len(by_type) else "—"
    count_block = stat_block(total, "puntos", RED)
    insights = html.Div(style={**BLOCK_STYLE, "padding": "16px 18px", "marginBottom": "16px"}, children=[
        mondrian_title("Key Insights"),
        insight_card("¿Problema?", f"{total} solicitudes dispersas sin priorización visible por tipo ni calle.", RED),
        insight_card("¿Metodología?", f"Georreferenciación validada + top tipo '{top_type}' ({by_type.iloc[0] if len(by_type) else 0} casos) para focalizar cuadrillas.", BLUE),
        insight_card("¿Decisión?", "Asignar rutas por calle frecuente y tipo dominante; clic en barras de Distribución para filtrar.", GREEN),
        sparkline(by_type.values.tolist(), RED),
    ])
    type_codes = {t: i for i, t in enumerate(sorted(df["type"].unique()))}
    fig3d = go.Figure()
    for t in sorted(df["type"].unique()):
        tdf = df[df["type"] == t]
        fig3d.add_trace(go.Scatter3d(
            x=tdf["lon"], y=tdf["lat"], z=[type_codes[t]] * len(tdf),
            mode="markers", name=t,
            marker=dict(size=5, opacity=0.85, color=TYPE_COLORS.get(t, RED)),
            hovertemplate=f"<b>Tipo: {t}</b><br>Lon: %{{x:.4f}}<br>Lat: %{{y:.4f}}<extra></extra>",
        ))
    fig3d.update_layout(
        **CHART_TEMPLATE, height=550, margin=dict(t=10, b=10, l=10, r=10),
        title="Torre 3D por tipo — arrastra para rotar",
        scene=dict(
            xaxis_title="Longitud", yaxis_title="Latitud", zaxis_title="Tipo",
            xaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.06)"),
            zaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.06)",
                       tickvals=list(type_codes.values()), ticktext=list(type_codes.keys())),
        ),
    )
    return html.Div(children=[
        insights,
        html.Div(style={"display": "flex", "gap": "14px", "flexWrap": "wrap"}, children=[
            html.Div(style={**BLOCK_STYLE, "flex": "3", "minWidth": "300px"}, children=[
                html.Div(style=CARD_BODY, children=[
                    mondrian_title("Mapa de Sanitización"),
                    dcc.Graph(figure=fig, style={"margin": "0"}),
                ]),
            ]),
            html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "140px",
                             "display": "flex", "flexDirection": "column", "gap": "14px",
                             "backgroundColor": "transparent", "border": "none", "padding": "0"}, children=[
                count_block,
                html.Div(style={**BLOCK_STYLE, "backgroundColor": "#0f2a4a", "flex": "1",
                                 "display": "flex", "alignItems": "center", "justifyContent": "center",
                                 "minHeight": "90px"}, children=[
                    html.Div(f"{len(df['type'].unique())} tipos", style={
                        "color": TEXT, "fontSize": "1.4rem", "fontWeight": "800",
                        "fontFamily": FONT_DATA,
                    }),
                ]),
                html.Div(style={**BLOCK_STYLE, "backgroundColor": "#12261c", "flex": "1",
                                 "display": "flex", "alignItems": "center", "justifyContent": "center",
                                 "minHeight": "90px"}, children=[
                    html.Div(f"{df['lat'].mean():.4f}°", style={
                        "color": TEXT, "fontSize": "1.4rem", "fontWeight": "800",
                        "fontFamily": FONT_DATA,
                    }),
                ]),
            ]),
        ]),
        html.Div(style={**BLOCK_STYLE, "marginTop": "16px"}, children=[
            html.Div(style=CARD_BODY, children=[
                mondrian_title("Torre 3D por Tipo"),
                dcc.Graph(figure=fig3d),
            ]),
        ]),
    ])


def dist_tab(df):
    total = len(df)
    tipo_counts = df["type"].value_counts()

    fig_bar = px.bar(
        x=tipo_counts.index, y=tipo_counts.values,
        color=tipo_counts.index, color_discrete_map=TYPE_COLORS,
        labels={"x": "Tipo", "y": "Cantidad"},
        title="Puntos por Tipo — clic una barra para filtrar",
    )
    fig_bar.update_traces(
        hovertemplate="<b>%{x}</b><br>Cantidad: %{y}<br>%{y:.0%} de " + str(total) + "<extra></extra>",
    )
    fig_bar.update_layout(**CHART_TEMPLATE, height=380, showlegend=False, bargap=0.3)

    fig_pie = px.pie(
        values=tipo_counts.values, names=tipo_counts.index,
        color=tipo_counts.index, color_discrete_map=TYPE_COLORS,
    )
    fig_pie.update_traces(
        textfont_size=12,
        hovertemplate="<b>%{label}</b><br>%{value} puntos<br>%{percent}<extra></extra>",
    )
    fig_pie.update_layout(**CHART_TEMPLATE, height=380, showlegend=True)

    df_copy = df.copy()
    df_copy["street"] = df_copy["name"].str.extract(r"^([A-Za-z0-9áéíóúñü\s\.\-]+)")
    df_copy["street"] = df_copy["street"].str.strip()
    street_counts = df_copy["street"].dropna().value_counts().head(15)
    fig_streets = px.bar(
        x=street_counts.values, y=street_counts.index, orientation="h",
        color_discrete_sequence=[BLUE],
    )
    fig_streets.update_traces(
        hovertemplate="Calle: %{y}<br>Puntos: %{x}<extra></extra>",
    )
    fig_streets.update_layout(**CHART_TEMPLATE, height=500, showlegend=False)
    fig_streets.update_layout(yaxis_categoryorder="total ascending")

    return html.Div(children=[
        html.Div(id="dist-crossfilter-output", style={"fontWeight": "600", "color": MUTED, "padding": "4px 20px 12px 20px"}),
        html.Div(style={"display": "flex", "gap": "14px", "flexWrap": "wrap"}, children=[
            html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px"}, children=[
                html.Div(style=CARD_BODY, children=[
                    mondrian_title("Puntos por Tipo"),
                    dcc.Graph(id="dist-type-bar", figure=fig_bar),
                ]),
            ]),
            html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px"}, children=[
                html.Div(style=CARD_BODY, children=[
                    mondrian_title("Distribución por Tipo"),
                    dcc.Graph(figure=fig_pie),
                ]),
            ]),
            html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px"}, children=[
                html.Div(style=CARD_BODY, children=[
                    mondrian_title("Calles Más Frecuentes"),
                    dcc.Graph(figure=fig_streets),
                ]),
            ]),
            html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px"}, children=[
                html.Div(style=CARD_BODY, children=[
                    mondrian_title("Nube de Puntos — latitud por tipo"),
                    dcc.Graph(figure=_strip_fig(df)),
                ]),
            ]),
        ]),
    ])


def _strip_fig(df):
    fig = px.strip(
        df, x="type", y="lat", color="type",
        title="Dot-density: cada punto es una solicitud",
        color_discrete_map=TYPE_COLORS,
        hover_name="name",
    )
    fig.update_traces(
        marker=dict(size=10, opacity=0.8),
        hovertemplate="<b>%{hovertext}</b><br>Tipo: %{x}<br>Lat: %{y:.4f}°<extra></extra>",
    )
    fig.update_layout(
        **CHART_TEMPLATE, height=500, showlegend=False,
        yaxis_title="Latitud",
    )
    return fig


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
        **CHART_TEMPLATE, height=320, title="Distribución de Latitud",
        xaxis_title="Latitud", yaxis_title="Cantidad",
    )

    fig_lon = px.histogram(
        df, x="lon", nbins=20,
        color_discrete_sequence=[BLUE],
    )
    fig_lon.update_layout(
        **CHART_TEMPLATE, height=320, title="Distribución de Longitud",
        xaxis_title="Longitud", yaxis_title="Cantidad",
    )

    fig_scatter = px.scatter(
        df, x="lon", y="lat",
        color="type", color_discrete_map=TYPE_COLORS,
    )
    fig_scatter.update_traces(
        marker=dict(size=8, opacity=0.8),
        hovertemplate="Lon: %{x:.4f}<br>Lat: %{y:.4f}<extra></extra>",
    )
    fig_scatter.update_layout(
        **CHART_TEMPLATE, height=450, title="Mapa de Densidad",
        xaxis_title="Longitud", yaxis_title="Latitud",
    )

    return html.Div(style={"display": "flex", "gap": "14px", "flexWrap": "wrap"}, children=[
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px"}, children=[
            html.Div(style=CARD_BODY, children=[
                mondrian_title("Distribución Geográfica"),
                dcc.Graph(figure=fig_lat),
                dcc.Graph(figure=fig_lon),
            ]),
        ]),
        html.Div(style={**BLOCK_STYLE, "flex": "1", "minWidth": "300px"}, children=[
            html.Div(style=CARD_BODY, children=[
                mondrian_title("Mapa de Densidad"),
                dcc.Graph(figure=fig_scatter),
            ]),
        ]),
    ])


def data_tab(df):
    from dash import dash_table
    return html.Div(style={
        **BLOCK_STYLE, "padding": "20px",
    }, children=[
        mondrian_title(f"Todos los Registros ({len(df)} puntos)"),
        dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": c, "id": c} for c in ["name", "description", "lat", "lon", "type"]],
            sort_action="native", page_size=20, filter_action="native",
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#0f2a4a", "color": TEXT,
                "fontWeight": "700", "fontSize": "0.8rem",
                "border": "1px solid rgba(255,255,255,0.08)",
            },
            style_cell={
                "backgroundColor": CARD, "color": TEXT,
                "border": "1px solid rgba(255,255,255,0.06)", "padding": "10px 12px",
                "textAlign": "left", "fontFamily": FONT_UI,
                "fontSize": "0.85rem",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#0d1320"},
            ],
        ),
    ])


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8056)))
