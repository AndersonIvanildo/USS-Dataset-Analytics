from __future__ import annotations

import pandas as pd
import streamlit as st

from pages_app import (
    dataset_annotations,
    dataset_comparison,
    dialogue_inspection,
    guide,
    instance_analysis,
    overview,
    sentiment_preparation,
)
from src.config import RATING_LABELS
from src.loaders import ensure_annotation_columns, load_normalized_dataset


st.set_page_config(
    page_title="Explorador USS",
    page_icon='https://images.icon-icons.com/1502/PNG/512/officedatabase_103574.png',
    layout="wide",
)


def apply_custom_styles() -> None:
    """Aplica estilos leves aos blocos explicativos da interface."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Comfortaa:wght@300;400;500;600;700&display=swap');
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
            font-family: "Comfortaa", sans-serif;
        }
        .stMarkdown, .stText, .stCaption, .stDataFrame, .stMetric, button, input, textarea {
            font-family: "Comfortaa", sans-serif;
        }
        code, pre {
            font-family: "Source Code Pro", monospace;
        }
        .guide-card {
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 8px;
            padding: 1rem;
            background: rgba(250, 250, 250, 0.7);
            height: 100%;
            box-sizing: border-box;
        }
        .guide-card h4 {
            margin: 0 0 0.35rem 0;
        }
        .dataset-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            align-items: stretch;
        }
        .source-help {
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.15rem;
            height: 1.15rem;
            margin-left: 0.25rem;
            border-radius: 50%;
            border: 1px solid rgba(37, 99, 235, 0.55);
            color: #1d4ed8;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: help;
        }
        .source-help .source-tooltip {
            visibility: hidden;
            opacity: 0;
            position: absolute;
            z-index: 1000;
            left: 50%;
            bottom: 135%;
            transform: translateX(-50%);
            width: max-content;
            max-width: 28rem;
            padding: 0.55rem 0.65rem;
            border-radius: 6px;
            background: #111827;
            color: #ffffff;
            font-size: 0.82rem;
            line-height: 1.35;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.22);
            white-space: normal;
        }
        .source-help:hover .source-tooltip {
            visibility: visible;
            opacity: 1;
        }
        .overall-callout {
            border-left: 4px solid #2563eb;
            background: rgba(37, 99, 235, 0.08);
            padding: 0.85rem 1rem;
            border-radius: 6px;
            margin: 1rem 0;
        }
        .turn-meta {
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-radius: 8px;
            padding: 0.65rem 0.75rem;
            margin-top: 0.65rem;
            background: rgba(250, 250, 250, 0.72);
        }
        .turn-meta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            align-items: center;
            margin-top: 0.35rem;
        }
        .meta-label {
            color: rgba(49, 51, 63, 0.68);
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 0.35rem;
            text-transform: uppercase;
        }
        .rating-chip {
            display: inline-flex;
            align-items: center;
            border: 1px solid rgba(37, 99, 235, 0.20);
            border-radius: 999px;
            padding: 0.22rem 0.55rem;
            background: rgba(37, 99, 235, 0.08);
            color: #1f2937;
            font-size: 0.86rem;
            line-height: 1.35;
        }
        .selected-turn {
            border-color: rgba(37, 99, 235, 0.55);
            background: rgba(37, 99, 235, 0.10);
        }
        @media (max-width: 900px) {
            .dataset-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner="Carregando, baixando se necessário, e normalizando os datasets...")
def load_data() -> pd.DataFrame:
    """Carrega o dataframe normalizado usado pela interface."""
    return ensure_annotation_columns(load_normalized_dataset())


def show_missing_data_help(error: Exception) -> None:
    """Exibe instruções quando os arquivos brutos ainda não foram baixados."""
    st.error("Não foi possível carregar os arquivos do dataset.")
    st.info(
        "O app tenta usar os arquivos em `data/raw` e baixa automaticamente se eles "
        "não estiverem disponíveis. Verifique a conexão com a internet ou execute "
        "`uv run python scripts/download_data.py`."
    )
    st.code(str(error), language="text")


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica filtros globais escolhidos na barra lateral."""
    st.sidebar.header("Filtros")

    datasets = sorted(df["dataset"].unique())
    selected_datasets = st.sidebar.multiselect(
        "Datasets",
        datasets,
        default=datasets,
    )

    include_overall = st.sidebar.checkbox("Incluir linhas OVERALL", value=False)
    include_system = st.sidebar.checkbox("Incluir falas do sistema", value=True)

    ratings = sorted(
        int(value) for value in df["satisfaction_mode"].dropna().unique().tolist()
    )
    selected_ratings = st.sidebar.multiselect(
        "Notas de satisfação",
        ratings,
        default=ratings,
        format_func=lambda value: f"{value} · {RATING_LABELS.get(value, '')}",
    )

    filtered = df[df["dataset"].isin(selected_datasets)].copy()

    if not include_overall:
        filtered = filtered[~filtered["is_overall"]]

    if not include_system:
        filtered = filtered[filtered["role"] != "SYSTEM"]

    # Linhas do sistema não têm satisfação, por isso são preservadas quando o filtro permite.
    if selected_ratings:
        filtered = filtered[
            filtered["satisfaction_mode"].isin(selected_ratings)
            | filtered["satisfaction_mode"].isna()
        ]

    return filtered


def main() -> None:
    """Executa o aplicativo Streamlit."""
    apply_custom_styles()
    st.title("Explorador USS")
    st.caption(
        "Interface para estudar satisfação do usuário em datasets de diálogo "
        "orientados a tarefa."
    )

    try:
        df = load_data()
    except Exception as error:
        show_missing_data_help(error)
        return

    filtered = filter_dataframe(df)
    filtered = ensure_annotation_columns(filtered)

    if filtered.empty:
        st.warning("Nenhuma linha encontrada para os filtros selecionados.")
        return

    pages = [
        st.Page(
            lambda: guide.render(df),
            title="Guia do projeto",
            url_path="guia",
            default=True,
        ),
        st.Page(
            lambda: overview.render(filtered),
            title="Visão geral",
            url_path="visao-geral",
        ),
        st.Page(
            lambda: dialogue_inspection.render(df),
            title="Dataset e diálogos",
            url_path="inspecao-dialogo",
        ),
        st.Page(
            lambda: instance_analysis.render(filtered),
            title="Análise de instâncias",
            url_path="analise-instancias",
        ),
        st.Page(
            lambda: dataset_annotations.render(filtered),
            title="Anotações por dataset",
            url_path="anotacoes-dataset",
        ),
        st.Page(
            lambda: dataset_comparison.render(filtered),
            title="Comparação",
            url_path="comparacao",
        ),
        st.Page(
            lambda: sentiment_preparation.render(filtered),
            title="Sentimentos e bot",
            url_path="sentimentos-bot",
        ),
    ]
    navigation = st.navigation(
        pages,
        position="top",
    )
    navigation.run()


if __name__ == "__main__":
    main()
