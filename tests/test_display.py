import pandas as pd

from src.display import dataframe_for_display, format_cell_for_display


def test_format_cell_for_display_converts_lists_and_none() -> None:
    assert format_cell_for_display([4, 3, 4]) == "[4, 3, 4]"
    assert format_cell_for_display(None) == "None"


def test_dataframe_for_display_makes_object_columns_arrow_friendly() -> None:
    df = pd.DataFrame(
        {
            "campo": ["satisfaction_scores", "annotation_status"],
            "valor": [[4, 3, 4], "anotação disponível"],
        }
    )

    display = dataframe_for_display(df)

    assert display.loc[0, "valor"] == "[4, 3, 4]"
    assert not isinstance(display.loc[0, "valor"], list)
