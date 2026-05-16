from dash import Input, Output, State, html
import plotly.express as px

from services.simulacion_service import (
    get_simulation_filter_options,
    run_simulation,
    build_simulation_chart,
)


def register_simulacion_callbacks(app):
    @app.callback(
        Output("sim-departamento", "options"),
        Output("sim-anio", "options"),
        Output("sim-mes", "options"),
        Input("sim-departamento", "id"),
    )
    def load_simulation_filters(_):
        opts = get_simulation_filter_options()

        deptos = [{"label": d, "value": d} for d in opts["departamentos"]]
        anios = [{"label": str(a), "value": a} for a in opts["anios"]]
        meses = [{"label": str(m), "value": m} for m in opts["meses"]]

        return deptos, anios, meses

    @app.callback(
        Output("sim-prod-base", "children"),
        Output("sim-prod-esc", "children"),
        Output("sim-delta-abs", "children"),
        Output("sim-delta-pct", "children"),
        Output("sim-loss", "children"),
        Output("sim-severidad", "children"),
        Output("sim-riesgo", "children"),
        Output("sim-trigger", "children"),
        Output("sim-cobertura", "children"),
        Output("sim-prima", "children"),
        Output("sim-grafico-resultado", "figure"),
        Output("sim-comentario", "children"),
        Input("btn-simular", "n_clicks"),
        State("sim-departamento", "value"),
        State("sim-anio", "value"),
        State("sim-mes", "value"),
        State("sim-modelo-final", "value"),
        State("sim-shock-precip", "value"),
        State("sim-shock-gwetroot", "value"),
        State("sim-shock-temp", "value"),
        State("sim-shock-indice", "value"),
        State("sim-shock-precio", "value"),
        State("sim-shock-trm", "value"),
        prevent_initial_call=True,
    )
    def ejecutar_simulacion(
        n_clicks,
        departamento,
        anio,
        mes,
        modelo_final,
        shock_precip,
        shock_gwetroot,
        shock_temp,
        shock_indice,
        shock_precio,
        shock_trm,
    ):
        try:
            resultado = run_simulation(
                departamento=departamento,
                anio=anio,
                mes=mes,
                modelo_final=modelo_final or "hibrido",
                shock_precip=shock_precip or 0,
                shock_gwetroot=shock_gwetroot or 0,
                shock_temp=shock_temp or 0,
                shock_indice=shock_indice or 0,
                shock_precio=shock_precio or 0,
                shock_trm=shock_trm or 0,
            )

            df_chart = build_simulation_chart(resultado)
            fig = px.bar(
                df_chart,
                x="modelo",
                y="valor",
                color="escenario",
                barmode="group",
                title="Base vs escenario por modelo"
            )

            comentario = html.Ul([html.Li(x) for x in resultado["comentarios"]])

            return (
                f"{resultado['produccion_base']:,}",
                f"{resultado['produccion_escenario']:,}",
                f"{resultado['delta_abs']:,}",
                f"{resultado['delta_pct']:,}%",
                f"{resultado['perdida_proxy']:,}",
                f"{resultado['severidad_pct']:,}%",
                resultado["nivel_riesgo"],
                resultado["trigger"],
                f"{resultado['cobertura_indicativa']:,}",
                f"{resultado['prima_indicativa']:,}",
                fig,
                comentario,
            )

        except Exception as e:
            fig = px.bar(title="No fue posible ejecutar la simulación")
            return (
                "Error", "Error", "Error", "Error", str(e), "Error",
                "Error", "Error", "Error", "Error", fig,
                html.Div(str(e))
            )
