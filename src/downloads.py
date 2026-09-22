from __future__ import annotations

from pathlib import Path

import requests

from src.config import BASE_DATA_URL, DATASET_FILES, OPTIONAL_FILES, RAW_DATA_DIR


def download_file(filename: str, overwrite: bool = False) -> Path:
    """Baixa um arquivo oficial do USS para a pasta data/raw."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = RAW_DATA_DIR / filename

    if destination.exists() and not overwrite:
        return destination

    url = f"{BASE_DATA_URL}/{filename}"
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination


def ensure_dataset_files(include_optional: bool = True) -> list[Path]:
    """Garante que os arquivos oficiais estejam disponíveis dentro do projeto."""
    files = DATASET_FILES.copy()
    if include_optional:
        files.update(OPTIONAL_FILES)

    return [download_file(filename) for filename in files.values()]

