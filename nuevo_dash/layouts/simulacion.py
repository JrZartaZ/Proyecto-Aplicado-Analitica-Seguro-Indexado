from dash import html, dcc
import dash_bootstrap_components as dbc


def build_simulacion_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H2("Capítulo 2. Simulación", className="mb-3"),
                        html.P(
                            "Construye escenarios y evalúa su impacto en producción proxy, "
                            "riesgo, cobertura y prima indicativa.",
                            className="text-muted"
                        ),
                    ]
                )
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Departamento"),
                                    dcc.Dropdown(id="sim-departamento", options=[], clearable=False),

                                    html.Br(),
                                    html.Label("Año"),
                                    dcc.Dropdown(id="sim-anio", options=[], clearable=False),

                                    html.Br(),
                                    html.Label("Mes"),
                                    dcc.Dropdown(id="sim-mes", options=[], clearable=False),

                                    html.Br(),
                                    html.Label("Modelo de salida"),
                                    dcc.Dropdown(
                                        id="sim-modelo-final",
                                        options=[
                                            {"label": "M5 - referencia climática", "value": "m5"},
                                            {"label": "M6 - operativo mensual", "value": "m6"},
                                            {"label": "Híbrido M5/M6", "value": "hibrido"},
                                        ],
                                        value="hibrido",
                                        clearable=False,
                                    ),
                                ]
                            )
                        ),
                        md=3
                    ),

                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Shock precipitación (%)"),
                                    dcc.Slider(id="sim-shock-precip", min=-50, max=50, step=5, value=0,
                                               marks={-50: "-50", -25: "-25", 0: "0", 25: "25", 50: "50"}),

                                    html.Br(),
                                    html.Label("Shock humedad radicular (%)"),
                                    dcc.Slider(id="sim-shock-gwetroot", min=-50, max=50, step=5, value=0,
                                               marks={-50: "-50", -25: "-25", 0: "0", 25: "25", 50: "50"}),

                                    html.Br(),
                                    html.Label("Shock temperatura (%)"),
                                    dcc.Slider(id="sim-shock-temp", min=-20, max=20, step=5, value=0,
                                               marks={-20: "-20", -10: "-10", 0: "0", 10: "10", 20: "20"}),

                                    html.Br(),
                                    html.Label("Shock índice climático (%)"),
                                    dcc.Slider(id="sim-shock-indice", min=-30, max=30, step=5, value=0,
                                               marks={-30: "-30", -15: "-15", 0: "0", 15: "15", 30: "30"}),

                                    html.Br(),
                                    html.Label("Shock precio interno (%)"),
                                    dcc.Slider(id="sim-shock-precio", min=-30, max=30, step=5, value=0,
                                               marks={-30: "-30", -15: "-15", 0: "0", 15: "15", 30: "30"}),

                                    html.Br(),
                                    html.Label("Shock TRM (%)"),
                                    dcc.Slider(id="sim-shock-trm", min=-20, max=20, step=5, value=0,
                                               marks={-20: "-20", -10: "-10", 0: "0", 10: "10", 20: "20"}),

                                    html.Br(),
                                    dbc.Button("Ejecutar simulación", id="btn-simular", color="success", className="mt-2")
                                ]
                            )
                        ),
                        md=5
                    ),

                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Resultados del escenario"),
                                    html.Hr(),
                                    html.P(["Producción base: ", html.Strong(id="sim-prod-base", children="-")]),
                                    html.P(["Producción escenario: ", html.Strong(id="sim-prod-esc", children="-")]),
                                    html.P(["Cambio absoluto: ", html.Strong(id="sim-delta-abs", children="-")]),
                                    html.P(["Cambio %: ", html.Strong(id="sim-delta-pct", children="-")]),
                                    html.P(["Pérdida proxy: ", html.Strong(id="sim-loss", children="-")]),
                                    html.P(["Severidad %: ", html.Strong(id="sim-severidad", children="-")]),
                                    html.P(["Nivel de riesgo: ", html.Strong(id="sim-riesgo", children="-")]),
                                    html.P(["Trigger sugerido: ", html.Strong(id="sim-trigger", children="-")]),
                                    html.P(["Cobertura indicativa: ", html.Strong(id="sim-cobertura", children="-")]),
                                    html.P(["Prima indicativa: ", html.Strong(id="sim-prima", children="-")]),
                                ]
                            )
                        ),
                        md=4
                    ),
                ],
                className="mb-4"
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Comparación base vs escenario"),
                                    dcc.Graph(id="sim-grafico-resultado")
                                ]
                            )
                        ),
                        md=7
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Lectura del escenario"),
                                    html.Div(id="sim-comentario")
                                ]
                            )
                        ),
                        md=5
                    )
                ]
            )
        ],
        fluid=True
    )
