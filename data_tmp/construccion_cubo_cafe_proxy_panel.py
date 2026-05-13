"""
Construcción del cubo semanal de café v4
---------------------------------------
Entregables:
1) base_proxy_nacional_semanal_cafe_2021_2024_v4.csv
2) base_panel_departamental_semanal_cafe_2021_2024_v4.csv
3) cubo_cafe_semanal_proxy_y_panel_2021_2024_v4.xlsx

Cambio metodológico v4:
- La Y semanal NO usa clima para construirse.
- Producción anual -> mensual usando estacionalidad nacional mensual oficial.
- Producción mensual -> semanal usando proporción de días calendario.
- Las variables climáticas, incluido el índice climático, quedan como X explicativas.

Requisitos:
pip install pandas openpyxl numpy requests
"""

from __future__ import annotations

from calendar import monthrange
from datetime import timedelta
from typing import Callable

import numpy as np
import pandas as pd

INPUT_XLSX = "Variables_cafe_seguro_agricola.xlsx"
OUT_PROXY_CSV = "base_proxy_nacional_semanal_cafe_2021_2024_v4.csv"
OUT_PANEL_CSV = "base_panel_departamental_semanal_cafe_2021_2024_v4.csv"
OUT_XLSX = "cubo_cafe_semanal_proxy_y_panel_2021_2024_v4.xlsx"

NASA_COLS = [
    "PRECTOTCORR",
    "IMERG_PRECTOT",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "QV2M",
    "GWETTOP",
    "GWETROOT",
    "ALLSKY_SFC_SW_DWN",
    "WS2M",
]


def normalize_depto(value: object) -> str:
    return str(value).strip().upper()


