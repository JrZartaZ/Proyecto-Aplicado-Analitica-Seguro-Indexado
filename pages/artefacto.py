from dash import html, dcc, callback, Input, Output, register_page
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.dashboard_utils import load_csv, get_department_options, get_year_options, filter_df, fmt_num, apply_figure_style
from src.simulation_utils import (
    load_simulation_base,
    load_scenario_bounds,
    simulate_hybrid_monthly_scenario,
)

register_page(__name__, path="/artefacto", name="Artefacto")

# =========================
# Carga de datos
# =========================
MONTHLY = load_csv("monthly_app.csv")
MONTHLY["fecha_mes"] = pd.to_datetime(MONTHLY["fecha_mes"], errors="coerce")

WEEKLY = load_csv("weekly_app.csv")
WEEKLY["fecha_semana_inicio"] = pd.to_datetime(WEEKLY["fecha_semana_inicio"], errors="coerce")
WEEKLY["fecha_semana_fin"] = pd.to_datetime(WEEKLY["fecha_semana_fin"], errors="coerce")

SIM_BASE = load_simulation_base()
SCENARIO_BOUNDS = load_scenario_bounds()

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


def style_figure(fig, title=None, height=370):
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


def add_risk_signal(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Construcción operativa simple de señal de riesgo mensual
    comp_exceso = out["dummy_exceso_lluvia_p75_any"].fillna(0) * 35 if "dummy_exceso_lluvia_p75_any" in out.columns else 0
    comp_estres = out["dummy_estres_hidrico_p25_any"].fillna(0) * 35 if "dummy_estres_hidrico_p25_any" in out.columns else 0
    comp_temp = out["dummy_temp_max_alta_p75_any"].fillna(0) * 20 if "dummy_temp_max_alta_p75_any" in out.columns else 0

    if "anomalia_lluvia_semana_iso_mean" in out.columns:
        comp_anom = np.clip(out["anomalia_lluvia_semana_iso_mean"].fillna(0).abs(), 0, 2) / 2 * 10
    else:
        comp_anom = 0

    out["senal_riesgo"] = np.clip(comp_exceso + comp_estres + comp_temp + comp_anom, 0, 100)

    out["mes_con_alerta"] = (
        out["dummy_exceso_lluvia_p75_any"].fillna(0).astype(int)
        + out["dummy_estres_hidrico_p25_any"].fillna(0).astype(int)
        + out["dummy_temp_max_alta_p75_any"].fillna(0).astype(int)
    )
    out["mes_con_alerta"] = (out["mes_con_alerta"] > 0).astype(int)

    return out


def add_weekly_alerts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["alerta_climatica"] = (
        out["dummy_exceso_lluvia_p75"].fillna(0).astype(int)
        + out["dummy_estres_hidrico_p25"].fillna(0).astype(int)
        + out["dummy_temp_max_alta_p75"].fillna(0).astype(int)
    )
    return out


def risk_label(score: float) -> str:
    if pd.isna(score):
        return "Sin lectura"
    if score < 20:
        return "Bajo"
    if score < 40:
        return "Moderado"
    if score < 60:
        return "Alto"
    return "Crítico"


def action_label(score: float) -> str:
    if pd.isna(score):
        return "Revisar datos disponibles"
    if score < 20:
        return "Monitoreo rutinario"
    if score < 40:
        return "Seguimiento preventivo"
    if score < 60:
        return "Revisión técnica prioritaria"
    return "Monitoreo intensivo y revisión inmediata"


def kpi_block(title, value, subtitle=None):
    children = [
        html.H3(title),
        html.P(value)
    ]
    if subtitle:
        children.append(html.Small(subtitle, style={"color": "#5f6c67"}))
    return children

def cop_fmt(x):
    if pd.isna(x):
        return "NA"
    return "$ " + f"{x:,.0f}".replace(",", ".")


def slider_cfg(var_name, fallback_min=0.0, fallback_max=1.0, fallback_default=0.5, fallback_step=0.01):
    cfg = SCENARIO_BOUNDS.get(var_name, {})
    return {
        "min": cfg.get("min", fallback_min),
        "max": cfg.get("max", fallback_max),
        "default": cfg.get("default", fallback_default),
        "step": cfg.get("step", fallback_step),
    }


def sim_card(title, value, subtitle=None):
    children = [html.H3(title), html.P(value)]
    if subtitle:
        children.append(html.Small(subtitle, style={"color": "#5f6c67"}))
    return children

layout = html.Div(
    className="page-content",
    children=[
        html.H2("Monitoreo y soporte técnico del seguro indexado", className="page-title"),
        html.P(
            "Lectura operativa de riesgo por departamento, usando la capa monthly como soporte principal y weekly como monitoreo fino.",
            className="page-intro",
        ),
        html.Div(
            className="note-card",
            children=[
                html.H4("Alcance del simulador técnico"),
                html.P(
                    "El artefacto no calcula una prima actuarial definitiva, pero sí permite simular escenarios "
                    "climáticos y económicos, estimar su impacto proxy sobre la producción mensual y traducir dicho "
                    "impacto en una cobertura indicativa y una prima de referencia para fines de monitoreo y soporte técnico."
                ),
            ],
        ),
        html.Div(
            className="table-wrap",
            children=[
                html.H3("Simulador técnico de escenario"),
                html.P(
                    "Usa una fila base mensual real y ajusta variables climáticas y económicas dentro de rangos controlados. "
                    "La producción base se apoya en M6 y la sensibilidad climática en M5."
                ),

                html.Div(
                    className="filter-row",
                    children=[
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Mes base"),
                                dcc.Dropdown(
                                    id="sim-month",
                                    options=[{"label": str(m), "value": m} for m in range(1, 13)],
                                    value=6,
                                    clearable=False,
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Hectáreas aseguradas"),
                                dcc.Slider(
                                    id="sim-hectareas",
                                    min=0,
                                    max=10000,
                                    step=1,
                                    value=1000,
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Cobertura (%)"),
                                dcc.Slider(
                                    id="sim-cobertura",
                                    min=0.50,
                                    max=0.90,
                                    step=0.05,
                                    value=0.70,
                                    marks={0.5: "50%", 0.7: "70%", 0.9: "90%"},
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Tasa prima (%)"),
                                dcc.Slider(
                                    id="sim-prima",
                                    min=0.03,
                                    max=0.12,
                                    step=0.01,
                                    value=0.06,
                                    marks={0.03: "3%", 0.06: "6%", 0.12: "12%"},
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                    ],
                ),

                html.Div(
                    className="filter-row",
                    children=[
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Índice climático ajustado"),
                                dcc.Slider(
                                    id="sim-indice",
                                    min=slider_cfg("indice_climatico_ajustado_x_mean", 0, 2, 1, 0.05)["min"],
                                    max=slider_cfg("indice_climatico_ajustado_x_mean", 0, 2, 1, 0.05)["max"],
                                    step=slider_cfg("indice_climatico_ajustado_x_mean", 0, 2, 1, 0.05)["step"],
                                    value=slider_cfg("indice_climatico_ajustado_x_mean", 0, 2, 1, 0.05)["default"],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Precipitación"),
                                dcc.Slider(
                                    id="sim-rain",
                                    min=slider_cfg("PRECTOTCORR", 0, 100, 20, 0.1)["min"],
                                    max=slider_cfg("PRECTOTCORR", 0, 100, 20, 0.1)["max"],
                                    step=slider_cfg("PRECTOTCORR", 0, 100, 20, 0.1)["step"],
                                    value=slider_cfg("PRECTOTCORR", 0, 100, 20, 0.1)["default"],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Temperatura media"),
                                dcc.Slider(
                                    id="sim-temp",
                                    min=slider_cfg("T2M_mean", 0, 40, 20, 0.1)["min"],
                                    max=slider_cfg("T2M_mean", 0, 40, 20, 0.1)["max"],
                                    step=slider_cfg("T2M_mean", 0, 40, 20, 0.1)["step"],
                                    value=slider_cfg("T2M_mean", 0, 40, 20, 0.1)["default"],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Humedad del suelo"),
                                dcc.Slider(
                                    id="sim-gwet",
                                    min=slider_cfg("GWETROOT_mean", 0, 1, 0.5, 0.01)["min"],
                                    max=slider_cfg("GWETROOT_mean", 0, 1, 0.5, 0.01)["max"],
                                    step=slider_cfg("GWETROOT_mean", 0, 1, 0.5, 0.01)["step"],
                                    value=slider_cfg("GWETROOT_mean", 0, 1, 0.5, 0.01)["default"],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("Precio interno"),
                                dcc.Slider(
                                    id="sim-price",
                                    min=slider_cfg("precio_interno_cop_carga_mean", 100000, 3000000, 1800000, 1000)["min"],
                                    max=slider_cfg("precio_interno_cop_carga_mean", 100000, 3000000, 1800000, 1000)["max"],
                                    step=slider_cfg("precio_interno_cop_carga_mean", 100000, 3000000, 1800000, 1000)["step"],
                                    value=slider_cfg("precio_interno_cop_carga_mean", 100000, 3000000, 1800000, 1000)["default"],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                        html.Div(
                            className="filter-card",
                            children=[
                                html.Label("TRM"),
                                dcc.Slider(
                                    id="sim-trm",
                                    min=slider_cfg("trm_promedio_semana_cop_usd_mean", 3000, 6000, 4000, 1)["min"],
                                    max=slider_cfg("trm_promedio_semana_cop_usd_mean", 3000, 6000, 4000, 1)["max"],
                                    step=slider_cfg("trm_promedio_semana_cop_usd_mean", 3000, 6000, 4000, 1)["step"],
                                    value=slider_cfg("trm_promedio_semana_cop_usd_mean", 3000, 6000, 4000, 1)["default"],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                ),
                            ],
                        ),
                    ],
                ),

                html.Div(
                    className="kpi-row",
                    children=[
                        html.Div(className="kpi-card", id="sim-kpi-1"),
                        html.Div(className="kpi-card", id="sim-kpi-2"),
                        html.Div(className="kpi-card", id="sim-kpi-3"),
                        html.Div(className="kpi-card", id="sim-kpi-4"),
                        html.Div(className="kpi-card", id="sim-kpi-5"),
                        html.Div(className="kpi-card", id="sim-kpi-6"),
                    ],
                ),

                html.Div(className="note-card", id="sim-note"),
            ],
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
                dcc.Graph(id="risk-ranking-chart", className="chart-card"),
                dcc.Graph(id="risk-series-chart", className="chart-card"),
                dcc.Graph(id="risk-components-chart", className="chart-card"),
                dcc.Graph(id="risk-weekly-chart", className="chart-card"),
            ],
        ),

        html.Div(
            className="chart-grid",
            children=[
                html.Div(className="note-card", id="risk-reading-card"),
                html.Div(className="note-card", id="risk-action-card"),
            ],
        ),
    ],
)

@callback(
    Output("risk-kpi-1", "children"),
    Output("risk-kpi-2", "children"),
    Output("risk-kpi-3", "children"),
    Output("risk-kpi-4", "children"),
    Output("risk-ranking-chart", "figure"),
    Output("risk-series-chart", "figure"),
    Output("risk-components-chart", "figure"),
    Output("risk-weekly-chart", "figure"),
    Output("risk-reading-card", "children"),
    Output("risk-action-card", "children"),
    Input("risk-dept", "value"),
    Input("risk-year", "value"),
)
def update_artefacto(dept_value, year_value):
    dfm = filter_df(MONTHLY, dept_value, year_value).copy()
    dfm = add_risk_signal(dfm)

    dfw = filter_df(WEEKLY, dept_value, year_value).copy()
    dfw = add_weekly_alerts(dfw)

    risk_mean = dfm["senal_riesgo"].mean()
    alert_rate = dfm["mes_con_alerta"].mean() * 100
    idx_mean = dfm["indice_climatico_ajustado_x_mean"].mean()
    prod_mean = dfm["produccion_mensual_proxy_t"].mean()

    kpi_1 = kpi_block("Señal promedio de riesgo", fmt_num(risk_mean, 1), f"Nivel: {risk_label(risk_mean)}")
    kpi_2 = kpi_block("% de meses con alerta", fmt_num(alert_rate, 1) + "%", "Activación mensual de alertas")
    kpi_3 = kpi_block("Índice climático ajustado", fmt_num(idx_mean, 2), "Promedio del período")
    kpi_4 = kpi_block("Producción mensual proxy", fmt_num(prod_mean, 1), "Promedio del período")

    risk_rank = add_risk_signal(filter_df(MONTHLY, "TODOS", year_value).copy())
    risk_rank = (
        risk_rank.groupby("departamento", as_index=False)[["senal_riesgo", "produccion_mensual_proxy_t"]]
        .mean()
        .sort_values("senal_riesgo", ascending=False)
    )

    fig_rank = px.bar(
        risk_rank,
        x="departamento",
        y="senal_riesgo",
        color="produccion_mensual_proxy_t",
        color_continuous_scale=["#dcebe5", "#7ca694", "#1d5243"],
        title="Ranking departamental por señal de riesgo"
    )
    fig_rank.update_xaxes(title_text="Departamento")
    fig_rank.update_yaxes(title_text="Señal de riesgo")
    fig_rank = style_figure(fig_rank, "Ranking departamental por señal de riesgo")
    fig_rank.update_layout(coloraxis_colorbar_title="Producción")

    risk_ts = (
        dfm.groupby("fecha_mes", as_index=False)[["senal_riesgo", "produccion_mensual_proxy_t"]]
        .mean()
        .sort_values("fecha_mes")
    )

    fig_series = make_subplots(specs=[[{"secondary_y": True}]])
    fig_series.add_trace(
        go.Scatter(
            x=risk_ts["fecha_mes"],
            y=risk_ts["senal_riesgo"],
            mode="lines+markers",
            name="Señal de riesgo",
            line=dict(color=COLOR_RED, width=3),
            marker=dict(color=COLOR_RED, size=6),
        ),
        secondary_y=False,
    )
    fig_series.add_trace(
        go.Scatter(
            x=risk_ts["fecha_mes"],
            y=risk_ts["produccion_mensual_proxy_t"],
            mode="lines",
            name="Producción proxy",
            line=dict(color=COLOR_GREEN, width=3, dash="dot"),
        ),
        secondary_y=True,
    )
    fig_series.update_yaxes(title_text="Señal de riesgo", secondary_y=False)
    fig_series.update_yaxes(title_text="Producción mensual proxy (t)", secondary_y=True)
    fig_series.update_xaxes(title_text="Fecha")
    fig_series = style_figure(fig_series, "Señal de riesgo vs producción mensual")

    comp = pd.DataFrame({
        "componente": ["Exceso de lluvia", "Estrés hídrico", "Temperatura alta"],
        "valor": [
            dfm["dummy_exceso_lluvia_p75_any"].mean() * 100 if "dummy_exceso_lluvia_p75_any" in dfm.columns else 0,
            dfm["dummy_estres_hidrico_p25_any"].mean() * 100 if "dummy_estres_hidrico_p25_any" in dfm.columns else 0,
            dfm["dummy_temp_max_alta_p75_any"].mean() * 100 if "dummy_temp_max_alta_p75_any" in dfm.columns else 0,
        ]
    })

    fig_comp = px.bar(
        comp,
        x="componente",
        y="valor",
        color="componente",
        color_discrete_map={
            "Exceso de lluvia": COLOR_BLUE,
            "Estrés hídrico": COLOR_GOLD,
            "Temperatura alta": COLOR_RED
        },
        title="Composición de alertas climáticas"
    )
    fig_comp.update_xaxes(title_text="Componente")
    fig_comp.update_yaxes(title_text="% de meses con señal")
    fig_comp = style_figure(fig_comp, "Composición de alertas climáticas")
    fig_comp.update_layout(showlegend=False)

    weekly_alert = (
        dfw.groupby("fecha_semana_inicio", as_index=False)["alerta_climatica"]
        .mean()
        .sort_values("fecha_semana_inicio")
    )

    fig_week = go.Figure()
    fig_week.add_trace(
        go.Scatter(
            x=weekly_alert["fecha_semana_inicio"],
            y=weekly_alert["alerta_climatica"],
            mode="lines+markers",
            name="Alertas weekly",
            line=dict(color=COLOR_BROWN, width=3),
            marker=dict(color=COLOR_BROWN, size=6),
            fill="tozeroy",
            fillcolor="rgba(138, 106, 74, 0.12)"
        )
    )
    fig_week.update_xaxes(title_text="Semana")
    fig_week.update_yaxes(title_text="Señal semanal")
    fig_week = style_figure(fig_week, "Monitoreo semanal de alertas")

    label = risk_label(risk_mean)
    action = action_label(risk_mean)

    reading_card = html.Div(
        [
            html.H4("Lectura técnica del período"),
            html.P(
                f"La señal promedio de riesgo se ubica en nivel {label.lower()}, con "
                f"{fmt_num(alert_rate, 1)}% de meses con al menos una alerta climática. "
                f"El índice climático ajustado promedio fue {fmt_num(idx_mean, 2)} y la producción mensual proxy promedio "
                f"fue {fmt_num(prod_mean, 1)} toneladas."
            ),
            html.P(
                "Esta lectura sintetiza la capa monthly como soporte principal del artefacto y usa weekly como monitoreo fino de alertas."
            ),
        ]
    )

    action_card = html.Div(
        [
            html.H4("Acción sugerida"),
            html.P(f"Recomendación actual: {action}."),
            html.Ul(
                [
                    html.Li("Usar esta señal para comparación territorial y priorización de seguimiento."),
                    html.Li("No interpretar esta salida como cálculo actuarial definitivo del seguro."),
                    html.Li("Complementar la revisión con la página de modelos para entender supuestos y limitaciones."),
                ]
            ),
        ]
    )

    return (
        kpi_1,
        kpi_2,
        kpi_3,
        kpi_4,
        fig_rank,
        fig_series,
        fig_comp,
        fig_week,
        reading_card,
        action_card,
    )


@callback(
    Output("sim-kpi-1", "children"),
    Output("sim-kpi-2", "children"),
    Output("sim-kpi-3", "children"),
    Output("sim-kpi-4", "children"),
    Output("sim-kpi-5", "children"),
    Output("sim-kpi-6", "children"),
    Output("sim-note", "children"),
    Input("risk-dept", "value"),
    Input("risk-year", "value"),
    Input("sim-month", "value"),
    Input("sim-hectareas", "value"),
    Input("sim-cobertura", "value"),
    Input("sim-prima", "value"),
    Input("sim-indice", "value"),
    Input("sim-rain", "value"),
    Input("sim-temp", "value"),
    Input("sim-gwet", "value"),
    Input("sim-price", "value"),
    Input("sim-trm", "value"),
)
def update_simulator(
    dept_value, year_value, month_value,
    hectareas_value, cobertura_value, prima_value,
    indice_value, rain_value, temp_value, gwet_value, price_value, trm_value
):
    if dept_value == "TODOS" or year_value == "TODOS":
        empty = sim_card("Simulador", "Selecciona departamento y año", "La simulación requiere una fila base específica")
        return empty, empty, empty, empty, empty, empty, html.Div(
            [
                html.H4("Simulación no disponible"),
                html.P("Para activar el simulador técnico, selecciona un departamento y un año específicos.")
            ]
        )

    try:
        sample = SIM_BASE[
            (SIM_BASE["departamento"] == dept_value) &
            (SIM_BASE["anio_referencia_y"] == year_value) &
            (SIM_BASE["mes_referencia_y"] == month_value)
        ].head(1).copy()

        if sample.empty:
            raise ValueError("No se encontró fila base para esa combinación.")

        resultado = simulate_hybrid_monthly_scenario(
            base_row=sample,
            overrides={
                "indice_climatico_ajustado_x_mean": indice_value,
                "PRECTOTCORR": rain_value,
                "T2M_mean": temp_value,
                "GWETROOT_mean": gwet_value,
                "precio_interno_cop_carga_mean": price_value,
                "trm_promedio_semana_cop_usd_mean": trm_value,
            },
            hectareas_aseguradas=hectareas_value,
            cobertura_pct=cobertura_value,
            tasa_prima_pct=prima_value,
        )

        k1 = sim_card("Producción base operativa", fmt_num(resultado["hybrid_base_prediction"], 2), "Base M6")
        k2 = sim_card("Producción simulada", fmt_num(resultado["hybrid_scenario_prediction"], 2), "Base M6 + deterioro adverso M5")
        k3 = sim_card("Pérdida proxy", fmt_num(resultado["perdida_proxy_t"], 2) + " t", f"{fmt_num(resultado['perdida_proxy_pct'] * 100, 2)}%")
        k4 = sim_card("Valor expuesto proxy", cop_fmt(resultado["valor_expuesto_proxy_cop"]), "Diferencia base vs escenario")
        k5 = sim_card("Cobertura indicativa", cop_fmt(resultado["cobertura_indicativa_cop"]), f"Cobertura {int(cobertura_value*100)}%")
        k6 = sim_card("Prima indicativa", cop_fmt(resultado["prima_indicativa_cop"]), f"Tasa {fmt_num(prima_value*100, 1)}%")

        note = html.Div(
            [
                html.H4("Lectura del simulador"),
                html.P(
                    f"Para {dept_value.title()}, {year_value}-{str(month_value).zfill(2)}, el escenario simulado genera una "
                    f"producción ajustada de {fmt_num(resultado['hybrid_scenario_prediction'], 2)} frente a una base operativa "
                    f"de {fmt_num(resultado['hybrid_base_prediction'], 2)}. Esto implica una pérdida proxy de "
                    f"{fmt_num(resultado['perdida_proxy_t'], 2)} toneladas y un valor expuesto aproximado de "
                    f"{cop_fmt(resultado['valor_expuesto_proxy_cop'])}."
                ),
                html.P(
                    "La base productiva se apoya en M6 y la sensibilidad climática en M5. "
                    "Esta salida es una referencia técnica de simulación, no una cotización actuarial definitiva."
                ),
            ]
        )

        return k1, k2, k3, k4, k5, k6, note

    except Exception as e:
        empty = sim_card("Simulador", "Error en simulación", "Revisa la combinación seleccionada")
        note = html.Div(
            [
                html.H4("No fue posible simular"),
                html.P(str(e))
            ]
        )
        return empty, empty, empty, empty, empty, empty, note