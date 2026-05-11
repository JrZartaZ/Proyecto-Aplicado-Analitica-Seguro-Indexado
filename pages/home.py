import pandas as pd
import plotly.express as px
from dash import html, dcc, callback, Input, Output, register_page
from src.dashboard_utils import load_csv, get_department_options, get_year_options, filter_df, fmt_num, apply_figure_style
register_page(__name__, path="/", name="Diagnóstico")

MONTHLY = load_csv("monthly_app.csv")
MONTHLY["fecha_mes"] = pd.to_datetime(MONTHLY["fecha_mes"], errors="coerce")
WEEKLY = load_csv("weekly_app.csv")
WEEKLY["fecha_semana_inicio"] = pd.to_datetime(WEEKLY["fecha_semana_inicio"], errors="coerce")

layout = html.Div(
    className="page-content",
    children=[
        html.H2("Diagnóstico descriptivo y contexto territorial", className="page-title"),
        html.P(
            "Vista descriptiva del comportamiento productivo, climático y económico por departamento.",
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
                html.Div(className="kpi-card", id="kpi-rain"),
                html.Div(className="kpi-card", id="kpi-price"),
            ],
        ),
        html.Div(
            className="chart-grid",
            children=[
                dcc.Graph(id="prod-chart", className="chart-card"),
                dcc.Graph(id="clima-chart", className="chart-card"),
                dcc.Graph(id="bar-chart", className="chart-card"),
                dcc.Graph(id="weekly-alert-chart", className="chart-card"),
            ],
        ),
    ],
)

@callback(
    Output("kpi-prod", "children"),
    Output("kpi-rend", "children"),
    Output("kpi-rain", "children"),
    Output("kpi-price", "children"),
    Output("prod-chart", "figure"),
    Output("clima-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("weekly-alert-chart", "figure"),
    Input("diag-dept", "value"),
    Input("diag-year", "value"),
)
def update_page(dept_value, year_value):
    df = filter_df(MONTHLY, dept_value, year_value)
    dfw = filter_df(WEEKLY, dept_value, year_value)

    prod_mean = df["produccion_mensual_proxy_t"].mean()
    rend_mean = df["rendimiento_departamental_t_ha"].mean()
    rain_mean = df["PRECTOTCORR"].mean()
    price_mean = df["precio_interno_cop_carga_mean"].mean()

    prod_kpi = [html.H3("Producción mensual proxy"), html.P(fmt_num(prod_mean, 1))]
    rend_kpi = [html.H3("Rendimiento"), html.P(fmt_num(rend_mean, 2))]
    rain_kpi = [html.H3("Precipitación"), html.P(fmt_num(rain_mean, 1))]
    price_kpi = [html.H3("Precio interno"), html.P(fmt_num(price_mean, 0))]

    prod_ts = (
        df.groupby("fecha_mes", as_index=False)["produccion_mensual_proxy_t"].mean()
        .sort_values("fecha_mes")
    )
    fig_prod = px.line(
        prod_ts, x="fecha_mes", y="produccion_mensual_proxy_t",
        markers=True, title="Producción mensual proxy"
    )
    fig_prod = apply_figure_style(fig_prod, "Producción mensual proxy")

    clima_ts = (
        df.groupby("fecha_mes", as_index=False)[["PRECTOTCORR", "T2M_mean"]].mean()
        .sort_values("fecha_mes")
    )
    fig_clima = px.line(
        clima_ts, x="fecha_mes", y=["PRECTOTCORR", "T2M_mean"],
        title="Clima mensual: precipitación y temperatura"
    )
    fig_clima.update_layout(template="plotly_white", legend_title_text="Variable")

    by_dept = (
        filter_df(MONTHLY, "TODOS", year_value)
        .groupby("departamento", as_index=False)["produccion_mensual_proxy_t"]
        .mean()
        .sort_values("produccion_mensual_proxy_t", ascending=False)
    )
    fig_bar = px.bar(
        by_dept, x="departamento", y="produccion_mensual_proxy_t",
        title="Producción proxy promedio por departamento"
    )
    fig_bar.update_layout(template="plotly_white")

    dfw["alerta_climatica"] = (
        dfw["dummy_exceso_lluvia_p75"].fillna(0).astype(int)
        + dfw["dummy_estres_hidrico_p25"].fillna(0).astype(int)
        + dfw["dummy_temp_max_alta_p75"].fillna(0).astype(int)
    )
    weekly_alert = (
        dfw.groupby("fecha_semana_inicio", as_index=False)["alerta_climatica"].mean()
        .sort_values("fecha_semana_inicio")
    )
    fig_weekly = px.line(
        weekly_alert, x="fecha_semana_inicio", y="alerta_climatica",
        markers=True, title="Señal semanal de alertas climáticas"
    )
    fig_weekly.update_layout(template="plotly_white")

    return prod_kpi, rend_kpi, rain_kpi, price_kpi, fig_prod, fig_clima, fig_bar, fig_weekly