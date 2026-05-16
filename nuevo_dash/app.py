from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

from layouts.descriptivo import build_descriptivo_layout
from layouts.simulacion import build_simulacion_layout
from callbacks.descriptivo_callbacks import register_descriptivo_callbacks
from callbacks.simulacion_callbacks import register_simulacion_callbacks


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Seguro Indexado Café - Dashboard"
)

server = app.server


def build_home():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1(
                            "Dashboard Analítico para Seguro Agrícola Indexado de Café",
                            className="mt-4 mb-3"
                        ),
                        html.P(
                            "Artefacto analítico para diagnóstico descriptivo y simulación "
                            "de escenarios de riesgo, cobertura y prima indicativa.",
                            className="lead"
                        ),
                        html.Hr(),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Capítulo 1. Descriptivo", className="card-title"),
                                    html.P(
                                        "Explora KPIs, series históricas, comparación territorial "
                                        "y lectura técnica de variables climáticas, productivas y económicas."
                                    ),
                                    dbc.Button(
                                        "Ir al descriptivo",
                                        href="/descriptivo",
                                        color="primary"
                                    )
                                ]
                            ),
                            className="mb-3"
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Capítulo 2. Simulación", className="card-title"),
                                    html.P(
                                        "Construye escenarios y evalúa su impacto en riesgo, producción proxy, "
                                        "cobertura y prima indicativa."
                                    ),
                                    dbc.Button(
                                        "Ir a simulación",
                                        href="/simulacion",
                                        color="success"
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        ],
        fluid=True
    )


app.layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),

        dbc.Navbar(
            dbc.Container(
                [
                    dbc.NavbarBrand("Seguro Indexado Café", className="fw-bold"),
                    dbc.Nav(
                        [
                            dbc.NavLink("Inicio", href="/", active="exact"),
                            dbc.NavLink("Descriptivo", href="/descriptivo", active="exact"),
                            dbc.NavLink("Simulación", href="/simulacion", active="exact"),
                        ],
                        pills=True
                    )
                ]
            ),
            color="dark",
            dark=True,
            className="mb-4"
        ),

        html.Div(id="page-content")
    ],
    fluid=True
)


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/descriptivo":
        return build_descriptivo_layout()
    elif pathname == "/simulacion":
        return build_simulacion_layout()
    return build_home()


register_descriptivo_callbacks(app)
register_simulacion_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True)
