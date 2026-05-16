from pathlib import Path
from functools import lru_cache
import pandas as pd
import joblib


DASH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = DASH_ROOT.parent

DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "model"


def _find_existing(paths):
    for p in paths:
        if p.exists():
            return p
    raise FileNotFoundError(f"No se encontró ninguno de estos archivos: {paths}")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


def _parse_possible_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    date_candidates = [
        "fecha", "date", "week_start", "month_start",
        "periodo", "period", "fecha_mes",
        "fecha_semana_inicio", "fecha_semana_fin"
    ]
    for col in date_candidates:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except Exception:
                pass
    return df


@lru_cache(maxsize=3)
def load_weekly() -> pd.DataFrame:
    path = _find_existing([
        DATA_PROCESSED / "weekly.csv",
        PROJECT_ROOT / "data" / "weekly.csv"
    ])
    df = pd.read_csv(path)
    df = _normalize_columns(df)
    df = _parse_possible_dates(df)
    return df


@lru_cache(maxsize=3)
def load_monthly() -> pd.DataFrame:
    path = _find_existing([
        DATA_PROCESSED / "monthly.csv",
        PROJECT_ROOT / "data" / "monthly.csv"
    ])
    df = pd.read_csv(path)
    df = _normalize_columns(df)
    df = _parse_possible_dates(df)
    return df


@lru_cache(maxsize=3)
def load_annual() -> pd.DataFrame:
    path = _find_existing([
        DATA_PROCESSED / "annual.csv",
        PROJECT_ROOT / "data" / "annual.csv"
    ])
    df = pd.read_csv(path)
    df = _normalize_columns(df)
    df = _parse_possible_dates(df)
    return df


def load_dataset(freq: str) -> pd.DataFrame:
    freq = freq.lower()
    if freq == "weekly":
        return load_weekly()
    elif freq == "monthly":
        return load_monthly()
    elif freq == "annual":
        return load_annual()
    else:
        raise ValueError("freq debe ser 'weekly', 'monthly' o 'annual'")


@lru_cache(maxsize=2)
def load_m5_model():
    path = MODEL_DIR / "m5_model.joblib"
    if not path.exists():
        raise FileNotFoundError(f"No existe el modelo: {path}")
    return joblib.load(path)


@lru_cache(maxsize=2)
def load_m6_model():
    path = MODEL_DIR / "m6_model.joblib"
    if not path.exists():
        raise FileNotFoundError(f"No existe el modelo: {path}")
    return joblib.load(path)


def get_possible_column(df: pd.DataFrame, candidates: list[str]):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def get_filter_options(freq: str) -> dict:
    df = load_dataset(freq)

    dept_col = get_possible_column(df, [
        "departamento", "department", "depto"
    ])
    year_col = get_possible_column(df, [
        "anio", "año", "year", "anio_referencia_y", "anio_semana_fin"
    ])
    month_col = get_possible_column(df, [
        "mes", "month", "mes_referencia_y"
    ])

    out = {
        "departamentos": [],
        "anios": [],
        "meses": []
    }

    if dept_col:
        out["departamentos"] = sorted(df[dept_col].dropna().astype(str).unique().tolist())

    if year_col:
        out["anios"] = sorted(pd.to_numeric(df[year_col], errors="coerce").dropna().astype(int).unique().tolist())

    if month_col:
        out["meses"] = sorted(pd.to_numeric(df[month_col], errors="coerce").dropna().astype(int).unique().tolist())

    return out


def get_basic_info() -> dict:
    weekly = load_weekly()
    monthly = load_monthly()
    annual = load_annual()

    return {
        "weekly_rows": len(weekly),
        "monthly_rows": len(monthly),
        "annual_rows": len(annual),
        "weekly_cols": weekly.columns.tolist(),
        "monthly_cols": monthly.columns.tolist(),
        "annual_cols": annual.columns.tolist(),
    }
