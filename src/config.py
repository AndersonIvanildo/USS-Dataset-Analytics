from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
NORMALIZED_DATA_PATH = PROCESSED_DATA_DIR / "uss_normalized.parquet"

BASE_DATA_URL = (
    "https://raw.githubusercontent.com/"
    "sunnweiwei/user-satisfaction-simulation/master/dataset"
)

DATASET_FILES = {
    "SGD": "SGD.txt",
    "MWOZ": "MWOZ.txt",
    "ReDial": "ReDial.txt",
    "CCPE": "CCPE.txt",
}

OPTIONAL_FILES = {
    "ReDial-action": "ReDial-action.txt",
    "JDDC": "JDDC.txt",
    "JDDC-ActionList": "JDDC-ActionList.txt",
}

DATASET_LANGUAGES = {
    "SGD": "en",
    "MWOZ": "en",
    "ReDial": "en",
    "CCPE": "en",
    "JDDC": "zh",
}

RATING_LABELS = {
    1: "Muito insatisfeito",
    2: "Insatisfeito",
    3: "Normal",
    4: "Satisfeito",
    5: "Muito satisfeito",
}

EXPECTED_DIALOGUE_COUNTS = {
    "SGD": 1000,
    "MWOZ": 1000,
    "ReDial": 1000,
    "CCPE": 500,
}
