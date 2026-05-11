from pathlib import Path
import pandas as pd

RAW_FILE = Path("data/raw/bases_panel_cafe_semanal_mensual_anual.xlsx")
PROCESSED_DIR = Path("data/processed")

SHEETS = {
    "weekly": "weekly.csv",
    "monthly": "monthly.csv",
    "annual": "annual.csv",
}

DATE_COLUMNS = {
    "weekly": ["fecha_semana_inicio", "fecha_semana_fin"],
    "monthly": [],
    "annual": [],
}


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def export_sheet(xls: pd.ExcelFile, sheet_name: str, output_name: str) -> pd.DataFrame:
    df = pd.read_excel(xls, sheet_name=sheet_name)

    for col in DATE_COLUMNS.get(sheet_name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df = clean_text_columns(df)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DIR / output_name
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[OK] Exportado: {output_path} -> shape={df.shape}")
    return df


def basic_checks(name: str, df: pd.DataFrame) -> None:
    print(f"\n--- Verificación: {name} ---")
    print("Filas, columnas:", df.shape)
    print("Primeras columnas:", list(df.columns[:10]))

    if "departamento" in df.columns:
        print("Departamentos:", sorted(df["departamento"].dropna().astype(str).unique().tolist()))

    if name == "weekly":
        key_cols = [c for c in ["departamento", "anio_referencia_y", "semana_iso"] if c in df.columns]
    elif name == "monthly":
        key_cols = [c for c in ["departamento", "anio_referencia_y", "mes_referencia_y"] if c in df.columns]
    else:
        key_cols = [c for c in ["departamento", "anio_referencia_y"] if c in df.columns]

    if key_cols:
        dup_count = df.duplicated(subset=key_cols).sum()
        print("Duplicados por llave esperada:", int(dup_count))

    null_share = (df.isna().mean() * 100).sort_values(ascending=False)
    print("Top 10 porcentajes de nulos:")
    print(null_share.head(10).round(2))

    if name == "monthly":
        if "produccion_mensual_desde_semana_t" in df.columns and "produccion_mensual_proxy_t" in df.columns:
            diff = (df["produccion_mensual_desde_semana_t"] - df["produccion_mensual_proxy_t"]).abs()
            print("Máx diferencia target mensual:", round(diff.max(), 6))
            print("Prom diferencia target mensual:", round(diff.mean(), 6))

    if name == "annual":
        if "produccion_anual_desde_semana_t" in df.columns and "produccion_anual_departamental_t" in df.columns:
            diff = (df["produccion_anual_desde_semana_t"] - df["produccion_anual_departamental_t"]).abs()
            print("Máx diferencia target anual:", round(diff.max(), 6))
            print("Prom diferencia target anual:", round(diff.mean(), 6))


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"No encontré el archivo maestro: {RAW_FILE}")

    print(f"Leyendo archivo maestro: {RAW_FILE}")
    xls = pd.ExcelFile(RAW_FILE)

    missing = [s for s in SHEETS if s not in xls.sheet_names]
    if missing:
        raise ValueError(f"Faltan hojas esperadas en el Excel: {missing}. Hojas disponibles: {xls.sheet_names}")

    exported = {}
    for sheet_name, output_name in SHEETS.items():
        exported[sheet_name] = export_sheet(xls, sheet_name, output_name)

    for name, df in exported.items():
        basic_checks(name, df)

    print("\nProceso finalizado. CSV listos en data/processed/.")


if __name__ == "__main__":
    main()
