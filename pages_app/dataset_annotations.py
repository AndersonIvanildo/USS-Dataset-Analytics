from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import annotation_frequency_chart, annotation_rating_heatmap
from src.config import RATING_LABELS
from src.content import annotation_narrative, explain_annotation
from src.loaders import ensure_annotation_columns
from src.metrics import annotation_frequencies, real_user_turns


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


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


def _render_annotation_card(dataset: str, action: str, total: int, percent: float) -> None:
    guide = explain_annotation(dataset, action)
    with st.container(border=True):
        st.markdown(f"#### `{guide.code}`")
        left, right = st.columns(2)
        left.metric("Ocorrências", _format_number(total))
        right.metric("% das falas", f"{percent:.2f}%".replace(".", ","))
        st.markdown(guide.meaning)
        st.markdown(guide.how_to_read)


def render(df: pd.DataFrame) -> None:
    """Renderiza gráficos, glossário e exemplos de anotações por dataset."""
    df = ensure_annotation_columns(df)
    st.subheader("Anotações por dataset")
    st.markdown(
        """
        As anotações do USS não formam um vocabulário único. Cada dataset traz marcas
        próprias da sua origem: atos de diálogo em SGD, domínio e ato em MWOZ, ausência
        de ação no arquivo principal de ReDial e entidades de preferência no CCPE. Essa
        diferença é parte dos dados, não ruído que deva ser apagado.
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
            "Quantidade de anotações nos gráficos",
            min_value=5,
            max_value=30,
            value=15,
            step=1,
            help=(
                "Limita quantas categorias aparecem nas barras e no mapa de calor. "
                "Não altera os dados originais."
            ),
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

    actions = sorted(chart_data["action_raw"].dropna().unique())
    narrative = annotation_narrative(dataset)
    st.markdown(f"#### {narrative.title}")
    st.success(narrative.body)
    st.warning(narrative.examples_intro)

    frequencies_all = annotation_frequencies(
        dataset_df,
        include_unknown=include_unknown,
    )

    st.markdown("#### Investigar uma anotação específica")
    st.info(
        "A busca abaixo serve para aproximar a explicação de um código concreto. "
        "Ela não troca o significado original do dataset; só traz a anotação para perto "
        "dos exemplos e dos gráficos."
    )
    query = st.text_input(
        "Buscar anotação",
        placeholder="Ex.: THANK_YOU, Hotel-Inform, ENTITY_OTHER",
    )
    matched_actions = [
        action for action in actions if not query or query.lower() in action.lower()
    ]
    if matched_actions:
        selected_explained_action = st.selectbox(
            "Anotação explicada",
            matched_actions,
            index=0,
        )
        frequency_row = frequencies_all[
            frequencies_all["action_raw"] == selected_explained_action
        ]
        if frequency_row.empty:
            action_total = 0
            action_percent = 0.0
        else:
            action_total = int(frequency_row.iloc[0]["total"])
            action_percent = float(frequency_row.iloc[0]["percentual"])
        _render_annotation_card(
            dataset,
            selected_explained_action,
            action_total,
            action_percent,
        )
    else:
        st.info("Nenhuma anotação encontrada para essa busca.")

    st.markdown("#### Quais anotações aparecem mais?")
    st.markdown(
        """
        A frequência mostra quais partes do vocabulário dominam o dataset selecionado.
        Em MWOZ, por exemplo, domínios muito presentes aparecem no topo; em ReDial, a
        predominância de `UNKNOWN` revela a ausência de ações no arquivo principal.
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

    st.markdown("#### Como as notas se distribuem dentro de cada anotação?")
    st.markdown(
        """
        O mapa de calor aproxima duas camadas do USS: o que a fala faz na conversa e como
        ela foi avaliada em satisfação. Ele não prova causalidade, mas ajuda a escolher
        bons pontos de leitura qualitativa. Quando uma anotação concentra quase todas as
        falas na nota 3, isso revela mais sobre o desbalanceamento da amostra do que sobre
        um comportamento necessariamente neutro.
        """
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

    st.markdown("#### Frequência das anotações")
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
    st.markdown(
        """
        A decomposição mantém o código original e separa suas partes quando existe uma
        estrutura clara. Isso é especialmente útil em MWOZ, onde domínio e ato aparecem
        juntos, e em CCPE, onde tipo de entidade e alvo aparecem no mesmo código.
        """
    )
    st.dataframe(decomposition, width="stretch", hide_index=True)

    st.markdown("#### Exemplos reais")
    st.markdown(
        """
        A melhor forma de conferir uma anotação é voltar ao texto. Os exemplos abaixo
        preservam a fala original e as notas individuais, porque o significado de uma
        marca só fica completo quando aparece dentro de uma conversa.
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
