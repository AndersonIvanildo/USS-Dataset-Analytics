from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import annotation_frequency_chart, annotation_rating_heatmap
from src.config import RATING_LABELS
from src.content import explain_annotation
from src.loaders import ensure_annotation_columns
from src.metrics import annotation_frequencies, real_user_turns


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _glossary_table(dataset: str, actions: list[str]) -> pd.DataFrame:
    rows = []
    for action in actions:
        guide = explain_annotation(dataset, action)
        rows.append(
            {
                "Anotação": guide.code,
                "Explicação": guide.meaning,
                "Como ler": guide.how_to_read,
                "Fonte": guide.source,
            }
        )
    return pd.DataFrame(rows)


def _examples_table(data: pd.DataFrame, annotation: str, rating: int | None) -> pd.DataFrame:
    examples = data[data["action_raw"] == annotation].copy()
    if rating is not None:
        examples = examples[examples["satisfaction_mode"] == rating]

    examples = examples.sort_values(["dialogue_id", "turn_id"]).head(12)
    return examples[
        [
            "dataset",
            "dialogue_id",
            "turn_id",
            "text",
            "action_raw",
            "satisfaction_scores",
            "satisfaction_mode",
        ]
    ].rename(
        columns={
            "dataset": "Dataset",
            "dialogue_id": "Diálogo",
            "turn_id": "Posição",
            "text": "Fala",
            "action_raw": "Anotação",
            "satisfaction_scores": "Notas",
            "satisfaction_mode": "Nota mais frequente",
        }
    )


def render(df: pd.DataFrame) -> None:
    """Renderiza gráficos, glossário e exemplos de anotações por dataset."""
    df = ensure_annotation_columns(df)
    st.subheader("Anotações por dataset")
    st.markdown(
        """
        Cada dataset preserva seu próprio vocabulário de anotação. Esta página mostra
        frequência, decomposição, exemplos e relação com notas de satisfação para ajudar
        a ler códigos simples e compostos sem perder a origem de cada base.
        """
    )

    user_turns = real_user_turns(df)
    if user_turns.empty:
        st.warning("Não há falas reais de usuário para analisar.")
        return

    datasets = sorted(user_turns["dataset"].unique())
    default_index = datasets.index("MWOZ") if "MWOZ" in datasets else 0

    control_left, control_right = st.columns([2, 1])
    with control_left:
        dataset = st.selectbox("Dataset", datasets, index=default_index)
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
            "UNKNOWN marca ausência de anotação identificada. Em especial no ReDial, "
            "isso vem do arquivo principal carregado."
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
    col1.metric("Diálogos", _format_number(dataset_df["dialogue_id"].nunique()))
    col2.metric("Falas analisadas", _format_number(len(chart_data)))
    col3.metric("Anotações distintas", _format_number(unique_annotations))
    col4.metric("Falas com nota", _format_number(int(scored_turns)))

    st.markdown("#### Como ler os códigos deste dataset?")
    st.markdown(
        """
        O mesmo campo `action_raw` guarda formatos diferentes. Em SGD, o código costuma
        ser um ato de diálogo. Em MWOZ, o hífen separa domínio e ato. Em CCPE, o sinal de
        mais separa tipo de marcação e entidade. Em ReDial, `UNKNOWN` aparece porque o
        arquivo principal não traz ações no mesmo padrão.
        """
    )

    actions = sorted(chart_data["action_raw"].dropna().unique())
    query = st.text_input(
        "Buscar anotação no glossário",
        placeholder="Ex.: THANK_YOU, Hotel-Inform, ENTITY_OTHER",
    )
    glossary_actions = [
        action for action in actions if not query or query.lower() in action.lower()
    ]
    glossary_df = _glossary_table(dataset, glossary_actions)
    st.dataframe(glossary_df, width="stretch", hide_index=True)

    st.markdown("#### Quais anotações aparecem mais?")
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
        "Unidade: falas reais de usuário. O hover mostra contagem e percentual dentro "
        "do dataset selecionado."
    )

    st.markdown("#### Como as notas se distribuem dentro de cada anotação?")
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
        "Cada linha do mapa de calor soma 100% entre as notas 1 a 5 para aquela "
        "anotação. A célula mostra a porcentagem e o hover mostra a contagem."
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

    st.markdown("#### Tabela do recorte mostrado")
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
    st.markdown("#### Decomposição das anotações")
    st.dataframe(decomposition, width="stretch", hide_index=True)

    st.markdown("#### Exemplos reais")
    st.markdown(
        """
        Os exemplos ajudam a conferir como uma anotação aparece no texto. A nota exibida
        é a nota mais frequente entre os anotadores, e a lista preserva as notas
        individuais para leitura qualitativa.
        """
    )
    example_left, example_right = st.columns([2, 1])
    with example_left:
        selected_annotation = st.selectbox(
            "Anotação para exemplos",
            actions,
            index=0,
        )
    with example_right:
        rating_options = [None] + sorted(
            int(value) for value in chart_data["satisfaction_mode"].dropna().unique()
        )
        selected_rating = st.selectbox(
            "Nota",
            rating_options,
            format_func=lambda value: (
                "Todas" if value is None else f"{value} · {RATING_LABELS[value]}"
            ),
        )

    examples = _examples_table(chart_data, selected_annotation, selected_rating)
    if examples.empty:
        st.info("Nenhum exemplo encontrado para essa combinação.")
    else:
        st.dataframe(examples, width="stretch", hide_index=True)
