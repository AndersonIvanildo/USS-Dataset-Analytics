from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetGuide:
    """Descreve um dataset usado no USS."""

    name: str
    full_name: str
    language: str
    domain: str
    description: str
    how_to_read: str
    source_context: str = ""


@dataclass(frozen=True)
class ArticleNote:
    """Guarda uma leitura em português com contexto do artigo."""

    title: str
    translated: str
    source_context: str


@dataclass(frozen=True)
class AnnotationGuide:
    """Explica uma anotação ou padrão de anotação."""

    dataset: str
    code: str
    meaning: str
    how_to_read: str
    source: str


DATASET_GUIDES = [
    DatasetGuide(
        name="SGD",
        full_name="Schema Guided Dialogue",
        language="Inglês",
        domain="Assistente virtual com múltiplos domínios",
        description=(
            "O SGD reúne conversas entre uma pessoa e um assistente virtual. No USS, "
            "ele representa interações orientadas a tarefa em vários domínios, com "
            "anotações de ação como informar, confirmar, negar, pedir alternativas ou "
            "agradecer."
        ),
        how_to_read=(
            "A anotação costuma ser um ato de diálogo direto. `THANK_YOU`, por exemplo, "
            "indica que a fala do usuário agradece ao sistema; a nota deve ser lida "
            "junto com o que aconteceu antes desse agradecimento."
        ),
        source_context=(
            "...o artigo descreve SGD como conversas entre uma pessoa e um assistente "
            "virtual, cobrindo múltiplos domínios..."
        ),
    ),
    DatasetGuide(
        name="MWOZ",
        full_name="MultiWOZ 2.1",
        language="Inglês",
        domain="Hotel, restaurante, táxi, trem, atrações e serviços",
        description=(
            "O MultiWOZ 2.1 é uma base multidomínio de tarefas urbanas, como reservas "
            "e busca por serviços. No USS, suas anotações frequentemente combinam o "
            "domínio da conversa com o ato realizado pelo usuário."
        ),
        how_to_read=(
            "`Hotel-Inform` deve ser lido como domínio `Hotel` e ato `Inform`. A parte "
            "antes do hífen indica o assunto da tarefa; a parte depois do hífen indica "
            "o tipo de movimento feito na fala."
        ),
        source_context=(
            "...o artigo identifica MultiWOZ 2.1 como um dos datasets usados na "
            "construção do USS, ao lado de JDDC, SGD, ReDial e CCPE..."
        ),
    ),
    DatasetGuide(
        name="ReDial",
        full_name="Recommendation Dialogues",
        language="Inglês",
        domain="Recomendação de filmes",
        description=(
            "O ReDial contém diálogos de recomendação de filmes. No arquivo principal "
            "do USS, as ações não aparecem no mesmo formato dos demais datasets, por "
            "isso as linhas sem ação são preservadas como `UNKNOWN`."
        ),
        how_to_read=(
            "`UNKNOWN` no ReDial não deve ser interpretado como uma intenção do usuário. "
            "Ele marca a ausência de ação no arquivo principal carregado para análise."
        ),
        source_context=(
            "...o artigo inclui ReDial entre os datasets de recomendação usados para "
            "compor o USS..."
        ),
    ),
    DatasetGuide(
        name="CCPE",
        full_name="Coached Conversational Preference Elicitation",
        language="Inglês",
        domain="Preferências sobre filmes",
        description=(
            "O CCPE registra conversas sobre preferências de filmes. Suas anotações "
            "podem combinar o tipo de informação marcada com a entidade mencionada, o "
            "que torna o código mais composto do que em SGD."
        ),
        how_to_read=(
            "`ENTITY_OTHER+MOVIE_OR_SERIES` deve ser lido como tipo `ENTITY_OTHER` e "
            "alvo `MOVIE_OR_SERIES`. O sinal de mais separa a função da marcação e a "
            "entidade à qual ela se refere."
        ),
        source_context=(
            "...o artigo descreve CCPE como parte do conjunto de diálogos de filmes e "
            "preferências usado no USS..."
        ),
    ),
    DatasetGuide(
        name="JDDC",
        full_name="Jingdong Dialogue Corpus",
        language="Chinês",
        domain="Comércio eletrônico e atendimento ao cliente",
        description=(
            "O JDDC é o componente chinês do USS e vem de atendimento em comércio "
            "eletrônico. Ele ajuda a explicar o desenho geral do dataset, mas não entra "
            "nas análises principais desta versão porque exige tratamento próprio de "
            "idioma e categorias."
        ),
        how_to_read=(
            "O JDDC permanece como contexto de origem do USS. As análises visuais se "
            "concentram em SGD, MWOZ, ReDial e CCPE para manter comparação em inglês."
        ),
        source_context=(
            "...a preparação do USS começa com JDDC, um corpus chinês de atendimento "
            "em comércio eletrônico com grande volume de diálogos..."
        ),
    ),
]


