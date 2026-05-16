import numpy as np
import pandas as pd

from services.data_loader import load_monthly, load_m5_model, load_m6_model, get_possible_column


def _get_columns(df: pd.DataFrame):
    dept_col = get_possible_column(df, ["departamento", "department", "depto"])
    year_col = get_possible_column(df, ["anio", "año", "year", "anio_referencia_y"])
    month_col = get_possible_column(df, ["mes", "month", "mes_referencia_y"])
    return dept_col, year_col, month_col


def get_simulation_filter_options():
    df = load_monthly().copy()
    dept_col, year_col, month_col = _get_columns(df)

    out = {"departamentos": [], "anios": [], "meses": []}

    if dept_col:
        out["departamentos"] = sorted(df[dept_col].dropna().astype(str).unique().tolist())
    if year_col:
        out["anios"] = sorted(pd.to_numeric(df[year_col], errors="coerce").dropna().astype(int).unique().tolist())
    if month_col:
        out["meses"] = sorted(pd.to_numeric(df[month_col], errors="coerce").dropna().astype(int).unique().tolist())

    return out


def _find_monthly_row(departamento, anio, mes):
    df = load_monthly().copy()
    dept_col, year_col, month_col = _get_columns(df)

    row = df[
        (df[dept_col].astype(str) == str(departamento)) &
        (pd.to_numeric(df[year_col], errors="coerce") == int(anio)) &
        (pd.to_numeric(df[month_col], errors="coerce") == int(mes))
    ].copy()

    if row.empty:
        raise ValueError("No existe registro para el escenario seleccionado")

    return row.iloc[[0]].copy()


def _safe_predict(model, row: pd.DataFrame):
    try:
        if hasattr(model, "feature_names_in_"):
            features = list(model.feature_names_in_)
            X = row.reindex(columns=features, fill_value=0)
        elif hasattr(model, "named_steps"):
            estimator = list(model.named_steps.values())[-1]
            if hasattr(estimator, "feature_names_in_"):
                features = list(estimator.feature_names_in_)
                X = row.reindex(columns=features, fill_value=0)
            else:
                X = row.select_dtypes(include="number").copy()
        else:
            X = row.select_dtypes(include="number").copy()

        pred = model.predict(X)[0]
        return float(pred)
    except Exception:
        return np.nan


def _apply_shocks(row, shock_precip=0, shock_gwetroot=0, shock_temp=0, shock_indice=0, shock_precio=0, shock_trm=0):
    row = row.copy()

    mapping = {
        "precip": ["PRECTOTCORR", "lluvia_acum_4s", "lluvia_acum_8s"],
        "gwetroot": ["GWETROOT_mean", "GWETROOT", "gwetroot_ma_4s_mean", "score_humedad"],
        "temp": ["T2M_mean", "T2M_MAX_mean", "T2M_MIN_mean", "T2M", "t2m_max_ma_4s_mean"],
        "indice": ["indice_climatico_base_x_mean", "indice_climatico_ajustado_x_mean", "indice_climatico_base_x", "indice_climatico_ajustado_x"],
        "precio": ["precio_interno_cop_carga_mean", "precio_interno_cop_carga", "precio_interno"],
        "trm": ["trm_viernes_cop_usd_mean", "trm_promedio_semana_cop_usd_mean", "trm_viernes_cop_usd"],
    }

    shocks = {
        "precip": shock_precip,
        "gwetroot": shock_gwetroot,
        "temp": shock_temp,
        "indice": shock_indice,
        "precio": shock_precio,
        "trm": shock_trm,
    }

    for key, cols in mapping.items():
        for c in cols:
            if c in row.columns:
                row[c] = row[c] * (1 + shocks[key] / 100.0)

    return row


def _select_output(modelo_final, m5_val, m6_val, fallback):
    vals = {"m5": m5_val, "m6": m6_val}

    if modelo_final == "m5":
        return m5_val if not np.isnan(m5_val) else fallback

    if modelo_final == "m6":
        return m6_val if not np.isnan(m6_val) else fallback

    disponibles = [v for v in [m5_val, m6_val] if not np.isnan(v)]
    if not disponibles:
        return fallback
    if len(disponibles) == 1:
        return disponibles[0]

    return 0.4 * m5_val + 0.6 * m6_val


def _risk_bucket(severidad):
    if severidad < 5:
        return "Bajo"
    elif severidad < 15:
        return "Medio"
    else:
        return "Alto"


def _trigger_label(severidad):
    if severidad >= 15:
        return "Activación alta sugerida"
    elif severidad >= 8:
        return "Monitoreo reforzado / trigger preventivo"
    else:
        return "Sin activación sugerida"


