import numpy as np
import pandas as pd
import plotly.express as px

from services.data_loader import load_dataset, load_m5_model, load_m6_model, get_possible_column


def _get_columns(df: pd.DataFrame):
    dept_col = get_possible_column(df, ["departamento", "department", "depto"])
    year_col = get_possible_column(df, ["anio", "año", "year", "anio_referencia_y", "anio_semana_fin"])
    month_col = get_possible_column(df, ["mes", "month", "mes_referencia_y"])
    week_col = get_possible_column(df, ["semana", "week", "week_iso", "semana_iso"])
    date_col = get_possible_column(df, [
        "fecha", "date", "fecha_mes", "periodo", "period",
        "fecha_semana_inicio", "fecha_semana_fin"
    ])
    return dept_col, year_col, month_col, week_col, date_col


def classify_family(col: str):
    c = col.lower()

    if any(x in c for x in ["produccion", "rendimiento", "area_cosechada", "dias_productivos"]):
        return "productiva"

    if any(x in c for x in ["precio", "trm", "exportaciones", "valor_cosecha"]):
        return "economica"

    if any(x in c for x in ["indice_climatico", "score_", "anomalia_", "lluvia_acum", "dummy_"]):
        return "derivada"

    if any(x in c for x in ["prectot", "t2m", "rh2m", "qv2m", "gwet", "allsky", "ws2m"]):
        return "climatica"

    return None


def get_family_options(freq: str):
    df = load_dataset(freq)
    familias = []
    for c in df.columns:
        fam = classify_family(c)
        if fam and fam not in familias:
            familias.append(fam)

    etiquetas = {
        "productiva": "Productiva",
        "climatica": "Climática",
        "derivada": "Derivada",
        "economica": "Económica",
    }

    return [{"label": etiquetas[f], "value": f} for f in familias]


def get_variable_options(freq: str, familia: str):
    df = load_dataset(freq)
    opciones = []

    for c in df.columns:
        if classify_family(c) == familia:
            opciones.append({"label": c, "value": c})

    return opciones


def get_filtered_dataset(freq: str, departamento=None, anio=None):
    df = load_dataset(freq).copy()
    dept_col, year_col, month_col, week_col, date_col = _get_columns(df)

    if departamento and dept_col:
        df = df[df[dept_col].astype(str) == str(departamento)]

    if anio is not None and year_col:
        df = df[pd.to_numeric(df[year_col], errors="coerce") == int(anio)]

    return df


def _format_number(x):
    if x is None or pd.isna(x):
        return "-"
    try:
        return f"{float(x):,.2f}"
    except Exception:
        return str(x)


def get_variable_kpis(freq: str, variable: str, departamento=None, anio=None):
    df = get_filtered_dataset(freq, departamento, anio)

    if df.empty or variable not in df.columns:
        return {"mean": "-", "max": "-", "min": "-", "std": "-"}

    serie = pd.to_numeric(df[variable], errors="coerce").dropna()

    if serie.empty:
        return {"mean": "-", "max": "-", "min": "-", "std": "-"}

    return {
        "mean": _format_number(serie.mean()),
        "max": _format_number(serie.max()),
        "min": _format_number(serie.min()),
        "std": _format_number(serie.std()),
    }


def build_variable_series(freq: str, variable: str, departamento=None, anio=None):
    df = get_filtered_dataset(freq, departamento, anio)
    dept_col, year_col, month_col, week_col, date_col = _get_columns(df)

    if df.empty or variable not in df.columns:
        return px.line(title="No hay información disponible")

    plot_df = df.copy()

    if not departamento and dept_col:
        if date_col and pd.api.types.is_datetime64_any_dtype(plot_df[date_col]):
            plot_df = plot_df.groupby(date_col, as_index=False)[variable].mean()
            return px.line(plot_df, x=date_col, y=variable, title=f"Serie de {variable}")
        elif year_col and month_col:
            plot_df = plot_df.groupby([year_col, month_col], as_index=False)[variable].mean()
            plot_df["time_label"] = plot_df[year_col].astype(str) + "-" + plot_df[month_col].astype(str).str.zfill(2)
            return px.line(plot_df, x="time_label", y=variable, title=f"Serie de {variable}")
        elif year_col and week_col:
            plot_df = plot_df.groupby([year_col, week_col], as_index=False)[variable].mean()
            plot_df["time_label"] = plot_df[year_col].astype(str) + "-W" + plot_df[week_col].astype(str).str.zfill(2)
            return px.line(plot_df, x="time_label", y=variable, title=f"Serie de {variable}")
        elif year_col:
            plot_df = plot_df.groupby(year_col, as_index=False)[variable].mean()
            return px.line(plot_df, x=year_col, y=variable, title=f"Serie de {variable}")

    if date_col and pd.api.types.is_datetime64_any_dtype(plot_df[date_col]):
        plot_df = plot_df.sort_values(date_col)
        return px.line(plot_df, x=date_col, y=variable, title=f"Serie de {variable}")

    if year_col and month_col:
        plot_df["time_label"] = plot_df[year_col].astype(str) + "-" + plot_df[month_col].astype(str).str.zfill(2)
        return px.line(plot_df, x="time_label", y=variable, title=f"Serie de {variable}")

    if year_col and week_col:
        plot_df["time_label"] = plot_df[year_col].astype(str) + "-W" + plot_df[week_col].astype(str).str.zfill(2)
        return px.line(plot_df, x="time_label", y=variable, title=f"Serie de {variable}")

    if year_col:
        return px.line(plot_df, x=year_col, y=variable, title=f"Serie de {variable}")

    return px.line(title="No fue posible construir la serie")