COLUMN_GUIDE = [
    ("dataset", "Origem da linha, como SGD, MWOZ, ReDial ou CCPE."),
    ("dialogue_id", "Identificador do diálogo dentro de cada dataset."),
    ("turn_id", "Posição da linha dentro do diálogo."),
    ("role", "Papel da linha: USER ou SYSTEM."),
    ("text", "Texto original da fala ou a marca OVERALL."),
    ("action_raw", "Anotação original do arquivo. Valores vazios viram UNKNOWN."),
    ("action_group", "Agrupamento derivado da anotação original."),
    ("action_type", "Tipo principal quando a anotação pode ser separada."),
    ("action_target", "Alvo da anotação quando o dataset fornece código composto."),
    ("satisfaction_scores", "Notas individuais dos anotadores humanos."),
    ("satisfaction_annotation_count", "Quantidade de notas registradas naquela linha."),
    ("satisfaction_mode", "Nota mais frequente; em empate, fica a menor nota."),
    ("satisfaction_mean", "Média das notas dos anotadores."),
    ("satisfaction_interpretation", "Leitura textual das notas individuais."),
    ("satisfaction_disagreement", "Desvio padrão das notas registradas."),
    ("is_overall", "Marca a linha de satisfação geral do diálogo."),
    ("language", "Idioma principal do dataset original."),
    ("satisfaction_3_classes", "Agrupamento derivado da escala 1 a 5."),
    ("satisfaction_binary", "Agrupamento auxiliar para separar notas abaixo de 3."),
]


ARTICLE_NOTES = [
    ArticleNote(
        title="Por que satisfação precisa do diálogo inteiro",
        translated=(
            "A motivação do USS nasce da limitação de avaliar apenas respostas isoladas. "
            "Uma interação pode parecer correta em um turno e ainda assim produzir uma "
            "experiência ruim quando a conversa completa é considerada."
        ),
        source_context=(
            "...o artigo contrasta avaliação offline por turno com a necessidade de "
            "entender utilidade geral e satisfação ao longo do fluxo do diálogo..."
        ),
    ),
    ArticleNote(
        title="Como o USS foi construído",
        translated=(
            "O USS combina datasets já existentes e adiciona anotações humanas de "
            "satisfação. A composição mistura comércio eletrônico, reservas, assistentes "
            "virtuais e recomendação de filmes."
        ),
        source_context=(
            "...a seção de preparação lista JDDC, SGD, MultiWOZ 2.1, ReDial e CCPE como "
            "as cinco bases usadas para formar a coleção..."
        ),
    ),
    ArticleNote(
        title="O momento da anotação",
        translated=(
            "A satisfação é atribuída antes da fala do usuário. Isso significa que a nota "
            "representa uma leitura do contexto anterior, não uma análise de sentimento "
            "da frase que aparece na mesma linha."
        ),
        source_context=(
            "...a descrição da coleta diz que os anotadores viam o contexto do diálogo e "
            "avaliavam a satisfação antes do próximo enunciado do usuário..."
        ),
    ),
    ArticleNote(
        title="A escala de 1 a 5",
        translated=(
            "A escala vai de muito insatisfeito a muito satisfeito. As notas extremas "
            "dependem de entender se o sistema compreendeu a necessidade do usuário e se "
            "a resposta anterior ajudou a resolver a tarefa."
        ),
        source_context=(
            "...a tabela de avaliação define cinco níveis, indo de falha em entender o "
            "pedido até resolução completa e eficiente..."
        ),
    ),
    ArticleNote(
        title="A linha OVERALL",
        translated=(
            "`OVERALL` representa satisfação no nível do diálogo completo. Ela deve ser "
            "separada das falas reais de usuário, porque muda a unidade de análise."
        ),
        source_context=(
            "...nos detalhes experimentais, os autores tratam a satisfação do diálogo "
            "como o último enunciado de usuário e usam `overall` como identificador..."
        ),
    ),
    ArticleNote(
        title="O desbalanceamento das notas",
        translated=(
            "A nota 3 aparece com muita frequência. Por isso, gráficos e comentários "
            "numéricos precisam mostrar denominadores e não devem transformar diferenças "
            "entre bases em ranking de qualidade."
        ),
        source_context=(
            "...o artigo relata desbalanceamento sério nos rótulos de satisfação e, nos "
            "experimentos, compensa parcialmente as notas diferentes de 3..."
        ),
    ),
]


