from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetGuide:
    """Descreve um dataset usado no explorador USS."""

    name: str
    full_name: str
    language: str
    domain: str
    role_in_app: str
    description: str
    how_to_read: str
    original_excerpt: str = ""


@dataclass(frozen=True)
class ArticleNote:
    """Guarda uma leitura traduzida com um trecho curto original do artigo."""

    title: str
    translated: str
    original_excerpt: str


DATASET_GUIDES = [
    DatasetGuide(
        name="SGD",
        full_name="Schema Guided Dialogue",
        language="Inglês",
        domain="Assistente virtual com múltiplos domínios",
        role_in_app="Dataset principal",
        description=(
            "O SGD é formado por conversas orientadas a tarefa entre uma pessoa e "
            "um assistente virtual, cobrindo 16 domínios. No USS, ele ajuda a observar "
            "como a satisfação muda em interações típicas de assistente."
        ),
        how_to_read=(
            "Observe ações como informar, pedir dados, confirmar, negar ou agradecer. "
            "Na inspeção de diálogo, veja se a satisfação cai depois de respostas que "
            "pedem correção ou deixam a tarefa incompleta."
        ),
        original_excerpt="a human and a virtual assistant spanning 16 domains",
    ),
    DatasetGuide(
        name="MWOZ",
        full_name="MultiWOZ 2.1",
        language="Inglês",
        domain="Hotel, restaurante, táxi, trem e atrações",
        role_in_app="Dataset principal",
        description=(
            "O MultiWOZ 2.1 é uma base multidomínio com diálogos sobre tarefas como "
            "hotel, restaurante, táxi, trem e atrações. No app, ele é útil para comparar "
            "satisfação por domínio e por tipo de ação."
        ),
        how_to_read=(
            "As ações frequentemente combinam domínio e ato, como Hotel-Inform "
            "ou Restaurant-Request. O campo action_group separa o domínio para facilitar "
            "comparações entre áreas da conversa."
        ),
        original_excerpt="spanning 7 distinct domains and containing over 10K dialogues",
    ),
    DatasetGuide(
        name="ReDial",
        full_name="Recommendation Dialogues",
        language="Inglês",
        domain="Recomendação de filmes",
        role_in_app="Dataset principal",
        description=(
            "O ReDial contém conversas de recomendação de filmes. No USS, ele traz "
            "satisfação anotada, mas o dataset original não fornecia ações no mesmo "
            "formato dos demais."
        ),
        how_to_read=(
            "As ações usadas no projeto vieram de uma anotação externa, o IARD. "
            "No arquivo principal, o app preserva as linhas e marca ações vazias "
            "como UNKNOWN."
        ),
        original_excerpt="the original dataset does not provide actions",
    ),
    DatasetGuide(
        name="CCPE",
        full_name="Coached Conversational Preference Elicitation",
        language="Inglês",
        domain="Preferências sobre filmes",
        role_in_app="Dataset principal",
        description=(
            "O CCPE registra conversas em que usuário e assistente discutem preferências "
            "de filmes. Ele é menor, mas muito útil para observar como preferências, "
            "entidades e recomendações aparecem na conversa."
        ),
        how_to_read=(
            "As ações podem vir no formato ENTITY_PREFERENCE+MOVIE_OR_SERIES. "
            "O app separa isso em action_type e action_target para indicar o tipo "
            "de informação e o alvo da preferência."
        ),
        original_excerpt="discussing movie preferences",
    ),
    DatasetGuide(
        name="JDDC",
        full_name="Jingdong Dialogue Corpus",
        language="Chinês",
        domain="Comércio eletrônico e atendimento ao cliente",
        role_in_app="Bônus para estudo futuro",
        description=(
            "O JDDC é um grande corpus chinês de atendimento e comércio eletrônico. "
            "Ele é o maior componente do USS e possui categorias de ação ricas."
        ),
        how_to_read=(
            "No Streamlit, ele deve permanecer como bônus por exigir tradução ou "
            "tratamento específico de idioma. As análises principais priorizam os "
            "datasets em inglês."
        ),
        original_excerpt="real-world Chinese e-commerce conversation corpus",
    ),
]


