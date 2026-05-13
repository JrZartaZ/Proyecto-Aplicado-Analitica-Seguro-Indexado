
from dash import html, dcc, callback, Input, Output, dash_table, register_page
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard_utils import load_csv, fmt_num, apply_figure_style

register_page(__name__, path="/modelos", name="Modelos")

# =========================
# Carga de datos
# =========================
RESULTS = load_csv("model_results.csv")
TRACE = load_csv("model_traceability.csv")

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

COLOR_FREQ = {
    "weekly": COLOR_BLUE,
    "monthly": COLOR_GREEN_2,
    "annual": COLOR_BROWN
}


def style_figure(fig, title=None, height=390):
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


def add_interpretation_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    family_adv = {
        "ridge": "Interpretable y estable",
        "random_forest": "Capta no linealidad",
        "xgboost": "Alta flexibilidad",
        "dummy": "Benchmark mínimo"
    }

    family_lim = {
        "ridge": "Menor flexibilidad no lineal",
        "random_forest": "Menor interpretabilidad",
        "xgboost": "Más complejo y menos trazable",
        "dummy": "No útil para operación"
    }

    out["ventaja_modelo"] = out["familia_modelo"].map(family_adv).fillna("No especificada")
    out["limitacion_modelo"] = out["familia_modelo"].map(family_lim).fillna("No especificada")

    # Ajustes específicos por modelo
    out.loc[out["modelo"] == "V7_clima_mas_economicas_rf", "limitacion_modelo"] = "Alta influencia territorial"
    out.loc[out["modelo"] == "M6_clima_econ_struct_rf", "limitacion_modelo"] = "Dominancia estructural"
    out.loc[out["modelo"] == "M5_clima_econ_rf", "ventaja_modelo"] = "Más alineado con lógica climática"
    out.loc[out["modelo"] == "A1_baseline_ridge", "ventaja_modelo"] = "Contraste parsimonioso y defendible"

    return out


def build_card(title, model_name, subtext):
    return [
        html.H3(title),
        html.H4(model_name, style={"margin": "8px 0 6px 0", "color": "#13352c", "fontSize": "22px"}),
        html.Small(subtext, style={"color": "#5f6c67", "fontSize": "14px"})
    ]


RESULTS = add_interpretation_columns(RESULTS)

