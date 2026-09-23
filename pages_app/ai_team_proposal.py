from __future__ import annotations

from math import ceil

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import RATING_LABELS
from src.unified_proposal import (
    build_unified_proposal,
    unified_coverage_by_dataset,
    unified_schema_counts,
    unified_summary,
)

DISPLAY_COLUMNS = {
    "dataset": "Dataset",
    "dialogue_uid": "Diálogo unificado",
    "dialogue_id": "ID original",
    "turn_id": "Posição",
    "role": "Papel original",
    "row_kind": "Tipo de linha",
    "text": "Texto",
    "annotation_code": "Código original",
    "annotation_status": "Status da anotação",
    "annotation_layer": "Camada de anotação",
    "dialogue_action": "Ação de diálogo",
    "domain": "Domínio",
    "semantic_type": "Tipo semântico",
    "semantic_target": "Alvo semântico",
    "satisfaction_scores": "Notas individuais",
    "satisfaction_annotation_count": "Nº de notas",
    "satisfaction_mode": "Nota mais frequente",
    "satisfaction_mean": "Média das notas",
    "satisfaction_disagreement": "Discordância",
    "is_overall": "É OVERALL",
}

TABLE_COLUMNS = [
    "dataset",
    "dialogue_uid",
    "turn_id",
    "row_kind",
    "text",
    "annotation_code",
    "dialogue_action",
    "domain",
    "semantic_type",
    "semantic_target",
    "satisfaction_mode",
]

COLOR_SEQUENCE = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#0891b2", "#dc2626"]
STATUS_COLORS = {
    "anotação disponível": "#059669",
    "sem anotação de ação": "#d97706",
    "OVERALL": "#2563eb",
}


@st.cache_data(show_spinner="Montando a proposta unificada do time de IA...")
def _build_unified_cached(df: pd.DataFrame) -> pd.DataFrame:
    return build_unified_proposal(df)


def _format_number(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(value):,}".replace(",", ".")


