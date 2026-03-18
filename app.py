"""
app.py — KONE Elevator Energy Analytics Dashboard
Run with: python app.py
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import db

# ── Colour palette ───────────────────────────────────────────────────────────
KONE_BLUE   = "#0071B2"
KONE_DARK   = "#00304E"
KONE_LIGHT  = "#E8F4FD"
ACCENT      = "#00A3E0"
REGEN_GREEN = "#00B398"
WARN_AMBER  = "#F5A623"
BG          = "#F0F4F8"
CARD_BG     = "#FFFFFF"
TEXT_DARK   = "#0D1B2A"
TEXT_MID    = "#4A5568"
BORDER      = "#D1DCE8"

FONT_MONO   = "'IBM Plex Mono', monospace"
FONT_SANS   = "'IBM Plex Sans', sans-serif"

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_SANS, color=TEXT_DARK),
        colorway=[KONE_BLUE, REGEN_GREEN, WARN_AMBER, ACCENT, "#8B5CF6"],
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    )
)

# ── App init ─────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    title="KONE | Energy Analytics",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def kpi_card(title, value, unit, sub=None, accent_color=KONE_BLUE):
    return html.Div([
        html.P(title, style={"margin": 0, "fontSize": "11px", "fontWeight": "600",
                              "letterSpacing": "0.08em", "textTransform": "uppercase",
                              "color": TEXT_MID, "fontFamily": FONT_MONO}),
        html.Div([
            html.Span(value, style={"fontSize": "32px", "fontWeight": "700",
                                     "color": accent_color, "fontFamily": FONT_MONO,
                                     "lineHeight": "1.1"}),
            html.Span(f" {unit}", style={"fontSize": "14px", "color": TEXT_MID,
                                          "fontFamily": FONT_SANS, "marginLeft": "4px"}),
        ], style={"marginTop": "6px", "display": "flex", "alignItems": "baseline"}),
        html.P(sub or "", style={"margin": "4px 0 0", "fontSize": "12px",
                                   "color": TEXT_MID, "fontFamily": FONT_SANS}),
    ], style={
        "background": CARD_BG, "borderRadius": "10px", "padding": "20px 24px",
        "border": f"1px solid {BORDER}", "flex": "1",
        "borderTop": f"3px solid {accent_color}",
        "boxShadow": "0 1px 4px rgba(0,71,178,0.06)",
    })


def section_header(title, sub=None):
    return html.Div([
        html.H3(title, style={"margin": 0, "fontSize": "15px", "fontWeight": "600",
                               "color": TEXT_DARK, "fontFamily": FONT_SANS}),
        html.P(sub or "", style={"margin": "2px 0 0", "fontSize": "12px",
                                   "color": TEXT_MID, "fontFamily": FONT_SANS}) if sub else None,
    ], style={"marginBottom": "14px"})


def card(children, style=None):
    base = {"background": CARD_BG, "borderRadius": "10px", "padding": "20px 22px",
            "border": f"1px solid {BORDER}", "boxShadow": "0 1px 4px rgba(0,71,178,0.06)",
            "marginBottom": "18px"}
    base.update(style or {})
    return html.Div(children, style=base)


# ── Layout ────────────────────────────────────────────────────────────────────
buildings_df = db.get_buildings()
bld_options = [{"label": "All Buildings", "value": "ALL"}] + [
    {"label": row["name"], "value": row["id"]} for _, row in buildings_df.iterrows()
]

app.layout = html.Div([

    # ── Top bar ───────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div("KONE", style={
                "fontFamily": FONT_MONO, "fontSize": "22px", "fontWeight": "600",
                "color": "white", "letterSpacing": "0.12em",
                "background": KONE_BLUE, "padding": "4px 14px",
                "borderRadius": "4px", "marginRight": "14px",
            }),
            html.Div([
                html.Span("Energy Analytics", style={
                    "fontFamily": FONT_SANS, "fontSize": "18px",
                    "fontWeight": "600", "color": "white"}),
                html.Span("  //  Elevator Monitoring Platform", style={
                    "fontFamily": FONT_MONO, "fontSize": "12px",
                    "color": "rgba(255,255,255,0.55)", "marginLeft": "8px"}),
            ]),
        ], style={"display": "flex", "alignItems": "center"}),

        html.Div([
            html.Span("● LIVE", style={
                "fontFamily": FONT_MONO, "fontSize": "11px", "color": REGEN_GREEN,
                "letterSpacing": "0.08em"}),
        ]),
    ], style={
        "background": KONE_DARK, "padding": "14px 32px",
        "display": "flex", "alignItems": "center",
        "justifyContent": "space-between",
        "borderBottom": f"2px solid {KONE_BLUE}",
    }),

    # ── Controls bar ─────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Label("Building", style={"fontFamily": FONT_MONO, "fontSize": "11px",
                                          "color": TEXT_MID, "fontWeight": "600",
                                          "letterSpacing": "0.07em", "textTransform": "uppercase",
                                          "marginBottom": "4px", "display": "block"}),
            dcc.Dropdown(
                id="bld-filter",
                options=bld_options,
                value="ALL",
                clearable=False,
                style={"fontFamily": FONT_SANS, "fontSize": "13px", "width": "260px"},
            ),
        ]),
        html.Div([
            html.Label("Time Range", style={"fontFamily": FONT_MONO, "fontSize": "11px",
                                             "color": TEXT_MID, "fontWeight": "600",
                                             "letterSpacing": "0.07em", "textTransform": "uppercase",
                                             "marginBottom": "4px", "display": "block"}),
            dcc.RadioItems(
                id="days-filter",
                options=[
                    {"label": "7 days", "value": 7},
                    {"label": "30 days", "value": 30},
                    {"label": "90 days", "value": 90},
                ],
                value=30,
                inline=True,
                style={"fontFamily": FONT_SANS, "fontSize": "13px", "paddingTop": "6px"},
                inputStyle={"marginRight": "4px", "marginLeft": "14px"},
            ),
        ]),
    ], style={
        "background": CARD_BG, "padding": "14px 32px",
        "display": "flex", "alignItems": "flex-end", "gap": "32px",
        "borderBottom": f"1px solid {BORDER}",
    }),

    # ── Main content ──────────────────────────────────────────────────────────
    html.Div([

        # KPI row
        html.Div(id="kpi-row", style={"display": "flex", "gap": "16px", "marginBottom": "18px"}),

        # Row 2: Daily energy + Hourly profile
        html.Div([
            html.Div([
                card([
                    section_header("Daily Energy Consumption", "Total kWh consumed vs. regenerated per day"),
                    dcc.Graph(id="daily-chart", config={"displayModeBar": False},
                              style={"height": "280px"}),
                ])
            ], style={"flex": "3"}),
            html.Div([
                card([
                    section_header("Hourly Traffic Profile", "Avg. trips & energy by hour of day"),
                    dcc.Graph(id="hourly-chart", config={"displayModeBar": False},
                              style={"height": "280px"}),
                ])
            ], style={"flex": "2"}),
        ], style={"display": "flex", "gap": "18px"}),

        # Row 3: Building comparison + Regen breakdown
        html.Div([
            html.Div([
                card([
                    section_header("Building Energy Comparison", "Last 30 days — total consumption per building"),
                    dcc.Graph(id="bld-bar", config={"displayModeBar": False},
                              style={"height": "260px"}),
                ])
            ], style={"flex": "1"}),
            html.Div([
                card([
                    section_header("Regenerative Energy Savings", "kWh recovered via regenerative braking"),
                    dcc.Graph(id="regen-pie", config={"displayModeBar": False},
                              style={"height": "260px"}),
                ])
            ], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "18px"}),

        # Row 4: Elevator ranking table
        card([
            section_header("Elevator Performance Ranking", "Energy efficiency & utilisation per elevator unit"),
            html.Div(id="elv-table"),
        ]),

    ], style={"padding": "22px 32px", "background": BG, "minHeight": "calc(100vh - 120px)"}),

], style={"fontFamily": FONT_SANS, "background": BG})


# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("kpi-row", "children"),
    Input("bld-filter", "value"),
    Input("days-filter", "value"),
)
def update_kpis(bld, days):
    df = db.get_daily_energy(bld, days)
    if df.empty:
        return []
    total_kwh    = df["total_kwh"].sum()
    regen_kwh    = df["total_regen_kwh"].sum()
    trips        = int(df["total_trips"].sum())
    avg_load     = df["avg_load"].mean()
    savings_pct  = regen_kwh / total_kwh * 100 if total_kwh else 0

    return [
        kpi_card("Total Consumption", f"{total_kwh:,.0f}", "kWh",
                 f"Over last {days} days", KONE_BLUE),
        kpi_card("Regen Savings", f"{regen_kwh:,.0f}", "kWh",
                 f"{savings_pct:.1f}% of total recovered", REGEN_GREEN),
        kpi_card("Total Trips", f"{trips:,}", "",
                 "Elevator rides recorded", KONE_DARK),
        kpi_card("Avg Load", f"{avg_load:.1f}", "%",
                 "Mean cabin utilisation", WARN_AMBER),
    ]


@app.callback(
    Output("daily-chart", "figure"),
    Input("bld-filter", "value"),
    Input("days-filter", "value"),
)
def update_daily(bld, days):
    df = db.get_daily_energy(bld, days)
    if df.empty:
        return go.Figure()

    agg = df.groupby("day").agg(
        total_kwh=("total_kwh", "sum"),
        total_regen_kwh=("total_regen_kwh", "sum"),
    ).reset_index()

    fig = go.Figure(layout_template=PLOTLY_TEMPLATE)
    fig.add_trace(go.Bar(
        x=agg["day"], y=agg["total_kwh"],
        name="Consumed kWh", marker_color=KONE_BLUE, opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        x=agg["day"], y=agg["total_regen_kwh"],
        name="Regenerated kWh", marker_color=REGEN_GREEN, opacity=0.9,
    ))
    fig.update_layout(
        barmode="overlay",
        legend=dict(orientation="h", y=1.12, x=0),
        yaxis_title="kWh",
    )
    return fig


@app.callback(
    Output("hourly-chart", "figure"),
    Input("bld-filter", "value"),
    Input("days-filter", "value"),
)
def update_hourly(bld, days):
    df = db.get_hourly_profile(bld, days)
    if df.empty:
        return go.Figure()

    fig = go.Figure(layout_template=PLOTLY_TEMPLATE)
    fig.add_trace(go.Scatter(
        x=df["hour"], y=df["avg_kwh"],
        mode="lines+markers", name="Avg kWh",
        line=dict(color=KONE_BLUE, width=2.5),
        fill="tozeroy", fillcolor=f"rgba(0,113,178,0.12)",
    ))
    fig.add_trace(go.Scatter(
        x=df["hour"], y=df["avg_trips"],
        mode="lines", name="Avg Trips",
        line=dict(color=WARN_AMBER, width=2, dash="dot"),
        yaxis="y2",
    ))
    fig.update_layout(
        xaxis=dict(tickvals=list(range(0, 24, 3)),
                   ticktext=[f"{h:02d}:00" for h in range(0, 24, 3)]),
        yaxis=dict(title="kWh"),
        yaxis2=dict(title="Trips", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return fig


@app.callback(
    Output("bld-bar", "figure"),
    Input("bld-filter", "value"),
)
def update_bld_bar(_):
    df = db.get_building_summary()
    if df.empty:
        return go.Figure()

    fig = go.Figure(layout_template=PLOTLY_TEMPLATE)
    fig.add_trace(go.Bar(
        x=df["name"], y=df["total_kwh"],
        marker_color=KONE_BLUE, opacity=0.85, name="Consumed",
    ))
    fig.add_trace(go.Bar(
        x=df["name"], y=df["total_regen_kwh"],
        marker_color=REGEN_GREEN, opacity=0.9, name="Regenerated",
    ))
    fig.update_layout(barmode="group", yaxis_title="kWh",
                      xaxis_tickangle=-20)
    return fig


@app.callback(
    Output("regen-pie", "figure"),
    Input("bld-filter", "value"),
    Input("days-filter", "value"),
)
def update_pie(bld, days):
    df = db.get_daily_energy(bld, days)
    if df.empty:
        return go.Figure()

    consumed = df["total_kwh"].sum() - df["total_regen_kwh"].sum()
    regen    = df["total_regen_kwh"].sum()
    standby  = df["total_standby_kwh"].sum()

    fig = go.Figure(go.Pie(
        labels=["Net Active", "Regen Recovered", "Standby"],
        values=[consumed, regen, standby],
        hole=0.55,
        marker_colors=[KONE_BLUE, REGEN_GREEN, WARN_AMBER],
        textfont=dict(family=FONT_SANS, size=12),
    ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        legend=dict(orientation="h", y=-0.08),
        annotations=[dict(text="Energy<br>Split", x=0.5, y=0.5,
                          font_size=13, showarrow=False,
                          font_color=TEXT_DARK, font_family=FONT_MONO)],
    )
    return fig


@app.callback(
    Output("elv-table", "children"),
    Input("bld-filter", "value"),
    Input("days-filter", "value"),
)
def update_table(bld, days):
    df = db.get_elevator_ranking(bld, days)
    if df.empty:
        return html.P("No data available.", style={"color": TEXT_MID})

    df = df.rename(columns={
        "elevator_id": "Unit ID", "model": "Model", "install_year": "Year",
        "building_name": "Building", "total_kwh": "Total kWh",
        "regen_kwh": "Regen kWh", "trips": "Trips",
        "avg_load": "Avg Load %", "kwh_per_trip": "kWh / Trip",
    })

    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        sort_action="native",
        page_size=10,
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": KONE_DARK, "color": "white",
            "fontFamily": FONT_MONO, "fontSize": "11px",
            "fontWeight": "600", "letterSpacing": "0.06em",
            "border": "none", "padding": "10px 14px",
        },
        style_cell={
            "fontFamily": FONT_SANS, "fontSize": "13px",
            "color": TEXT_DARK, "padding": "9px 14px",
            "border": f"1px solid {BORDER}", "textAlign": "left",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": KONE_LIGHT},
            {"if": {"filter_query": "{kWh / Trip} > 0.02"},
             "color": WARN_AMBER, "fontWeight": "600"},
        ],
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
