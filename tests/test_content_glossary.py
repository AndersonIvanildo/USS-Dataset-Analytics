from src.content import explain_annotation


def test_annotation_glossary_known_examples() -> None:
    thank_you = explain_annotation("SGD", "THANK_YOU")
    hotel = explain_annotation("MWOZ", "Hotel-Inform")
    ccpe = explain_annotation("CCPE", "ENTITY_OTHER+MOVIE_OR_SERIES")

    assert "agradece" in thank_you.meaning
    assert "Domínio Hotel" in hotel.meaning
    assert "ENTITY_OTHER" in ccpe.meaning
    assert "MOVIE_OR_SERIES" in ccpe.meaning


def test_annotation_glossary_unknown_and_fallback() -> None:
    redial_unknown = explain_annotation("ReDial", "UNKNOWN")
    fallback = explain_annotation("SGD", "SOMETHING_NEW")

    assert "Ausência de ação" in redial_unknown.meaning
    assert fallback.meaning == "Código original preservado do dataset."
