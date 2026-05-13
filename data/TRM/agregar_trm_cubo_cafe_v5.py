"""
Agrega TRM semanal al cubo de café v4 y genera archivos v5
------------------------------------------------------------

Este script toma las bases generadas en v4:
- base_proxy_nacional_semanal_cafe_2021_2024_v4.csv
- base_panel_departamental_semanal_cafe_2021_2024_v4.csv

y les agrega las variables:
- trm_viernes_cop_usd
- trm_promedio_semana_cop_usd
- trm_viernes_cop_usd_lag_1s
- trm_viernes_cop_usd_lag_4s
- trm_viernes_cop_usd_ma_4s
- trm_viernes_cop_usd_var_4s

Fuente recomendada: Datos Abiertos Colombia, dataset 32sa-8pi3.
La TRM es certificada por la Superintendencia Financiera de Colombia.

Requisitos:
pip install pandas requests openpyxl

Uso normal, con internet:
python agregar_trm_cubo_cafe_v5.py

Uso con archivo TRM descargado manualmente:
python agregar_trm_cubo_cafe_v5.py --trm_csv ruta/al/archivo_trm.csv

El archivo TRM manual debe contener, idealmente, columnas equivalentes a:
valor, vigenciadesde, vigenciahasta
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests

# --------------------------
# Entradas y salidas
# --------------------------
INPUT_PROXY = Path("base_proxy_nacional_semanal_cafe_2021_2024_v4.csv")
INPUT_PANEL = Path("base_panel_departamental_semanal_cafe_2021_2024_v4.csv")

OUT_PROXY = Path("base_proxy_nacional_semanal_cafe_2021_2024_v5_trm.csv")
OUT_PANEL = Path("base_panel_departamental_semanal_cafe_2021_2024_v5_trm.csv")
OUT_XLSX = Path("cubo_cafe_semanal_proxy_y_panel_2021_2024_v5_trm.xlsx")
OUT_TRM_WEEKLY = Path("trm_semanal_2021_2024.csv")

TRM_COLS = [
    "trm_viernes_cop_usd",
    "trm_promedio_semana_cop_usd",
    "trm_viernes_cop_usd_lag_1s",
    "trm_viernes_cop_usd_lag_4s",
    "trm_viernes_cop_usd_ma_4s",
    "trm_viernes_cop_usd_var_4s",
]

TRM_DATASET_URL = "https://www.datos.gov.co/resource/32sa-8pi3.json"
TRM_DATASET_PAGE = "https://www.datos.gov.co/Econom-a-y-Finanzas/Tasa-de-Cambio-Representativa-del-Mercado-TRM/32sa-8pi3"


# --------------------------
# Utilidades
# --------------------------
def _find_col(columns: Iterable[str], candidates: Iterable[str]) -> str:
    """Busca una columna por coincidencia flexible."""
    norm = {c.lower().strip().replace(" ", "").replace("_", ""): c for c in columns}
    for cand in candidates:
        key = cand.lower().strip().replace(" ", "").replace("_", "")
        if key in norm:
            return norm[key]
    # Búsqueda por contiene
    for c in columns:
        c_norm = c.lower().strip().replace(" ", "").replace("_", "")
        if any(cand.lower().replace(" ", "").replace("_", "") in c_norm for cand in candidates):
            return c
    raise ValueError(f"No encontré columna compatible con: {list(candidates)}. Columnas disponibles: {list(columns)}")


def _parse_number_col(s: pd.Series) -> pd.Series:
    """Convierte valores con formatos latinos o anglos a float."""
    # Ejemplos posibles: '3,987.50', '3.987,50', '3987.50', '$3,987.50'
    txt = s.astype(str).str.replace("$", "", regex=False).str.strip()
    txt = txt.str.replace(" ", "", regex=False)

    def parse_one(x: str) -> float:
        if x in {"", "nan", "None", "NaN"}:
            return np.nan
        # Si contiene punto y coma, detectar el último separador como decimal.
        if "," in x and "." in x:
            if x.rfind(",") > x.rfind("."):
                x = x.replace(".", "").replace(",", ".")
            else:
                x = x.replace(",", "")
        elif "," in x and "." not in x:
            # Si solo tiene coma, asumir decimal latino.
            x = x.replace(",", ".")
        try:
            return float(x)
        except ValueError:
            return np.nan

    return txt.map(parse_one)


# --------------------------
# Descarga/carga TRM
# --------------------------
def download_trm_from_datos_abiertos(start_date: str, end_date: str) -> pd.DataFrame:
    """Descarga TRM desde Socrata/Datos Abiertos Colombia."""
    params = {
        "$limit": 50000,
        "$select": "valor,vigenciadesde,vigenciahasta",
        "$where": f"vigenciadesde between '{start_date}T00:00:00' and '{end_date}T23:59:59'",
        "$order": "vigenciadesde asc",
    }
    response = requests.get(TRM_DATASET_URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise RuntimeError("La consulta a Datos Abiertos no devolvió registros de TRM.")
    return pd.DataFrame(data)


def load_trm_raw(trm_csv: str | None, start_date: str, end_date: str) -> pd.DataFrame:
    """Carga TRM desde archivo local o desde Datos Abiertos."""
    if trm_csv:
        print(f"Leyendo TRM desde archivo local: {trm_csv}")
        return pd.read_csv(trm_csv)

    print("Descargando TRM desde Datos Abiertos Colombia...")
    return download_trm_from_datos_abiertos(start_date, end_date)


def build_daily_trm(raw: pd.DataFrame) -> pd.DataFrame:
    """Normaliza y expande la TRM a un registro por día de vigencia."""
    valor_col = _find_col(raw.columns, ["valor", "trm", "tcrm", "tasa"])
    desde_col = _find_col(raw.columns, ["vigenciadesde", "vigencia_desde", "fecha", "desde"])
    try:
        hasta_col = _find_col(raw.columns, ["vigenciahasta", "vigencia_hasta", "hasta"])
    except ValueError:
        hasta_col = None

    work = raw.copy()
    work["trm"] = _parse_number_col(work[valor_col])
    work["vigenciadesde"] = pd.to_datetime(work[desde_col], errors="coerce").dt.normalize()
    if hasta_col:
        work["vigenciahasta"] = pd.to_datetime(work[hasta_col], errors="coerce").dt.normalize()
    else:
        work["vigenciahasta"] = work["vigenciadesde"]

    work = work.dropna(subset=["trm", "vigenciadesde"]).copy()
    work["vigenciahasta"] = work["vigenciahasta"].fillna(work["vigenciadesde"])
    work.loc[work["vigenciahasta"] < work["vigenciadesde"], "vigenciahasta"] = work["vigenciadesde"]

    daily_rows = []
    for row in work[["vigenciadesde", "vigenciahasta", "trm"]].itertuples(index=False):
        for d in pd.date_range(row.vigenciadesde, row.vigenciahasta, freq="D"):
            daily_rows.append({"fecha": d.normalize(), "trm": float(row.trm)})

    daily = pd.DataFrame(daily_rows)
    daily = daily.sort_values("fecha").drop_duplicates("fecha", keep="last")
    return daily


def build_weekly_trm(daily: pd.DataFrame, week_ends: pd.Series) -> pd.DataFrame:
    """Construye TRM viernes/promedio semanal y transformaciones."""
    min_date = week_ends.min() - pd.Timedelta(days=6)
    max_date = week_ends.max()
    full_dates = pd.DataFrame({"fecha": pd.date_range(min_date, max_date, freq="D")})
    daily = full_dates.merge(daily, on="fecha", how="left")
    daily["trm"] = daily["trm"].ffill().bfill()

    trm_by_date = daily.set_index("fecha")["trm"]

    rows = []
    for week_end in sorted(pd.to_datetime(week_ends).dt.normalize().unique()):
        week_end = pd.Timestamp(week_end)
        week_start = week_end - pd.Timedelta(days=6)
        friday = week_start + pd.Timedelta(days=4)

        trm_viernes = trm_by_date.loc[friday] if friday in trm_by_date.index else np.nan
        week_values = trm_by_date.loc[week_start:week_end]
        trm_prom = week_values.mean() if not week_values.empty else np.nan

        rows.append({
            "fecha_semana_fin": week_end,
            "trm_viernes_cop_usd": trm_viernes,
            "trm_promedio_semana_cop_usd": trm_prom,
        })

    weekly = pd.DataFrame(rows).sort_values("fecha_semana_fin")
    weekly["trm_viernes_cop_usd_lag_1s"] = weekly["trm_viernes_cop_usd"].shift(1)
    weekly["trm_viernes_cop_usd_lag_4s"] = weekly["trm_viernes_cop_usd"].shift(4)
    weekly["trm_viernes_cop_usd_ma_4s"] = weekly["trm_viernes_cop_usd"].rolling(4, min_periods=1).mean()
    weekly["trm_viernes_cop_usd_var_4s"] = (
        weekly["trm_viernes_cop_usd"] / weekly["trm_viernes_cop_usd_lag_4s"] - 1
    )
    return weekly


def merge_trm(base: pd.DataFrame, weekly_trm: pd.DataFrame) -> pd.DataFrame:
    """Elimina TRM vacía/antigua y pega la TRM calculada."""
    base = base.copy()
    base["fecha_semana_fin"] = pd.to_datetime(base["fecha_semana_fin"]).dt.normalize()
    drop_cols = [c for c in TRM_COLS if c in base.columns]
    base = base.drop(columns=drop_cols, errors="ignore")
    return base.merge(weekly_trm[["fecha_semana_fin"] + TRM_COLS], on="fecha_semana_fin", how="left")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trm_csv", default=None, help="Ruta opcional a un CSV local de TRM descargado de Datos Abiertos.")
    args = parser.parse_args()

    if not INPUT_PROXY.exists() or not INPUT_PANEL.exists():
        print("ERROR: no encontré las bases v4 en la carpeta actual.", file=sys.stderr)
        print(f"Esperaba: {INPUT_PROXY} y {INPUT_PANEL}", file=sys.stderr)
        sys.exit(1)

    base_proxy = pd.read_csv(INPUT_PROXY)
    base_panel = pd.read_csv(INPUT_PANEL)
    base_proxy["fecha_semana_fin"] = pd.to_datetime(base_proxy["fecha_semana_fin"]).dt.normalize()
    base_panel["fecha_semana_fin"] = pd.to_datetime(base_panel["fecha_semana_fin"]).dt.normalize()

    week_ends = pd.Series(sorted(base_proxy["fecha_semana_fin"].unique()))
    start_date = (pd.to_datetime(week_ends.min()) - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    end_date = (pd.to_datetime(week_ends.max()) + pd.Timedelta(days=10)).strftime("%Y-%m-%d")

    raw = load_trm_raw(args.trm_csv, start_date, end_date)
    daily = build_daily_trm(raw)
    weekly_trm = build_weekly_trm(daily, week_ends)

    base_proxy_v5 = merge_trm(base_proxy, weekly_trm)
    base_panel_v5 = merge_trm(base_panel, weekly_trm)

    # Dummies adicionales de presión cambiaria, si se desean en modelación.
    for df in [base_proxy_v5, base_panel_v5]:
        df["dummy_trm_lag4_alta_p75"] = (
            df["trm_viernes_cop_usd_lag_4s"] >= df["trm_viernes_cop_usd_lag_4s"].quantile(0.75)
        ).astype(int)
        df["dummy_devaluacion_4s_p75"] = (
            df["trm_viernes_cop_usd_var_4s"] >= df["trm_viernes_cop_usd_var_4s"].quantile(0.75)
        ).astype(int)

    weekly_trm.to_csv(OUT_TRM_WEEKLY, index=False, encoding="utf-8-sig")
    base_proxy_v5.to_csv(OUT_PROXY, index=False, encoding="utf-8-sig")
    base_panel_v5.to_csv(OUT_PANEL, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
        base_proxy_v5.to_excel(writer, sheet_name="base_proxy_nacional", index=False)
        base_panel_v5.to_excel(writer, sheet_name="base_panel_deptal", index=False)
        weekly_trm.to_excel(writer, sheet_name="trm_semanal", index=False)

    print("Listo. Archivos generados:")
    print(f"- {OUT_PROXY}")
    print(f"- {OUT_PANEL}")
    print(f"- {OUT_TRM_WEEKLY}")
    print(f"- {OUT_XLSX}")
    print("\nValidación de nulos TRM:")
    print(base_proxy_v5[TRM_COLS].isna().sum())
    print("\nPrimeras filas TRM semanal:")
    print(weekly_trm.head(8))


if __name__ == "__main__":
    main()
