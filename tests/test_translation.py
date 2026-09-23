import pytest

from src.translation import DialogueTranslationError, translate_dialogue_texts


class FakeTranslator:
    def __init__(self) -> None:
        self.calls = 0

    def translate_batch(self, texts: list[str]) -> list[str]:
        self.calls += 1
        return [f"pt:{text}" for text in texts]


def test_translate_dialogue_texts_uses_batch_and_deduplicates() -> None:
    translator = FakeTranslator()

    result = translate_dialogue_texts(
        ["Hello", "Hello", "I need a hotel"],
        translator_factory=lambda: translator,
    )

    assert translator.calls == 1
    assert result == {
        "Hello": "pt:Hello",
        "I need a hotel": "pt:I need a hotel",
    }


def test_translate_dialogue_texts_rejects_unexpected_batch_size() -> None:
    class BrokenTranslator:
        def translate_batch(self, texts: list[str]) -> list[str]:
            return ["só uma tradução"]

    with pytest.raises(DialogueTranslationError):
        translate_dialogue_texts(
            ["Hello", "I need a hotel"],
            translator_factory=BrokenTranslator,
        )