def _display_df(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    selected = df.copy() if columns is None else df[columns].copy()
    for column in selected.columns:
        selected[column] = selected[column].apply(lambda value: "None" if value is None else value)
    return selected.rename(columns=DISPLAY_COLUMNS)


def _schema_table() -> pd.DataFrame:
    rows = [
        {
            "Coluna proposta": "annotation_code",
            "Função": "Preserva o código original quando ele existe.",
            "Como evita mistura indevida": "Em UNKNOWN e OVERALL fica None, porque não há código semântico real ali.",
        },
        {
            "Coluna proposta": "dialogue_action",
            "Função": "Guarda atos de diálogo comparáveis, como THANK_YOU, Inform ou Request.",
            "Como evita mistura indevida": "CCPE não é forçado para esta coluna, porque suas marcas são semânticas, não atos de diálogo no mesmo sentido de SGD e MWOZ.",
        },
        {
            "Coluna proposta": "domain",
            "Função": "Guarda o domínio de MWOZ, como Hotel, Restaurant ou Train.",
            "Como evita mistura indevida": "SGD, CCPE e ReDial ficam como None quando não há domínio explícito no código.",
        },
        {
            "Coluna proposta": "semantic_type",
            "Função": "Guarda o tipo da marcação semântica do CCPE, como ENTITY_PREFERENCE ou ENTITY_OTHER.",
            "Como evita mistura indevida": "MWOZ e SGD não são preenchidos aqui, porque seus códigos têm outra natureza.",
        },
        {
            "Coluna proposta": "semantic_target",
            "Função": "Guarda o alvo semântico do CCPE, como MOVIE_OR_SERIES ou PERSON.",
            "Como evita mistura indevida": "Só aparece quando o código composto tem um alvo após o sinal de mais.",
        },
        {
            "Coluna proposta": "annotation_status",
            "Função": "Diz se a linha tem anotação, se falta ação ou se é OVERALL.",
            "Como evita mistura indevida": "Separa ausência de ação de avaliação geral do diálogo.",
        },
    ]
    return pd.DataFrame(rows)


def _render_construction_story() -> None:
    st.markdown(
        """
        A proposta do time de IA parte de um princípio simples: unificar o que é comum e
        preservar separado o que tem significado próprio em cada origem. O dataset não
        deve fingir que `THANK_YOU`, `Hotel-Inform` e `ENTITY_OTHER+MOVIE_OR_SERIES`
        pertencem ao mesmo tipo de vocabulário. Eles podem conviver na mesma tabela,
        mas precisam ocupar colunas que explicam sua estrutura.

        O processo começa mantendo a origem da linha, o identificador do diálogo e a
        posição da fala. Depois separa o tipo de linha: fala real de usuário, fala do
        sistema ou avaliação geral `OVERALL`. Por fim, a anotação original é decomposta
        apenas quando o próprio código permite essa leitura. Em MWOZ, o hífen separa
        domínio e ato. Em CCPE, o sinal de mais separa tipo semântico e alvo. Em SGD, a
        ação já aparece como um ato direto. Em ReDial, o arquivo principal não traz ações,
        então a proposta marca a ausência em vez de inventar uma categoria.
        """
    )


def _render_dataset_mapping_cards() -> None:
    st.markdown("#### Como cada subdataset entra na proposta")
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.success("SGD · atos de diálogo")
            st.markdown(
                "SGD preenche `dialogue_action` diretamente. Um código como `THANK_YOU` "
                "já é uma ação de diálogo e não precisa ser dividido em domínio ou alvo."
            )
        with st.container(border=True):
            st.info("MWOZ · domínio + ato")
            st.markdown(
                "MWOZ separa o código em duas partes. `Hotel-Inform` vira "
                "`domain = Hotel` e `dialogue_action = Inform`. A coluna original continua "
                "guardando `Hotel-Inform` para rastreabilidade."
            )
    with right:
        with st.container(border=True):
            st.warning("ReDial · satisfação sem ação no arquivo principal")
            st.markdown(
                "ReDial mantém textos e notas, mas `dialogue_action`, `domain`, "
                "`semantic_type` e `semantic_target` ficam como `None`. Isso evita tratar "
                "a ausência de anotação como se fosse uma intenção do usuário."
            )
        with st.container(border=True):
            st.success("CCPE · marcação semântica")
            st.markdown(
                "CCPE não é forçado para ação de diálogo. `ENTITY_OTHER+MOVIE_OR_SERIES` "
                "vira `semantic_type = ENTITY_OTHER` e `semantic_target = MOVIE_OR_SERIES`."
            )


def _coverage_chart(coverage: pd.DataFrame) -> go.Figure:
    melted = coverage.melt(
        id_vars="dataset",
        value_vars=["acoes_dialogo", "dominios", "marcacoes_semanticas", "sem_anotacao"],
        var_name="campo",
        value_name="total",
    )
    labels = {
        "acoes_dialogo": "Ação de diálogo preenchida",
        "dominios": "Domínio preenchido",
        "marcacoes_semanticas": "Tipo semântico preenchido",
        "sem_anotacao": "Sem anotação de ação",
    }
    melted["campo"] = melted["campo"].map(labels)
    fig = px.bar(
        melted,
        x="dataset",
        y="total",
        color="campo",
        barmode="group",
        color_discrete_sequence=COLOR_SEQUENCE,
        title="Quais campos estruturais ficam preenchidos em cada dataset?",
        labels={"dataset": "Dataset", "total": "Falas de usuário", "campo": "Campo"},
    )
    return fig


def _status_chart(unified: pd.DataFrame) -> go.Figure:
    data = unified[unified["row_kind"].isin(["fala de usuário", "avaliação geral"])].copy()
    counts = (
        data.groupby(["dataset", "annotation_status"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )
    denominators = counts.groupby("dataset")["total"].transform("sum")
    counts["percentual"] = counts["total"] / denominators * 100
    fig = px.bar(
        counts,
        x="dataset",
        y="percentual",
        color="annotation_status",
        barmode="stack",
        color_discrete_map=STATUS_COLORS,
        title="Qual é a proporção de anotação disponível, ausência de ação e OVERALL?",
        labels={
            "dataset": "Dataset",
            "percentual": "% das linhas USER e OVERALL",
            "annotation_status": "Status",
        },
        custom_data=["total"],
    )
    fig.update_traces(
        hovertemplate=(
            "Dataset: %{x}<br>Status: %{legendgroup}<br>Linhas: %{customdata[0]}<br>Percentual: %{y:.1f}%<extra></extra>"
        )
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return fig


def _schema_heatmap(unified: pd.DataFrame) -> go.Figure:
    data = unified[unified["row_kind"].eq("fala de usuário")].copy()
    data["annotation_layer"] = data["annotation_layer"].fillna("sem camada")
    pivot = pd.crosstab(data["annotation_layer"], data["dataset"])
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        text_auto=True,
        title="Como as camadas de anotação se distribuem entre os datasets?",
        labels={"x": "Dataset", "y": "Camada de anotação", "color": "Falas"},
    )
    return fig


def _rating_heatmap(unified: pd.DataFrame) -> go.Figure:
    data = unified[
        unified["row_kind"].eq("fala de usuário")
        & unified["satisfaction_mode"].notna()
    ].copy()
    data["annotation_layer"] = data["annotation_layer"].fillna("sem camada")
    data["rating"] = data["satisfaction_mode"].astype(int)
    pivot = pd.crosstab(data["annotation_layer"], data["rating"]).reindex(
        columns=[1, 2, 3, 4, 5],
        fill_value=0,
    )
    percentages = pivot.div(pivot.sum(axis=1), axis=0).fillna(0) * 100
    text = percentages.round(0).astype(int).astype(str) + "%"
    fig = go.Figure(
        data=go.Heatmap(
            z=percentages.to_numpy(),
            x=[str(value) for value in [1, 2, 3, 4, 5]],
            y=percentages.index.tolist(),
            text=text.to_numpy(),
            texttemplate="%{text}",
            customdata=pivot.to_numpy(),
            zmin=0,
            zmax=100,
            colorscale="Blues",
            colorbar={"title": "% das falas"},
            hovertemplate=(
                "Camada: %{y}<br>Nota: %{x}<br>% na camada: %{z:.1f}%<br>Falas: %{customdata}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Como as notas aparecem dentro de cada camada de anotação?",
        xaxis_title="Nota mais frequente",
        yaxis_title="Camada de anotação",
    )
    fig.update_xaxes(
        tickmode="array",
        tickvals=[str(value) for value in [1, 2, 3, 4, 5]],
        ticktext=[f"{value} · {RATING_LABELS[value]}" for value in [1, 2, 3, 4, 5]],
    )
    return fig


def _filter_unified(unified: pd.DataFrame) -> pd.DataFrame:
    filter_left, filter_middle, filter_right = st.columns([1.3, 1, 1])
    with filter_left:
        query = st.text_input("Busca textual", placeholder="Digite parte de uma fala ou anotação")
    with filter_middle:
        datasets = sorted(unified["dataset"].unique())
        selected_datasets = st.multiselect("Dataset", datasets, default=datasets)
    with filter_right:
        row_kinds = sorted(unified["row_kind"].unique())
        selected_kinds = st.multiselect("Tipo de linha", row_kinds, default=row_kinds)

    status_values = sorted(unified["annotation_status"].unique())
    selected_status = st.multiselect("Status da anotação", status_values, default=status_values)

    rating_values = sorted(
        int(value) for value in unified["satisfaction_mode"].dropna().unique().tolist()
    )
    selected_ratings = st.multiselect(
        "Nota mais frequente, deixe vazio para mostrar todas",
        rating_values,
        format_func=lambda value: f"{value} · {RATING_LABELS[value]}",
    )
    include_without_rating = st.checkbox("Incluir linhas sem nota", value=True)

    data = unified[
        unified["dataset"].isin(selected_datasets)
        & unified["row_kind"].isin(selected_kinds)
        & unified["annotation_status"].isin(selected_status)
    ].copy()
    if selected_ratings:
        rating_mask = data["satisfaction_mode"].isin(selected_ratings)
        if include_without_rating:
            rating_mask = rating_mask | data["satisfaction_mode"].isna()
        data = data[rating_mask]
    if not include_without_rating:
        data = data[data["satisfaction_mode"].notna()]
    if query:
        query_mask = data["text"].str.contains(query, case=False, na=False, regex=False)
        for column in ["annotation_code", "dialogue_action", "domain", "semantic_type", "semantic_target"]:
            query_mask = query_mask | data[column].fillna("").str.contains(
                query,
                case=False,
                na=False,
                regex=False,
            )
        data = data[query_mask]

    return data.sort_values(["dataset", "dialogue_id", "turn_id"])


def _paginated_table(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        st.warning("Nenhuma linha encontrada para os filtros selecionados.")
        return data

    total_rows = len(data)
    st.caption(f"{_format_number(total_rows)} linha(s) encontrada(s).")
    left, right = st.columns(2)
    with left:
        page_size = st.selectbox("Linhas por página", [10, 25, 50, 100], index=0)
    page_count = max(ceil(total_rows / page_size), 1)
    with right:
        page = st.number_input("Página", min_value=1, max_value=page_count, value=1, step=1)

    start = (int(page) - 1) * page_size
    end = start + page_size
    page_df = data.iloc[start:end].copy()
    st.caption(f"Mostrando linhas {start + 1} a {min(end, total_rows)} de {total_rows}.")
    st.dataframe(_display_df(page_df, TABLE_COLUMNS), width="stretch", hide_index=True)

    csv = _display_df(data).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar proposta filtrada em CSV",
        data=csv,
        file_name="uss_proposta_unificada.csv",
        mime="text/csv",
    )
    return page_df


def _render_selected_row(page_df: pd.DataFrame) -> None:
    if page_df.empty:
        return
    labels = {
        index: (
            f"{row['dataset']} · {row['dialogue_uid']} · linha {row['turn_id']} · "
            f"{row['row_kind']} · {str(row['text'])[:80]}"
        )
        for index, row in page_df.iterrows()
    }
    selected_index = st.selectbox(
        "Inspecionar linha da proposta",
        page_df.index.tolist(),
        format_func=lambda index: labels[index],
    )
    row = page_df.loc[selected_index]

    st.markdown("#### Leitura da linha selecionada")
    left, right = st.columns(2)
    with left:
        st.info(
            f"Origem: {row['dataset']} · diálogo {row['dialogue_id']} · posição {row['turn_id']} · {row['row_kind']}"
        )
        st.markdown(row["text"])
    with right:
        st.success(
            "A proposta preserva o código original e preenche somente as colunas que "
            "têm sentido para o esquema daquela origem."
        )
        detail = row[
            [
                "annotation_code",
                "annotation_status",
                "annotation_layer",
                "dialogue_action",
                "domain",
                "semantic_type",
                "semantic_target",
                "satisfaction_scores",
                "satisfaction_mode",
            ]
        ].to_frame("valor")
        st.dataframe(_display_df(detail.reset_index().rename(columns={"index": "campo"})), width="stretch", hide_index=True)


def render(df: pd.DataFrame) -> None:
    """Renderiza a proposta de dataset unificado do time de IA."""
    st.subheader("Proposta do Time de IA")
    _render_construction_story()

    unified = _build_unified_cached(df)
    summary = unified_summary(unified)
    coverage = unified_coverage_by_dataset(unified)

    st.markdown("#### O desenho da tabela unificada")
    st.markdown(
        """
        A tabela proposta não tenta transformar todos os datasets no mesmo vocabulário.
        Ela cria uma espinha dorsal comum para texto, diálogo, papel e satisfação, e abre
        colunas específicas para a estrutura de anotação quando ela existe. O resultado é
        uma base única para análise, mas com rastreabilidade para o subdataset de origem.
        """
    )
    st.dataframe(_schema_table(), width="stretch", hide_index=True)
    _render_dataset_mapping_cards()

    st.markdown("#### O que a proposta revela sobre o acervo")
    st.markdown(
        """
        Ao separar ação de diálogo, domínio e marcação semântica, fica mais claro que o
        acervo não tem uma lacuna uniforme. O ReDial não tem ações no arquivo principal;
        o MWOZ tem códigos ricos porque combinam domínio e ato; o CCPE traz estrutura de
        entidades e preferências; o SGD fornece atos diretos. Essa diferença é o ponto
        central da proposta: ela permite comparar sem apagar a origem das categorias.
        """
    )
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Linhas", _format_number(summary["rows"]))
    col2.metric("Diálogos", _format_number(summary["dialogues"]))
    col3.metric("Falas de usuário", _format_number(summary["user_turns"]))
    col4.metric("OVERALL", _format_number(summary["overall"]))
    col5.metric("Com anotação", _format_number(summary["available_annotations"]))
    col6.metric("Sem ação", _format_number(summary["missing_annotations"]))

    tab_overview, tab_maps, tab_search = st.tabs([
        "Análise da proposta",
        "Mapas de calor",
        "Busca e inspeção",
    ])

    with tab_overview:
        st.markdown("##### Cobertura por dataset")
        st.info(
            "Ações de diálogo, domínios e marcações semânticas são colunas diferentes. "
            "Quando uma origem não possui aquele tipo de estrutura, o campo fica como None."
        )
        st.dataframe(
            coverage.rename(
                columns={
                    "dataset": "Dataset",
                    "falas_usuario": "Falas de usuário",
                    "anotacoes_disponiveis": "Anotações disponíveis",
                    "sem_anotacao": "Sem anotação de ação",
                    "acoes_dialogo": "Ações de diálogo preenchidas",
                    "dominios": "Domínios preenchidos",
                    "marcacoes_semanticas": "Marcações semânticas preenchidas",
                    "overall": "OVERALL",
                }
            ),
            width="stretch",
            hide_index=True,
        )
        st.plotly_chart(_coverage_chart(coverage), width="stretch", key="ai_coverage_chart")
        st.plotly_chart(_status_chart(unified), width="stretch", key="ai_status_chart")

        schema_counts = unified_schema_counts(unified)
        st.markdown("##### Camadas de anotação")
        st.markdown(
            """
            A camada de anotação descreve a natureza do código, não a qualidade da fala.
            Ela mostra se o registro usa ato de diálogo, domínio mais ato, marcação
            semântica ou se não há camada de anotação disponível.
            """
        )
        st.dataframe(
            schema_counts.rename(
                columns={
                    "dataset": "Dataset",
                    "annotation_layer": "Camada de anotação",
                    "total": "Falas de usuário",
                }
            ),
            width="stretch",
            hide_index=True,
        )

    with tab_maps:
        st.markdown("##### Mapas de calor da proposta")
        st.markdown(
            """
            Os mapas de calor ajudam a ver padrões estruturais sem transformar diferenças
            de esquema em ranking. O primeiro cruza datasets e camadas de anotação. O
            segundo aproxima essas camadas da distribuição de notas, sempre usando apenas
            falas reais de usuário.
            """
        )
        st.plotly_chart(_schema_heatmap(unified), width="stretch", key="ai_schema_heatmap")
        st.plotly_chart(_rating_heatmap(unified), width="stretch", key="ai_rating_heatmap")

    with tab_search:
        st.markdown("##### Buscar e inspecionar a tabela proposta")
        st.markdown(
            """
            Esta área permite testar a utilidade prática do desenho. Busque por texto,
            código ou parte de uma decomposição e veja como a mesma linha ficaria na
            proposta unificada. A exportação baixa o recorte filtrado, não altera os
            arquivos originais.
            """
        )
        filtered = _filter_unified(unified)
        page_df = _paginated_table(filtered)
        _render_selected_row(page_df)