layout = html.Div(
    className="page-content",
    children=[
        html.H2("Modelos, métricas, supuestos y selección metodológica", className="page-title"),
        html.P(
            "Trazabilidad entre preguntas analíticas, modelos seleccionados, métricas, ventajas y limitaciones.",
            className="page-intro",
        ),

        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    className="filter-card",
                    children=[
                        html.Label("Frecuencia"),
                        dcc.Dropdown(
                            id="model-freq",
                            options=[
                                {"label": "Todas", "value": "TODAS"},
                                {"label": "Weekly", "value": "weekly"},
                                {"label": "Monthly", "value": "monthly"},
                                {"label": "Annual", "value": "annual"},
                            ],
                            value="TODAS",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-card",
                    children=[
                        html.Label("Familia de modelo"),
                        dcc.Dropdown(
                            id="model-family",
                            options=[
                                {"label": "Todas", "value": "TODAS"},
                                {"label": "Ridge", "value": "ridge"},
                                {"label": "Random Forest", "value": "random_forest"},
                                {"label": "XGBoost", "value": "xgboost"},
                                {"label": "Dummy", "value": "dummy"},
                            ],
                            value="TODAS",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-card",
                    children=[
                        html.Label("Target"),
                        dcc.Dropdown(
                            id="model-target",
                            options=[{"label": "Todos", "value": "TODOS"}] + [
                                {"label": t, "value": t}
                                for t in sorted(RESULTS["target"].dropna().unique().tolist())
                            ],
                            value="TODOS",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-card",
                    children=[
                        html.Label("Métrica principal"),
                        dcc.Dropdown(
                            id="metric-view",
                            options=[
                                {"label": "test_R2", "value": "test_R2"},
                                {"label": "test_RMSE", "value": "test_RMSE"},
                                {"label": "test_Corr", "value": "test_Corr"},
                                {"label": "val_RMSE", "value": "val_RMSE"},
                                {"label": "val_R2", "value": "val_R2"},
                            ],
                            value="test_R2",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    className="filter-card",
                    children=[
                        html.Label("Mostrar"),
                        dcc.RadioItems(
                            id="selected-only",
                            options=[
                                {"label": "Todos", "value": "todos"},
                                {"label": "Solo seleccionados", "value": "seleccionados"},
                            ],
                            value="todos",
                            inline=True,
                        ),
                    ],
                ),
            ],
        ),

        html.Div(
            className="kpi-row",
            children=[
                html.Div(className="kpi-card", id="card-weekly"),
                html.Div(className="kpi-card", id="card-monthly-op"),
                html.Div(className="kpi-card", id="card-monthly-ref"),
                html.Div(className="kpi-card", id="card-annual"),
            ],
        ),

        html.Div(
            className="chart-grid",
            children=[
                dcc.Graph(id="metric-chart", className="chart-card"),
                dcc.Graph(id="compare-chart", className="chart-card"),
            ],
        ),

        html.Div(
            className="table-wrap",
            children=[
                html.H3("Resumen de modelos"),
                dash_table.DataTable(
                    id="results-table",
                    page_size=12,
                    sort_action="native",
                    filter_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "8px",
                        "fontFamily": "Arial",
                        "fontSize": "13px",
                        "whiteSpace": "normal",
                        "height": "auto",
                    },
                    style_header={"fontWeight": "bold"},
                    style_data_conditional=[
                        {
                            "if": {"filter_query": "{seleccionado} = 1"},
                            "backgroundColor": "#eef6f2",
                            "borderLeft": "4px solid #1d5243",
                        }
                    ],
                ),
            ],
        ),

        html.Div(
            className="table-wrap",
            children=[
                html.H3("Trazabilidad metodológica"),
                dash_table.DataTable(
                    id="trace-table",
                    page_size=8,
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "8px",
                        "fontFamily": "Arial",
                        "fontSize": "13px",
                        "whiteSpace": "normal",
                        "height": "auto",
                    },
                    style_header={"fontWeight": "bold"},
                ),
            ],
        ),

        html.Div(
            className="note-card",
            children=[
                html.H4("Supuestos y limitaciones que deben quedar visibles"),
                html.Ul(
                    [
                        html.Li("Weekly usa una Y proxy y debe interpretarse como capa operativa, no como validación causal fuerte."),
                        html.Li("Monthly es la base principal del artefacto; M6 maximiza ajuste y M5 preserva mejor la lógica climática."),
                        html.Li("Annual opera con muestra pequeña y cumple un rol de contraste metodológico más que de capa operativa."),
                        html.Li("Random Forest y XGBoost capturan no linealidades, pero son menos interpretables que Ridge."),
                    ]
                ),
            ],
        ),
    ],
)


@callback(
    Output("card-weekly", "children"),
    Output("card-monthly-op", "children"),
    Output("card-monthly-ref", "children"),
    Output("card-annual", "children"),
    Output("metric-chart", "figure"),
    Output("compare-chart", "figure"),
    Output("results-table", "data"),
    Output("results-table", "columns"),
    Output("trace-table", "data"),
    Output("trace-table", "columns"),
    Input("model-freq", "value"),
    Input("model-family", "value"),
    Input("model-target", "value"),
    Input("metric-view", "value"),
    Input("selected-only", "value"),
)
def update_modelos(freq_value, family_value, target_value, metric_value, selected_value):
    df = RESULTS.copy()

    if freq_value != "TODAS":
        df = df[df["frecuencia"] == freq_value]

    if family_value != "TODAS":
        df = df[df["familia_modelo"] == family_value]

    if target_value != "TODOS":
        df = df[df["target"] == target_value]

    if selected_value == "seleccionados":
        df = df[df["seleccionado"] == 1]

    # =========================
    # Cards fijas de decisión metodológica
    # =========================
    weekly_row = RESULTS[RESULTS["rol_modelo"] == "capa operativa semanal"].iloc[0]
    monthly_op_row = RESULTS[RESULTS["rol_modelo"] == "capa operativa mensual"].iloc[0]
    monthly_ref_row = RESULTS[RESULTS["rol_modelo"] == "referencia climática mensual"].iloc[0]

    annual_rows = RESULTS[
        (RESULTS["frecuencia"] == "annual") &
        (RESULTS["modelo"] == "A1_baseline_ridge")
    ]
    annual_targets = ", ".join(sorted(annual_rows["target"].unique().tolist()))

    card_weekly = build_card(
        "Capa operativa semanal",
        weekly_row["modelo"],
        f"Seleccionado por test_R2={weekly_row['test_R2']:.3f} y test_Corr={weekly_row['test_Corr']:.3f}"
    )

    card_monthly_op = build_card(
        "Capa operativa mensual",
        monthly_op_row["modelo"],
        f"Mejor ajuste global | test_R2={monthly_op_row['test_R2']:.3f}"
    )

    card_monthly_ref = build_card(
        "Referencia climática mensual",
        monthly_ref_row["modelo"],
        f"Mejor lectura climática | test_Corr={monthly_ref_row['test_Corr']:.3f}"
    )

    card_annual = build_card(
        "Contraste metodológico anual",
        "A1_baseline_ridge",
        f"Aplica a: {annual_targets}"
    )

    # =========================
    # Gráfico 1: métrica principal elegida
    # =========================
    plot_df = df.copy().sort_values(metric_value, ascending=(metric_value in ["test_RMSE", "val_RMSE"]))
    fig_metric = px.bar(
        plot_df,
        x="modelo",
        y=metric_value,
        color="frecuencia",
        color_discrete_map=COLOR_FREQ,
        hover_data=["target", "rol_modelo", "ventaja_modelo", "limitacion_modelo"],
        title=f"Comparación de {metric_value} por modelo",
        barmode="group"
    )
    fig_metric.update_xaxes(tickangle=-35, title_text="Modelo")
    fig_metric.update_yaxes(title_text=metric_value)
    fig_metric = style_figure(fig_metric, f"Comparación de {metric_value} por modelo")

    # =========================
    # Gráfico 2: trade-off test_R2 vs test_RMSE
    # =========================
    scatter_df = df.copy()
    fig_compare = px.scatter(
        scatter_df,
        x="test_RMSE",
        y="test_R2",
        color="frecuencia",
        color_discrete_map=COLOR_FREQ,
        symbol="familia_modelo",
        hover_name="modelo",
        hover_data=["target", "test_Corr", "rol_modelo"],
        size="seleccionado",
        size_max=18,
        title="Trade-off entre error y capacidad explicativa"
    )
    fig_compare.update_xaxes(title_text="test_RMSE")
    fig_compare.update_yaxes(title_text="test_R2")
    fig_compare = style_figure(fig_compare, "Trade-off entre error y capacidad explicativa")

    # =========================
    # Tabla de resultados
    # =========================
    table_df = df.copy()
    numeric_cols = [
        "val_RMSE", "val_MAE", "val_MAPE_pct", "val_R2", "val_Corr",
        "test_RMSE", "test_MAE", "test_MAPE_pct", "test_R2", "test_Corr"
    ]
    for c in numeric_cols:
        if c in table_df.columns:
            table_df[c] = table_df[c].round(3)

    cols_show = [
        "frecuencia", "modelo", "familia_modelo", "target",
        "val_RMSE", "val_R2", "test_RMSE", "test_R2", "test_Corr",
        "seleccionado", "rol_modelo", "ventaja_modelo", "limitacion_modelo"
    ]
    cols_show = [c for c in cols_show if c in table_df.columns]

    # =========================
    # Tabla de trazabilidad
    # =========================
    trace_df = TRACE.copy()
    if freq_value != "TODAS":
        trace_df = trace_df[trace_df["frecuencia"].str.contains(freq_value, case=False, na=False)]

    return (
        card_weekly,
        card_monthly_op,
        card_monthly_ref,
        card_annual,
        fig_metric,
        fig_compare,
        table_df[cols_show].to_dict("records"),
        [{"name": c, "id": c} for c in cols_show],
        trace_df.to_dict("records"),
        [{"name": c, "id": c} for c in trace_df.columns],
    )