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


@dataclass(frozen=True)
class ArticleNote:
    """Guarda uma leitura em português com contexto do artigo."""

    title: str
    translated: str
    source_reference: str
    source_excerpt: str


@dataclass(frozen=True)
class AnnotationGuide:
    """Explica uma anotação ou padrão de anotação."""

    dataset: str
    code: str
    meaning: str
    how_to_read: str
    source: str


@dataclass(frozen=True)
class DatasetAnnotationNarrative:
    """Explica o vocabulário de anotação de um dataset."""

    dataset: str
    title: str
    body: str
    examples_intro: str


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
        title="Por que o USS junta datasets diferentes",
        translated=(
            "O USS não nasce como uma coleta única. Ele combina bases já existentes para "
            "reunir domínios diferentes e observar satisfação em vários tipos de tarefa."
        ),
        source_reference="Seção 4.1, Data preparation",
        source_excerpt="...five benchmark task-oriented dialogue datasets...",
    ),
    ArticleNote(
        title="O momento da anotação",
        translated=(
            "A satisfação é atribuída antes da fala do usuário. Isso significa que a nota "
            "representa uma leitura do contexto anterior, não uma análise de sentimento "
            "da frase que aparece na mesma linha."
        ),
        source_reference="Seção 4.2, User satisfaction assessment",
        source_excerpt="...before the user utterance...",
    ),
    ArticleNote(
        title="A linha OVERALL",
        translated=(
            "`OVERALL` representa satisfação no nível do diálogo completo. Ela deve ser "
            "separada das falas reais de usuário, porque muda a unidade de análise."
        ),
        source_reference="Seção 5.2, Implementation details",
        source_excerpt='...use “overall” as the identification...',
    ),
    ArticleNote(
        title="O desbalanceamento das notas",
        translated=(
            "A nota 3 aparece com muita frequência. Por isso, gráficos e comentários "
            "numéricos precisam mostrar denominadores e não devem transformar diferenças "
            "entre bases em ranking de qualidade."
        ),
        source_reference="Seção 5.2, Implementation details",
        source_excerpt="...serious imbalance of the satisfaction label...",
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


ANNOTATION_NARRATIVES = {
    "SGD": DatasetAnnotationNarrative(
        dataset="SGD",
        title="SGD: atos de diálogo de um assistente orientado a tarefa",
        body=(
            "No SGD, as anotações funcionam como atos de diálogo. Elas descrevem o tipo "
            "de movimento que a fala do usuário faz dentro da tarefa: informar algo, "
            "confirmar, negar, pedir uma alternativa, agradecer ou encerrar. Esses atos "
            "são úteis porque aproximam o texto livre de uma estrutura de interação. Em "
            "vez de olhar apenas para a frase, a análise consegue perguntar que papel "
            "aquela fala exerce na conversa."
        ),
        examples_intro=(
            "`THANK_YOU` é um agradecimento, mas não deve ser lido automaticamente como "
            "satisfação alta. A nota continua ligada ao contexto anterior. Um usuário "
            "pode agradecer depois de uma solução boa, mas também pode encerrar uma "
            "interação apenas porque não há mais o que tentar."
        ),
    ),
    "MWOZ": DatasetAnnotationNarrative(
        dataset="MWOZ",
        title="MWOZ: domínio e ato na mesma anotação",
        body=(
            "No MWOZ, a anotação geralmente combina o domínio da tarefa com o ato de "
            "diálogo. Isso torna o código mais informativo do que um rótulo isolado, "
            "porque ele preserva o assunto da conversa e o movimento feito pelo usuário. "
            "Quando aparece `Hotel-Inform`, a fala está no domínio de hotel e fornece "
            "alguma informação relevante para a tarefa. Quando aparece "
            "`Restaurant-Request`, a fala pede informação dentro do domínio de restaurante."
        ),
        examples_intro=(
            "O hífen em `Hotel-Inform` não é decoração: ele separa duas camadas. A "
            "primeira parte localiza o domínio; a segunda descreve o ato. Por isso, "
            "comparar apenas `Inform` sem considerar o domínio pode apagar diferenças "
            "importantes entre tipos de tarefa."
        ),
    ),
    "ReDial": DatasetAnnotationNarrative(
        dataset="ReDial",
        title="ReDial: recomendação de filmes sem ação no arquivo principal",
        body=(
            "O ReDial é diferente dos outros datasets desta análise porque o arquivo "
            "principal carregado não traz ações no mesmo campo usado por SGD, MWOZ e "
            "CCPE. Por isso, as falas aparecem como `UNKNOWN`. Esse valor não representa "
            "uma intenção do usuário nem uma categoria semântica; ele sinaliza ausência "
            "de anotação de ação nesse arquivo."
        ),
        examples_intro=(
            "Nesse caso, o mais importante é não comparar `UNKNOWN` do ReDial com "
            "`UNKNOWN` de outro dataset como se fossem a mesma coisa. No ReDial, ele "
            "domina porque a ação não está disponível no arquivo principal."
        ),
    ),
    "CCPE": DatasetAnnotationNarrative(
        dataset="CCPE",
        title="CCPE: tipo de entidade e alvo da preferência",
        body=(
            "No CCPE, os códigos frequentemente ligam uma marcação sobre entidade ao "
            "tipo de objeto mencionado na conversa. O sinal de mais cria uma anotação "
            "composta: antes dele aparece o tipo da marcação; depois dele aparece o alvo. "
            "Isso combina bem com o domínio do dataset, porque conversas sobre filmes "
            "dependem de preferências, nomes, gêneros, descrições e referências a obras "
            "ou pessoas."
        ),
        examples_intro=(
            "`ENTITY_OTHER+MOVIE_OR_SERIES` indica uma marcação do tipo `ENTITY_OTHER` "
            "aplicada ao alvo `MOVIE_OR_SERIES`. A graça desse formato é preservar a "
            "estrutura da menção: não é só uma ação geral, mas uma ação ligada a um tipo "
            "de entidade."
        ),
    ),
}


def annotation_narrative(dataset: str) -> DatasetAnnotationNarrative:
    """Retorna a explicação narrativa de anotações para um dataset."""
    return ANNOTATION_NARRATIVES.get(
        dataset,
        DatasetAnnotationNarrative(
            dataset=dataset,
            title=f"{dataset}: vocabulário preservado do arquivo original",
            body=(
                "As anotações deste dataset foram preservadas como aparecem no USS. "
                "A interpretação deve combinar frequência, exemplos reais e distribuição "
                "de notas."
            ),
            examples_intro=(
                "Códigos desconhecidos devem ser lidos com apoio dos exemplos, porque "
                "nem todo dataset usa o mesmo esquema de anotação."
            ),
        ),
    )


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
