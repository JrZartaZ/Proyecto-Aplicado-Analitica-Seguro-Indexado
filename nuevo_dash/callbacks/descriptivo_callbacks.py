from dash import Input, Output, html
import dash_bootstrap_components as dbc

from services.data_loader import get_filter_options
from services.descriptivo_service import (
    get_family_options,
    get_variable_options,
    get_variable_kpis,
    build_variable_series,
    build_heatmap,
    build_distribution_plot,
    build_model_drivers,
    get_model_reading,
    get_preview_table,
)


def register_descriptivo_callbacks(app):
    @app.callback(
        Output("desc-departamento", "options"),
        Output("desc-anio", "options"),
        Output("desc-familia", "options"),
        Output("desc-familia", "value"),
        Input("desc-freq", "value"),
    )
    def update_base_filters(freq):
        opts = get_filter_options(freq)
        fams = get_family_options(freq)

        deptos = [{"label": d, "value": d} for d in opts["departamentos"]]
        anios = [{"label": str(a), "value": a} for a in opts["anios"]]
        fam_value = fams[0]["value"] if fams else None

        return deptos, anios, fams, fam_value

    @app.callback(
        Output("desc-variable", "options"),
        Output("desc-variable", "value"),
        Input("desc-freq", "value"),
        Input("desc-familia", "value"),
    )
    def update_variable_options(freq, familia):
        if not familia:
            return [], None

        opciones = get_variable_options(freq, familia)
        value = opciones[0]["value"] if opciones else None
        return opciones, value

    @app.callback(
        Output("kpi-mean", "children"),
        Output("kpi-max", "children"),
        Output("kpi-min", "children"),
        Output("kpi-std", "children"),
        Output("desc-serie-principal", "figure"),
        Output("desc-heatmap", "figure"),
        Output("desc-distribucion", "figure"),
        Output("desc-modelo-drivers", "figure"),
        Output("desc-lectura-modelo", "children"),
        Output("desc-tabla-preview", "children"),
        Input("desc-freq", "value"),
        Input("desc-familia", "value"),
        Input("desc-variable", "value"),
        Input("desc-departamento", "value"),
        Input("desc-anio", "value"),
        Input("desc-modelo", "value"),
    )
    def update_descriptivo_content(freq, familia, variable, departamento, anio, modelo):
        if not variable:
            vacio = html.Div("Seleccione una variable para iniciar el análisis.")
            return "-", "-", "-", "-", {}, {}, {}, {}, vacio, vacio

        kpis = get_variable_kpis(freq, variable, departamento, anio)
        fig_series = build_variable_series(freq, variable, departamento, anio)
        fig_heatmap = build_heatmap(freq, variable, anio)
        fig_dist = build_distribution_plot(freq, variable, departamento, anio)
        fig_model = build_model_drivers(modelo)

        lectura = get_model_reading(modelo, variable, familia)
        lectura_html = html.Ul([html.Li(x) for x in lectura])

        preview = get_preview_table(freq, variable, departamento, anio)
        if preview.empty:
            tabla = html.Div("No hay datos disponibles para los filtros seleccionados.")
        else:
            tabla = dbc.Table.from_dataframe(
                preview,
                striped=True,
                bordered=True,
                hover=True,
                size="sm"
            )

        return (
            kpis["mean"],
            kpis["max"],
            kpis["min"],
            kpis["std"],
            fig_series,
            fig_heatmap,
            fig_dist,
            fig_model,
            lectura_html,
            tabla,
        )
