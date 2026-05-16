from dash import html, dcc
import dash_bootstrap_components as dbc


def build_descriptivo_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H2("Capítulo 1. Descriptivo", className="mb-2"),
                        html.P(
                            "Vista analítica del artefacto: comportamiento climático, "
                            "productivo y económico por frecuencia, zona y variable.",
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
                                    html.Label("Frecuencia"),
                                    dcc.Dropdown(
                                        id="desc-freq",
                                        options=[
                                            {"label": "Semanal", "value": "weekly"},
                                            {"label": "Mensual", "value": "monthly"},
                                            {"label": "Anual", "value": "annual"},
                                        ],
                                        value="monthly",
                                        clearable=False,
                                    ),
                                ]
                            )
                        ),
                        md=2
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Familia de variable"),
                                    dcc.Dropdown(
                                        id="desc-familia",
                                        options=[],
                                        value=None,
                                        clearable=False,
                                    ),
                                ]
                            )
                        ),
                        md=2
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Variable"),
                                    dcc.Dropdown(
                                        id="desc-variable",
                                        options=[],
                                        value=None,
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
                                    html.Label("Departamento"),
                                    dcc.Dropdown(
                                        id="desc-departamento",
                                        options=[],
                                        placeholder="Todos",
                                        clearable=True,
                                    ),
                                ]
                            )
                        ),
                        md=2
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Año"),
                                    dcc.Dropdown(
                                        id="desc-anio",
                                        options=[],
                                        placeholder="Todos",
                                        clearable=True,
                                    ),
                                ]
                            )
                        ),
                        md=1
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Label("Modelo de referencia"),
                                    dcc.Dropdown(
                                        id="desc-modelo",
                                        options=[
                                            {"label": "M5 - clima + economía", "value": "m5"},
                                            {"label": "M6 - clima + economía + estructura", "value": "m6"},
                                        ],
                                        value="m5",
                                        clearable=False,
                                    ),
                                ]
                            )
                        ),
                        md=2
                    ),
                ],
                className="mb-4"
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.Div("Promedio", className="text-muted"),
                            html.H3(id="kpi-mean", children="-")
                        ])),
                        md=3
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.Div("Máximo", className="text-muted"),
                            html.H3(id="kpi-max", children="-")
                        ])),
                        md=3
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.Div("Mínimo", className="text-muted"),
                            html.H3(id="kpi-min", children="-")
                        ])),
                        md=3
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody([
                            html.Div("Desv. estándar", className="text-muted"),
                            html.H3(id="kpi-std", children="-")
                        ])),
                        md=3
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
                                    html.H5("Serie temporal de la variable seleccionada"),
                                    dcc.Graph(id="desc-serie-principal")
                                ]
                            )
                        ),
                        md=8
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Heatmap territorial / temporal"),
                                    dcc.Graph(id="desc-heatmap")
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
                                    html.H5("Distribución analítica"),
                                    dcc.Graph(id="desc-distribucion")
                                ]
                            )
                        ),
                        md=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Variables influyentes del modelo"),
                                    dcc.Graph(id="desc-modelo-drivers")
                                ]
                            )
                        ),
                        md=6
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
                                    html.H5("Lectura técnica"),
                                    html.Div(id="desc-lectura-modelo")
                                ]
                            )
                        ),
                        md=5
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Vista previa de datos"),
                                    html.Div(id="desc-tabla-preview")
                                ]
                            )
                        ),
                        md=7
                    ),
                ]
            )
        ],
        fluid=True
    )