def build_heatmap(freq: str, variable: str, anio=None):
    df = get_filtered_dataset(freq, None, anio)
    dept_col, year_col, month_col, week_col, date_col = _get_columns(df)

    if df.empty or variable not in df.columns or dept_col is None:
        return px.imshow(title="No hay información disponible")

    if month_col:
        piv = df.pivot_table(index=dept_col, columns=month_col, values=variable, aggfunc="mean")
        return px.imshow(
            piv,
            aspect="auto",
            labels=dict(x="Mes", y="Departamento", color=variable),
            title=f"Heatmap territorial de {variable}"
        )

    if week_col:
        piv = df.pivot_table(index=dept_col, columns=week_col, values=variable, aggfunc="mean")
        return px.imshow(
            piv,
            aspect="auto",
            labels=dict(x="Semana", y="Departamento", color=variable),
            title=f"Heatmap territorial de {variable}"
        )

    if year_col:
        piv = df.pivot_table(index=dept_col, columns=year_col, values=variable, aggfunc="mean")
        return px.imshow(
            piv,
            aspect="auto",
            labels=dict(x="Año", y="Departamento", color=variable),
            title=f"Heatmap territorial de {variable}"
        )

    return px.imshow(title="No fue posible construir el heatmap")


def build_distribution_plot(freq: str, variable: str, departamento=None, anio=None):
    df = get_filtered_dataset(freq, departamento, anio)
    dept_col, year_col, month_col, week_col, date_col = _get_columns(df)

    if df.empty or variable not in df.columns:
        return px.histogram(title="No hay información disponible")

    if departamento and month_col:
        return px.box(df, x=month_col, y=variable, title=f"Distribución mensual de {variable}")

    if dept_col:
        return px.box(df, x=dept_col, y=variable, title=f"Distribución territorial de {variable}")

    return px.histogram(df, x=variable, title=f"Distribución de {variable}")


def build_model_drivers(model_key="m5"):
    try:
        model = load_m5_model() if model_key == "m5" else load_m6_model()

        # Pipeline: steps ['prep', 'model']
        if hasattr(model, "named_steps"):
            prep = model.named_steps.get("prep", None)
            estimator = model.named_steps.get("model", None)
        else:
            prep = None
            estimator = model

        if estimator is None:
            return px.bar(title="No fue posible leer la importancia del modelo")

        # Importancias / coeficientes
        if hasattr(estimator, "feature_importances_"):
            importances = np.asarray(estimator.feature_importances_, dtype=float)
        elif hasattr(estimator, "coef_"):
            importances = np.abs(np.ravel(estimator.coef_)).astype(float)
        else:
            return px.bar(title="No fue posible leer la importancia del modelo")

        # Nombres de variables transformadas
        if prep is not None and hasattr(prep, "get_feature_names_out"):
            try:
                feature_names = list(prep.get_feature_names_out(model.feature_names_in_))
            except Exception:
                try:
                    feature_names = list(prep.get_feature_names_out())
                except Exception:
                    feature_names = [f"var_{i+1}" for i in range(len(importances))]
        else:
            if hasattr(model, "feature_names_in_"):
                feature_names = list(model.feature_names_in_)
            else:
                feature_names = [f"var_{i+1}" for i in range(len(importances))]

        if len(feature_names) != len(importances):
            feature_names = [f"var_{i+1}" for i in range(len(importances))]

        imp = pd.Series(importances, index=feature_names)
        imp = imp.sort_values(ascending=False).head(12).sort_values()

        fig = px.bar(
            x=imp.values,
            y=imp.index,
            orientation="h",
            title=f"Top drivers del modelo {model_key.upper()}"
        )
        fig.update_layout(yaxis_title="", xaxis_title="Importancia")
        return fig

    except Exception:
        return px.bar(title="No fue posible leer la importancia del modelo")


def get_model_reading(model_key="m5", variable=None, familia=None):
    textos = {
        "m5": [
            "M5 se usa como referencia técnica más limpia para interpretar la lógica climática y económica del seguro indexado.",
            "Su lectura prioriza señal climática y contexto económico, con menor peso de variables estructurales.",
        ],
        "m6": [
            "M6 se conserva como modelo operativo principal mensual por su mejor ajuste global.",
            "Su lectura puede estar parcialmente dominada por variables estructurales, por lo que conviene interpretarlo junto con M5.",
        ]
    }

    extra = []
    if familia == "climatica":
        extra.append("La familia climática permite observar precipitación, temperatura, humedad y radiación como señales explicativas directas del riesgo.")
    elif familia == "derivada":
        extra.append("La familia derivada resume patrones complejos mediante índices, acumulados y dummies de activación.")
    elif familia == "economica":
        extra.append("La familia económica debe interpretarse como contexto de mercado y exposición, no como sustituto de la lógica climática.")
    elif familia == "productiva":
        extra.append("La familia productiva conecta el comportamiento observado/proxy con el desempeño del sistema productivo y la estructura territorial.")

    if variable:
        extra.append(f"Variable seleccionada: {variable}")

    return textos.get(model_key, []) + extra


def get_preview_table(freq: str, variable: str, departamento=None, anio=None, n=12):
    df = get_filtered_dataset(freq, departamento, anio).copy()
    if df.empty:
        return pd.DataFrame()

    dept_col, year_col, month_col, week_col, date_col = _get_columns(df)

    cols = []
    for c in [dept_col, year_col, month_col, week_col, date_col, variable]:
        if c and c in df.columns and c not in cols:
            cols.append(c)

    if not cols:
        cols = df.columns[: min(len(df.columns), 8)].tolist()

    preview = df[cols].head(n).copy()
    return preview
