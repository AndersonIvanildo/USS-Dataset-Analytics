from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from statistics import mean, pstdev


UNKNOWN_ACTION = "UNKNOWN"

SATISFACTION_LABELS = {
    1: "muito insatisfeito",
    2: "insatisfeito",
    3: "normal",
    4: "satisfeito",
    5: "muito satisfeito",
}


def parse_satisfaction_scores(raw_value: str | None) -> list[int]:
    """Converte a anotação bruta de satisfação em uma lista de notas inteiras."""
    if raw_value is None:
        return []

    cleaned = str(raw_value).strip()
    if not cleaned:
        return []

    scores: list[int] = []
    for value in cleaned.split(","):
        value = value.strip()
        if value:
            scores.append(int(value))
    return scores


def compute_satisfaction_mode(scores: list[int]) -> int | None:
    """Calcula a nota majoritária e escolhe a menor nota em caso de empate."""
    if not scores:
        return None

    counts = Counter(scores)
    max_count = max(counts.values())
    tied_scores = [score for score, count in counts.items() if count == max_count]
    return min(tied_scores)


def compute_satisfaction_mean(scores: list[int]) -> float | None:
    """Calcula a média das notas de satisfação."""
    if not scores:
        return None
    return round(mean(scores), 2)


def compute_satisfaction_disagreement(scores: list[int]) -> float | None:
    """Calcula a divergência entre anotadores pelo desvio padrão populacional."""
    if not scores:
        return None
    if len(scores) == 1:
        return 0.0
    return round(pstdev(scores), 2)


def normalize_score_sequence(scores: object) -> list[int]:
    """Normaliza listas, tuplas ou arrays de notas para uma lista de inteiros."""
    if scores is None:
        return []

    if isinstance(scores, float) and scores != scores:
        return []

    if isinstance(scores, str):
        return parse_satisfaction_scores(scores)

    if isinstance(scores, Iterable):
        return [int(score) for score in scores]

    return []


def translate_satisfaction_scores(scores: object) -> str:
    """Traduz a lista de notas de satisfação para uma leitura em palavras."""
    normalized_scores = normalize_score_sequence(scores)
    if not normalized_scores:
        return "Sem anotação de satisfação."

    translated_scores = [
        f"anotador {index}: {score} ({SATISFACTION_LABELS.get(score, 'nota desconhecida')})"
        for index, score in enumerate(normalized_scores, start=1)
    ]
    score_count = len(normalized_scores)
    score_word = "avaliação" if score_count == 1 else "avaliações"
    return f"{score_count} {score_word}: " + "; ".join(translated_scores) + "."


def normalize_action(action_raw: str | None) -> str:
    """Normaliza ações vazias para uma categoria explícita."""
    action = "" if action_raw is None else str(action_raw).strip()
    return action if action else UNKNOWN_ACTION


def split_action(dataset_name: str, action_raw: str) -> tuple[str, str | None, str | None]:
    """Extrai agrupamentos úteis a partir da ação original de cada dataset."""
    action = normalize_action(action_raw)

    if action == UNKNOWN_ACTION:
        return UNKNOWN_ACTION, None, None

    if dataset_name == "CCPE" and "+" in action:
        action_type, action_target = action.split("+", 1)
        return action_type, action_type, action_target

    if dataset_name == "MWOZ" and "-" in action:
        domain, act = action.split("-", 1)
        return domain, domain, act

    return action, action, None


def label_three_classes(score: int | None) -> str:
    """Mapeia a escala de 5 pontos para três classes interpretáveis."""
    if score is None:
        return "Sem nota"
    if score <= 2:
        return "Insatisfeito"
    if score == 3:
        return "Neutro ou normal"
    return "Satisfeito"


def label_binary_classes(score: int | None) -> str:
    """Mapeia a escala de 5 pontos para baixa satisfação ou não baixa satisfação."""
    if score is None:
        return "Sem nota"
    if score < 3:
        return "Baixa satisfação"
    return "Não baixa satisfação"