def _build_comment(resultado, shocks):
    comentarios = []

    if resultado["nivel_riesgo"] == "Alto":
        comentarios.append("El escenario proyecta una afectación relevante y sugiere una revisión inmediata de cobertura y trigger.")
    elif resultado["nivel_riesgo"] == "Medio":
        comentarios.append("El escenario incrementa la sensibilidad del sistema y justifica monitoreo reforzado.")
    else:
        comentarios.append("El escenario no genera una afectación severa bajo la lógica actual del modelo.")

    if shocks["precip"] > 0:
        comentarios.append("El aumento de precipitación eleva la probabilidad de estrés hídrico/exceso de lluvia.")
    if shocks["gwetroot"] > 0:
        comentarios.append("La humedad radicular alta puede reforzar señales de saturación del suelo.")
    if shocks["temp"] != 0:
        comentarios.append("El shock térmico modifica el contexto fisiológico del cultivo.")
    if shocks["precio"] != 0 or shocks["trm"] != 0:
        comentarios.append("Las variables económicas alteran la lectura de exposición y sensibilidad financiera.")

    return comentarios


def run_simulation(
    departamento,
    anio,
    mes,
    modelo_final="hibrido",
    shock_precip=0,
    shock_gwetroot=0,
    shock_temp=0,
    shock_indice=0,
    shock_precio=0,
    shock_trm=0,
):
    base_row = _find_monthly_row(departamento, anio, mes)
    escenario_row = _apply_shocks(
        base_row,
        shock_precip=shock_precip,
        shock_gwetroot=shock_gwetroot,
        shock_temp=shock_temp,
        shock_indice=shock_indice,
        shock_precio=shock_precio,
        shock_trm=shock_trm,
    )

    m5 = load_m5_model()
    m6 = load_m6_model()

    pred_m5_base = _safe_predict(m5, base_row)
    pred_m6_base = _safe_predict(m6, base_row)
    pred_m5_esc = _safe_predict(m5, escenario_row)
    pred_m6_esc = _safe_predict(m6, escenario_row)

    proxy_candidates = [
        "produccion_mensual_proxy_t",
        "produccion_mensual_desde_semana_t",
        "produccion_semanal_proxy_t",
        "produccion_anual_departamental_t"
    ]

    prod_base_proxy = np.nan
    for c in proxy_candidates:
        if c in base_row.columns:
            prod_base_proxy = float(base_row[c].iloc[0])
            break

    base_final = _select_output(modelo_final, pred_m5_base, pred_m6_base, prod_base_proxy)
    esc_final = _select_output(modelo_final, pred_m5_esc, pred_m6_esc, prod_base_proxy)

    delta_abs = esc_final - base_final
    delta_pct = 0 if base_final == 0 else (delta_abs / base_final) * 100.0
    perdida_proxy = max(0.0, base_final - esc_final)
    severidad_pct = 0 if base_final == 0 else (perdida_proxy / base_final) * 100.0

    nivel_riesgo = _risk_bucket(severidad_pct)
    trigger = _trigger_label(severidad_pct)

    cobertura_indicativa = perdida_proxy * 0.70
    factor_prima = {"Bajo": 0.06, "Medio": 0.08, "Alto": 0.12}[nivel_riesgo]
    prima_indicativa = max(0.0, cobertura_indicativa * factor_prima)

    shocks = {
        "precip": shock_precip,
        "gwetroot": shock_gwetroot,
        "temp": shock_temp,
        "indice": shock_indice,
        "precio": shock_precio,
        "trm": shock_trm,
    }

    resultado = {
        "produccion_base": round(base_final, 2),
        "produccion_escenario": round(esc_final, 2),
        "delta_abs": round(delta_abs, 2),
        "delta_pct": round(delta_pct, 2),
        "perdida_proxy": round(perdida_proxy, 2),
        "severidad_pct": round(severidad_pct, 2),
        "nivel_riesgo": nivel_riesgo,
        "trigger": trigger,
        "cobertura_indicativa": round(cobertura_indicativa, 2),
        "prima_indicativa": round(prima_indicativa, 2),
        "detalle_modelos": {
            "m5_base": None if np.isnan(pred_m5_base) else round(float(pred_m5_base), 2),
            "m6_base": None if np.isnan(pred_m6_base) else round(float(pred_m6_base), 2),
            "m5_escenario": None if np.isnan(pred_m5_esc) else round(float(pred_m5_esc), 2),
            "m6_escenario": None if np.isnan(pred_m6_esc) else round(float(pred_m6_esc), 2),
        },
        "comentarios": _build_comment(
            {
                "nivel_riesgo": nivel_riesgo
            },
            shocks
        )
    }

    return resultado


def build_simulation_chart(resultado: dict):
    return pd.DataFrame({
        "modelo": ["M5", "M5", "M6", "M6", "Seleccionado", "Seleccionado"],
        "escenario": ["Base", "Simulado", "Base", "Simulado", "Base", "Simulado"],
        "valor": [
            resultado["detalle_modelos"]["m5_base"] if resultado["detalle_modelos"]["m5_base"] is not None else 0,
            resultado["detalle_modelos"]["m5_escenario"] if resultado["detalle_modelos"]["m5_escenario"] is not None else 0,
            resultado["detalle_modelos"]["m6_base"] if resultado["detalle_modelos"]["m6_base"] is not None else 0,
            resultado["detalle_modelos"]["m6_escenario"] if resultado["detalle_modelos"]["m6_escenario"] is not None else 0,
            resultado["produccion_base"],
            resultado["produccion_escenario"],
        ]
    })
