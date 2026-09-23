from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd


def format_cell_for_display(value: Any) -> Any:
    """Converte valores problemáticos para células seguras no st.dataframe."""
    if value is None:
        return "None"

    if isinstance(value, list | tuple | set):
        return "[" + ", ".join(str(item) for item in value) + "]"

    if isinstance(value, dict):
        return str(value)

    try:
        if pd.isna(value):
            return "None"
    except (TypeError, ValueError):
        pass

    if isinstance(value, Iterable) and not isinstance(value, str | bytes):
        return str(value)

    return value


def dataframe_for_display(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    rename: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Prepara uma cópia do dataframe para exibição segura no Streamlit."""
    selected = df.copy() if columns is None else df[columns].copy()
    for column in selected.columns:
        if selected[column].dtype == "object":
            selected[column] = selected[column].apply(format_cell_for_display)
    if rename:
        selected = selected.rename(columns=rename)
    return selected
