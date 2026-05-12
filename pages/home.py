from dash import html, dcc, callback, Input, Output, register_page
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.dashboard_utils import load_csv, get_department_options, get_year_options, filter_df, fmt_num, apply_figure_style

register_page(__name__, path="/", name="Diagnóstico")

# =========================
# Carga de datos
# =========================
MONTHLY = load_csv("monthly_app.csv")
MONTHLY["fecha_mes"] = pd.to_datetime(MONTHLY["fecha_mes"], errors="coerce")

WEEKLY = load_csv("weekly_app.csv")
WEEKLY["fecha_semana_inicio"] = pd.to_datetime(WEEKLY["fecha_semana_inicio"], errors="coerce")
WEEKLY["fecha_semana_fin"] = pd.to_datetime(WEEKLY["fecha_semana_fin"], errors="coerce")

# =========================
# Paleta
# =========================
COLOR_GREEN = "#13352c"
COLOR_GREEN_2 = "#1d5243"
COLOR_BLUE = "#2b6777"
COLOR_BROWN = "#8a6a4a"
COLOR_GOLD = "#c49a00"
COLOR_RED = "#b94a48"
COLOR_BG = "white"
COLOR_GRID = "#e8ece9"
COLOR_TEXT = "#1f2a24"


def style_figure(fig, title=None, height=360):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(
            family='"Abadi MT Condensed Light", "Segoe UI", Arial, sans-serif',
            size=13,
            color=COLOR_TEXT
        ),
        title=dict(
            text=title if title else fig.layout.title.text,
            x=0.03,
            xanchor="left",
            font=dict(size=20, color=COLOR_GREEN)
        ),
        margin=dict(l=45, r=25, t=65, b=45),
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#d6ddd9",
        title_font=dict(size=13, color=COLOR_TEXT),
        tickfont=dict(size=12, color=COLOR_TEXT)
    )
    fig.update_yaxes(
        gridcolor=COLOR_GRID,
        zerolinecolor=COLOR_GRID,
        title_font=dict(size=13, color=COLOR_TEXT),
        tickfont=dict(size=12, color=COLOR_TEXT)
    )
    return fig


def kpi_block(title, value, subtitle=None):
    children = [
        html.H3(title),
        html.P(value)
    ]
    if subtitle:
        children.append(html.Small(subtitle, style={"color": "#5f6c67"}))
    return children


layout = html.Div(
    className="page-content",
    children=[
        html.H2("Diagnóstico territorial del sistema cafetero", className="page-title"),
        html.P(
            "Producción proxy, señal climática y contexto económico por departamento.",
            className="page-intro",
        ),

        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-card",
                    children=[
                        html.Label("Departamento"),
                        dcc.Dropdown(
                            id="diag-dept",
                            options=get_department_options(MONTHLY),
                            value="TODOS",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-card",
                    children=[
                        html.Label("Año"),
                        dcc.Dropdown(
                            id="diag-year",
                            options=get_year_options(MONTHLY),
                            value="TODOS",
                            clearable=False,
                        ),
                    ],
                ),
            ],
        ),

        html.Div(
            className="kpi-row",
            children=[
                html.Div(className="kpi-card", id="kpi-prod"),
                html.Div(className="kpi-card", id="kpi-rend"),
                html.Div(className="kpi-card", id="kpi-index"),
                html.Div(className="kpi-card", id="kpi-alert"),
            ],
        ),

        html.Div(
            className="chart-grid",
            children=[
                dcc.Graph(id="prod-chart", className="chart-card"),
                dcc.Graph(id="index-prod-chart", className="chart-card"),
                dcc.Graph(id="ranking-chart", className="chart-card"),
                dcc.Graph(id="weekly-alert-chart", className="chart-card"),
                dcc.Graph(id="price-trm-chart", className="chart-card"),
                dcc.Graph(id="exports-external-chart", className="chart-card"),
            ],
        ),
    ],
)