def safe_minmax(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    min_val = series.min()
    max_val = series.max()
    if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
        return pd.Series(np.nan, index=series.index)
    return (series - min_val) / (max_val - min_val)


def add_climate_scores(df: pd.DataFrame, group_col: str | None = None) -> pd.DataFrame:
    """Agrega scores climáticos e índice climático como X, nunca como parte de la Y."""

    def _one_group(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("fecha_semana_fin").copy()

        g["score_humedad"] = (
            safe_minmax(g["GWETROOT"]) + safe_minmax(g["GWETTOP"])
        ) / 2

        rain_cap = g["PRECTOTCORR"].clip(upper=g["PRECTOTCORR"].quantile(0.90))
        g["score_precipitacion"] = safe_minmax(rain_cap)

        ref_temp = g["T2M"].median()
        max_dev = (g["T2M"] - ref_temp).abs().max()
        if pd.isna(max_dev) or max_dev == 0:
            g["score_temperatura"] = np.nan
        else:
            g["score_temperatura"] = 1 - ((g["T2M"] - ref_temp).abs() / max_dev)

        g["score_radiacion"] = safe_minmax(g["ALLSKY_SFC_SW_DWN"])

        g["indice_climatico_base_x"] = (
            0.35 * g["score_humedad"]
            + 0.25 * g["score_precipitacion"]
            + 0.25 * g["score_temperatura"]
            + 0.15 * g["score_radiacion"]
        )
        g["indice_climatico_ajustado_x"] = 0.70 + 0.30 * g["indice_climatico_base_x"]

        g["lluvia_acum_4s"] = g["PRECTOTCORR"].rolling(4, min_periods=1).sum()
        g["lluvia_acum_8s"] = g["PRECTOTCORR"].rolling(8, min_periods=1).sum()
        g["t2m_max_ma_4s"] = g["T2M_MAX"].rolling(4, min_periods=1).mean()
        g["gwetroot_ma_4s"] = g["GWETROOT"].rolling(4, min_periods=1).mean()
        g["gwettop_ma_4s"] = g["GWETTOP"].rolling(4, min_periods=1).mean()

        g["semana_iso"] = g["fecha_semana_fin"].dt.isocalendar().week.astype(int)
        g["anomalia_lluvia_semana_iso"] = g["PRECTOTCORR"] - g.groupby("semana_iso")[
            "PRECTOTCORR"
        ].transform("mean")

        g["dummy_exceso_lluvia_p75"] = (
            g["lluvia_acum_4s"] >= g["lluvia_acum_4s"].quantile(0.75)
        ).astype(int)
        g["dummy_estres_hidrico_p25"] = (
            g["gwetroot_ma_4s"] <= g["gwetroot_ma_4s"].quantile(0.25)
        ).astype(int)
        g["dummy_temp_max_alta_p75"] = (
            g["t2m_max_ma_4s"] >= g["t2m_max_ma_4s"].quantile(0.75)
        ).astype(int)
        g["dummy_indice_climatico_bajo_p25"] = (
            g["indice_climatico_base_x"] <= g["indice_climatico_base_x"].quantile(0.25)
        ).astype(int)
        g["dummy_indice_climatico_alto_p75"] = (
            g["indice_climatico_base_x"] >= g["indice_climatico_base_x"].quantile(0.75)
        ).astype(int)

        return g

    if group_col:
        return df.groupby(group_col, group_keys=False).apply(_one_group)
    return _one_group(df)


def calendar_week_value(
    week_end: pd.Timestamp,
    monthly_value_func: Callable[[int, int], float],
) -> tuple[float, int]:
    """Suma el aporte diario de cada mes dentro de una semana calendario."""
    week_start = week_end - timedelta(days=6)
    total = 0.0
    days_used = 0

    for day in pd.date_range(week_start, week_end, freq="D"):
        if pd.Timestamp("2021-01-01") <= day <= pd.Timestamp("2024-12-31"):
            monthly_value = monthly_value_func(day.year, day.month)
            total += monthly_value / monthrange(day.year, day.month)[1]
            days_used += 1

    return total, days_used


def reference_year_month(week_end: pd.Timestamp) -> tuple[int, int]:
    """Año/mes con más días dentro de la semana, solo para columnas descriptivas."""
    week_start = week_end - timedelta(days=6)
    days = [
        d
        for d in pd.date_range(week_start, week_end, freq="D")
        if pd.Timestamp("2021-01-01") <= d <= pd.Timestamp("2024-12-31")
    ]
    if not days:
        return week_end.year, week_end.month
    ref = pd.Series([(d.year, d.month) for d in days]).mode().iloc[0]
    return int(ref[0]), int(ref[1])


def add_economic_transforms(df: pd.DataFrame, group_col: str | None = None) -> pd.DataFrame:
    df = df.sort_values(([group_col] if group_col else []) + ["fecha_semana_fin"]).copy()
    variables = [
        "precio_interno_cop_carga",
        "precio_externo_exdock_cent_usd_lb",
        "exportaciones_mensual_miles_sacos",
        "trm_viernes_cop_usd",
    ]
    for var in variables:
        if var not in df.columns:
            df[var] = np.nan
        if group_col:
            group = df.groupby(group_col)[var]
            df[f"{var}_lag_1s"] = group.shift(1)
            df[f"{var}_lag_4s"] = group.shift(4)
            df[f"{var}_ma_4s"] = group.transform(lambda s: s.rolling(4, min_periods=1).mean())
        else:
            df[f"{var}_lag_1s"] = df[var].shift(1)
            df[f"{var}_lag_4s"] = df[var].shift(4)
            df[f"{var}_ma_4s"] = df[var].rolling(4, min_periods=1).mean()
        df[f"{var}_var_4s"] = df[var] / df[f"{var}_lag_4s"] - 1

    df["dummy_precio_interno_alto_p75"] = (
        df["precio_interno_cop_carga"] >= df["precio_interno_cop_carga"].quantile(0.75)
    ).astype(int)
    df["dummy_precio_externo_alto_p75"] = (
        df["precio_externo_exdock_cent_usd_lb"]
        >= df["precio_externo_exdock_cent_usd_lb"].quantile(0.75)
    ).astype(int)
    df["dummy_exportaciones_altas_p75"] = (
        df["exportaciones_mensual_miles_sacos"]
        >= df["exportaciones_mensual_miles_sacos"].quantile(0.75)
    ).astype(int)
    df["dummy_trm_lag4_alta_p75"] = (
        df["trm_viernes_cop_usd_lag_4s"]
        >= df["trm_viernes_cop_usd_lag_4s"].quantile(0.75)
    ).astype(int)
    df["dummy_devaluacion_4s_p75"] = (
        df["trm_viernes_cop_usd_var_4s"]
        >= df["trm_viernes_cop_usd_var_4s"].quantile(0.75)
    ).astype(int)
    return df


def load_trm_weekly(week_ends: pd.DatetimeIndex) -> pd.DataFrame:
    """Descarga TRM diaria desde Datos Abiertos si hay internet y la alinea a semanas.

    Si no hay conexión o cambia la estructura del dataset, devuelve columnas vacías.
    """
    try:
        url = "https://www.datos.gov.co/resource/32sa-8pi3.csv?$limit=50000"
        raw = pd.read_csv(url)
        date_col = next(c for c in raw.columns if "vigencia" in c.lower() or "fecha" in c.lower())
        val_col = next(c for c in raw.columns if "valor" in c.lower() or "trm" in c.lower())
        raw["fecha"] = pd.to_datetime(raw[date_col])
        raw["trm"] = pd.to_numeric(raw[val_col], errors="coerce")
        raw = raw.sort_values("fecha").dropna(subset=["fecha", "trm"])
        rows = []
        for week_end in week_ends:
            week_start = week_end - timedelta(days=6)
            week = raw[(raw["fecha"] >= week_start) & (raw["fecha"] <= week_end)]
            friday = week[week["fecha"].dt.weekday == 4]
            if not friday.empty:
                trm_viernes = friday.iloc[-1]["trm"]
            elif not week.empty:
                trm_viernes = week.iloc[-1]["trm"]
            else:
                prev = raw[raw["fecha"] <= week_end]
                trm_viernes = prev.iloc[-1]["trm"] if not prev.empty else np.nan
            rows.append(
                {
                    "fecha_semana_fin": week_end,
                    "trm_viernes_cop_usd": trm_viernes,
                    "trm_promedio_semana_cop_usd": week["trm"].mean() if not week.empty else np.nan,
                }
            )
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame(
            {
                "fecha_semana_fin": week_ends,
                "trm_viernes_cop_usd": np.nan,
                "trm_promedio_semana_cop_usd": np.nan,
            }
        )


def main() -> None:
    # ---------- Cargar hojas ----------
    prod = pd.read_excel(INPUT_XLSX, sheet_name="Produccion", header=6)
    prod = prod[prod["Año"].between(2021, 2024)].copy()
    prod["Departamento"] = prod["Departamento"].map(normalize_depto)

    prod_nat = pd.read_excel(INPUT_XLSX, sheet_name="Produccion Nacional", header=3)
    prod_nat["Mes"] = pd.to_datetime(prod_nat["Mes"])
    prod_nat = prod_nat[prod_nat["Mes"].dt.year.between(2021, 2024)].copy()
    prod_nat["anio"] = prod_nat["Mes"].dt.year
    prod_nat["mes"] = prod_nat["Mes"].dt.month
    prod_nat["peso_mensual_prod_nacional"] = prod_nat["Producción"] / prod_nat.groupby("anio")["Producción"].transform("sum")
    month_weight = prod_nat.set_index(["anio", "mes"])["peso_mensual_prod_nacional"].to_dict()
    prod_nat_map = prod_nat.set_index(["anio", "mes"])["Producción"].to_dict()

    nasa_cons = pd.read_excel(INPUT_XLSX, sheet_name="VARIABLES_NASA_CONSOLIDADO")
    nasa_cons["fecha_semana_fin"] = pd.to_datetime(nasa_cons["date"])

    nasa_dept = pd.read_excel(INPUT_XLSX, sheet_name="VARIABLES_NASA_DEPARTAMENTAL")
    nasa_dept["fecha_semana_fin"] = pd.to_datetime(nasa_dept["date"])
    nasa_dept["DEPARTAMENTO"] = nasa_dept["DEPARTAMENTO"].map(normalize_depto)

    precio_int = pd.read_excel(INPUT_XLSX, sheet_name="precio_interno")
    precio_int["fecha_semana_fin"] = pd.to_datetime(precio_int["date"])
    precio_int = precio_int[["fecha_semana_fin", "precio_interno"]].rename(columns={"precio_interno": "precio_interno_cop_carga"})

    precio_ext = pd.read_excel(
        INPUT_XLSX,
        sheet_name="Precio Ex_Dock",
        header=None,
        skiprows=3,
        names=["fecha", "precio_externo_exdock_cent_usd_lb"],
    )
    # En el Excel las fechas vienen como 1921-1924; se corrigen a 2021-2024.
    precio_ext["fecha"] = pd.to_datetime(precio_ext["fecha"]) + pd.DateOffset(years=100)
    precio_ext["anio"] = precio_ext["fecha"].dt.year
    precio_ext["mes"] = precio_ext["fecha"].dt.month
    precio_ext_map = precio_ext.set_index(["anio", "mes"])["precio_externo_exdock_cent_usd_lb"].to_dict()

    export = pd.read_excel(INPUT_XLSX, sheet_name="Exportaciones", header=4)
    export["MES"] = pd.to_datetime(export["MES"])
    export["anio"] = export["MES"].dt.year
    export["mes"] = export["MES"].dt.month
    export_map = export.set_index(["anio", "mes"])["Total Exportaciones"].to_dict()

    valor = pd.read_excel(INPUT_XLSX, sheet_name="Valor Cosecha", header=3)
    valor_map = valor.set_index("Año Calendario")["Valor de la cosecha"].to_dict()

    # ---------- Producción anual ----------
    prod_dept = prod.set_index(["Departamento", "Año"])
    departamentos = sorted(prod["Departamento"].unique())

    annual_proxy = prod.groupby("Año").agg(
        produccion_anual_proxy_5mun_t=("Producción (t)", "sum"),
        area_cosechada_proxy_ha=("Área cosechada (ha)", "sum"),
    )
    annual_proxy["rendimiento_proxy_t_ha"] = (
        annual_proxy["produccion_anual_proxy_5mun_t"] / annual_proxy["area_cosechada_proxy_ha"]
    )
    annual_proxy_map = annual_proxy.to_dict("index")

    week_ends = pd.date_range("2021-01-03", "2025-01-05", freq="W-SUN")
    trm_weekly = load_trm_weekly(week_ends)

    def monthly_proxy_value(year: int, month: int) -> float:
        return annual_proxy_map[year]["produccion_anual_proxy_5mun_t"] * month_weight[(year, month)]

    def monthly_dept_value(depto: str, year: int, month: int) -> float:
        return prod_dept.loc[(depto, year), "Producción (t)"] * month_weight[(year, month)]

    # ---------- Base proxy nacional ----------
    proxy_rows = []
    for week_end in week_ends:
        y_week, days_used = calendar_week_value(week_end, monthly_proxy_value)
        ref_year, ref_month = reference_year_month(week_end)
        annual_info = annual_proxy_map[ref_year]
        proxy_rows.append(
            {
                "fecha_semana_inicio": week_end - timedelta(days=6),
                "fecha_semana_fin": week_end,
                "anio_semana_fin": week_end.year,
                "anio_referencia_y": ref_year,
                "mes_referencia_y": ref_month,
                "semana_iso": week_end.isocalendar().week,
                "dias_productivos_periodo_2021_2024": days_used,
                "nivel": "PROXY_NACIONAL_5_DEPARTAMENTOS",
                "produccion_semanal_proxy_t": y_week,
                "produccion_anual_proxy_5mun_t": annual_info["produccion_anual_proxy_5mun_t"],
                "area_cosechada_proxy_ha": annual_info["area_cosechada_proxy_ha"],
                "rendimiento_proxy_t_ha": annual_info["rendimiento_proxy_t_ha"],
                "produccion_mensual_proxy_t": monthly_proxy_value(ref_year, ref_month),
                "peso_mensual_prod_nacional": month_weight[(ref_year, ref_month)],
                "produccion_nacional_mensual_oficial_miles_sacos": prod_nat_map.get((ref_year, ref_month)),
                "exportaciones_mensual_miles_sacos": export_map.get((ref_year, ref_month)),
                "precio_externo_exdock_cent_usd_lb": precio_ext_map.get((ref_year, ref_month)),
                "valor_cosecha_anual_millones": valor_map.get(ref_year),
                "fuente_y_semanal": "mensualizacion_estacionalidad_nacional_y_semanalizacion_calendario_dias",
                "tipo_target": "proxy_operacional_no_observada",
            }
        )
    base_proxy = pd.DataFrame(proxy_rows)
    base_proxy = base_proxy.merge(nasa_cons[["fecha_semana_fin"] + NASA_COLS], on="fecha_semana_fin", how="left")
    base_proxy = add_climate_scores(base_proxy)
    base_proxy = base_proxy.merge(precio_int, on="fecha_semana_fin", how="left")
    base_proxy = base_proxy.merge(trm_weekly, on="fecha_semana_fin", how="left")
    base_proxy["valor_cosecha_semanal_proxy_millones"] = (
        base_proxy["valor_cosecha_anual_millones"]
        * base_proxy["produccion_semanal_proxy_t"]
        / base_proxy["produccion_anual_proxy_5mun_t"]
    )
    base_proxy = add_economic_transforms(base_proxy)

    # ---------- Base panel departamental ----------
    panel_rows = []
    for depto in departamentos:
        for week_end in week_ends:
            y_week, days_used = calendar_week_value(week_end, lambda y, m: monthly_dept_value(depto, y, m))
            ref_year, ref_month = reference_year_month(week_end)
            annual_dept = prod_dept.loc[(depto, ref_year)]
            panel_rows.append(
                {
                    "fecha_semana_inicio": week_end - timedelta(days=6),
                    "fecha_semana_fin": week_end,
                    "anio_semana_fin": week_end.year,
                    "anio_referencia_y": ref_year,
                    "mes_referencia_y": ref_month,
                    "semana_iso": week_end.isocalendar().week,
                    "dias_productivos_periodo_2021_2024": days_used,
                    "departamento": depto,
                    "nivel": "PANEL_DEPARTAMENTAL",
                    "produccion_semanal_proxy_t": y_week,
                    "produccion_anual_departamental_t": annual_dept["Producción (t)"],
                    "area_cosechada_departamental_ha": annual_dept["Área cosechada (ha)"],
                    "rendimiento_departamental_t_ha": annual_dept["Rendimiento (t/ha)"],
                    "produccion_mensual_proxy_t": monthly_dept_value(depto, ref_year, ref_month),
                    "peso_mensual_prod_nacional": month_weight[(ref_year, ref_month)],
                    "produccion_nacional_mensual_oficial_miles_sacos": prod_nat_map.get((ref_year, ref_month)),
                    "exportaciones_mensual_miles_sacos": export_map.get((ref_year, ref_month)),
                    "precio_externo_exdock_cent_usd_lb": precio_ext_map.get((ref_year, ref_month)),
                    "valor_cosecha_anual_millones": valor_map.get(ref_year),
                    "fuente_y_semanal": "mensualizacion_estacionalidad_nacional_y_semanalizacion_calendario_dias",
                    "tipo_target": "proxy_operacional_no_observada",
                }
            )
    base_panel = pd.DataFrame(panel_rows)
    base_panel = base_panel.merge(
        nasa_dept[["fecha_semana_fin", "DEPARTAMENTO"] + NASA_COLS],
        left_on=["fecha_semana_fin", "departamento"],
        right_on=["fecha_semana_fin", "DEPARTAMENTO"],
        how="left",
    ).drop(columns=["DEPARTAMENTO"])
    base_panel = add_climate_scores(base_panel, "departamento")
    base_panel = base_panel.merge(precio_int, on="fecha_semana_fin", how="left")
    base_panel = base_panel.merge(trm_weekly, on="fecha_semana_fin", how="left")
    base_panel["valor_cosecha_semanal_proxy_millones"] = (
        base_panel["valor_cosecha_anual_millones"]
        * base_panel["produccion_semanal_proxy_t"]
        / base_panel["produccion_anual_departamental_t"]
    )
    base_panel = add_economic_transforms(base_panel, "departamento")

    # ---------- Guardar ----------
    base_proxy.to_csv(OUT_PROXY_CSV, index=False, encoding="utf-8-sig")
    base_panel.to_csv(OUT_PANEL_CSV, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_XLSX) as writer:
        base_proxy.to_excel(writer, sheet_name="base_proxy_nacional", index=False)
        base_panel.to_excel(writer, sheet_name="base_panel_deptal", index=False)

    print(f"Base proxy: {base_proxy.shape}")
    print(f"Base panel: {base_panel.shape}")
    print("Clima vacío proxy:", base_proxy[NASA_COLS + ["indice_climatico_base_x"]].isna().sum().to_dict())
    print("Clima vacío panel:", base_panel[NASA_COLS + ["indice_climatico_base_x"]].isna().sum().to_dict())


if __name__ == "__main__":
    main()
