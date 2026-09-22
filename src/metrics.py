from __future__ import annotations

import pandas as pd

RATING_VALUES = [1, 2, 3, 4, 5]


def real_user_turns(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona falas reais de usuário, excluindo linhas OVERALL."""
    return df[(df["role"] == "USER") & (~df["is_overall"])].copy()


def overall_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona linhas de satisfação geral do diálogo."""
    return df[df["is_overall"]].copy()


def summary_metrics(df: pd.DataFrame) -> dict[str, int]:
    """Calcula os indicadores principais exibidos na visão geral."""
    user_turns = real_user_turns(df)
    overall = overall_rows(df)

    return {
        "datasets": int(df["dataset"].nunique()),
        "dialogues": int(df.groupby("dataset")["dialogue_id"].nunique().sum()),
        "user_turns": int(len(user_turns)),
        "overall_rows": int(len(overall)),
        "system_turns": int((df["role"] == "SYSTEM").sum()),
    }


def dialogue_lengths(df: pd.DataFrame) -> pd.DataFrame:
    """Conta turnos por diálogo para analisar o tamanho das conversas."""
    return (
        df[~df["is_overall"]]
        .groupby(["dataset", "dialogue_id"], as_index=False)
        .size()
        .rename(columns={"size": "turn_count"})
    )


def low_satisfaction_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula a proporção de baixa satisfação por dataset."""
    user_turns = real_user_turns(df).dropna(subset=["satisfaction_mode"]).copy()
    user_turns["low_satisfaction"] = user_turns["satisfaction_mode"] < 3

    return (
        user_turns.groupby("dataset", as_index=False)["low_satisfaction"]
        .mean()
        .assign(low_satisfaction=lambda data: data["low_satisfaction"] * 100)
    )


def annotation_frequencies(
    df: pd.DataFrame,
    limit: int | None = None,
    include_unknown: bool = True,
) -> pd.DataFrame:
    """Conta anotações em falas reais de usuário."""
    data = real_user_turns(df)
    if not include_unknown:
        data = data[data["action_raw"] != "UNKNOWN"]

    columns = ["action_raw", "total", "percentual"]
    if data.empty:
        return pd.DataFrame(columns=columns)

    counts = (
        data.groupby("action_raw", as_index=False)
        .size()
        .rename(columns={"size": "total"})
        .sort_values("total", ascending=False)
    )
    counts["percentual"] = counts["total"] / len(data) * 100

    if limit is not None:
        counts = counts.head(limit)

    return counts.reset_index(drop=True)


def annotation_rating_distribution(
    df: pd.DataFrame,
    annotations: list[str] | None = None,
    include_unknown: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cruza anotações com a nota mais frequente de satisfação."""
    data = real_user_turns(df).dropna(subset=["satisfaction_mode"]).copy()
    if not include_unknown:
        data = data[data["action_raw"] != "UNKNOWN"]
    if annotations is not None:
        data = data[data["action_raw"].isin(annotations)]

    empty = pd.DataFrame(columns=RATING_VALUES, dtype=float)
    if data.empty:
        return empty.copy(), empty.copy()

    data["rating"] = data["satisfaction_mode"].astype(int)
    counts = pd.crosstab(data["action_raw"], data["rating"]).reindex(
        columns=RATING_VALUES,
        fill_value=0,
    )

    if annotations is not None:
        ordered_annotations = [action for action in annotations if action in counts.index]
        counts = counts.reindex(ordered_annotations)

    percentages = counts.div(counts.sum(axis=1), axis=0).fillna(0) * 100
    return counts, percentages
