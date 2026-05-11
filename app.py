from dash import Dash, html, dcc, page_container

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Seguro Café - Artefacto Analítico"
)
server = app.server

app.layout = html.Div(
    className="app-shell",
    children=[
        html.Div(
            className="topbar",
            children=[
                html.Div(
                    [
                        html.H1("Seguro Café", className="app-title"),
                        html.P(
                            "Artefacto analítico para diseño y monitoreo de seguro indexado",
                            className="app-subtitle",
                        ),
                    ]
                ),
                html.Div(
                    className="nav-links",
                    children=[
                        dcc.Link("Diagnóstico", href="/", className="nav-link"),
                        dcc.Link("Modelos", href="/modelos", className="nav-link"),
                        dcc.Link("Artefacto", href="/artefacto", className="nav-link"),
                    ],
                ),
            ],
        ),
        html.Div(className="page-wrap", children=page_container),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)