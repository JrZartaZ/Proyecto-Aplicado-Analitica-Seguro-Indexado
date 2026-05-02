"""
Construcción del cubo semanal de café para seguro agrícola indexado
===================================================================

Genera dos bases:
1) Base proxy nacional semanal.
2) Base panel departamental semanal.

Cambio metodológico clave:
- La Y semanal NO usa variables climáticas para construirse.
- La producción anual se mensualiza usando la estacionalidad mensual nacional observada.
- La producción mensual proxy se semanaliza usando pesos de calendario: proporción de días de cada semana dentro del mes.
- Las variables climáticas quedan disponibles como X explicativas.
- El índice climático se calcula como X derivada, no como insumo de la Y.

Requisitos:
    pip install pandas numpy openpyxl requests

Uso:
    python construccion_cubo_cafe_proxy_panel.py

Entrada esperada en la misma carpeta:
    Variables_cafe_seguro_agricola.xlsx

Salidas:
    cubo_cafe_semanal_proxy_y_panel_2021_2024.xlsx
    base_proxy_nacional_semanal_cafe_2021_2024.csv
    base_panel_departamental_semanal_cafe_2021_2024.csv
"""

import calendar
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

INPUT_XLSX = Path("Variables_cafe_seguro_agricola.xlsx")
OUTPUT_XLSX = Path("cubo_cafe_semanal_proxy_y_panel_2021_2024.xlsx")
OUTPUT_PROXY_CSV = Path("base_proxy_nacional_semanal_cafe_2021_2024.csv")
OUTPUT_PANEL_CSV = Path("base_panel_departamental_semanal_cafe_2021_2024.csv")

PERIODO_INICIO = pd.Timestamp("2021-01-01")
PERIODO_FIN = pd.Timestamp("2024-12-31")

NASA_COLS = [
    "PRECTOTCORR", "IMERG_PRECTOT", "T2M", "T2M_MAX", "T2M_MIN",
    "RH2M", "QV2M", "GWETTOP", "GWETROOT", "ALLSKY_SFC_SW_DWN", "WS2M"
]


def excel_date_fix(x):
    """Convierte fechas de Excel y corrige años 1921-1924 usados como 2021-2024."""
    d = pd.to_datetime(x, errors="coerce")
    if pd.isna(d):
        return pd.NaT
    if d.year < 2000:
        d = d + pd.DateOffset(years=100)
    return d.normalize()