COLUMN_GUIDE = [
    ("dataset", "Identifica a origem da linha, como SGD, MWOZ, ReDial ou CCPE."),
    ("dialogue_id", "Número do diálogo dentro de cada dataset."),
    ("turn_id", "Posição da linha dentro do diálogo."),
    ("role", "Indica se a linha pertence ao USER ou ao SYSTEM."),
    ("text", "Texto original da fala ou a marca OVERALL."),
    ("action_raw", "Ação original do arquivo. Quando está vazia, o app usa UNKNOWN."),
    ("action_group", "Agrupamento derivado da ação, útil para filtros e gráficos."),
    ("action_type", "Parte principal da ação quando ela pode ser separada."),
    ("action_target", "Alvo da ação quando o dataset fornece uma ação composta."),
    ("satisfaction_scores", "Lista com as notas dadas pelos anotadores humanos."),
    ("satisfaction_annotation_count", "Quantidade de notas registradas naquela linha."),
    ("satisfaction_mode", "Nota majoritária na escala de 1 a 5, usada em gráficos."),
    ("satisfaction_mean", "Média das notas dos anotadores, usada em análises auxiliares."),
    ("satisfaction_interpretation", "Tradução textual das notas para leitura humana."),
    ("satisfaction_disagreement", "Medida de discordância entre anotadores."),
    ("is_overall", "Marca linhas USER OVERALL, que representam a satisfação geral do diálogo."),
    ("language", "Idioma principal do dataset."),
    ("satisfaction_3_classes", "Agrupa notas em insatisfeito, neutro ou satisfeito."),
    ("satisfaction_binary", "Agrupa notas em baixa satisfação ou não baixa satisfação."),
]


ARTICLE_NOTES = [
    ArticleNote(
        title="O problema: avaliar conversas inteiras",
        translated=(
            "O artigo argumenta que avaliar apenas um turno isolado não captura "
            "a utilidade geral do sistema nem a satisfação do usuário com o fluxo "
            "do diálogo."
        ),
        original_excerpt="the overall usefulness of the system or about users’ satisfaction",
    ),
    ArticleNote(
        title="A proposta: simular satisfação do usuário",
        translated=(
            "A tarefa proposta combina simulação de usuário com predição de satisfação, "
            "para tornar a avaliação de sistemas de diálogo mais próxima de uma "
            "experiência humana."
        ),
        original_excerpt="make the simulation more human-like",
    ),
    ArticleNote(
        title="A origem: cinco datasets de diálogo",
        translated=(
            "O USS é baseado em cinco datasets de diálogo orientados a tarefa, cobrindo "
            "comércio eletrônico, assistentes virtuais, reservas e recomendação de filmes."
        ),
        original_excerpt="five benchmark task-oriented dialogue datasets",
    ),
    ArticleNote(
        title="A anotação: contexto antes da fala",
        translated=(
            "A satisfação é avaliada antes da fala do usuário e depende do histórico "
            "anterior, não apenas do sentimento expresso na frase atual."
        ),
        original_excerpt="before the user utterance",
    ),
    ArticleNote(
        title="A qualidade: rechecagem quando há divergência",
        translated=(
            "O artigo explica que pelo menos três anotadores avaliaram os dados e que "
            "um quarto podia ser chamado quando havia discrepância entre as notas."
        ),
        original_excerpt="we ask a fourth annotator to recheck it",
    ),
    ArticleNote(
        title="O cuidado: classes desbalanceadas",
        translated=(
            "Como a classe 3 domina muitos recortes, as visualizações e modelos futuros "
            "precisam considerar o desbalanceamento das notas de satisfação."
        ),
        original_excerpt="serious imbalance of the satisfaction label",
    ),
]


RATING_GUIDE = [
    (1, "Muito insatisfeito", "O sistema falha em entender ou atender a solicitação."),
    (2, "Insatisfeito", "O sistema entende algo do pedido, mas não satisfaz o usuário."),
    (3, "Normal", "O sistema atende parcialmente ou orienta como o pedido pode ser resolvido."),
    (4, "Satisfeito", "O sistema atende, mas pode exigir turnos extras ou informação excessiva."),
    (5, "Muito satisfeito", "O sistema entende e resolve a solicitação de modo completo e eficiente."),
]
