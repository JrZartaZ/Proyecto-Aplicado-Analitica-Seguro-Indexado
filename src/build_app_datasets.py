from pathlib import Path
import pandas as pd

BASE_DIR = Path("data/processed")
APP_DIR = BASE_DIR / "app"
APP_DIR.mkdir(parents=True, exist_ok=True)

WEEKLY_FILE = BASE_DIR / "weekly.csv"
MONTHLY_FILE = BASE_DIR / "monthly.csv"
ANNUAL_FILE = BASE_DIR / "annual.csv"

WEEKLY_COLS = [
    "fecha_semana_inicio", "fecha_semana_fin", "anio_referencia_y", "mes_referencia_y",
    "semana_iso", "departamento", "produccion_semanal_proxy_t", "PRECTOTCORR", "T2M",
    "T2M_MAX", "T2M_MIN", "RH2M", "GWETROOT", "ALLSKY_SFC_SW_DWN", "WS2M",
    "lluvia_acum_4s", "lluvia_acum_8s", "anomalia_lluvia_semana_iso", "t2m_max_ma_4s",
    "gwetroot_ma_4s", "gwettop_ma_4s", "dummy_exceso_lluvia_p75",
    "dummy_estres_hidrico_p25", "dummy_temp_max_alta_p75",
    "precio_interno_cop_carga", "precio_externo_exdock_cent_usd_lb",
    "exportaciones_mensual_miles_sacos", "trm_promedio_semana_cop_usd"
]

MONTHLY_COLS = [
    "departamento", "anio_referencia_y", "mes_referencia_y",
    "produccion_mensual_desde_semana_t", "produccion_mensual_proxy_t",
    "produccion_anual_departamental_t", "area_cosechada_departamental_ha",
    "rendimiento_departamental_t_ha", "valor_cosecha_anual_millones",
    "PRECTOTCORR", "IMERG_PRECTOT", "lluvia_acum_4s", "lluvia_acum_8s",
    "T2M_mean", "T2M_MAX_mean", "T2M_MIN_mean", "RH2M_mean", "GWETROOT_mean",
    "ALLSKY_SFC_SW_DWN_mean", "WS2M_mean", "anomalia_lluvia_semana_iso_mean",
    "indice_climatico_base_x_mean", "indice_climatico_ajustado_x_mean",
    "dummy_exceso_lluvia_p75_any", "dummy_estres_hidrico_p25_any",
    "dummy_temp_max_alta_p75_any", "precio_interno_cop_carga_mean",
    "precio_externo_exdock_cent_usd_lb_mean", "exportaciones_mensual_miles_sacos_mean",
    "trm_promedio_semana_cop_usd_mean", "diff_target_mensual"
]

ANNUAL_COLS = [
    "departamento", "anio_referencia_y", "produccion_anual_desde_semana_t",
    "produccion_anual_departamental_t", "area_cosechada_departamental_ha",
    "rendimiento_departamental_t_ha", "valor_cosecha_anual_millones",
    "PRECTOTCORR", "IMERG_PRECTOT", "lluvia_acum_4s", "lluvia_acum_8s",
    "T2M_mean", "T2M_MAX_mean", "T2M_MIN_mean", "RH2M_mean", "GWETROOT_mean",
    "ALLSKY_SFC_SW_DWN_mean", "WS2M_mean", "indice_climatico_base_x_mean",
    "indice_climatico_ajustado_x_mean", "precio_interno_cop_carga_mean",
    "precio_externo_exdock_cent_usd_lb_mean", "exportaciones_mensual_miles_sacos_mean",
    "trm_promedio_semana_cop_usd_mean", "diff_target_anual"
]

def keep_existing(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    existing = [c for c in cols if c in df.columns]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        print(f"[WARN] Columnas no encontradas y omitidas: {missing}")
    return df[existing].copy()

def add_derived_columns():
    weekly = pd.read_csv(WEEKLY_FILE, parse_dates=["fecha_semana_inicio", "fecha_semana_fin"])
    monthly = pd.read_csv(MONTHLY_FILE)
    annual = pd.read_csv(ANNUAL_FILE)

    weekly_app = keep_existing(weekly, WEEKLY_COLS)
    monthly_app = keep_existing(monthly, MONTHLY_COLS)
    annual_app = keep_existing(annual, ANNUAL_COLS)

    # derivados útiles para Dash
    weekly_app["fecha_semana_label"] = weekly_app["fecha_semana_inicio"].dt.strftime("%Y-%m-%d")
    monthly_app["fecha_mes"] = pd.to_datetime(
        monthly_app["anio_referencia_y"].astype(str) + "-" +
        monthly_app["mes_referencia_y"].astype(str).str.zfill(2) + "-01",
        errors="coerce"
    )
    monthly_app["mes_label"] = monthly_app["fecha_mes"].dt.strftime("%Y-%m")
    annual_app["anio_label"] = annual_app["anio_referencia_y"].astype(str)

    weekly_app.to_csv(APP_DIR / "weekly_app.csv", index=False, encoding="utf-8")
    monthly_app.to_csv(APP_DIR / "monthly_app.csv", index=False, encoding="utf-8")
    annual_app.to_csv(APP_DIR / "annual_app.csv", index=False, encoding="utf-8")

    print("[OK] weekly_app.csv", weekly_app.shape)
    print("[OK] monthly_app.csv", monthly_app.shape)
    print("[OK] annual_app.csv", annual_app.shape)

if __name__ == "__main__":
    add_derived_columns()