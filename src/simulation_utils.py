from pathlib import Path
import json
import joblib
import pandas as pd

MODEL_DIR = Path("model")
META_DIR = MODEL_DIR / "metadata"
APP_DIR = Path("data/processed/app")

CARGAS_POR_TON = 8.0  # proxy simple usada en el artefacto


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_simulation_base() -> pd.DataFrame:
    path = APP_DIR / "monthly_simulation_base.csv"
    df = pd.read_csv(path)
    if "fecha_mes" in df.columns:
        df["fecha_mes"] = pd.to_datetime(df["fecha_mes"], errors="coerce")
    return df


def load_model_bundle(model_key: str):
    model_key = model_key.lower()

    if model_key not in ["m5", "m6"]:
        raise ValueError("model_key debe ser 'm5' o 'm6'.")

    model_path = MODEL_DIR / f"{model_key}_model.joblib"
    meta_path = META_DIR / f"{model_key}_metadata.json"

    model = joblib.load(model_path)
    meta = load_json(meta_path)
    return model, meta


def load_scenario_bounds():
    return load_json(META_DIR / "scenario_bounds.json")


def get_base_row(df: pd.DataFrame, departamento: str, anio: int, mes: int) -> pd.DataFrame:
    out = df[
        (df["departamento"] == departamento) &
        (df["anio_referencia_y"] == anio) &
        (df["mes_referencia_y"] == mes)
    ].copy()

    if out.empty:
        raise ValueError(
            f"No encontré fila base para departamento={departamento}, año={anio}, mes={mes}"
        )

    return out.head(1).copy()


def predict_scenario(model_key: str, base_row: pd.DataFrame, overrides: dict | None = None) -> dict:
    model, meta = load_model_bundle(model_key)
    features = meta["features"]

    scenario_row = base_row.copy()

    if overrides:
        for col, value in overrides.items():
            if col in scenario_row.columns:
                scenario_row.loc[:, col] = value

    missing = [c for c in features if c not in scenario_row.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas por el modelo {model_key}: {missing}")

    pred = float(model.predict(scenario_row[features])[0])

    return {
        "model_key": model_key,
        "model_name": meta["model_name"],
        "role": meta["role"],
        "prediction": pred,
        "features_used": features,
        "scenario_row": scenario_row.copy()
    }


def compute_insurance_proxy(
    base_prediction: float,
    scenario_prediction: float,
    precio_interno_cop_carga: float,
    area_cosechada_hist: float,
    hectareas_aseguradas: float,
    cobertura_pct: float = 0.7,
    tasa_prima_pct: float = 0.06,
):
    base_prediction = max(float(base_prediction), 0.0)
    scenario_prediction = max(float(scenario_prediction), 0.0)

    precio_interno_cop_carga = float(precio_interno_cop_carga) if pd.notna(precio_interno_cop_carga) else 0.0
    area_cosechada_hist = float(area_cosechada_hist) if pd.notna(area_cosechada_hist) else 0.0
    hectareas_aseguradas = float(hectareas_aseguradas) if pd.notna(hectareas_aseguradas) else 0.0

    perdida_t = max(0.0, base_prediction - scenario_prediction)
    perdida_pct = 0.0 if base_prediction == 0 else perdida_t / base_prediction

    if area_cosechada_hist <= 0:
        factor_area = 1.0
    else:
        factor_area = min(max(hectareas_aseguradas / area_cosechada_hist, 0.0), 1.0)

    perdida_ajustada_t = perdida_t * factor_area

    ingreso_base_proxy = base_prediction * CARGAS_POR_TON * precio_interno_cop_carga
    ingreso_escenario_proxy = scenario_prediction * CARGAS_POR_TON * precio_interno_cop_carga
    valor_expuesto_proxy = max(0.0, ingreso_base_proxy - ingreso_escenario_proxy)
    valor_expuesto_ajustado = valor_expuesto_proxy * factor_area

    cobertura_indicativa = valor_expuesto_ajustado * cobertura_pct
    prima_indicativa = cobertura_indicativa * tasa_prima_pct

    return {
        "base_prediction": base_prediction,
        "scenario_prediction": scenario_prediction,
        "delta_t": scenario_prediction - base_prediction,
        "perdida_proxy_t": perdida_ajustada_t,
        "perdida_proxy_pct": perdida_pct,
        "ingreso_base_proxy_cop": ingreso_base_proxy,
        "ingreso_escenario_proxy_cop": ingreso_escenario_proxy,
        "valor_expuesto_proxy_cop": valor_expuesto_proxy,
        "valor_expuesto_ajustado_cop": valor_expuesto_ajustado,
        "cobertura_indicativa_cop": cobertura_indicativa,
        "prima_indicativa_cop": prima_indicativa,
        "factor_area": factor_area,
    }


def simulate_hybrid_monthly_scenario(
    base_row: pd.DataFrame,
    overrides: dict | None = None,
    hectareas_aseguradas: float | None = None,
    cobertura_pct: float = 0.7,
    tasa_prima_pct: float = 0.06,
):
    """
    Lógica híbrida del artefacto:
    - M6 aporta la estimación base operativa
    - M5 aporta la sensibilidad climática
    - Solo se traslada el efecto adverso de M5 al escenario final
    """

    # Predicciones base
    m6_base = predict_scenario("m6", base_row)
    m5_base = predict_scenario("m5", base_row)

    # Predicción escenario sensible al clima
    m5_scenario = predict_scenario("m5", base_row, overrides=overrides or {})

    # Efecto climático: solo trasladamos deterioro, no mejoras
    delta_climatico_m5 = m5_scenario["prediction"] - m5_base["prediction"]
    delta_adverso = min(0.0, delta_climatico_m5)

    # Producción escenario híbrida
    hybrid_base_prediction = m6_base["prediction"]
    hybrid_scenario_prediction = max(0.0, hybrid_base_prediction + delta_adverso)

    # Valores económicos base
    row = base_row.iloc[0]
    precio = float(row["precio_interno_cop_carga_mean"]) if "precio_interno_cop_carga_mean" in base_row.columns else 0.0
    area_hist = float(row["area_cosechada_departamental_ha"]) if "area_cosechada_departamental_ha" in base_row.columns else 0.0

    if hectareas_aseguradas is None:
        hectareas_aseguradas = area_hist

    insurance = compute_insurance_proxy(
        base_prediction=hybrid_base_prediction,
        scenario_prediction=hybrid_scenario_prediction,
        precio_interno_cop_carga=precio,
        area_cosechada_hist=area_hist,
        hectareas_aseguradas=hectareas_aseguradas,
        cobertura_pct=cobertura_pct,
        tasa_prima_pct=tasa_prima_pct,
    )

    result = {
        "departamento": row.get("departamento"),
        "anio_referencia_y": row.get("anio_referencia_y"),
        "mes_referencia_y": row.get("mes_referencia_y"),
        "m6_base_prediction": m6_base["prediction"],
        "m5_base_prediction": m5_base["prediction"],
        "m5_scenario_prediction": m5_scenario["prediction"],
        "delta_climatico_m5": delta_climatico_m5,
        "delta_adverso_aplicado": delta_adverso,
        "hybrid_base_prediction": hybrid_base_prediction,
        "hybrid_scenario_prediction": hybrid_scenario_prediction,
        "precio_interno_cop_carga_mean": precio,
        "area_cosechada_departamental_ha": area_hist,
        "hectareas_aseguradas": hectareas_aseguradas,
        "cobertura_pct": cobertura_pct,
        "tasa_prima_pct": tasa_prima_pct,
    }

    result.update(insurance)
    return result