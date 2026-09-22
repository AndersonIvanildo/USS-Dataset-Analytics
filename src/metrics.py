from __future__ import annotations

import pandas as pd

RATING_VALUES = [1, 2, 3, 4, 5]
AGREEMENT_ORDER = [
    "Uma nota",
    "Unanimidade",
    "Discordância leve",
    "Discordância forte",
]


def real_user_turns(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona falas reais de usuário, excluindo linhas OVERALL."""
    return df[(df["role"] == "USER") & (~df["is_overall"])].copy()


def overall_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona linhas de satisfação geral do diálogo."""
    return df[df["is_overall"]].copy()


def user_scored_rows(df: pd.DataFrame, include_overall: bool = True) -> pd.DataFrame:
    """Seleciona linhas USER com pelo menos uma nota de satisfação."""
    data = df[df["role"] == "USER"].copy()
    if not include_overall:
        data = data[~data["is_overall"]]
    return data[data["satisfaction_annotation_count"] > 0].copy()


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


def dataset_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Resume volume, cobertura e nota mais frequente por dataset."""
    user_turns = real_user_turns(df)
    lengths = dialogue_lengths(df)

    summary = (
        df.groupby("dataset")
        .agg(
            dialogos=("dialogue_id", "nunique"),
            falas_sistema=("role", lambda values: int((values == "SYSTEM").sum())),
            overall=("is_overall", "sum"),
        )
        .reset_index()
    )

    user_counts = user_turns.groupby("dataset").size().rename("falas_usuario")
    annotation_counts = (
        user_turns.groupby("dataset")["action_raw"]
        .nunique()
        .rename("anotacoes_distintas")
    )
    unknown_counts = (
        user_turns.groupby("dataset")["action_raw"]
        .apply(lambda values: int((values == "UNKNOWN").sum()))
        .rename("unknown")
    )
    median_lengths = (
        lengths.groupby("dataset")["turn_count"].median().rename("mediana_falas_dialogo")
    )
    missing_scores = (
        user_turns.groupby("dataset")["satisfaction_mode"]
        .apply(lambda values: int(values.isna().sum()))
        .rename("falas_sem_nota")
    )
    top_rating = (
        user_turns.dropna(subset=["satisfaction_mode"])
        .assign(satisfaction_mode=lambda data: data["satisfaction_mode"].astype(int))
        .groupby("dataset")["satisfaction_mode"]
        .agg(lambda values: values.value_counts().sort_values(ascending=False).index[0])
        .rename("nota_mais_frequente")
    )

    summary = summary.join(user_counts, on="dataset")
    summary = summary.join(annotation_counts, on="dataset")
    summary = summary.join(unknown_counts, on="dataset")
    summary = summary.join(median_lengths, on="dataset")
    summary = summary.join(missing_scores, on="dataset")
    summary = summary.join(top_rating, on="dataset")

    numeric_columns = [
        "falas_usuario",
        "anotacoes_distintas",
        "unknown",
        "mediana_falas_dialogo",
        "falas_sem_nota",
    ]
    summary[numeric_columns] = summary[numeric_columns].fillna(0)
    summary["nota_mais_frequente"] = summary["nota_mais_frequente"].fillna("Sem nota")
    return summary.sort_values("dataset").reset_index(drop=True)


def rating_distribution(
    df: pd.DataFrame,
    level: str = "turn",
    percent: bool = True,
) -> pd.DataFrame:
    """Calcula distribuição de notas para falas de usuário ou OVERALL."""
    if level == "overall":
        data = overall_rows(df)
    else:
        data = real_user_turns(df)

    data = data.dropna(subset=["satisfaction_mode"]).copy()
    columns = ["dataset", "satisfaction_mode", "total", "percentual"]
    if data.empty:
        return pd.DataFrame(columns=columns)

    data["satisfaction_mode"] = data["satisfaction_mode"].astype(int)
    counts = (
        data.groupby(["dataset", "satisfaction_mode"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )

    datasets = sorted(data["dataset"].unique())
    complete_index = pd.MultiIndex.from_product(
        [datasets, RATING_VALUES],
        names=["dataset", "satisfaction_mode"],
    )
    counts = (
        counts.set_index(["dataset", "satisfaction_mode"])
        .reindex(complete_index, fill_value=0)
        .reset_index()
    )
    denominators = counts.groupby("dataset")["total"].transform("sum")
    counts["percentual"] = counts["total"].div(denominators).fillna(0) * 100

    if not percent:
        counts["percentual"] = counts["total"]

    return counts


def _agreement_category(scores: object) -> str:
    normalized = scores if isinstance(scores, list) else []
    if len(normalized) <= 1:
        return "Uma nota"
    if len(set(normalized)) == 1:
        return "Unanimidade"
    if max(normalized) - min(normalized) <= 1:
        return "Discordância leve"
    return "Discordância forte"


def agreement_summary(df: pd.DataFrame, include_overall: bool = True) -> pd.DataFrame:
    """Resume concordância entre anotadores por dataset."""
    data = user_scored_rows(df, include_overall=include_overall)
    columns = ["dataset", "concordancia", "total", "percentual"]
    if data.empty:
        return pd.DataFrame(columns=columns)

    data = data.assign(
        concordancia=data["satisfaction_scores"].apply(_agreement_category)
    )
    counts = (
        data.groupby(["dataset", "concordancia"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )
    complete_index = pd.MultiIndex.from_product(
        [sorted(data["dataset"].unique()), AGREEMENT_ORDER],
        names=["dataset", "concordancia"],
    )
    counts = (
        counts.set_index(["dataset", "concordancia"])
        .reindex(complete_index, fill_value=0)
        .reset_index()
    )
    denominators = counts.groupby("dataset")["total"].transform("sum")
    counts["percentual"] = counts["total"].div(denominators).fillna(0) * 100
    return counts


def coverage_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Resume cobertura das anotações por dataset."""
    user_turns = real_user_turns(df)
    overall = overall_rows(df)
    if user_turns.empty:
        return pd.DataFrame()

    coverage = (
        user_turns.groupby("dataset")
        .agg(
            falas_reais=("role", "size"),
            unknown_falas_reais=(
                "action_raw",
                lambda values: int((values == "UNKNOWN").sum()),
            ),
        )
        .reset_index()
    )
    overall_counts = overall.groupby("dataset").size().rename("overall")
    coverage = coverage.join(overall_counts, on="dataset").fillna({"overall": 0})
    coverage["overall"] = coverage["overall"].astype(int)
    return coverage.sort_values("dataset").reset_index(drop=True)


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
