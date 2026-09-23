from __future__ import annotations

from typing import Any

import pandas as pd

from src.loaders import ensure_annotation_columns
from src.preprocessing import UNKNOWN_ACTION

UNIFIED_COLUMNS = [
    "dataset",
    "dialogue_uid",
    "dialogue_id",
    "turn_id",
    "role",
    "row_kind",
    "text",
    "annotation_code",
    "annotation_status",
    "annotation_layer",
    "dialogue_action",
    "domain",
    "semantic_type",
    "semantic_target",
    "satisfaction_scores",
    "satisfaction_annotation_count",
    "satisfaction_mode",
    "satisfaction_mean",
    "satisfaction_disagreement",
    "is_overall",
]


def _none_if_missing(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def _row_kind(row: pd.Series) -> str:
    if bool(row["is_overall"]):
        return "avaliação geral"
    if row["role"] == "USER":
        return "fala de usuário"
    if row["role"] == "SYSTEM":
        return "fala do sistema"
    return "outro registro"


def _annotation_status(row: pd.Series) -> str:
    action = str(row["action_raw"])
    if bool(row["is_overall"]):
        return "OVERALL"
    if action == UNKNOWN_ACTION:
        return "sem anotação de ação"
    return "anotação disponível"


def _annotation_layer(row: pd.Series) -> str | None:
    dataset = row["dataset"]
    action = str(row["action_raw"])
    if bool(row["is_overall"]) or action == UNKNOWN_ACTION:
        return None
    if dataset == "MWOZ":
        return "domínio + ato"
    if dataset == "CCPE":
        return "marcação semântica"
    if dataset == "SGD":
        return "ato de diálogo"
    return "anotação original"


def _dialogue_action(row: pd.Series) -> str | None:
    dataset = row["dataset"]
    action = str(row["action_raw"])
    if bool(row["is_overall"]) or action == UNKNOWN_ACTION:
        return None
    if dataset == "SGD":
        return action
    if dataset == "MWOZ" and "-" in action:
        return action.split("-", 1)[1]
    return None


def _domain(row: pd.Series) -> str | None:
    dataset = row["dataset"]
    action = str(row["action_raw"])
    if bool(row["is_overall"]) or action == UNKNOWN_ACTION:
        return None
    if dataset == "MWOZ" and "-" in action:
        return action.split("-", 1)[0]
    return None


def _semantic_type(row: pd.Series) -> str | None:
    dataset = row["dataset"]
    action = str(row["action_raw"])
    if bool(row["is_overall"]) or action == UNKNOWN_ACTION:
        return None
    if dataset == "CCPE":
        return action.split("+", 1)[0] if "+" in action else action
    return None


def _semantic_target(row: pd.Series) -> str | None:
    dataset = row["dataset"]
    action = str(row["action_raw"])
    if bool(row["is_overall"]) or action == UNKNOWN_ACTION:
        return None
    if dataset == "CCPE" and "+" in action:
        return action.split("+", 1)[1]
    return None


def _annotation_code(row: pd.Series) -> str | None:
    action = str(row["action_raw"])
    if bool(row["is_overall"]) or action == UNKNOWN_ACTION:
        return None
    return action


def build_unified_proposal(df: pd.DataFrame) -> pd.DataFrame:
    """Monta uma proposta de tabela unificada sem alterar os dados originais."""
    data = ensure_annotation_columns(df).copy()
    data["dialogue_uid"] = data["dataset"].astype(str) + "::" + data["dialogue_id"].astype(str)

    unified = pd.DataFrame(
        {
            "dataset": data["dataset"],
            "dialogue_uid": data["dialogue_uid"],
            "dialogue_id": data["dialogue_id"],
            "turn_id": data["turn_id"],
            "role": data["role"],
            "row_kind": data.apply(_row_kind, axis=1),
            "text": data["text"],
            "annotation_code": data.apply(_annotation_code, axis=1),
            "annotation_status": data.apply(_annotation_status, axis=1),
            "annotation_layer": data.apply(_annotation_layer, axis=1),
            "dialogue_action": data.apply(_dialogue_action, axis=1),
            "domain": data.apply(_domain, axis=1),
            "semantic_type": data.apply(_semantic_type, axis=1),
            "semantic_target": data.apply(_semantic_target, axis=1),
            "satisfaction_scores": data["satisfaction_scores"],
            "satisfaction_annotation_count": data["satisfaction_annotation_count"],
            "satisfaction_mode": data["satisfaction_mode"],
            "satisfaction_mean": data["satisfaction_mean"],
            "satisfaction_disagreement": data["satisfaction_disagreement"],
            "is_overall": data["is_overall"],
        }
    )

    for column in [
        "annotation_code",
        "annotation_layer",
        "dialogue_action",
        "domain",
        "semantic_type",
        "semantic_target",
    ]:
        unified[column] = unified[column].apply(_none_if_missing).astype(object)
        unified.loc[unified[column].isna(), column] = None

    return unified[UNIFIED_COLUMNS]


def unified_summary(unified: pd.DataFrame) -> dict[str, int]:
    """Resume volume e disponibilidade da proposta unificada."""
    real_user_turns = unified[unified["row_kind"].eq("fala de usuário")]
    return {
        "rows": int(len(unified)),
        "dialogues": int(unified["dialogue_uid"].nunique()),
        "user_turns": int(len(real_user_turns)),
        "overall": int(unified["row_kind"].eq("avaliação geral").sum()),
        "available_annotations": int(
            real_user_turns["annotation_status"].eq("anotação disponível").sum()
        ),
        "missing_annotations": int(
            real_user_turns["annotation_status"].eq("sem anotação de ação").sum()
        ),
    }


def unified_coverage_by_dataset(unified: pd.DataFrame) -> pd.DataFrame:
    """Conta os principais campos propostos por dataset."""
    user_turns = unified[unified["row_kind"].eq("fala de usuário")].copy()
    if user_turns.empty:
        return pd.DataFrame()

    coverage = (
        user_turns.groupby("dataset")
        .agg(
            falas_usuario=("row_kind", "size"),
            anotacoes_disponiveis=(
                "annotation_status",
                lambda values: int((values == "anotação disponível").sum()),
            ),
            sem_anotacao=(
                "annotation_status",
                lambda values: int((values == "sem anotação de ação").sum()),
            ),
            acoes_dialogo=("dialogue_action", lambda values: int(values.notna().sum())),
            dominios=("domain", lambda values: int(values.notna().sum())),
            marcacoes_semanticas=(
                "semantic_type",
                lambda values: int(values.notna().sum()),
            ),
        )
        .reset_index()
    )
    overall = (
        unified[unified["row_kind"].eq("avaliação geral")]
        .groupby("dataset")
        .size()
        .rename("overall")
    )
    coverage = coverage.join(overall, on="dataset").fillna({"overall": 0})
    coverage["overall"] = coverage["overall"].astype(int)
    return coverage.sort_values("dataset").reset_index(drop=True)


def unified_schema_counts(unified: pd.DataFrame) -> pd.DataFrame:
    """Conta camadas de anotação por dataset."""
    data = unified[unified["row_kind"].eq("fala de usuário")].copy()
    data["annotation_layer"] = data["annotation_layer"].fillna("sem camada de anotação")
    return (
        data.groupby(["dataset", "annotation_layer"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )
