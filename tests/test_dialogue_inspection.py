import pandas as pd

from pages_app.dialogue_inspection import _message_with_translation, _metadata_block


def test_metadata_block_starts_with_html_tag() -> None:
    row = pd.Series(
        {
            "action_raw": "ENTITY_NAME+MOVIE_OR_SERIES",
            "satisfaction_scores": [4, 3, 4],
        }
    )

    html = _metadata_block(row)

    assert html.startswith("<div")
    assert "\n    <div" not in html
    assert "Anotador 1" in html
    assert "[4, 3, 4]" not in html


def test_message_with_translation_adds_help_tooltip() -> None:
    html = _message_with_translation("Hello", "Olá")

    assert "translation-help" in html
    assert "Olá" in html
    assert "Hello" in html
