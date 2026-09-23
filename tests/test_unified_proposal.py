import pandas as pd

from src.unified_proposal import build_unified_proposal, unified_coverage_by_dataset


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": "SGD",
                "dialogue_id": 1,
                "turn_id": 0,
                "role": "USER",
                "text": "thanks",
                "action_raw": "THANK_YOU",
                "satisfaction_scores": [4, 4, 5],
                "satisfaction_annotation_count": 3,
                "satisfaction_mode": 4,
                "satisfaction_mean": 4.33,
                "satisfaction_disagreement": 0.47,
                "is_overall": False,
            },
            {
                "dataset": "MWOZ",
                "dialogue_id": 2,
                "turn_id": 0,
                "role": "USER",
                "text": "I need a hotel",
                "action_raw": "Hotel-Inform",
                "satisfaction_scores": [3, 3, 4],
                "satisfaction_annotation_count": 3,
                "satisfaction_mode": 3,
                "satisfaction_mean": 3.33,
                "satisfaction_disagreement": 0.47,
                "is_overall": False,
            },
            {
                "dataset": "CCPE",
                "dialogue_id": 3,
                "turn_id": 0,
                "role": "USER",
                "text": "I like that movie",
                "action_raw": "ENTITY_OTHER+MOVIE_OR_SERIES",
                "satisfaction_scores": [3, 4, 4],
                "satisfaction_annotation_count": 3,
                "satisfaction_mode": 4,
                "satisfaction_mean": 3.67,
                "satisfaction_disagreement": 0.47,
                "is_overall": False,
            },
            {
                "dataset": "ReDial",
                "dialogue_id": 4,
                "turn_id": 0,
                "role": "USER",
                "text": "Do you know any comedies?",
                "action_raw": "UNKNOWN",
                "satisfaction_scores": [3, 3, 3],
                "satisfaction_annotation_count": 3,
                "satisfaction_mode": 3,
                "satisfaction_mean": 3.0,
                "satisfaction_disagreement": 0.0,
                "is_overall": False,
            },
            {
                "dataset": "SGD",
                "dialogue_id": 1,
                "turn_id": 1,
                "role": "USER",
                "text": "OVERALL",
                "action_raw": "UNKNOWN",
                "satisfaction_scores": [5, 5, 5],
                "satisfaction_annotation_count": 3,
                "satisfaction_mode": 5,
                "satisfaction_mean": 5.0,
                "satisfaction_disagreement": 0.0,
                "is_overall": True,
            },
        ]
    )


def test_unified_proposal_decomposes_without_forcing_equivalence() -> None:
    unified = build_unified_proposal(_sample_df())

    sgd = unified[unified["dataset"].eq("SGD") & unified["turn_id"].eq(0)].iloc[0]
    assert sgd["dialogue_action"] == "THANK_YOU"
    assert sgd["domain"] is None
    assert sgd["semantic_type"] is None

    mwoz = unified[unified["dataset"].eq("MWOZ")].iloc[0]
    assert mwoz["annotation_code"] == "Hotel-Inform"
    assert mwoz["dialogue_action"] == "Inform"
    assert mwoz["domain"] == "Hotel"
    assert mwoz["semantic_type"] is None

    ccpe = unified[unified["dataset"].eq("CCPE")].iloc[0]
    assert ccpe["dialogue_action"] is None
    assert ccpe["semantic_type"] == "ENTITY_OTHER"
    assert ccpe["semantic_target"] == "MOVIE_OR_SERIES"

    redial = unified[unified["dataset"].eq("ReDial")].iloc[0]
    assert redial["annotation_code"] is None
    assert redial["annotation_status"] == "sem anotação de ação"

    overall = unified[unified["row_kind"].eq("avaliação geral")].iloc[0]
    assert overall["annotation_code"] is None
    assert overall["annotation_status"] == "OVERALL"


def test_unified_coverage_counts_structural_fields() -> None:
    unified = build_unified_proposal(_sample_df())
    coverage = unified_coverage_by_dataset(unified).set_index("dataset")

    assert coverage.loc["MWOZ", "acoes_dialogo"] == 1
    assert coverage.loc["MWOZ", "dominios"] == 1
    assert coverage.loc["CCPE", "marcacoes_semanticas"] == 1
    assert coverage.loc["ReDial", "sem_anotacao"] == 1
    assert coverage.loc["SGD", "overall"] == 1
