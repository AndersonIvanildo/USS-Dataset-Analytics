from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import three_class_distribution_chart
from src.loaders import ensure_annotation_columns
from src.metrics import real_user_turns


def render(df: pd.DataFrame) -> None:
    """Renderiza a página de preparação para análise de sentimentos e bot."""
    df = ensure_annotation_columns(df)
    st.subheader("Preparação para sentimentos e bot")
    st.info(
        "A satisfação no USS é contextual. Ela avalia a experiência do usuário com o "
        "histórico da conversa, não apenas a polaridade textual da fala atual."
    )

    st.markdown(
        """
        Esta página traduz a escala original de 1 a 5 para agrupamentos que podem ser úteis
        em projetos futuros. Ela não treina modelos, mas ajuda a pensar em possíveis alvos
        para classificação e em exemplos representativos de cada classe.
        """
    )

    user_turns = real_user_turns(df).dropna(subset=["satisfaction_mode"])

    mapping = user_turns[
        [
            "dataset",
            "text",
            "satisfaction_scores",
            "satisfaction_interpretation",
            "satisfaction_3_classes",
            "satisfaction_binary",
            "action_raw",
        ]
    ].copy()

    st.markdown("#### Distribuição em três classes")
    st.markdown(
        """
        O agrupamento em três classes usa notas 1 e 2 como insatisfeito, nota 3 como
        neutro ou normal, e notas 4 e 5 como satisfeito. Esse mapeamento simplifica a
        leitura, mas a escala original deve ser preservada para análise detalhada.
        """
    )
    three_class_counts = (
        mapping.groupby(["dataset", "satisfaction_3_classes"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )
    st.plotly_chart(
        three_class_distribution_chart(three_class_counts),
        width="stretch",
        key="sentiment_three_class_distribution",
    )
    st.dataframe(three_class_counts, width="stretch", hide_index=True)

    selected_class = st.selectbox(
        "Exemplos por classe",
        sorted(mapping["satisfaction_3_classes"].unique()),
    )
    st.markdown(
        """
        Os exemplos abaixo são úteis para leitura qualitativa. Antes de concluir que uma
        fala expressa sentimento positivo ou negativo, abra a mesma conversa na página de
        inspeção de diálogo e observe o contexto anterior.
        """
    )
    examples = mapping[mapping["satisfaction_3_classes"] == selected_class].head(20)
    st.dataframe(examples, width="stretch", hide_index=True)
