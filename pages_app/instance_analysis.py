from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import (
    action_rating_heatmap,
    dialogue_length_chart,
    disagreement_chart,
    low_satisfaction_chart,
    top_actions_chart,
)
from src.metrics import low_satisfaction_rate


def render(df: pd.DataFrame) -> None:
    """Renderiza análises estatísticas das instâncias."""
    st.subheader("Análise de instâncias")
    st.markdown(
        """
        Esta página reúne análises de padrão. Ela ajuda a observar quais ações aparecem
        com mais frequência, onde existe maior divergência entre anotadores, como os
        diálogos variam em tamanho e quais datasets concentram mais baixa satisfação.
        """
    )

    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            **Ações mais frequentes.** Mostra quais atos de diálogo aparecem mais no
            recorte. Ações muito frequentes podem dominar a análise se não forem lidas
            junto com a distribuição de satisfação.
            """
        )
        st.plotly_chart(
            top_actions_chart(df),
            width="stretch",
            key="analysis_top_actions",
        )

        st.markdown(
            """
            **Divergência entre anotadores.** Valores maiores indicam que os avaliadores
            discordaram mais sobre a satisfação provável do usuário.
            """
        )
        st.plotly_chart(
            disagreement_chart(df),
            width="stretch",
            key="analysis_disagreement",
        )
    with right:
        st.markdown(
            """
            **Tamanho dos diálogos.** O boxplot mostra como o número de turnos varia por
            dataset. Diálogos mais longos podem acumular mais oportunidades de falha ou
            recuperação do sistema.
            """
        )
        st.plotly_chart(
            dialogue_length_chart(df),
            width="stretch",
            key="analysis_dialogue_length",
        )

        st.markdown(
            """
            **Ação por satisfação.** O heatmap cruza ações frequentes com notas de
            satisfação para apontar combinações que merecem leitura qualitativa.
            """
        )
        st.plotly_chart(
            action_rating_heatmap(df),
            width="stretch",
            key="analysis_action_rating_heatmap",
        )

    low_rate = low_satisfaction_rate(df)
    low_rate["low_satisfaction"] = low_rate["low_satisfaction"].round(2)
    st.markdown(
        """
        **Baixa satisfação.** Considera baixa satisfação quando a nota majoritária é menor
        que 3. Essa métrica ajuda a encontrar datasets ou recortes com mais sinais de
        problema na interação.
        """
    )
    st.plotly_chart(
        low_satisfaction_chart(low_rate),
        width="stretch",
        key="analysis_low_satisfaction",
    )
    st.dataframe(
        low_rate.rename(
            columns={
                "dataset": "Dataset",
                "low_satisfaction": "Baixa satisfação (%)",
            }
        ),
        width="stretch",
        hide_index=True,
    )