def read_produccion(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Produccion", header=6)
    df = df[df["Año"].between(2021, 2024)].copy()
    df["DEPARTAMENTO_NASA"] = df["Departamento"].astype(str).str.upper()
    df["departamento"] = df["Departamento"].astype(str).str.title()
    return df.rename(columns={
        "Año": "anio",
        "Área sembrada (ha)": "area_sembrada_ha",
        "Área cosechada (ha)": "area_cosechada_ha",
        "Producción (t)": "produccion_anual_t",
        "Rendimiento (t/ha)": "rendimiento_t_ha",
    })


def read_monthly_series(path: Path, sheet_name: str, header_row: int, date_col: str, value_col: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
    df = df[[date_col, value_col]].dropna().copy()
    df[date_col] = df[date_col].apply(excel_date_fix)
    df = df[(df[date_col] >= PERIODO_INICIO) & (df[date_col] <= PERIODO_FIN)].copy()
    df["anio"] = df[date_col].dt.year
    df["mes"] = df[date_col].dt.month
    return df.rename(columns={date_col: "fecha_mes", value_col: "valor"})


def read_nasa(path: Path, sheet_name: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name)
    df["date"] = df["date"].apply(excel_date_fix)
    df = df.rename(columns={"date": "fecha_semana_fin", "DEPARTAMENTO": "departamento"})
    df["departamento"] = df["departamento"].astype(str).str.upper()
    df = df[(df["fecha_semana_fin"] >= PERIODO_INICIO) & (df["fecha_semana_fin"] <= pd.Timestamp("2025-01-05"))].copy()
    for col in NASA_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def build_week_ends() -> list[pd.Timestamp]:
    """Semanas ISO aproximadas usando fecha de cierre domingo, incluyendo la semana que contiene 2024-12-31."""
    start = PERIODO_INICIO.date()
    end = PERIODO_FIN.date()
    first_end = start + timedelta(days=(6 - start.weekday()) % 7)
    last_end = end + timedelta(days=(6 - end.weekday()) % 7)
    out = []
    d = first_end
    while d <= last_end:
        out.append(pd.Timestamp(d))
        d += timedelta(days=7)
    return out


def month_overlap_days(week_end: pd.Timestamp, year: int, month: int) -> int:
    week_end_date = week_end.date()
    week_start = week_end_date - timedelta(days=6)
    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    a = max(week_start, month_start)
    b = min(week_end_date, month_end)
    return max(0, (b - a).days + 1)


def week_month_components(week_end: pd.Timestamp):
    week_start = (week_end - pd.Timedelta(days=6)).date()
    week_end_date = week_end.date()
    y, m = week_start.year, week_start.month
    components = []
    while (y, m) <= (week_end_date.year, week_end_date.month):
        if 2021 <= y <= 2024:
            days = month_overlap_days(week_end, y, m)
            if days > 0:
                components.append({"anio": y, "mes": m, "dias": days})
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1
    return components


def compute_climate_index(df: pd.DataFrame, group_cols=None) -> pd.DataFrame:
    """Calcula índice climático como X derivada. No participa en la construcción de Y."""
    if group_cols is None:
        group_cols = []
    df = df.copy()

    def _calc(g):
        g = g.copy()
        p90 = g["PRECTOTCORR"].quantile(0.90)
        g["_prect_cap"] = g["PRECTOTCORR"].clip(upper=p90)

        def mm(x):
            rng = x.max() - x.min()
            if pd.isna(rng) or rng == 0:
                return pd.Series(0.5, index=x.index)
            return (x - x.min()) / rng

        g["score_humedad"] = (mm(g["GWETROOT"]) + mm(g["GWETTOP"])) / 2
        g["score_precipitacion"] = mm(g["_prect_cap"])
        med = g["T2M"].median()
        max_abs = (g["T2M"] - med).abs().max()
        g["score_temperatura"] = 1 - (g["T2M"] - med).abs() / max_abs if max_abs != 0 else 0.5
        g["score_radiacion"] = mm(g["ALLSKY_SFC_SW_DWN"])
        g["indice_climatico_base_x"] = (
            0.35 * g["score_humedad"]
            + 0.25 * g["score_precipitacion"]
            + 0.25 * g["score_temperatura"]
            + 0.15 * g["score_radiacion"]
        )
        g["indice_climatico_ajustado_x"] = 0.70 + 0.30 * g["indice_climatico_base_x"]
        return g.drop(columns=["_prect_cap"], errors="ignore")

    if group_cols:
        return df.groupby(group_cols, group_keys=False).apply(_calc)
    return _calc(df)


def fetch_trm_daily(start="2021-01-01", end="2025-01-05") -> pd.DataFrame:
    """
    Descarga TRM oficial desde Datos Abiertos Colombia.
    Dataset: https://www.datos.gov.co/resource/32sa-8pi3.json
    Si no hay internet, retorna vacío y la base queda con columnas TRM en blanco.
    """
    url = "https://www.datos.gov.co/resource/32sa-8pi3.json"
    params = {
        "$limit": 5000,
        "$select": "valor,vigenciadesde,vigenciahasta",
        "$where": f"vigenciadesde between '{start}T00:00:00' and '{end}T23:59:59'",
        "$order": "vigenciadesde ASC",
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        trm = pd.DataFrame(data)
        trm["fecha"] = pd.to_datetime(trm["vigenciadesde"]).dt.date
        trm["trm_cop_usd"] = pd.to_numeric(trm["valor"], errors="coerce")
        return trm[["fecha", "trm_cop_usd"]].dropna().sort_values("fecha")
    except Exception as exc:
        print(f"No fue posible descargar TRM. Se dejan columnas vacías. Detalle: {exc}")
        return pd.DataFrame(columns=["fecha", "trm_cop_usd"])


def build_weekly_trm(week_ends: list[pd.Timestamp]) -> pd.DataFrame:
    trm = fetch_trm_daily()
    rows = []
    if trm.empty:
        return pd.DataFrame({
            "fecha_semana_fin": week_ends,
            "trm_viernes_cop_usd": np.nan,
            "trm_promedio_semana_cop_usd": np.nan,
        })
    for week_end in week_ends:
        week_start = (week_end - pd.Timedelta(days=6)).date()
        friday = (week_end - pd.Timedelta(days=2)).date()
        week = trm[(trm["fecha"] >= week_start) & (trm["fecha"] <= week_end.date())]
        available_until_friday = trm[trm["fecha"] <= friday]
        trm_friday = available_until_friday.iloc[-1]["trm_cop_usd"] if not available_until_friday.empty else np.nan
        rows.append({
            "fecha_semana_fin": week_end,
            "trm_viernes_cop_usd": trm_friday,
            "trm_promedio_semana_cop_usd": week["trm_cop_usd"].mean() if not week.empty else np.nan,
        })
    return pd.DataFrame(rows)


def add_features(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    df = df.sort_values(group_cols + ["fecha_semana_fin"]).copy()
    transform_cols = [
        "produccion_semanal_proxy_t", "precio_interno_cop_carga", "precio_externo_exdock_cent_usd_lb",
        "exportaciones_mensual_miles_sacos", "trm_viernes_cop_usd", "PRECTOTCORR", "T2M_MAX",
        "GWETTOP", "GWETROOT", "indice_climatico_base_x", "indice_climatico_ajustado_x"
    ]
    for col in transform_cols:
        if col not in df.columns:
            continue
        g = df.groupby(group_cols)[col] if group_cols else df[col]
        if group_cols:
            df[f"{col}_lag_1s"] = g.shift(1)
            df[f"{col}_lag_4s"] = g.shift(4)
            df[f"{col}_ma_4s"] = g.transform(lambda x: x.rolling(4, min_periods=1).mean())
            df[f"{col}_var_4s"] = g.pct_change(4)
        else:
            df[f"{col}_lag_1s"] = df[col].shift(1)
            df[f"{col}_lag_4s"] = df[col].shift(4)
            df[f"{col}_ma_4s"] = df[col].rolling(4, min_periods=1).mean()
            df[f"{col}_var_4s"] = df[col].pct_change(4)
    if group_cols:
        df["lluvia_acum_4s"] = df.groupby(group_cols)["PRECTOTCORR"].transform(lambda x: x.rolling(4, min_periods=1).sum())
        df["lluvia_acum_8s"] = df.groupby(group_cols)["PRECTOTCORR"].transform(lambda x: x.rolling(8, min_periods=1).sum())
        mean_iso = df.groupby(group_cols + ["semana_iso"])["PRECTOTCORR"].transform("mean")
    else:
        df["lluvia_acum_4s"] = df["PRECTOTCORR"].rolling(4, min_periods=1).sum()
        df["lluvia_acum_8s"] = df["PRECTOTCORR"].rolling(8, min_periods=1).sum()
        mean_iso = df.groupby("semana_iso")["PRECTOTCORR"].transform("mean")
    df["anomalia_lluvia_semana_iso"] = df["PRECTOTCORR"] - mean_iso

    def add_dummy(col, name, q, side):
        if group_cols:
            th = df.groupby(group_cols)[col].transform(lambda x: x.quantile(q))
        else:
            th = df[col].quantile(q)
        df[name] = np.where(df[col].isna(), np.nan, np.where(df[col] >= th, 1, 0) if side == "high" else np.where(df[col] <= th, 1, 0))

    add_dummy("PRECTOTCORR", "dummy_exceso_lluvia_p75", 0.75, "high")
    add_dummy("GWETROOT", "dummy_estres_hidrico_p25", 0.25, "low")
    add_dummy("T2M_MAX", "dummy_temp_max_alta_p75", 0.75, "high")
    add_dummy("precio_interno_cop_carga", "dummy_precio_interno_alto_p75", 0.75, "high")
    add_dummy("exportaciones_mensual_miles_sacos", "dummy_exportaciones_altas_p75", 0.75, "high")
    add_dummy("indice_climatico_base_x", "dummy_indice_climatico_bajo_p25", 0.25, "low")
    add_dummy("indice_climatico_base_x", "dummy_indice_climatico_alto_p75", 0.75, "high")
    if "trm_viernes_cop_usd" in df.columns and df["trm_viernes_cop_usd"].notna().any():
        add_dummy("trm_viernes_cop_usd", "dummy_trm_alta_p75", 0.75, "high")
        add_dummy("trm_viernes_cop_usd_var_4s", "dummy_devaluacion_4s_p75", 0.75, "high")
    return df


def main():
    if not INPUT_XLSX.exists():
        raise FileNotFoundError(f"No encuentro {INPUT_XLSX}. Pon el Excel en la misma carpeta del script.")

    produccion = read_produccion(INPUT_XLSX)
    prod_nacional = read_monthly_series(INPUT_XLSX, "Produccion Nacional", 3, "Mes", "Producción")
    precio_ext = read_monthly_series(INPUT_XLSX, "Precio Ex_Dock", 2, "*Resultado de la ponderación de los precios de los 6 días anteriores", "Unnamed: 1")
    exportaciones = read_monthly_series(INPUT_XLSX, "Exportaciones", 4, "MES", "Total Exportaciones")
    valor_cosecha = pd.read_excel(INPUT_XLSX, sheet_name="Valor Cosecha", header=3).rename(columns={"Año Calendario": "anio", "Valor de la cosecha": "valor_cosecha_anual_millones_cop"})
    valor_cosecha = valor_cosecha[valor_cosecha["anio"].between(2021, 2024)]

    precio_int = pd.read_excel(INPUT_XLSX, sheet_name="precio_interno")
    precio_int["date"] = precio_int["date"].apply(excel_date_fix)
    precio_int = precio_int.rename(columns={"date": "fecha_semana_fin", "precio_interno": "precio_interno_cop_carga"})

    nasa_nat = compute_climate_index(read_nasa(INPUT_XLSX, "VARIABLES_NASA_CONSOLIDADO"))
    nasa_dept = compute_climate_index(read_nasa(INPUT_XLSX, "VARIABLES_NASA_DEPARTAMENTAL"), ["departamento"])

    prod_nacional["peso_mensual"] = prod_nacional["valor"] / prod_nacional.groupby("anio")["valor"].transform("sum")
    peso_mensual = prod_nacional.set_index(["anio", "mes"])["peso_mensual"].to_dict()
    prod_nacional_val = prod_nacional.set_index(["anio", "mes"])["valor"].to_dict()
    precio_ext_val = precio_ext.set_index(["anio", "mes"])["valor"].to_dict()
    export_val = exportaciones.set_index(["anio", "mes"])["valor"].to_dict()
    valor_cosecha_val = valor_cosecha.set_index("anio")["valor_cosecha_anual_millones_cop"].to_dict()

    annual_proxy = produccion.groupby("anio")["produccion_anual_t"].sum().to_dict()
    area_cosechada_proxy = produccion.groupby("anio")["area_cosechada_ha"].sum().to_dict()
    prod_dept = produccion.set_index(["DEPARTAMENTO_NASA", "anio"])

    week_ends = build_week_ends()
    trm_week = build_weekly_trm(week_ends)

    def weighted_month_value(components, values):
        num = 0
        den = 0
        for c in components:
            v = values.get((c["anio"], c["mes"]))
            if pd.notna(v):
                num += v * c["dias"]
                den += c["dias"]
        return num / den if den else np.nan

    def weekly_y(components, monthly_func):
        total = 0
        for c in components:
            days_month = calendar.monthrange(c["anio"], c["mes"])[1]
            total += monthly_func(c["anio"], c["mes"]) / days_month * c["dias"]
        return total

    proxy_rows = []
    panel_rows = []
    for wend in week_ends:
        comps = week_month_components(wend)
        main = max(comps, key=lambda x: x["dias"])
        iso = wend.isocalendar()
        base = {
            "fecha_semana_inicio": wend - pd.Timedelta(days=6),
            "fecha_semana_fin": wend,
            "anio_iso": iso.year,
            "semana_iso": iso.week,
            "anio_produccion_principal": main["anio"],
            "mes_produccion_principal": main["mes"],
            "dias_mes_principal_en_semana": main["dias"],
            "dias_asignados_semana": sum(c["dias"] for c in comps),
            "detalle_meses_asignados": ";".join([f"{c['anio']}-{c['mes']:02d}:{c['dias']}d" for c in comps]),
            "produccion_nacional_mensual_oficial_miles_sacos": weighted_month_value(comps, prod_nacional_val),
            "peso_mensual_prod_nacional_principal": peso_mensual.get((main["anio"], main["mes"]), np.nan),
            "precio_externo_exdock_cent_usd_lb": weighted_month_value(comps, precio_ext_val),
            "exportaciones_mensual_miles_sacos": weighted_month_value(comps, export_val),
            "valor_cosecha_anual_millones_cop": valor_cosecha_val.get(main["anio"], np.nan),
            "metodo_y": "mensualizacion_nacional_y_semanalizacion_calendario",
            "tipo_target": "proxy_operacional_no_observada",
        }
        proxy_y = weekly_y(comps, lambda y, m: annual_proxy[y] * peso_mensual[(y, m)])
        proxy_rows.append({
            **base,
            "produccion_semanal_proxy_t": proxy_y,
            "produccion_anual_proxy_5mun_t": annual_proxy[main["anio"]],
            "area_cosechada_proxy_5mun_ha": area_cosechada_proxy[main["anio"]],
            "rendimiento_proxy_t_ha": annual_proxy[main["anio"]] / area_cosechada_proxy[main["anio"]],
            "produccion_mensual_proxy_principal_t": annual_proxy[main["anio"]] * peso_mensual[(main["anio"], main["mes"])],
            "valor_cosecha_semanal_proxy_millones_cop": valor_cosecha_val.get(main["anio"], np.nan) * proxy_y / annual_proxy[main["anio"]],
        })
        for dept in sorted(produccion["DEPARTAMENTO_NASA"].unique()):
            pr = prod_dept.loc[(dept, main["anio"])]
            y_dept = weekly_y(comps, lambda y, m, dept=dept: prod_dept.loc[(dept, y)]["produccion_anual_t"] * peso_mensual[(y, m)])
            panel_rows.append({
                **base,
                "departamento": dept.title(),
                "produccion_semanal_proxy_t": y_dept,
                "produccion_anual_depto_mun_t": pr["produccion_anual_t"],
                "area_cosechada_depto_mun_ha": pr["area_cosechada_ha"],
                "rendimiento_depto_mun_t_ha": pr["rendimiento_t_ha"],
                "produccion_mensual_proxy_principal_t": pr["produccion_anual_t"] * peso_mensual[(main["anio"], main["mes"])],
                "valor_cosecha_semanal_proxy_millones_cop": valor_cosecha_val.get(main["anio"], np.nan) * y_dept / annual_proxy[main["anio"]],
            })

    proxy = pd.DataFrame(proxy_rows)
    panel = pd.DataFrame(panel_rows)

    proxy = proxy.merge(nasa_nat.drop(columns=["departamento"]), on="fecha_semana_fin", how="left")
    panel = panel.merge(nasa_dept, on=["departamento", "fecha_semana_fin"], how="left")
    proxy = proxy.merge(precio_int[["fecha_semana_fin", "precio_interno_cop_carga"]], on="fecha_semana_fin", how="left")
    panel = panel.merge(precio_int[["fecha_semana_fin", "precio_interno_cop_carga"]], on="fecha_semana_fin", how="left")
    proxy = proxy.merge(trm_week, on="fecha_semana_fin", how="left")
    panel = panel.merge(trm_week, on="fecha_semana_fin", how="left")

    proxy = add_features(proxy, [])
    panel = add_features(panel, ["departamento"])

    # Validación anual exacta por componentes de calendario
    validation = []
    for y in range(2021, 2025):
        total = 0
        for wend in week_ends:
            for c in week_month_components(wend):
                if c["anio"] == y:
                    total += annual_proxy[y] * peso_mensual[(y, c["mes"])] / calendar.monthrange(y, c["mes"])[1] * c["dias"]
        validation.append({"nivel": "proxy_nacional", "departamento": None, "anio": y, "produccion_anual_original_t": annual_proxy[y], "suma_produccion_semanal_proxy_t": total, "diferencia_t": total - annual_proxy[y]})
    for dept in sorted(produccion["DEPARTAMENTO_NASA"].unique()):
        for y in range(2021, 2025):
            original = prod_dept.loc[(dept, y)]["produccion_anual_t"]
            total = 0
            for wend in week_ends:
                for c in week_month_components(wend):
                    if c["anio"] == y:
                        total += original * peso_mensual[(y, c["mes"])] / calendar.monthrange(y, c["mes"])[1] * c["dias"]
            validation.append({"nivel": "panel_departamental", "departamento": dept.title(), "anio": y, "produccion_anual_original_t": original, "suma_produccion_semanal_proxy_t": total, "diferencia_t": total - original})
    validation = pd.DataFrame(validation)

    dictionary = pd.DataFrame([
        ["produccion_semanal_proxy_t", "Y proxy", "Producción semanal proxy en toneladas construida sin clima: anual -> mensual por estacionalidad nacional -> semanal por días calendario.", "Target semanal exploratorio/operacional."],
        ["indice_climatico_base_x", "X climática derivada", "Índice compuesto de humedad, precipitación, temperatura y radiación. No participa en la Y.", "X útil para modelos y sensibilidad."],
        ["indice_climatico_ajustado_x", "X climática derivada", "Versión suavizada: 0.70 + 0.30 * indice_climatico_base_x.", "X opcional para capturar condición climática agregada."],
        ["trm_viernes_cop_usd", "X económica", "TRM oficial del viernes o último dato hábil disponible.", "Usar preferiblemente rezagos, medias móviles y variaciones."],
    ], columns=["variable", "tipo", "descripcion", "uso_modelo"])

    proxy.to_csv(OUTPUT_PROXY_CSV, index=False, encoding="utf-8-sig")
    panel.to_csv(OUTPUT_PANEL_CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        proxy.to_excel(writer, sheet_name="base_proxy_nacional", index=False)
        panel.to_excel(writer, sheet_name="base_panel_deptal", index=False)
        validation.to_excel(writer, sheet_name="validacion_anual", index=False)
        dictionary.to_excel(writer, sheet_name="diccionario", index=False)

    print("Listo.")
    print(f"Proxy nacional: {proxy.shape}")
    print(f"Panel departamental: {panel.shape}")
    print(f"Máxima diferencia anual: {validation['diferencia_t'].abs().max():.10f}")


if __name__ == "__main__":
    main()
