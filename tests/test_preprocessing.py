from src.preprocessing import (
    compute_satisfaction_disagreement,
    compute_satisfaction_mean,
    compute_satisfaction_mode,
    normalize_action,
    normalize_score_sequence,
    parse_satisfaction_scores,
    split_action,
    translate_satisfaction_scores,
)


def test_parse_satisfaction_scores() -> None:
    assert parse_satisfaction_scores("2,3,3") == [2, 3, 3]
    assert parse_satisfaction_scores("") == []
    assert parse_satisfaction_scores(None) == []


def test_satisfaction_statistics() -> None:
    scores = [2, 3, 3]

    assert compute_satisfaction_mode(scores) == 3
    assert compute_satisfaction_mean(scores) == 2.67
    assert compute_satisfaction_disagreement([3, 3, 3]) == 0.0


def test_translate_satisfaction_scores() -> None:
    translated = translate_satisfaction_scores([3, 3, 4])

    assert "3 avaliações" in translated
    assert "3 (normal)" in translated
    assert "4 (satisfeito)" in translated


def test_translate_satisfaction_scores_accepts_iterables() -> None:
    translated = translate_satisfaction_scores((3, 4))

    assert translated.startswith("2 avaliações")
    assert normalize_score_sequence((3, 4)) == [3, 4]


def test_mode_uses_lowest_score_when_tied() -> None:
    assert compute_satisfaction_mode([2, 3, 4]) == 2


def test_normalize_empty_action() -> None:
    assert normalize_action("") == "UNKNOWN"
    assert normalize_action("   ") == "UNKNOWN"
    assert normalize_action("REQUEST") == "REQUEST"


def test_split_ccpe_action() -> None:
    group, action_type, action_target = split_action(
        "CCPE",
        "ENTITY_PREFERENCE+MOVIE_OR_SERIES",
    )

    assert group == "ENTITY_PREFERENCE"
    assert action_type == "ENTITY_PREFERENCE"
    assert action_target == "MOVIE_OR_SERIES"
