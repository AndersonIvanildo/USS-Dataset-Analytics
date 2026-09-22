from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import (
    agreement_chart,
    dialogue_length_chart,
    dialogues_by_dataset_chart,
    satisfaction_distribution_chart,
    top_actions_chart,
)
from src.config import RATING_LABELS
from src.metrics import (
    agreement_summary,
    coverage_summary,
    dataset_summary,
    summary_metrics,
)


def _format_number(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(value):,}".replace(",", ".")


def _rating_label(value: object) -> str:
    if value == "Sem nota":
        return "Sem nota"
    score = int(value)
    return f"{score} · {RATING_LABELS[score]}"


def _render_dataset_cards(summary: pd.DataFrame) -> None:
    st.markdown("#### O que cada dataset traz para o acervo carregado?")
    st.markdown(
        """
        Os quatro datasets têm origens e formatos de anotação diferentes. Os cartões
        abaixo mostram volume, cobertura e alguns sinais que ajudam a interpretar os
        gráficos seguintes sem transformar as bases em ranking de qualidade.
        """
    )

    for index in range(0, len(summary), 2):
        cols = st.columns(2)
        for column, (_, row) in zip(cols, summary.iloc[index : index + 2].iterrows()):
            with column:
                with st.container(border=True):
                    st.markdown(f"#### {row['dataset']}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Diálogos", _format_number(row["dialogos"]))
                    col2.metric("Falas de usuário", _format_number(row["falas_usuario"]))
                    col3.metric("Falas do sistema", _format_number(row["falas_sistema"]))

                    col4, col5, col6 = st.columns(3)
                    col4.metric("OVERALL", _format_number(row["overall"]))
                    col5.metric(
                        "Anotações distintas",
                        _format_number(row["anotacoes_distintas"]),
                    )
                    col6.metric("UNKNOWN", _format_number(row["unknown"]))

                    st.caption(
                        "Mediana de falas por diálogo: "
                        f"{_format_number(row['mediana_falas_dialogo'])}. "
                        "Nota mais frequente nas falas de usuário: "
                        f"{_rating_label(row['nota_mais_frequente'])}."
                    )


def _render_coverage_table(df: pd.DataFrame) -> None:
    coverage = coverage_summary(df)
    if coverage.empty:
        return

    coverage = coverage.rename(
        columns={
            "dataset": "Dataset",
            "registros_user": "Registros USER",
            "falas_reais": "Falas reais",
            "overall": "OVERALL",
            "sem_nota": "Sem nota",
            "uma_nota": "Uma nota",
            "tres_ou_mais_notas": "Três ou mais notas",
            "unknown": "UNKNOWN",
        }
    )
    st.dataframe(coverage, width="stretch", hide_index=True)


def _render_agreement_table(df: pd.DataFrame) -> None:
    agreement = agreement_summary(df, include_overall=True).copy()
    if agreement.empty:
        return

    agreement["percentual"] = agreement["percentual"].round(2)
    agreement = agreement.rename(
        columns={
            "dataset": "Dataset",
            "concordancia": "Concordância",
            "total": "Registros",
            "percentual": "% dos registros avaliados",
        }
    )
    st.dataframe(agreement, width="stretch", hide_index=True)


def render(df: pd.DataFrame) -> None:
    """Renderiza a visão geral analítica do corpus."""
    st.subheader("Visão geral")
    st.markdown(
        """
        Esta página reúne as perguntas principais para começar a leitura do USS. Ela
        separa falas de usuário, falas do sistema e `OVERALL`, porque cada uma dessas
        unidades responde a uma pergunta diferente sobre o corpus.
        """
    )

    metrics = summary_metrics(df)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Datasets", metrics["datasets"])
    col2.metric("Diálogos", _format_number(metrics["dialogues"]))
    col3.metric("Falas de usuário", _format_number(metrics["user_turns"]))
    col4.metric("OVERALL", _format_number(metrics["overall_rows"]))
    col5.metric("Falas do sistema", _format_number(metrics["system_turns"]))

    summary = dataset_summary(df)
    _render_dataset_cards(summary)

    st.markdown("#### Como o acervo se divide entre as bases?")
    st.markdown(
        """
        A quantidade de diálogos define o tamanho de cada subconjunto carregado. Esse
        gráfico é uma checagem de composição, não uma medida de desempenho dos sistemas
        que originaram as conversas.
        """
    )
    st.plotly_chart(
        dialogues_by_dataset_chart(df),
        width="stretch",
        key="overview_dialogues_by_dataset",
    )

    st.markdown("#### Como as notas se distribuem?")
    st.markdown(
        """
        A satisfação por fala mostra como os usuários foram avaliados ao longo das
        conversas. A satisfação geral usa apenas `OVERALL`, uma linha por diálogo. As
        duas leituras ficam separadas para não misturar momentos específicos da conversa
        com o julgamento final.
        """
    )
    measure = st.radio(
        "Medida dos gráficos de satisfação",
        ["Percentual", "Contagem"],
        horizontal=True,
    )
    percent = measure == "Percentual"

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            satisfaction_distribution_chart(df, level="turn", percent=percent),
            width="stretch",
            key=f"overview_turn_satisfaction_{percent}",
        )
    with right:
        st.plotly_chart(
            satisfaction_distribution_chart(df, level="overall", percent=percent),
            width="stretch",
            key=f"overview_overall_satisfaction_{percent}",
        )

    st.markdown("#### Quantas falas os diálogos têm?")
    st.markdown(
        """
        O comprimento dos diálogos ajuda a comparar a estrutura das conversas. Diálogos
        mais longos não são automaticamente melhores ou piores, mas podem indicar tarefas
        com mais etapas, mais correções ou mais oportunidades para mudança de satisfação.
        """
    )
    st.plotly_chart(
        dialogue_length_chart(df),
        width="stretch",
        key="overview_dialogue_length",
    )

    st.markdown("#### Onde os anotadores mais concordam ou discordam?")
    st.markdown(
        """
        A concordância considera as notas individuais registradas em cada linha avaliada.
        Registros com apenas uma nota ficam separados, porque eles não permitem medir
        acordo entre pessoas. Discordância forte indica distância maior que um ponto na
        escala de 1 a 5.
        """
    )
    st.plotly_chart(
        agreement_chart(df, include_overall=True),
        width="stretch",
        key="overview_agreement",
    )
    _render_agreement_table(df)

    st.markdown("#### Quais anotações aparecem mais no conjunto?")
    st.markdown(
        """
        As anotações ajudam a entender que tipo de movimento aparece nas falas de
        usuário. Como cada dataset usa vocabulário próprio, esse gráfico serve como
        ponto de partida; a interpretação detalhada fica na página de anotações.
        """
    )
    st.plotly_chart(
        top_actions_chart(df),
        width="stretch",
        key="overview_top_actions",
    )

    st.markdown("#### Como está a cobertura dos dados?")
    st.markdown(
        """
        A tabela abaixo mostra sinais de cobertura: registros sem nota, registros com uma
        nota, registros com três ou mais notas e presença de `UNKNOWN`. Esses números
        ajudam a separar lacunas de anotação de categorias semânticas reais.
        """
    )
    _render_coverage_table(df)
