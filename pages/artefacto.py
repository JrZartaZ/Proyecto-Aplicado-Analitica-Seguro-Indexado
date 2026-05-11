import numpy as np
import pandas as pd
import plotly.express as px
from dash import html, dcc, callback, Input, Output, register_page
from src.dashboard_utils import load_csv, get_department_options, get_year_options, filter_df, fmt_num, apply_figure_style
register_page(__name__, path="/artefacto", name="Artefacto")


MONTHLY = load_csv("monthly_app.csv")
MONTHLY["fecha_mes"] = pd.to_datetime(MONTHLY["fecha_mes"], errors="coerce")
WEEKLY = load_csv("weekly_app.csv")
WEEKLY["fecha_semana_inicio"] = pd.to_datetime(WEEKLY["fecha_semana_inicio"], errors="coerce")

def add_risk_signal(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    components = []
    if "dummy_exceso_lluvia_p75_any" in out.columns:
        components.append(out["dummy_exceso_lluvia_p75_any"].fillna(0) * 35)
    if "dummy_estres_hidrico_p25_any" in out.columns:
        components.append(out["dummy_estres_hidrico_p25_any"].fillna(0) * 35)
    if "dummy_temp_max_alta_p75_any" in out.columns:
        components.append(out["dummy_temp_max_alta_p75_any"].fillna(0) * 20)
    if "anomalia_lluvia_semana_iso_mean" in out.columns:
        z = out["anomalia_lluvia_semana_iso_mean"].fillna(0).abs()
        z = np.clip(z, 0, 2) / 2 * 10
        components.append(z)
    if not components:
        out["senal_riesgo"] = 0
    else:
        total = components[0]
        for comp in components[1:]:
            total = total + comp
        out["senal_riesgo"] = np.clip(total, 0, 100)
    return out

layout = html.Div(
    className="page-content",
    children=[
        html.H2("Herramienta analítica del seguro indexado", className="page-title"),
        html.P(
            "Lectura operativa de riesgo por departamento, usando monthly como capa principal y weekly como apoyo de monitoreo.",
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
                            id="risk-dept",
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
                            id="risk-year",
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
                html.Div(className="kpi-card", id="risk-kpi-1"),
                html.Div(className="kpi-card", id="risk-kpi-2"),
                html.Div(className="kpi-card", id="risk-kpi-3"),
                html.Div(className="kpi-card", id="risk-kpi-4"),
            ],
        ),
        html.Div(
            className="chart-grid",
            children=[
                dcc.Graph(id="risk-map-bar", className="chart-card"),
                dcc.Graph(id="risk-series", className="chart-card"),
                dcc.Graph(id="risk-clima", className="chart-card"),
                dcc.Graph(id="risk-weekly-alert", className="chart-card"),
            ],
        ),
        html.Div(
            className="note-card",
            id="risk-note",
        ),
    ],
)

@callback(
    Output("risk-kpi-1", "children"),
    Output("risk-kpi-2", "children"),
    Output("risk-kpi-3", "children"),
    Output("risk-kpi-4", "children"),
    Output("risk-map-bar", "figure"),
    Output("risk-series", "figure"),
    Output("risk-clima", "figure"),
    Output("risk-weekly-alert", "figure"),
    Output("risk-note", "children"),
    Input("risk-dept", "value"),
    Input("risk-year", "value"),
)
def update_page(dept_value, year_value):
    df = filter_df(MONTHLY, dept_value, year_value)
    df = add_risk_signal(df)

    dfw = filter_df(WEEKLY, dept_value, year_value).copy()
    dfw["alerta_climatica"] = (
        dfw["dummy_exceso_lluvia_p75"].fillna(0).astype(int)
        + dfw["dummy_estres_hidrico_p25"].fillna(0).astype(int)
        + dfw["dummy_temp_max_alta_p75"].fillna(0).astype(int)
    )

    k1 = [html.H3("Señal promedio de riesgo"), html.P(fmt_num(df["senal_riesgo"].mean(), 1))]
    k2 = [html.H3("Producción mensual proxy"), html.P(fmt_num(df["produccion_mensual_proxy_t"].mean(), 1))]
    k3 = [html.H3("Rendimiento"), html.P(fmt_num(df["rendimiento_departamental_t_ha"].mean(), 2))]
    k4 = [html.H3("TRM promedio"), html.P(fmt_num(df["trm_promedio_semana_cop_usd_mean"].mean(), 0))]

    dept_risk = (
        add_risk_signal(filter_df(MONTHLY, "TODOS", year_value))
        .groupby("departamento", as_index=False)["senal_riesgo"]
        .mean()
        .sort_values("senal_riesgo", ascending=False)
    )
    fig_bar = px.bar(dept_risk, x="departamento", y="senal_riesgo", title="Señal de riesgo promedio por departamento")
    fig_bar.update_layout(template="plotly_white")

    series = df.groupby("fecha_mes", as_index=False)[["senal_riesgo", "produccion_mensual_proxy_t"]].mean()
    fig_series = px.line(series, x="fecha_mes", y=["senal_riesgo", "produccion_mensual_proxy_t"], title="Riesgo y producción mensual")
    fig_series.update_layout(template="plotly_white", legend_title_text="Serie")

    clima = df.groupby("fecha_mes", as_index=False)[["PRECTOTCORR", "T2M_mean", "RH2M_mean"]].mean()
    fig_clima = px.line(clima, x="fecha_mes", y=["PRECTOTCORR", "T2M_mean", "RH2M_mean"], title="Señales climáticas mensuales")
    fig_clima.update_layout(template="plotly_white", legend_title_text="Variable")

    weekly_alert = dfw.groupby("fecha_semana_inicio", as_index=False)["alerta_climatica"].mean()
    fig_week = px.line(weekly_alert, x="fecha_semana_inicio", y="alerta_climatica", markers=True, title="Monitoreo semanal de alertas")
    fig_week.update_layout(template="plotly_white")

    note = html.Div(
        [
            html.H4("Lectura técnica"),
            html.P(
                "Esta señal de riesgo es un índice operativo de monitoreo construido con dummies climáticas y anomalías agregadas. "
                "Sirve para apoyar comparación territorial, seguimiento y revisión técnica del seguro, pero no reemplaza una estimación actuarial completa."
            ),
        ]
    )

    return k1, k2, k3, k4, fig_bar, fig_series, fig_clima, fig_week, note