from pathlib import Path
from functools import lru_cache
import pandas as pd

APP_DATA_DIR = Path("data/processed/app")

@lru_cache(maxsize=8)
def load_csv(name: str) -> pd.DataFrame:
    path = APP_DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"No encontré {path}. Verifica que existan los datasets app-ready en data/processed/app/."
        )
    return pd.read_csv(path)

def fmt_num(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "NA"
    return f"{value:,.{digits}f}"

def get_department_options(df: pd.DataFrame, col: str = "departamento") -> list[dict]:
    opts = [{"label": "Todos", "value": "TODOS"}]
    values = sorted(df[col].dropna().astype(str).unique().tolist())
    opts.extend({"label": v.title(), "value": v} for v in values)
    return opts

def get_year_options(df: pd.DataFrame, col: str = "anio_referencia_y") -> list[dict]:
    opts = [{"label": "Todos", "value": "TODOS"}]
    values = sorted(df[col].dropna().astype(int).unique().tolist())
    opts.extend({"label": str(v), "value": v} for v in values)
    return opts

def filter_df(df: pd.DataFrame, dept_value="TODOS", year_value="TODOS") -> pd.DataFrame:
    out = df.copy()
    if dept_value != "TODOS" and "departamento" in out.columns:
        out = out[out["departamento"] == dept_value]
    if year_value != "TODOS" and "anio_referencia_y" in out.columns:
        out = out[out["anio_referencia_y"] == year_value]
    return out

def apply_figure_style(fig, title=None):
    fig.update_layout(
        template="plotly_white",
        font=dict(
            family='"Abadi MT Condensed Light", "Segoe UI", Arial, sans-serif',
            size=14,
            color="#1f2a24"
        ),
        title=dict(
            text=title if title else fig.layout.title.text,
            font=dict(size=20, color="#13352c")
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#d9e0dc"
    )
    fig.update_yaxes(
        gridcolor="#e8ece9",
        zerolinecolor="#d9e0dc"
    )
    return fig