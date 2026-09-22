from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import rating_distribution_chart
from src.config import EXPECTED_DIALOGUE_COUNTS
from src.loaders import ensure_annotation_columns
from src.metrics import real_user_turns


def render(df: pd.DataFrame) -> None:
    """Renderiza comparações entre os datasets em inglês."""
    df = ensure_annotation_columns(df)
    st.subheader("Comparação entre datasets")
    st.markdown(
        """
        Esta página compara os datasets em inglês do USS. A comparação ajuda a mostrar que
        os arquivos pertencem ao mesmo projeto, mas têm domínios, ações e formatos de
        anotação diferentes.
        """
    )

    user_turns = real_user_turns(df)
    comparison = (
        user_turns.groupby("dataset")
        .agg(
            turnos=("turn_id", "size"),
            anotacoes_registradas=("satisfaction_annotation_count", "sum"),
            acoes_desconhecidas=("action_raw", lambda values: (values == "UNKNOWN").sum()),
        )
        .reset_index()
    )
    comparison["dialogos_esperados"] = comparison["dataset"].map(EXPECTED_DIALOGUE_COUNTS)

    st.markdown(
        """
        A tabela resume turnos reais de usuário, quantidade total de anotações de
        satisfação registradas e quantidade de ações desconhecidas. No ReDial, ações
        desconhecidas são esperadas no arquivo principal do USS.
        """
    )
    st.dataframe(comparison, width="stretch", hide_index=True)

    st.markdown(
        """
        O gráfico abaixo permite comparar o desbalanceamento das notas. Em geral, a classe
        3 aparece com muita força, o que é importante para qualquer análise futura.
        """
    )
    st.plotly_chart(
        rating_distribution_chart(df),
        width="stretch",
        key="comparison_rating_distribution",
    )
