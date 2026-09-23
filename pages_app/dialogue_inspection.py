from __future__ import annotations

from html import escape
from math import ceil

import pandas as pd
import streamlit as st

from src.charts import satisfaction_timeline_chart
from src.config import RATING_LABELS
from src.loaders import ensure_annotation_columns
from src.translation import DialogueTranslationError, translate_dialogue_texts


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


def _dialogue_row_label(row: pd.Series) -> str:
    role = "OVERALL" if row["is_overall"] else row["role"]
    return f"linha {row['turn_id']} · {role} · {_shorten_text(row['text'], 70)}"


def _message_with_translation(text: object, translation: str | None) -> str:
    original = escape(str(text))
    if not translation:
        return original
    translated = escape(translation)
    return (
        f"{original}"
        '<span class="translation-help">?'
        f'<span class="translation-tooltip">{translated}</span>'
        "</span>"
    )


@st.cache_data(show_spinner="Traduzindo falas do diálogo selecionado...")
def _translate_selected_dialogue(texts: tuple[str, ...]) -> dict[str, str]:
    return translate_dialogue_texts(texts)


def _direct_dialogue_selector(df: pd.DataFrame) -> pd.Series | None:
    st.markdown("**Abrir conversa por dataset e ID**")
    st.markdown(
        """
        Use esta seleção quando você já souber qual conversa quer abrir. O identificador
        continua sendo o par dataset e ID original do diálogo, porque os IDs se repetem
        entre bases diferentes.
        """
    )

    left, middle, right = st.columns([1, 1, 1.4])
    with left:
        datasets = sorted(df["dataset"].unique())
        dataset = st.selectbox("Dataset do diálogo", datasets, key="direct_dialogue_dataset")

    dataset_df = df[df["dataset"] == dataset].copy()
    dialogue_ids = sorted(dataset_df["dialogue_id"].unique().tolist())
    with middle:
        dialogue_id = st.selectbox(
            "ID do diálogo",
            dialogue_ids,
            index=0,
            key="direct_dialogue_id",
        )

    dialogue_df = dataset_df[dataset_df["dialogue_id"] == dialogue_id].sort_values("turn_id")
    with right:
        turn_options = dialogue_df.index.tolist()
        selected_index = st.selectbox(
            "Linha destacada",
            turn_options,
            format_func=lambda index: _dialogue_row_label(dialogue_df.loc[index]),
            key="direct_dialogue_turn",
        )

    return dialogue_df.loc[selected_index]


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
    ratings = sorted(
        int(value) for value in df["satisfaction_mode"].dropna().unique().tolist()
    )
    selected_ratings = st.multiselect(
        "Nota mais frequente, deixe vazio para mostrar todas",
        ratings,
        format_func=lambda value: f"{value} · {RATING_LABELS[value]}",
    )
    include_without_rating = st.checkbox("Incluir registros sem nota", value=True)
    actions = sorted(df["action_raw"].dropna().unique())
    selected_actions = st.multiselect(
        "Anotação, deixe vazio para mostrar todas",
        actions,
    )

    table_df = df[df["dataset"].isin(selected_datasets)].copy()
    table_df = table_df[table_df["role"].isin(selected_roles)]
    if not include_overall:
        table_df = table_df[~table_df["is_overall"]]
    if selected_ratings:
        rating_mask = table_df["satisfaction_mode"].isin(selected_ratings)
        if include_without_rating:
            rating_mask = rating_mask | table_df["satisfaction_mode"].isna()
        table_df = table_df[rating_mask]
    if not include_without_rating:
        table_df = table_df[table_df["satisfaction_mode"].notna()]
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


def _render_dialogue(
    df: pd.DataFrame,
    selected_row: pd.Series,
    enable_translation: bool = True,
) -> None:
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

    translations: dict[str, str] = {}
    if enable_translation:
        texts_to_translate = tuple(
            str(text)
            for text in dialogue_df.loc[~dialogue_df["is_overall"], "text"].dropna().tolist()
            if str(text).strip()
        )
        try:
            translations = _translate_selected_dialogue(texts_to_translate)
        except DialogueTranslationError as error:
            st.warning(
                "Não foi possível carregar as traduções deste diálogo agora. "
                "O texto original continua disponível. Detalhe: " + str(error)
            )

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
                st.markdown(
                    _message_with_translation(row["text"], translations.get(str(row["text"]))),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    _metadata_block(row, selected=selected),
                    unsafe_allow_html=True,
                )
        else:
            with st.chat_message("assistant"):
                st.markdown(
                    _message_with_translation(row["text"], translations.get(str(row["text"]))),
                    unsafe_allow_html=True,
                )
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

    st.markdown("---")
    st.markdown("**Escolher conversa para inspecionar**")
    selection_mode = st.radio(
        "Modo de seleção",
        ["Selecionar por dataset e ID", "Usar uma linha desta página"],
        horizontal=True,
    )

    if selection_mode == "Selecionar por dataset e ID":
        selected_row = _direct_dialogue_selector(df)
    else:
        selected_row = _selected_row(page_df)

    enable_translation = st.checkbox(
        "Mostrar tradução das falas no ícone ?",
        value=False,
        help=(
            "Ao ativar, o diálogo selecionado será recarregado com traduções nos símbolos ?. "
            "A tradução é feita somente para esse diálogo, em lote, e pode demorar alguns segundos."
        ),
    )

    if selected_row is not None:
        _render_dialogue(df, selected_row, enable_translation=enable_translation)
