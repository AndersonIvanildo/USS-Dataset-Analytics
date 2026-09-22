from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import dialogues_by_dataset_chart, rating_distribution_chart
from src.metrics import summary_metrics


def render(df: pd.DataFrame) -> None:
    """Renderiza a visão geral do corpus."""
    st.subheader("Visão geral")
    st.markdown(
        """
        Esta página resume o recorte selecionado na barra lateral. Use os indicadores
        para conferir o tamanho do corpus carregado e os gráficos para observar como os
        datasets se distribuem e como as notas de satisfação aparecem nas falas reais de
        usuário.
        """
    )

    metrics = summary_metrics(df)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Datasets", metrics["datasets"])
    col2.metric("Diálogos", f"{metrics['dialogues']:,}".replace(",", "."))
    col3.metric("Turnos de usuário", f"{metrics['user_turns']:,}".replace(",", "."))
    col4.metric("Linhas OVERALL", f"{metrics['overall_rows']:,}".replace(",", "."))
    col5.metric("Falas do sistema", f"{metrics['system_turns']:,}".replace(",", "."))

    st.markdown(
        """
        O gráfico de diálogos mostra quantas conversas existem em cada dataset. A
        distribuição de satisfação considera apenas falas reais de usuário, pois as linhas
        `OVERALL` representam outra unidade de análise.
        """
    )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            dialogues_by_dataset_chart(df),
            width="stretch",
            key="overview_dialogues_by_dataset",
        )
    with right:
        st.plotly_chart(
            rating_distribution_chart(df),
            width="stretch",
            key="overview_rating_distribution",
        )

    language_counts = df["language"].value_counts().reset_index()
    language_counts.columns = ["Idioma", "Linhas"]
    st.markdown(
        """
        A tabela abaixo confirma o idioma presente no recorte. No MVP, as análises
        principais usam os datasets em inglês.
        """
    )
    st.dataframe(language_counts, width="stretch", hide_index=True)
