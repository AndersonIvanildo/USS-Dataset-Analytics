from pathlib import Path

from src.loaders import ensure_annotation_columns, parse_dataset_file


def test_parse_dataset_file_detects_overall_and_unknown_action(tmp_path: Path) -> None:
    dataset_file = tmp_path / "SGD.txt"
    dataset_file.write_text(
        "\n".join(
            [
                "USER\tI need a restaurant.\tINFORM_INTENT\t2,3,3",
                "SYSTEM\tWhich city?\tREQUEST",
                "USER\tOVERALL\t\t3,4,3",
                "",
            ]
        ),
        encoding="utf-8",
    )

    df = parse_dataset_file(dataset_file, "SGD", "en")

    assert len(df) == 3
    assert df.loc[0, "satisfaction_scores"] == [2, 3, 3]
    assert df.loc[0, "satisfaction_mode"] == 3
    assert df.loc[1, "action_raw"] == "REQUEST"
    assert bool(df.loc[2, "is_overall"]) is True
    assert df.loc[2, "action_raw"] == "UNKNOWN"


def test_ensure_annotation_columns_updates_old_cache_shape(tmp_path: Path) -> None:
    dataset_file = tmp_path / "SGD.txt"
    dataset_file.write_text(
        "USER\tI need a restaurant.\tINFORM_INTENT\t3,3,4\n",
        encoding="utf-8",
    )
    old_df = parse_dataset_file(dataset_file, "SGD", "en").drop(
        columns=["satisfaction_annotation_count", "satisfaction_interpretation"]
    )

    updated_df = ensure_annotation_columns(old_df)

    assert updated_df.loc[0, "satisfaction_annotation_count"] == 3
    assert "4 (satisfeito)" in updated_df.loc[0, "satisfaction_interpretation"]
