from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import annotation_frequency_chart, annotation_rating_heatmap
from src.loaders import ensure_annotation_columns
from src.metrics import annotation_frequencies, real_user_turns


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def render(df: pd.DataFrame) -> None:
    """Renderiza gráficos de anotações e notas dentro de cada dataset."""
    df = ensure_annotation_columns(df)
    st.subheader("Anotações por dataset")
    st.markdown(
        """
        Esta página mostra como as anotações aparecem dentro de um dataset específico e
        como as notas de satisfação se distribuem em cada anotação. A unidade de análise
        é a fala real de usuário: linhas `OVERALL` e falas do sistema não entram nesses
        gráficos.
        """
    )

    user_turns = real_user_turns(df)
    if user_turns.empty:
        st.warning("Não há falas reais de usuário no recorte atual.")
        return

    datasets = sorted(user_turns["dataset"].unique())
    default_index = datasets.index("MWOZ") if "MWOZ" in datasets else 0

    control_left, control_right = st.columns([2, 1])
    with control_left:
        dataset = st.selectbox(
            "Dataset",
            datasets,
            index=default_index,
            help="Os gráficos respeitam os filtros globais da barra lateral.",
        )
    with control_right:
        limit = st.slider(
            "Top anotações",
            min_value=5,
            max_value=30,
            value=15,
            step=1,
        )

    include_unknown = st.checkbox(
        "Incluir UNKNOWN",
        value=True,
        help=(
            "UNKNOWN representa ausência de anotação identificada no arquivo principal, "
            "não uma categoria semântica comum a todos os datasets."
        ),
    )

    dataset_df = df[df["dataset"] == dataset].copy()
    dataset_user_turns = real_user_turns(dataset_df)
    chart_data = dataset_user_turns
    if not include_unknown:
        chart_data = chart_data[chart_data["action_raw"] != "UNKNOWN"]

    if chart_data.empty:
        st.warning("Nenhuma anotação disponível depois dos filtros escolhidos.")
        return

    scored_turns = chart_data["satisfaction_mode"].notna().sum()
    unique_annotations = chart_data["action_raw"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Diálogos no recorte", _format_number(dataset_df["dialogue_id"].nunique()))
    col2.metric("Falas analisadas", _format_number(len(chart_data)))
    col3.metric("Anotações distintas", _format_number(unique_annotations))
    col4.metric("Falas com nota", _format_number(int(scored_turns)))

    st.markdown(
        """
        **Como ler.** Em SGD, códigos como `THANK_YOU` são atos de diálogo. Em MWOZ,
        anotações como `Hotel-Inform` combinam domínio e ato. Em CCPE, códigos como
        `ENTITY_OTHER+MOVIE_OR_SERIES` combinam tipo de marcação e entidade. No ReDial,
        o arquivo principal do USS não traz ações, por isso é esperado encontrar
        `UNKNOWN`.
        """
    )

    st.plotly_chart(
        annotation_frequency_chart(
            dataset_df,
            dataset_name=dataset,
            limit=limit,
            include_unknown=include_unknown,
        ),
        width="stretch",
        key=f"annotation_frequency_{dataset}_{limit}_{include_unknown}",
    )
    st.caption(
        "Unidade: falas reais de usuário. Denominador: falas do dataset selecionado no "
        "recorte atual. Passe o mouse para ver contagem e percentual."
    )

    st.plotly_chart(
        annotation_rating_heatmap(
            dataset_df,
            dataset_name=dataset,
            limit=limit,
            include_unknown=include_unknown,
        ),
        width="stretch",
        key=f"annotation_heatmap_{dataset}_{limit}_{include_unknown}",
    )
    st.caption(
        "Cada linha do mapa de calor soma 100% entre as notas 1 a 5. A cor mostra a "
        "porcentagem das falas daquela anotação que recebeu cada nota mais frequente."
    )

    frequencies = annotation_frequencies(
        dataset_df,
        limit=limit,
        include_unknown=include_unknown,
    )
    frequencies = frequencies.rename(
        columns={
            "action_raw": "Anotação",
            "total": "Falas",
            "percentual": "% das falas",
        }
    )
    frequencies["% das falas"] = frequencies["% das falas"].round(2)

    st.markdown("**Tabela do recorte mostrado**")
    st.dataframe(frequencies, width="stretch", hide_index=True)

    decomposition = (
        chart_data[
            ["action_raw", "action_group", "action_type", "action_target"]
        ]
        .drop_duplicates()
        .sort_values("action_raw")
        .rename(
            columns={
                "action_raw": "Anotação original",
                "action_group": "Grupo",
                "action_type": "Tipo",
                "action_target": "Alvo",
            }
        )
    )
    st.markdown("**Decomposição das anotações**")
    st.dataframe(decomposition, width="stretch", hide_index=True)