@callback(
    Output("kpi-prod", "children"),
    Output("kpi-rend", "children"),
    Output("kpi-index", "children"),
    Output("kpi-alert", "children"),
    Output("prod-chart", "figure"),
    Output("index-prod-chart", "figure"),
    Output("ranking-chart", "figure"),
    Output("weekly-alert-chart", "figure"),
    Output("price-trm-chart", "figure"),
    Output("exports-external-chart", "figure"),
    Input("diag-dept", "value"),
    Input("diag-year", "value"),
)
def update_home(dept_value, year_value):
    dfm = filter_df(MONTHLY, dept_value, year_value).copy()
    dfw = filter_df(WEEKLY, dept_value, year_value).copy()

    # =========================
    # KPIs
    # =========================
    prod_mean = dfm["produccion_mensual_proxy_t"].mean()
    rend_mean = dfm["rendimiento_departamental_t_ha"].mean()
    idx_mean = dfm["indice_climatico_ajustado_x_mean"].mean()

    dfw["alerta_climatica"] = (
        dfw["dummy_exceso_lluvia_p75"].fillna(0).astype(int)
        + dfw["dummy_estres_hidrico_p25"].fillna(0).astype(int)
        + dfw["dummy_temp_max_alta_p75"].fillna(0).astype(int)
    )
    alert_mean = dfw["alerta_climatica"].mean()

    kpi_prod = kpi_block("Producción mensual proxy", fmt_num(prod_mean, 1), "Promedio del período seleccionado")
    kpi_rend = kpi_block("Rendimiento", fmt_num(rend_mean, 2), "t/ha promedio")
    kpi_index = kpi_block("Índice climático ajustado", fmt_num(idx_mean, 2), "Señal climática resumida")
    kpi_alert = kpi_block("Alertas climáticas promedio", fmt_num(alert_mean, 2), "Basado en señal weekly")

    # =========================
    # Gráfico 1: producción mensual
    # =========================
    prod_ts = (
        dfm.groupby("fecha_mes", as_index=False)["produccion_mensual_proxy_t"]
        .mean()
        .sort_values("fecha_mes")
    )

    fig_prod = go.Figure()
    fig_prod.add_trace(
        go.Scatter(
            x=prod_ts["fecha_mes"],
            y=prod_ts["produccion_mensual_proxy_t"],
            mode="lines+markers",
            name="Producción proxy",
            line=dict(color=COLOR_GREEN, width=3),
            marker=dict(color=COLOR_GREEN, size=7),
        )
    )
    fig_prod.update_yaxes(title_text="Producción mensual proxy (t)")
    fig_prod.update_xaxes(title_text="Fecha")
    fig_prod = style_figure(fig_prod, "Producción mensual proxy")

    # =========================
    # Gráfico 2: índice climático + producción
    # =========================
    idx_ts = (
        dfm.groupby("fecha_mes", as_index=False)[
            ["indice_climatico_ajustado_x_mean", "produccion_mensual_proxy_t"]
        ]
        .mean()
        .sort_values("fecha_mes")
    )

    fig_idx = make_subplots(specs=[[{"secondary_y": True}]])
    fig_idx.add_trace(
        go.Scatter(
            x=idx_ts["fecha_mes"],
            y=idx_ts["indice_climatico_ajustado_x_mean"],
            mode="lines+markers",
            name="Índice climático ajustado",
            line=dict(color=COLOR_BLUE, width=3),
            marker=dict(color=COLOR_BLUE, size=6),
        ),
        secondary_y=False,
    )
    fig_idx.add_trace(
        go.Scatter(
            x=idx_ts["fecha_mes"],
            y=idx_ts["produccion_mensual_proxy_t"],
            mode="lines",
            name="Producción proxy",
            line=dict(color=COLOR_BROWN, width=3, dash="dot"),
        ),
        secondary_y=True,
    )
    fig_idx.update_yaxes(title_text="Índice climático", secondary_y=False)
    fig_idx.update_yaxes(title_text="Producción proxy (t)", secondary_y=True)
    fig_idx.update_xaxes(title_text="Fecha")
    fig_idx = style_figure(fig_idx, "Índice climático ajustado vs producción")

    # =========================
    # Gráfico 3: ranking territorial
    # =========================
    ranking = (
        filter_df(MONTHLY, "TODOS", year_value)
        .groupby("departamento", as_index=False)[
            ["produccion_mensual_proxy_t", "indice_climatico_ajustado_x_mean"]
        ]
        .mean()
        .sort_values("produccion_mensual_proxy_t", ascending=False)
    )

    fig_rank = px.bar(
        ranking,
        x="departamento",
        y="produccion_mensual_proxy_t",
        color="indice_climatico_ajustado_x_mean",
        color_continuous_scale=["#dcebe5", "#7ca694", "#1d5243"],
        title="Ranking departamental por producción proxy"
    )
    fig_rank.update_yaxes(title_text="Producción mensual proxy promedio (t)")
    fig_rank.update_xaxes(title_text="Departamento")
    fig_rank = style_figure(fig_rank, "Ranking departamental por producción proxy")
    fig_rank.update_layout(coloraxis_colorbar_title="Índice climático")

    # =========================
    # Gráfico 4: alertas semanales
    # =========================
    weekly_alert = (
        dfw.groupby("fecha_semana_inicio", as_index=False)["alerta_climatica"]
        .mean()
        .sort_values("fecha_semana_inicio")
    )

    fig_weekly = go.Figure()
    fig_weekly.add_trace(
        go.Scatter(
            x=weekly_alert["fecha_semana_inicio"],
            y=weekly_alert["alerta_climatica"],
            mode="lines+markers",
            name="Alertas",
            line=dict(color=COLOR_RED, width=3),
            marker=dict(color=COLOR_RED, size=6),
            fill="tozeroy",
            fillcolor="rgba(185, 74, 72, 0.12)"
        )
    )
    fig_weekly.update_yaxes(title_text="Señal de alertas")
    fig_weekly.update_xaxes(title_text="Semana")
    fig_weekly = style_figure(fig_weekly, "Monitoreo semanal de alertas climáticas")

    # =========================
    # Gráfico 5: precio interno + TRM
    # =========================
    econ_1 = (
        dfm.groupby("fecha_mes", as_index=False)[
            ["precio_interno_cop_carga_mean", "trm_promedio_semana_cop_usd_mean"]
        ]
        .mean()
        .sort_values("fecha_mes")
    )

    fig_price = make_subplots(specs=[[{"secondary_y": True}]])
    fig_price.add_trace(
        go.Scatter(
            x=econ_1["fecha_mes"],
            y=econ_1["precio_interno_cop_carga_mean"],
            mode="lines+markers",
            name="Precio interno",
            line=dict(color=COLOR_GREEN_2, width=3),
            marker=dict(color=COLOR_GREEN_2, size=6),
        ),
        secondary_y=False,
    )
    fig_price.add_trace(
        go.Scatter(
            x=econ_1["fecha_mes"],
            y=econ_1["trm_promedio_semana_cop_usd_mean"],
            mode="lines",
            name="TRM",
            line=dict(color=COLOR_GOLD, width=3, dash="dash"),
        ),
        secondary_y=True,
    )
    fig_price.update_yaxes(title_text="Precio interno COP/carga", secondary_y=False)
    fig_price.update_yaxes(title_text="TRM COP/USD", secondary_y=True)
    fig_price.update_xaxes(title_text="Fecha")
    fig_price = style_figure(fig_price, "Precio interno y TRM")

    # =========================
    # Gráfico 6: exportaciones + precio externo
    # =========================
    econ_2 = (
        dfm.groupby("fecha_mes", as_index=False)[
            ["exportaciones_mensual_miles_sacos_mean", "precio_externo_exdock_cent_usd_lb_mean"]
        ]
        .mean()
        .sort_values("fecha_mes")
    )

    fig_exports = make_subplots(specs=[[{"secondary_y": True}]])
    fig_exports.add_trace(
        go.Bar(
            x=econ_2["fecha_mes"],
            y=econ_2["exportaciones_mensual_miles_sacos_mean"],
            name="Exportaciones",
            marker_color=COLOR_BLUE,
            opacity=0.75,
        ),
        secondary_y=False,
    )
    fig_exports.add_trace(
        go.Scatter(
            x=econ_2["fecha_mes"],
            y=econ_2["precio_externo_exdock_cent_usd_lb_mean"],
            mode="lines+markers",
            name="Precio externo",
            line=dict(color=COLOR_BROWN, width=3),
            marker=dict(color=COLOR_BROWN, size=6),
        ),
        secondary_y=True,
    )
    fig_exports.update_yaxes(title_text="Exportaciones (miles sacos)", secondary_y=False)
    fig_exports.update_yaxes(title_text="Precio externo (cent USD/lb)", secondary_y=True)
    fig_exports.update_xaxes(title_text="Fecha")
    fig_exports = style_figure(fig_exports, "Exportaciones y precio externo")

    return (
        kpi_prod,
        kpi_rend,
        kpi_index,
        kpi_alert,
        fig_prod,
        fig_idx,
        fig_rank,
        fig_weekly,
        fig_price,
        fig_exports,
    )