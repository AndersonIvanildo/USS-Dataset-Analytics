from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.config import (
    DATASET_FILES,
    DATASET_LANGUAGES,
    NORMALIZED_DATA_PATH,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)
from src.downloads import ensure_dataset_files
from src.preprocessing import (
    compute_satisfaction_disagreement,
    compute_satisfaction_mean,
    compute_satisfaction_mode,
    label_binary_classes,
    label_three_classes,
    normalize_action,
    normalize_score_sequence,
    parse_satisfaction_scores,
    split_action,
    translate_satisfaction_scores,
)


REQUIRED_NORMALIZED_COLUMNS = {
    "satisfaction_annotation_count",
    "satisfaction_interpretation",
}


def ensure_annotation_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona colunas novas de anotação quando um cache antigo é carregado."""
    normalized = df.copy()

    if "satisfaction_scores" not in normalized.columns:
        normalized["satisfaction_scores"] = [[] for _ in range(len(normalized))]
    else:
        normalized["satisfaction_scores"] = normalized["satisfaction_scores"].apply(
            normalize_score_sequence
        )

    if "satisfaction_annotation_count" not in normalized.columns:
        normalized["satisfaction_annotation_count"] = normalized[
            "satisfaction_scores"
        ].apply(len)

    if "satisfaction_interpretation" not in normalized.columns:
        normalized["satisfaction_interpretation"] = normalized[
            "satisfaction_scores"
        ].apply(translate_satisfaction_scores)

    return normalized


def parse_dataset_file(
    path: Path,
    dataset_name: str,
    language: str,
) -> pd.DataFrame:
    """Lê um arquivo TXT do USS e retorna uma tabela normalizada."""
    rows: list[dict[str, Any]] = []
    dialogue_id = 0
    turn_id = 0
    has_rows_in_dialogue = False

    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.rstrip("\n")

            # Linhas vazias separam diálogos. O contador só avança se o bloco tinha conteúdo.
            if not line.strip():
                if has_rows_in_dialogue:
                    dialogue_id += 1
                    turn_id = 0
                    has_rows_in_dialogue = False
                continue

            parts = line.split("\t")
            role = parts[0].strip() if len(parts) > 0 else ""
            text = parts[1].strip() if len(parts) > 1 else ""
            action_raw = normalize_action(parts[2] if len(parts) > 2 else "")
            satisfaction_raw = parts[3].strip() if len(parts) > 3 else ""
            explanation = parts[4].strip() if len(parts) > 4 else None

            scores = parse_satisfaction_scores(satisfaction_raw)
            satisfaction_mode = compute_satisfaction_mode(scores)
            satisfaction_mean = compute_satisfaction_mean(scores)
            satisfaction_disagreement = compute_satisfaction_disagreement(scores)
            action_group, action_type, action_target = split_action(dataset_name, action_raw)

            rows.append(
                {
                    "dataset": dataset_name,
                    "dialogue_id": dialogue_id,
                    "turn_id": turn_id,
                    "role": role,
                    "text": text,
                    "action_raw": action_raw,
                    "action_group": action_group,
                    "action_type": action_type,
                    "action_target": action_target,
                    "satisfaction_scores": scores,
                    "satisfaction_annotation_count": len(scores),
                    "satisfaction_interpretation": translate_satisfaction_scores(scores),
                    "satisfaction_mode": satisfaction_mode,
                    "satisfaction_mean": satisfaction_mean,
                    "satisfaction_disagreement": satisfaction_disagreement,
                    "is_overall": role == "USER" and text.upper() == "OVERALL",
                    "language": language,
                    "explanation": explanation,
                    "satisfaction_3_classes": label_three_classes(satisfaction_mode),
                    "satisfaction_binary": label_binary_classes(satisfaction_mode),
                }
            )

            turn_id += 1
            has_rows_in_dialogue = True

    return ensure_annotation_columns(pd.DataFrame(rows))


def load_raw_datasets(raw_dir: Path = RAW_DATA_DIR) -> pd.DataFrame:
    """Carrega todos os datasets principais que estiverem disponíveis em disco."""
    frames: list[pd.DataFrame] = []
    missing_files: list[str] = []

    for dataset_name, filename in DATASET_FILES.items():
        path = raw_dir / filename
        if not path.exists():
            missing_files.append(filename)
            continue

        language = DATASET_LANGUAGES[dataset_name]
        frames.append(parse_dataset_file(path, dataset_name, language))

    if not frames:
        files = ", ".join(missing_files)
        raise FileNotFoundError(
            "Nenhum dataset principal foi encontrado em data/raw. "
            f"Arquivos ausentes: {files}."
        )

    return pd.concat(frames, ignore_index=True)


def save_normalized_dataset(df: pd.DataFrame, path: Path = NORMALIZED_DATA_PATH) -> None:
    """Salva o dataframe normalizado em Parquet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def build_normalized_cache(
    raw_dir: Path = RAW_DATA_DIR,
    output_path: Path = NORMALIZED_DATA_PATH,
) -> pd.DataFrame:
    """Reconstrói o cache Parquet a partir dos arquivos TXT em data/raw."""
    ensure_dataset_files(include_optional=False)
    df = load_raw_datasets(raw_dir)
    save_normalized_dataset(df, output_path)
    return df


def load_normalized_dataset() -> pd.DataFrame:
    """Carrega o cache normalizado ou o reconstrói quando necessário."""
    ensure_dataset_files(include_optional=False)

    if not NORMALIZED_DATA_PATH.exists():
        return build_normalized_cache()

    df = pd.read_parquet(NORMALIZED_DATA_PATH)
    if not REQUIRED_NORMALIZED_COLUMNS.issubset(df.columns):
        return build_normalized_cache()

    return ensure_annotation_columns(df)


def ensure_data_directories() -> None:
    """Cria as pastas de dados usadas pelo projeto."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
