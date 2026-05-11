import plotly.express as px
from dash import html, dcc, callback, Input, Output, dash_table, register_page
from src.dashboard_utils import load_csv, fmt_num, apply_figure_style

register_page(__name__, path="/modelos", name="Modelos")


RESULTS = load_csv("model_results.csv")
TRACE = load_csv("model_traceability.csv")

layout = html.Div(
    className="page-content",
    children=[
        html.H2("Modelos, métricas, supuestos y selección metodológica", className="page-title"),
        html.P(
            "Trazabilidad entre preguntas analíticas, modelos seleccionados, métricas y limitaciones.",
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
            ],
        ),
        html.Div(
            className="kpi-row",
            children=[
                html.Div(className="kpi-card", id="sel-weekly"),
                html.Div(className="kpi-card", id="sel-monthly"),
                html.Div(className="kpi-card", id="sel-annual"),
            ],
        ),
        html.Div(
            className="chart-grid",
            children=[
                dcc.Graph(id="metric-chart", className="chart-card"),
                dcc.Graph(id="selected-chart", className="chart-card"),
            ],
        ),
        html.Div(
            className="table-wrap",
            children=[
                html.H3("Resumen de modelos"),
                dash_table.DataTable(
                    id="results-table",
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontFamily": "Arial"},
                    style_header={"fontWeight": "bold"},
                ),
            ],
        ),
        html.Div(
            className="table-wrap",
            children=[
                html.H3("Trazabilidad metodológica"),
                dash_table.DataTable(
                    data=TRACE.to_dict("records"),
                    columns=[{"name": c, "id": c} for c in TRACE.columns],
                    page_size=8,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "8px", "fontFamily": "Arial"},
                    style_header={"fontWeight": "bold"},
                ),
            ],
        ),
    ],
)

@callback(
    Output("sel-weekly", "children"),
    Output("sel-monthly", "children"),
    Output("sel-annual", "children"),
    Output("metric-chart", "figure"),
    Output("selected-chart", "figure"),
    Output("results-table", "data"),
    Output("results-table", "columns"),
    Input("model-freq", "value"),
)
def update_page(freq_value):
    df = RESULTS.copy()
    if freq_value != "TODAS":
        df = df[df["frecuencia"] == freq_value]

    wk = RESULTS[(RESULTS["frecuencia"] == "weekly") & (RESULTS["seleccionado"] == 1)]
    mo = RESULTS[(RESULTS["frecuencia"] == "monthly") & (RESULTS["seleccionado"] == 1)]
    an = RESULTS[(RESULTS["frecuencia"] == "annual") & (RESULTS["seleccionado"] == 1)]

    wk_card = [html.H3("Weekly"), html.P(", ".join(wk["modelo"].tolist()))]
    mo_card = [html.H3("Monthly"), html.P(", ".join(mo["modelo"].tolist()))]
    an_card = [html.H3("Annual"), html.P(", ".join(an["modelo"].tolist()))]

    fig_metric = px.bar(
        df,
        x="modelo",
        y="test_R2",
        color="frecuencia",
        title="Comparación de test_R2 por modelo",
        barmode="group"
    )
    fig_metric.update_layout(template="plotly_white", xaxis_tickangle=-35)

    sel_df = RESULTS[RESULTS["seleccionado"] == 1].copy()
    sel_df["label"] = sel_df["frecuencia"] + " | " + sel_df["modelo"]
    fig_selected = px.bar(
        sel_df,
        x="label",
        y="test_Corr",
        color="frecuencia",
        title="Modelos seleccionados: correlación en prueba",
    )
    fig_selected.update_layout(template="plotly_white", xaxis_tickangle=-30)

    table_df = df.copy()
    for c in ["val_RMSE", "val_R2", "test_RMSE", "test_R2", "test_Corr"]:
        if c in table_df.columns:
            table_df[c] = table_df[c].apply(lambda x: None if x != x else round(x, 3))

    cols = ["frecuencia", "modelo", "target", "val_RMSE", "val_R2", "test_RMSE", "test_R2", "test_Corr", "seleccionado", "rol_modelo"]
    cols = [c for c in cols if c in table_df.columns]

    return (
        wk_card,
        mo_card,
        an_card,
        fig_metric,
        fig_selected,
        table_df[cols].to_dict("records"),
        [{"name": c, "id": c} for c in cols],
    )