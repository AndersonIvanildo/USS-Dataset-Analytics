from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from src.content import ARTICLE_NOTES, COLUMN_GUIDE, DATASET_GUIDES, RATING_GUIDE
from src.loaders import ensure_annotation_columns


def source_badge(original_excerpt: str) -> str:
    """Cria um ícone de ajuda com trecho curto original em inglês."""
    excerpt = escape(original_excerpt)
    return (
        '<span class="source-help">?'
        f'<span class="source-tooltip">Trecho original do artigo: "{excerpt}"</span>'
        "</span>"
    )


def text_with_source(text: str, original_excerpt: str) -> str:
    """Combina uma afirmação em português com seu trecho curto original."""
    return f"{escape(text)} {source_badge(original_excerpt)}"


def render_article_note(title: str, body: str, original_excerpt: str) -> None:
    """Renderiza uma nota narrativa baseada no artigo."""
    st.markdown(
        f"**{escape(title)}** {source_badge(original_excerpt)}  \n{escape(body)}",
        unsafe_allow_html=True,
    )


def render_guide_card(
    title: str,
    body: str,
    footer: str | None = None,
    original_excerpt: str | None = None,
) -> None:
    """Renderiza um cartão textual usado no guia do projeto."""
    title_html = escape(title)
    if original_excerpt:
        title_html = f"{title_html} {source_badge(original_excerpt)}"

    footer_html = f"<p><strong>Como ler:</strong> {escape(footer)}</p>" if footer else ""
    st.markdown(
        f"""
        <div class="guide-card">
            <h4>{title_html}</h4>
            <p>{escape(body)}</p>
            {footer_html}
        </div>
        """,
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
        "Turno",
        "Papel",
        "Texto",
        "Ação",
        "Notas",
        "Interpretação das notas",
        "É OVERALL",
    ]
    return example


def render_loaded_summary(df: pd.DataFrame) -> None:
    """Mostra um resumo textual dos datasets carregados."""
    loaded = df.groupby("dataset")["dialogue_id"].nunique().sort_index()
    loaded_text = ", ".join(
        f"{dataset}: {count:,}".replace(",", ".")
        for dataset, count in loaded.items()
    )
    st.markdown("#### Datasets carregados nesta execução")
    st.markdown(
        f"Nesta execução, o app carregou **{len(loaded)} datasets**: {loaded_text}. "
        "Esse resumo serve apenas para confirmar a carga dos dados. As comparações "
        "detalhadas ficam nas páginas de visão geral e comparação entre datasets."
    )

    if "JDDC" in loaded.index:
        st.caption(
            "JDDC está disponível como corpus bônus em chinês. As análises principais "
            "continuam priorizando os datasets em inglês."
        )