RATING_GUIDE = [
    (1, "Muito insatisfeito", "O sistema falha em entender ou atender a solicitação."),
    (2, "Insatisfeito", "O sistema entende algo do pedido, mas não satisfaz o usuário."),
    (3, "Normal", "O sistema atende parcialmente ou orienta como resolver o pedido."),
    (4, "Satisfeito", "O sistema atende, mas pode exigir mais turnos ou informação excessiva."),
    (5, "Muito satisfeito", "O sistema entende e resolve a solicitação de modo eficiente."),
]


ANNOTATION_GUIDES = [
    AnnotationGuide(
        dataset="SGD",
        code="THANK_YOU",
        meaning="A fala do usuário agradece ao sistema.",
        how_to_read=(
            "O agradecimento não significa automaticamente nota alta. A satisfação "
            "continua dependendo do contexto anterior à fala."
        ),
        source="Atos de diálogo do SGD preservados no USS.",
    ),
    AnnotationGuide(
        dataset="MWOZ",
        code="Hotel-Inform",
        meaning="Domínio Hotel com ato Inform.",
        how_to_read=(
            "A primeira parte indica o domínio da tarefa. A segunda indica que o usuário "
            "fornece informação relevante para aquele domínio."
        ),
        source="Formato domínio-ato do MultiWOZ.",
    ),
    AnnotationGuide(
        dataset="CCPE",
        code="ENTITY_OTHER+MOVIE_OR_SERIES",
        meaning="Tipo ENTITY_OTHER aplicado ao alvo MOVIE_OR_SERIES.",
        how_to_read=(
            "O sinal de mais separa a função da marcação e o alvo. Nesse exemplo, a fala "
            "menciona algo sobre uma obra audiovisual sem cair nas categorias mais "
            "específicas de nome, descrição ou preferência."
        ),
        source="Esquema de anotação do CCPE preservado no USS.",
    ),
    AnnotationGuide(
        dataset="ReDial",
        code="UNKNOWN",
        meaning="Ausência de ação no arquivo principal carregado.",
        how_to_read=(
            "Não é uma intenção do usuário. No ReDial, `UNKNOWN` aparece porque o arquivo "
            "principal do USS não traz ações no mesmo campo usado pelos demais datasets."
        ),
        source="Arquivo principal do ReDial no USS.",
    ),
]


def explain_annotation(dataset: str, code: str) -> AnnotationGuide:
    """Retorna explicação para uma anotação conhecida ou para seu padrão."""
    normalized_code = str(code).strip()
    normalized_dataset = str(dataset).strip()

    for guide in ANNOTATION_GUIDES:
        if guide.dataset == normalized_dataset and guide.code == normalized_code:
            return guide

    if normalized_code == "UNKNOWN":
        return AnnotationGuide(
            dataset=normalized_dataset,
            code=normalized_code,
            meaning="Anotação ausente ou não identificada no arquivo original.",
            how_to_read=(
                "`UNKNOWN` deve ser lido como lacuna de anotação, não como categoria "
                "semântica comparável entre datasets."
            ),
            source="Normalização local de campos vazios.",
        )

    if normalized_dataset == "MWOZ" and "-" in normalized_code:
        domain, act = normalized_code.split("-", 1)
        return AnnotationGuide(
            dataset=normalized_dataset,
            code=normalized_code,
            meaning=f"Domínio {domain} com ato {act}.",
            how_to_read=(
                "A parte antes do hífen indica o domínio da tarefa; a parte depois do "
                "hífen indica o ato de diálogo."
            ),
            source="Formato domínio-ato do MultiWOZ.",
        )

    if normalized_dataset == "CCPE" and "+" in normalized_code:
        action_type, target = normalized_code.split("+", 1)
        return AnnotationGuide(
            dataset=normalized_dataset,
            code=normalized_code,
            meaning=f"Tipo {action_type} aplicado ao alvo {target}.",
            how_to_read=(
                "A parte antes do sinal de mais descreve o tipo de marcação; a parte "
                "depois do sinal de mais descreve a entidade ou alvo mencionado."
            ),
            source="Formato composto do CCPE.",
        )

    return AnnotationGuide(
        dataset=normalized_dataset,
        code=normalized_code,
        meaning="Código original preservado do dataset.",
        how_to_read=(
            "Use exemplos reais e a distribuição de notas para interpretar este código. "
            "Ele foi mantido como aparece no arquivo original."
        ),
        source="Arquivo original do USS.",
    )
