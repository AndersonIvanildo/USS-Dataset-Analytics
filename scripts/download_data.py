from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.downloads import ensure_dataset_files


def main() -> None:
    """Baixa os arquivos principais e auxiliares usados pelo explorador."""
    for path in ensure_dataset_files(include_optional=True):
        print(f"Arquivo disponível: {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
