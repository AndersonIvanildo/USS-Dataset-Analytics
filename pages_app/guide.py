from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from src.content import ARTICLE_NOTES, COLUMN_GUIDE, DATASET_GUIDES, RATING_GUIDE
from src.display import dataframe_for_display
from src.loaders import ensure_annotation_columns


def source_badge(source_reference: str, source_excerpt: str) -> str:
    """Cria um ícone de ajuda com trecho literal do artigo."""
    reference = escape(source_reference)
    excerpt = escape(source_excerpt)
    return (
        '<span class="source-help">?'
        f'<span class="source-tooltip">{reference}: “{excerpt}”</span>'
        "</span>"
    )


def render_article_note(
    title: str,
    body: str,
    source_reference: str,
    source_excerpt: str,
) -> None:
    """Renderiza uma nota narrativa baseada no artigo."""
    st.markdown(
        f"**{escape(title)}** {source_badge(source_reference, source_excerpt)}  \n"
        f"{escape(body)}",
        unsafe_allow_html=True,
    )


def overall_example(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona um exemplo real de diálogo que contém a linha OVERALL."""
    overall_rows = df[df["is_overall"]]
    if overall_rows.empty:
        return pd.DataFrame()

    row = overall_rows.iloc[0]
    dialogue_rows = df[
        (df["dataset"] == row["dataset"]) & (df["dialogue_id"] == row["dialogue_id"])
    ].sort_values("turn_id")

    example = dialogue_rows.tail(5)[
        [
            "dataset",
            "dialogue_id",
            "turn_id",
            "role",
            "text",
            "action_raw",
            "satisfaction_scores",
            "satisfaction_interpretation",
            "is_overall",
        ]
    ].copy()
    example.columns = [
        "Dataset",
        "Diálogo",
        "Posição",
        "Papel",
        "Texto",
        "Anotação",
        "Notas",
        "Interpretação das notas",
        "É OVERALL",
    ]
    return dataframe_for_display(example)


def _guide_dataset_callout(dataset_name: str, domain: str) -> None:
    renderers = {
        "CCPE": st.success,
        "MWOZ": st.info,
        "ReDial": st.warning,
        "SGD": st.success,
    }
    renderer = renderers.get(dataset_name, st.info)
    renderer(f"{dataset_name} · {domain}")


def render_dataset_cards() -> None:
    """Mostra os datasets de origem em containers nativos."""
    for index in range(0, len(DATASET_GUIDES), 2):
        cols = st.columns(2)
        for column, dataset_guide in zip(cols, DATASET_GUIDES[index : index + 2]):
            with column:
                with st.container(border=True):
                    st.markdown(
                        f"#### {dataset_guide.name}: {dataset_guide.full_name}"
                    )
                    _guide_dataset_callout(dataset_guide.name, dataset_guide.domain)
                    st.caption(f"Idioma: {dataset_guide.language}")
                    st.markdown(dataset_guide.description)
                    st.divider()
                    st.markdown(dataset_guide.how_to_read)


def render(df: pd.DataFrame) -> None:
    """Renderiza a narrativa inicial sobre o USS e seus datasets."""
    df = ensure_annotation_columns(df)
    st.subheader("Guia do projeto e do dataset")

    st.markdown(
        """
        O **User Satisfaction Simulation (USS)** é um dataset para estudar satisfação do
        usuário em sistemas de diálogo orientados a tarefa. Sua principal contribuição é
        ligar cada fala de usuário ao contexto que veio antes dela. A nota não descreve
        apenas o tom da frase; ela registra como o usuário provavelmente avaliaria a
        experiência naquele ponto da conversa.

        O recorte explorado aqui se concentra nos quatro datasets em inglês presentes
        nos arquivos principais: **SGD**, **MWOZ**, **ReDial** e **CCPE**. O **JDDC**
        ajuda a entender a origem do USS, mas exige tratamento próprio de idioma e fica
        como referência de contexto.
        """
    )
    st.markdown(
        """
        O USS foi criado para aproximar a avaliação automática da experiência real do
        usuário durante uma conversa.
        """
    )

    st.markdown("#### Por que esse dataset existe")
    st.markdown(
        """
        Em diálogos orientados a tarefa, uma resposta isolada pode parecer aceitável e,
        mesmo assim, a conversa pode frustrar o usuário. O sistema pode pedir informação
        repetida, entender parcialmente o pedido ou responder de forma que não resolve a
        tarefa. Por isso, o USS registra satisfação ao longo do diálogo e também uma
        avaliação geral da conversa.

        Essa estrutura permite investigar oscilações. Uma nota baixa no meio da conversa
        pode indicar falha de entendimento ou demora na solução. Uma nota mais alta no
        fim pode mostrar recuperação. A leitura correta depende de observar a sequência
        de falas, não apenas a linha isolada.
        """
    )

    for note in ARTICLE_NOTES:
        render_article_note(
            note.title,
            note.translated,
            note.source_reference,
            note.source_excerpt,
        )

    st.markdown("#### O que cada dataset é")
    st.markdown(
        """
        O USS junta bases com origens diferentes. Essa composição é útil porque amplia
        domínios e situações de diálogo, mas também exige cuidado: uma anotação de SGD
        não tem necessariamente o mesmo formato de uma anotação de CCPE ou MWOZ.
        """
    )
    render_dataset_cards()

    st.markdown("#### Como os arquivos brutos são organizados")
    st.markdown(
        """
        Os arquivos oficiais estão em TXT. Uma linha em branco separa diálogos, e cada
        linha preenchida guarda uma fala ou uma marca especial. Nos datasets em inglês,
        a estrutura geral é `role<TAB>text<TAB>action<TAB>satisfaction`. No JDDC há um
        campo adicional de explicação dos anotadores.

        A leitura mais importante é a separação entre fala real e `OVERALL`. Falas do
        sistema normalmente não têm nota de satisfação. Falas de usuário podem ter uma
        lista de notas. A linha `OVERALL` aparece como `USER`, mas registra satisfação
        geral do diálogo completo.
        """
    )

    st.markdown("#### Como a satisfação foi anotada")
    st.markdown(
        """
        Cada fala de usuário recebeu notas em uma escala de 1 a 5. Os anotadores
        avaliaram o contexto antes da fala do usuário. Por isso, uma frase curta como
        “ok” ou “thanks” pode ter leituras diferentes dependendo da resposta anterior do
        sistema.

        Quando aparece uma sequência como `3,3,4`, ela indica notas individuais. A nota
        mais frequente é usada em vários gráficos, mas as notas originais continuam
        preservadas para inspecionar concordância e divergência.
        """
    )
    st.markdown(
        """
        A satisfação deve ser lida como uma avaliação contextual da experiência, não
        como sentimento textual da frase.
        """
    )

    st.markdown("#### Escala de satisfação")
    rating_df = pd.DataFrame(
        RATING_GUIDE,
        columns=["Nota", "Interpretação", "Leitura prática"],
    )
    st.dataframe(rating_df, width="stretch", hide_index=True)

    st.markdown("#### O que é a linha OVERALL")
    st.info(
        "`OVERALL` é a avaliação geral do diálogo. Ela encerra a conversa como uma "
        "marca de satisfação, mas não deve ser contada como fala real de usuário."
    )
    st.markdown(
        """
        Nas análises por fala, `OVERALL` deve ficar fora do denominador. Nas análises de
        satisfação geral, ele passa a ser a unidade principal, com uma linha para cada
        diálogo. Essa separação evita comparar pontos diferentes da conversa como se
        fossem a mesma coisa.
        """
    )

    example = overall_example(df)
    if not example.empty:
        st.markdown(
            """
            O exemplo abaixo mostra as últimas linhas de um diálogo real. A última linha
            traz `OVERALL` no campo de texto e resume a avaliação geral da conversa.
            """
        )
        st.dataframe(example, width="stretch", hide_index=True)

    st.markdown("#### Colunas normalizadas")
    st.markdown(
        """
        Como os datasets originais usam formatos de anotação diferentes, as linhas são
        organizadas em uma tabela comum. A coluna `action_raw` preserva o código original.
        As colunas `action_group`, `action_type` e `action_target` ajudam a decompor
        códigos como `Hotel-Inform` e `ENTITY_OTHER+MOVIE_OR_SERIES`.
        """
    )
    column_df = pd.DataFrame(COLUMN_GUIDE, columns=["Coluna", "Como interpretar"])
    st.dataframe(column_df, width="stretch", hide_index=True)

    st.markdown("#### Fontes consultadas")
    st.markdown(
        """
        Artigo original: [Simulating User Satisfaction for the Evaluation of
        Task-oriented Dialogue Systems](https://arxiv.org/pdf/2105.03748)

        Repositório oficial: [sunnweiwei/user-satisfaction-simulation](https://github.com/sunnweiwei/user-satisfaction-simulation)

        Pasta oficial do dataset: [dataset](https://github.com/sunnweiwei/user-satisfaction-simulation/tree/master/dataset)
        """
    )
