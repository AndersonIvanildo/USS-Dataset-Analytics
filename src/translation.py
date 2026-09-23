from __future__ import annotations

from collections.abc import Callable, Sequence


class DialogueTranslationError(RuntimeError):
    """Erro controlado para falhas do serviço de tradução."""


def _unique_texts(texts: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in texts:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            unique.append(text)
    return unique


def translate_dialogue_texts(
    texts: Sequence[str],
    translator_factory: Callable[[], object] | None = None,
) -> dict[str, str]:
    """Traduz uma lista de falas em lote e devolve um mapa texto original -> tradução."""
    unique = _unique_texts(texts)
    if not unique:
        return {}

    if translator_factory is None:
        try:
            from deep_translator import MyMemoryTranslator
        except Exception as error:  # pragma: no cover - depende do ambiente de deploy
            raise DialogueTranslationError(
                "A biblioteca deep-translator não está disponível."
            ) from error

        translator_factory = lambda: MyMemoryTranslator(source="en-US", target="pt-BR")

    try:
        translator = translator_factory()
        translated = translator.translate_batch(unique)  # type: ignore[attr-defined]
    except Exception as error:  # pragma: no cover - serviço externo
        raise DialogueTranslationError(str(error)) from error

    if isinstance(translated, str):
        translated_values = [translated]
    else:
        translated_values = list(translated)

    if len(translated_values) != len(unique):
        raise DialogueTranslationError(
            "O serviço de tradução retornou uma quantidade inesperada de frases."
        )

    return dict(zip(unique, translated_values, strict=True))