def render(df: pd.DataFrame) -> None:
    """Renderiza a narrativa inicial sobre o projeto USS e seus datasets."""
    df = ensure_annotation_columns(df)
    st.subheader("Guia do projeto e do dataset")

    st.markdown(
        """
        Este aplicativo explora o **User Satisfaction Simulation (USS)**, um dataset
        criado para estudar satisfação do usuário em sistemas de diálogo orientados a
        tarefa. A ideia central do artigo é que avaliar um bot apenas por acerto de
        resposta ou por um turno isolado não mostra toda a experiência do usuário durante
        a conversa.

        O USS nasce justamente dessa lacuna: ele reúne diálogos de diferentes domínios,
        adiciona anotações humanas de satisfação e permite observar como a satisfação
        muda conforme o sistema entende, falha, pede esclarecimentos ou resolve a tarefa.

        Neste app, o foco principal está nos datasets em inglês: **SGD**, **MultiWOZ**,
        **ReDial** e **CCPE**. O **JDDC** também faz parte do USS, mas aparece como um
        dataset bônus por estar em chinês e exigir cuidados extras de idioma, tradução e
        agrupamento de ações.
        """
    )
    st.markdown(
        text_with_source(
            "USS inclui 6.800 diálogos de múltiplos domínios.",
            "User Satisfaction Simulation (USS), that includes 6,800 dialogues",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("#### Por que esse dataset existe")
    st.markdown(
        """
        O artigo parte de um problema simples: uma conversa com um sistema orientado a
        tarefa não é boa apenas porque uma resposta isolada parece correta. O usuário
        pode ficar frustrado se o sistema demora, pede informação repetida, entende
        parcialmente o pedido ou entrega uma resposta que não resolve o problema.

        Por isso, os autores propõem combinar simulação de usuário com satisfação do
        usuário. Em vez de simular apenas a próxima ação mecânica do usuário, o projeto
        tenta modelar também o estado de satisfação que acompanha essa ação.

        Essa diferença é importante para o app: as notas do USS não devem ser lidas como
        sentimento textual puro. Elas representam uma avaliação contextual da experiência
        do usuário até aquele ponto da conversa.
        """
    )

    for note in ARTICLE_NOTES:
        render_article_note(note.title, note.translated, note.original_excerpt)

    st.markdown("#### Como o USS foi construído")
    st.markdown(
        """
        O USS não foi criado do zero como uma única coleta. Ele foi construído a partir
        de cinco datasets de diálogo já existentes. Os autores reuniram bases de
        diferentes domínios, filtraram conversas com sinais de emoção negativa e depois
        adicionaram anotações humanas de satisfação.

        Esse processo tem três etapas principais:

        1. **Preparação dos dados:** selecionar diálogos de JDDC, SGD, MultiWOZ, ReDial
        e CCPE.
        2. **Avaliação da satisfação:** pedir que anotadores humanos avaliassem a
        satisfação por turno de usuário e também a satisfação geral do diálogo.
        3. **Controle de qualidade:** usar pelo menos três anotadores por conversa e
        pedir rechecagem quando as avaliações discordavam muito.

        O resultado é um corpus com diálogos de comércio eletrônico, reservas,
        assistentes virtuais e recomendação de filmes. Essa mistura torna o USS
        interessante para exploração, mas também exige cuidado para não tratar todos os
        datasets como se fossem iguais.
        """
    )
    st.markdown(
        text_with_source(
            "As anotações cobrem nível de troca e nível de diálogo.",
            "exchange-level and dialogue-level user satisfaction",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("#### O que cada dataset é")
    st.markdown(
        """
        O USS é uma composição de datasets. Isso significa que cada parte da base veio de
        um contexto diferente, com domínio, idioma e anotações de ação próprias. No app,
        os datasets em inglês formam o núcleo principal de análise. O JDDC permanece
        disponível como bônus, mas separado por causa do idioma chinês.
        """
    )

    for index in range(0, len(DATASET_GUIDES), 2):
        cols = st.columns(2)
        for column, dataset_guide in zip(cols, DATASET_GUIDES[index : index + 2]):
            with column:
                render_guide_card(
                    f"{dataset_guide.name}: {dataset_guide.full_name}",
                    (
                        f"Idioma: {dataset_guide.language}. "
                        f"Domínio: {dataset_guide.domain}. "
                        f"Papel no app: {dataset_guide.role_in_app}. "
                        f"{dataset_guide.description}"
                    ),
                    dataset_guide.how_to_read,
                    dataset_guide.original_excerpt,
                )

    st.markdown(
        text_with_source(
            "JDDC é tratado como bônus porque está em chinês, enquanto o MVP prioriza "
            "os datasets em inglês.",
            "JDDC (Chinese) and Others (English)",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("#### Como os arquivos brutos são separados")
    st.markdown(
        """
        Os arquivos oficiais do USS estão em formato TXT. Cada diálogo é separado por uma
        linha em branco, e cada linha dentro do diálogo representa uma fala ou uma
        anotação especial.

        Nos datasets em inglês, a estrutura geral é:

        `role<TAB>text<TAB>action<TAB>satisfaction`

        No JDDC, há um campo adicional de explicação:

        `role<TAB>text<TAB>action<TAB>satisfaction<TAB>explanation`

        Essa estrutura simples é uma vantagem para o Streamlit, porque permite
        transformar os arquivos em uma tabela normalizada. Ao mesmo tempo, ela exige
        cuidado: linhas do sistema geralmente não possuem satisfação, algumas ações podem
        vir vazias, e a linha `OVERALL` não é uma fala real.
        """
    )
    st.markdown(
        text_with_source(
            "O JDDC possui explicações textuais dos anotadores.",
            "annotators’ explanations on user satisfaction annotations",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("#### Como a satisfação foi anotada")
    st.markdown(
        """
        Cada fala de usuário recebeu notas de satisfação em uma escala de 1 a 5. A
        avaliação não foi feita depois de ler apenas a frase do usuário. Os anotadores
        deveriam olhar o histórico anterior da conversa e estimar a satisfação do usuário
        naquele momento.

        Esse detalhe muda a interpretação do dataset. Uma frase como "ok" ou "thanks"
        não deve ser classificada isoladamente. Ela pode representar alívio, neutralidade
        ou frustração dependendo do que o sistema respondeu antes.

        Os autores também pediram uma nota geral para o diálogo inteiro. Essa nota aparece
        nos arquivos como uma linha especial `OVERALL`.
        """
    )
    st.markdown(
        text_with_source(
            "A satisfação é avaliada antes da frase do usuário.",
            "before the user’s sentence",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("#### Escala de satisfação")
    st.markdown(
        text_with_source(
            "A escala deve ser lida como grau de sucesso ou falha do sistema em "
            "satisfazer a necessidade do usuário. Ela não é apenas polaridade emocional "
            "do texto.",
            "success or failure of a system’s response",
        ),
        unsafe_allow_html=True,
    )
    rating_df = pd.DataFrame(
        RATING_GUIDE,
        columns=["Nota", "Interpretação", "Leitura prática"],
    )
    st.dataframe(rating_df, width="stretch", hide_index=True)

    st.markdown("#### Glossário rápido")
    st.markdown(
        """
        - **Task-oriented dialogue:** conversa em que o sistema tenta ajudar o usuário a
          cumprir uma tarefa específica.
        - **User simulation:** método para simular comportamento de usuários e avaliar
          sistemas de diálogo em larga escala.
        - **Exchange-level satisfaction:** satisfação em nível de turno ou troca,
          associada a um ponto específico da conversa.
        - **Dialogue-level satisfaction:** satisfação geral do diálogo completo.
        - **Before utterance:** a nota é atribuída antes da fala do usuário, considerando
          o contexto anterior.
        - **Action:** ato ou intenção associada à fala, como informar, pedir, recomendar,
          agradecer ou negar.
        - **OVERALL:** identificador usado para registrar satisfação geral do diálogo.
        - **Fleiss Kappa:** medida de concordância entre vários anotadores.
        """
    )

    st.markdown("#### O que é a linha OVERALL")
    st.markdown(
        """
        <div class="overall-callout">
            <strong>OVERALL é uma marca de satisfação geral do diálogo.</strong>
            Ela aparece como uma linha `USER`, mas não representa uma frase dita pelo
            usuário.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        Na prática, o app deve tratar `OVERALL` como outro nível de análise. As falas
        reais de usuário mostram a satisfação ao longo da conversa; a linha `OVERALL`
        resume a avaliação final do diálogo completo.

        Por isso, gráficos por turno devem excluir `OVERALL` por padrão. Já análises de
        qualidade geral da conversa podem usar apenas as linhas `OVERALL`.
        """
    )
    st.markdown(
        text_with_source(
            "A satisfação geral é tratada como o último enunciado do usuário.",
            "dialogue-level satisfaction as the last user utterance",
        ),
        unsafe_allow_html=True,
    )

    example = overall_example(df)
    if not example.empty:
        st.markdown(
            """
            **Exemplo real no dataset carregado.** A última linha abaixo é `OVERALL`.
            Note que o campo de texto não traz uma frase dita pelo usuário, mas a marca
            de avaliação geral da conversa.
            """
        )
        st.dataframe(example, width="stretch", hide_index=True)

    st.markdown("#### Como ler notas como 3, 3, 4")
    st.markdown(
        """
        A coluna de satisfação guarda as notas dos anotadores separadas por vírgula.
        Assim, `3,3,4` significa que três pessoas avaliaram aquela instância: duas deram
        nota 3 e uma deu nota 4.

        O artigo afirma que cada diálogo foi rotulado por 3 anotadores, mas também
        explica que, quando havia discrepância forte entre os três, um quarto anotador era
        chamado para reavaliar. Por isso, algumas linhas podem aparecer com quatro ou mais
        notas no arquivo processado.

        No app, nenhuma nota deve ser descartada. A tabela normalizada preserva a lista
        original em `satisfaction_scores` e também adiciona a tradução textual em
        `satisfaction_interpretation`.
        """
    )
    st.markdown(
        text_with_source(
            "Um quarto anotador podia reavaliar casos de discrepância.",
            "we ask a fourth annotator to recheck it",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("#### Colunas normalizadas")
    st.markdown(
        """
        Como o USS junta datasets diferentes, o app precisa transformar os arquivos
        brutos em uma tabela comum. Essa normalização não apaga a origem dos dados; ela
        cria colunas padronizadas para permitir filtros, gráficos e comparações.

        O princípio é preservar o máximo de informação original e adicionar colunas
        derivadas apenas para facilitar a leitura. Por exemplo, a ação original fica em
        `action_raw`, enquanto agrupamentos como `action_group`, `action_type` e
        `action_target` ajudam a construir visualizações.
        """
    )
    column_df = pd.DataFrame(COLUMN_GUIDE, columns=["Coluna", "Como interpretar"])
    st.dataframe(column_df, width="stretch", hide_index=True)

    render_loaded_summary(df)

    st.markdown("#### Como navegar no app")
    st.markdown(
        """
        Use esta página como mapa conceitual. Depois, siga para a visão geral para ver
        volume, distribuição de notas e recortes por dataset. Em seguida, abra a inspeção
        de diálogo para ler conversas completas, porque a satisfação depende do histórico.

        A página de dataset bruto ajuda a conferir a estrutura original normalizada. A
        análise de instâncias mostra padrões por ação, nota e divergência entre
        anotadores. Por fim, a preparação para sentimentos e bot deve ser usada com
        cuidado: o USS mede satisfação contextual, não sentimento textual puro.
        """
    )
    st.markdown(
        text_with_source(
            "O USS também pode apoiar tarefas além de simulação de usuário.",
            "not only for user simulation",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("#### Fontes consultadas")
    st.markdown(
        """
        - Artigo original: [Simulating User Satisfaction for the Evaluation of
          Task-oriented Dialogue Systems](https://arxiv.org/pdf/2105.03748)
        - Repositório oficial: [sunnweiwei/user-satisfaction-simulation](https://github.com/sunnweiwei/user-satisfaction-simulation)
        - Pasta oficial do dataset: [dataset](https://github.com/sunnweiwei/user-satisfaction-simulation/tree/master/dataset)
        - Documento interno de estudo: `OVERVIEW_GUIA.md`
        - Página atual usada como base: `pages_app/guide.py`
        """
    )
