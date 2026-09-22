from __future__ import annotations

from html import escape
from math import ceil

import pandas as pd
import streamlit as st

from src.charts import satisfaction_timeline_chart
from src.config import RATING_LABELS
from src.loaders import ensure_annotation_columns


TABLE_COLUMNS = [
    "dataset",
    "dialogue_id",
    "turn_id",
    "role",
    "text",
    "action_raw",
    "satisfaction_mode",
    "is_overall",
]


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _shorten_text(value: object, limit: int = 90) -> str:
    text = "" if value is None else str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _rating_chips(scores: object) -> str:
    if not isinstance(scores, list) or not scores:
        return '<span class="rating-chip">Sem notas de satisfação</span>'

    chips = []
    for index, score in enumerate(scores, start=1):
        label = RATING_LABELS.get(int(score), "Nota desconhecida")
        chips.append(
            '<span class="rating-chip">'
            f"Anotador {index} · {int(score)} ({escape(label)})"
            "</span>"
        )
    return "".join(chips)


def _metadata_block(row: pd.Series, selected: bool = False) -> str:
    css_class = "turn-meta selected-turn" if selected else "turn-meta"
    action = escape(str(row["action_raw"]))
    selected_label = (
        '<span class="rating-chip">Linha selecionada na tabela</span>' if selected else ""
    )

    return (
        f'<div class="{css_class}">'
        "<div>"
        '<span class="meta-label">Anotação</span>'
        f"<code>{action}</code>"
        f"{selected_label}"
        "</div>"
        '<div class="turn-meta-row">'
        '<span class="meta-label">Notas</span>'
        f'{_rating_chips(row["satisfaction_scores"])}'
        "</div>"
        "</div>"
    )


def _selection_label(row: pd.Series) -> str:
    role = "OVERALL" if row["is_overall"] else row["role"]
    text = _shorten_text(row["text"])
    return (
        f"{row['dataset']} · diálogo {row['dialogue_id']} · "
        f"linha {row['turn_id']} · {role} · {text}"
    )


def _filter_table(df: pd.DataFrame) -> pd.DataFrame:
    st.markdown("**Dataset bruto normalizado**")
    st.markdown(
        """
        Use a tabela para localizar exemplos. Ao escolher uma linha, a conversa completa
        aparece logo abaixo, preservando as falas de usuário, sistema e `OVERALL`.
        """
    )

    filter_left, filter_middle, filter_right = st.columns([1.2, 1, 1])
    with filter_left:
        query = st.text_input("Busca textual", placeholder="Digite parte de uma fala")
    with filter_middle:
        datasets = sorted(df["dataset"].unique())
        selected_datasets = st.multiselect("Dataset", datasets, default=datasets)
    with filter_right:
        roles = sorted(df["role"].dropna().unique())
        selected_roles = st.multiselect("Papel", roles, default=roles)

    include_overall = st.checkbox("Incluir linhas OVERALL na tabela", value=True)
    actions = sorted(df["action_raw"].dropna().unique())
    selected_actions = st.multiselect(
        "Anotação, deixe vazio para mostrar todas",
        actions,
    )

    table_df = df[df["dataset"].isin(selected_datasets)].copy()
    table_df = table_df[table_df["role"].isin(selected_roles)]
    if not include_overall:
        table_df = table_df[~table_df["is_overall"]]
    if selected_actions:
        table_df = table_df[table_df["action_raw"].isin(selected_actions)]
    if query:
        table_df = table_df[
            table_df["text"].str.contains(query, case=False, na=False, regex=False)
        ]

    return table_df.sort_values(["dataset", "dialogue_id", "turn_id"])


def _paginated_table(table_df: pd.DataFrame) -> pd.DataFrame:
    if table_df.empty:
        st.warning("Nenhuma linha encontrada para os filtros selecionados.")
        return table_df

    total_rows = len(table_df)
    st.caption(f"{_format_number(total_rows)} linha(s) encontrada(s).")

    page_left, page_right = st.columns([1, 1])
    with page_left:
        page_size = st.selectbox(
            "Linhas por página",
            [10, 25, 50, 100],
            index=0,
        )

    page_count = max(ceil(total_rows / page_size), 1)
    with page_right:
        page = st.number_input(
            "Página",
            min_value=1,
            max_value=page_count,
            value=1,
            step=1,
        )

    start = (int(page) - 1) * page_size
    end = start + page_size
    page_df = table_df.iloc[start:end].copy()

    st.caption(f"Mostrando linhas {start + 1} a {min(end, total_rows)} de {total_rows}.")
    st.dataframe(page_df[TABLE_COLUMNS], width="stretch", hide_index=True)

    csv = table_df[TABLE_COLUMNS].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar recorte em CSV",
        data=csv,
        file_name="uss_recorte.csv",
        mime="text/csv",
    )

    return page_df


def _selected_row(page_df: pd.DataFrame) -> pd.Series | None:
    if page_df.empty:
        return None

    options = page_df.index.tolist()
    labels = {index: _selection_label(page_df.loc[index]) for index in options}
    selected_index = st.selectbox(
        "Abrir diálogo a partir de uma linha desta página",
        options,
        format_func=lambda index: labels[index],
    )
    return page_df.loc[selected_index]


def _render_dialogue(df: pd.DataFrame, selected_row: pd.Series) -> None:
    dataset = selected_row["dataset"]
    dialogue_id = selected_row["dialogue_id"]
    selected_turn_id = selected_row["turn_id"]

    st.markdown("**Conversa completa**")
    st.caption(
        f"{dataset} · diálogo {dialogue_id}. A linha selecionada na tabela aparece destacada."
    )

    dialogue_df = df[
        (df["dataset"] == dataset) & (df["dialogue_id"] == dialogue_id)
    ].sort_values("turn_id")

    st.plotly_chart(
        satisfaction_timeline_chart(dialogue_df),
        width="stretch",
        key=f"dialogue_timeline_{dataset}_{dialogue_id}_{selected_turn_id}",
    )

    for _, row in dialogue_df.iterrows():
        selected = row["turn_id"] == selected_turn_id

        if row["is_overall"]:
            st.success("Satisfação geral do diálogo")
            st.markdown(_metadata_block(row, selected=selected), unsafe_allow_html=True)
            continue

        if row["role"] == "USER":
            with st.chat_message("user"):
                st.markdown(row["text"])
                st.markdown(
                    _metadata_block(row, selected=selected),
                    unsafe_allow_html=True,
                )
        else:
            with st.chat_message("assistant"):
                st.markdown(row["text"])
                st.markdown(
                    _metadata_block(row, selected=selected),
                    unsafe_allow_html=True,
                )


def render(df: pd.DataFrame) -> None:
    """Renderiza a tabela bruta paginada e a inspeção de diálogo."""
    df = ensure_annotation_columns(df)
    st.subheader("Dataset e diálogos")
    st.markdown(
        """
        A tabela abaixo serve como ponto de entrada para a inspeção qualitativa. Ela lista
        o dataset normalizado em páginas, permite busca e abre o diálogo completo da linha
        escolhida logo em seguida.
        """
    )

    table_df = _filter_table(df)
    page_df = _paginated_table(table_df)
    selected_row = _selected_row(page_df)

    if selected_row is not None:
        _render_dialogue(df, selected_row)
