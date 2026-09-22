import pandas as pd

from src.metrics import annotation_frequencies, annotation_rating_distribution


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": "MWOZ",
                "dialogue_id": 1,
                "turn_id": 0,
                "role": "USER",
                "action_raw": "Hotel-Inform",
                "satisfaction_mode": 3,
                "is_overall": False,
            },
            {
                "dataset": "MWOZ",
                "dialogue_id": 1,
                "turn_id": 1,
                "role": "SYSTEM",
                "action_raw": "Hotel-Inform",
                "satisfaction_mode": None,
                "is_overall": False,
            },
            {
                "dataset": "MWOZ",
                "dialogue_id": 1,
                "turn_id": 2,
                "role": "USER",
                "action_raw": "Hotel-Inform",
                "satisfaction_mode": 4,
                "is_overall": False,
            },
            {
                "dataset": "MWOZ",
                "dialogue_id": 1,
                "turn_id": 3,
                "role": "USER",
                "action_raw": "Restaurant-Request",
                "satisfaction_mode": 2,
                "is_overall": False,
            },
            {
                "dataset": "MWOZ",
                "dialogue_id": 1,
                "turn_id": 4,
                "role": "USER",
                "action_raw": "UNKNOWN",
                "satisfaction_mode": 3,
                "is_overall": False,
            },
            {
                "dataset": "MWOZ",
                "dialogue_id": 1,
                "turn_id": 5,
                "role": "USER",
                "action_raw": "UNKNOWN",
                "satisfaction_mode": 5,
                "is_overall": True,
            },
        ]
    )


def test_annotation_frequencies_use_real_user_turns_only() -> None:
    frequencies = annotation_frequencies(_sample_df())

    assert frequencies["total"].sum() == 4
    assert frequencies.loc[0, "action_raw"] == "Hotel-Inform"
    assert frequencies.loc[0, "total"] == 2


def test_annotation_frequencies_can_hide_unknown() -> None:
    frequencies = annotation_frequencies(_sample_df(), include_unknown=False)

    assert "UNKNOWN" not in frequencies["action_raw"].tolist()
    assert frequencies["total"].sum() == 3


def test_annotation_rating_distribution_has_fixed_rating_columns() -> None:
    counts, percentages = annotation_rating_distribution(
        _sample_df(),
        annotations=["Hotel-Inform", "Restaurant-Request"],
    )

    assert counts.columns.tolist() == [1, 2, 3, 4, 5]
    assert counts.loc["Hotel-Inform", 3] == 1
    assert counts.loc["Hotel-Inform", 4] == 1
    assert percentages.loc["Hotel-Inform"].sum() == 100
    assert percentages.loc["Restaurant-Request", 2] == 100
