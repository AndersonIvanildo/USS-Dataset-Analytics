import pandas as pd

from src.loaders import ensure_annotation_columns, load_normalized_dataset
from src.metrics import (
    agreement_summary,
    coverage_summary,
    dataset_summary,
    rating_distribution,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": "SGD",
                "dialogue_id": 1,
                "turn_id": 0,
                "role": "USER",
                "action_raw": "THANK_YOU",
                "satisfaction_scores": [3, 3, 3],
                "satisfaction_annotation_count": 3,
                "satisfaction_mode": 3,
                "is_overall": False,
            },
            {
                "dataset": "SGD",
                "dialogue_id": 1,
                "turn_id": 1,
                "role": "SYSTEM",
                "action_raw": "OFFER",
                "satisfaction_scores": [],
                "satisfaction_annotation_count": 0,
                "satisfaction_mode": None,
                "is_overall": False,
            },
            {
                "dataset": "SGD",
                "dialogue_id": 1,
                "turn_id": 2,
                "role": "USER",
                "action_raw": "REQUEST",
                "satisfaction_scores": [2, 3],
                "satisfaction_annotation_count": 2,
                "satisfaction_mode": 2,
                "is_overall": False,
            },
            {
                "dataset": "SGD",
                "dialogue_id": 1,
                "turn_id": 3,
                "role": "USER",
                "action_raw": "UNKNOWN",
                "satisfaction_scores": [5],
                "satisfaction_annotation_count": 1,
                "satisfaction_mode": 5,
                "is_overall": True,
            },
            {
                "dataset": "MWOZ",
                "dialogue_id": 1,
                "turn_id": 0,
                "role": "USER",
                "action_raw": "Hotel-Inform",
                "satisfaction_scores": [1, 4, 4],
                "satisfaction_annotation_count": 3,
                "satisfaction_mode": 4,
                "is_overall": False,
            },
        ]
    )


def test_rating_distribution_separates_turns_and_overall() -> None:
    df = _sample_df()

    turn_distribution = rating_distribution(df, level="turn")
    overall_distribution = rating_distribution(df, level="overall")

    assert turn_distribution["total"].sum() == 3
    assert overall_distribution["total"].sum() == 1
    assert overall_distribution.loc[
        overall_distribution["satisfaction_mode"].eq(5), "total"
    ].sum() == 1


def test_agreement_summary_categories() -> None:
    agreement = agreement_summary(_sample_df(), include_overall=True)

    assert set(agreement["concordancia"]) == {
        "Uma nota",
        "Unanimidade",
        "Discordância leve",
        "Discordância forte",
    }
    assert agreement.loc[
        (agreement["dataset"] == "SGD")
        & (agreement["concordancia"] == "Unanimidade"),
        "total",
    ].item() == 1
    assert agreement.loc[
        (agreement["dataset"] == "MWOZ")
        & (agreement["concordancia"] == "Discordância forte"),
        "total",
    ].item() == 1


def test_dataset_summary_and_coverage_use_expected_units() -> None:
    df = _sample_df()
    summary = dataset_summary(df)
    coverage = coverage_summary(df)

    sgd_summary = summary[summary["dataset"] == "SGD"].iloc[0]
    assert sgd_summary["dialogos"] == 1
    assert sgd_summary["falas_usuario"] == 2
    assert sgd_summary["overall"] == 1
    assert sgd_summary["unknown"] == 0

    sgd_coverage = coverage[coverage["dataset"] == "SGD"].iloc[0]
    assert sgd_coverage["overall"] == 1
    assert sgd_coverage["uma_nota"] == 1


def test_loaded_dataset_counts_match_current_corpus() -> None:
    df = ensure_annotation_columns(load_normalized_dataset())
    summary = dataset_summary(df).set_index("dataset")

    assert summary.loc["SGD", "dialogos"] == 1000
    assert summary.loc["MWOZ", "dialogos"] == 1000
    assert summary.loc["ReDial", "dialogos"] == 1000
    assert summary.loc["CCPE", "dialogos"] == 500
    assert summary.loc["ReDial", "unknown"] == summary.loc["ReDial", "falas_usuario"]
