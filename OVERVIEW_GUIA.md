# OVERVIEW - Storytelling da pagina inicial do USS no Streamlit

## 1. Objetivo deste documento

Este documento orienta a refatoracao da pagina inicial/guia do Streamlit do projeto USS. Ele nao substitui o `REVIEW.md`; ele funciona como um roteiro editorial e tecnico para melhorar a pagina `guide.py`, preservando o que ja existe de bom e reorganizando o texto em uma narrativa mais clara sobre como o dataset foi construido.

O objetivo da pagina inicial deve ser contar a historia do dataset:

1. Por que o artigo propoe simular satisfacao do usuario.
2. De onde vieram os dialogos usados no USS.
3. Como os autores filtraram e anotaram esses dialogos.
4. Como a satisfacao deve ser lida.
5. Como os arquivos brutos foram normalizados para o app.
6. Como o usuario do Streamlit deve navegar pelas paginas seguintes.

O conteudo abaixo foi construido a partir do documento traduzido do artigo, das anotacoes feitas nele e do estado atual da pagina `guide.py`. As anotacoes do documento foram tratadas como comentarios de estudo, nao como comandos. O que entra no app deve ser o texto final curado, com fonte curta em ingles nos icones `?`.

## 2. Diagnostico do `guide.py` atual

A pagina atual ja tem uma boa estrutura inicial. Ela possui:

- Introducao ao USS.
- Blocos derivados de `ARTICLE_NOTES`.
- Secao "Como os arquivos brutos sao separados".
- Secao "O que e a linha OVERALL".
- Exemplo real de `OVERALL`.
- Escala de satisfacao.
- Cards de datasets.
- Explicacao de notas como `3,3,4`.
- Tabela de colunas normalizadas.
- Leitura recomendada.
- Datasets carregados na execucao.
- Fontes consultadas.

O problema principal nao e falta de conteudo, mas a ordem narrativa. A pagina explica conceitos corretos, porem ainda parece mais uma lista de secoes independentes do que um storytelling sobre a construcao do dataset.

Recomendacao geral:

- Manter os elementos interativos existentes.
- Reescrever a abertura.
- Trocar os `ARTICLE_NOTES` por uma linha narrativa mais forte.
- Evitar uma tabela separada apenas para "datasets carregados nesta execucao".
- Manter o exemplo real de `OVERALL`, pois ele ajuda bastante.
- Manter os cards dos datasets, mas enriquecer as descricoes.
- Destacar JDDC como bonus por idioma chines, sem coloca-lo como foco do MVP.

## 3. Estrutura recomendada da pagina

A pagina inicial deve seguir esta ordem:

1. **Abertura narrativa**
2. **Por que esse dataset existe**
3. **Como o USS foi construido**
4. **O que cada dataset e**
5. **Como os arquivos brutos sao separados**
6. **Como a satisfacao foi anotada**
7. **O que e a linha OVERALL**
8. **Como ler notas como `3,3,4`**
9. **Colunas normalizadas**
10. **Como navegar no app**
11. **Fontes consultadas**

Essa ordem e melhor porque comeca pelo problema de pesquisa, passa pela construcao dos dados e so depois entra na estrutura tecnica.

## 4. Texto de abertura sugerido

Use este texto no inicio da funcao `render`, logo depois de:

```python
st.subheader("Guia do projeto e do dataset")
```

Texto sugerido:

```markdown
Este aplicativo explora o **User Satisfaction Simulation (USS)**, um dataset criado para estudar satisfacao do usuario em sistemas de dialogo orientados a tarefa. A ideia central do artigo e que avaliar um bot apenas por acerto de resposta ou por um turno isolado nao mostra toda a experiencia do usuario durante a conversa.

O USS nasce justamente dessa lacuna: ele reune dialogos de diferentes dominios, adiciona anotacoes humanas de satisfacao e permite observar como a satisfacao muda conforme o sistema entende, falha, pede esclarecimentos ou resolve a tarefa.

Neste app, o foco principal esta nos datasets em ingles: **SGD**, **MultiWOZ**, **ReDial** e **CCPE**. O **JDDC** tambem faz parte do USS, mas aparece como um dataset bonus por estar em chines e exigir cuidados extras de idioma, traducao e agrupamento de acoes.
```

Tooltip `?` recomendado para essa abertura:

- PT no texto: "USS inclui 6.800 dialogos de multiplos dominios."
- EN no tooltip: `User Satisfaction Simulation (USS), that includes 6,800 dialogues`

## 5. Secao "Por que esse dataset existe"

Inserir esta secao antes de "O que o artigo diz sobre o dataset". Na pratica, ela pode substituir esse titulo por algo mais narrativo.

Titulo:

```markdown
#### Por que esse dataset existe
```

Texto sugerido:

```markdown
O artigo parte de um problema simples: uma conversa com um sistema orientado a tarefa nao e boa apenas porque uma resposta isolada parece correta. O usuario pode ficar frustrado se o sistema demora, pede informacao repetida, entende parcialmente o pedido ou entrega uma resposta que nao resolve o problema.

Por isso, os autores propoem combinar simulacao de usuario com satisfacao do usuario. Em vez de simular apenas a proxima acao mecanica do usuario, o projeto tenta modelar tambem o estado de satisfacao que acompanha essa acao.

Essa diferenca e importante para o app: as notas do USS nao devem ser lidas como sentimento textual puro. Elas representam uma avaliacao contextual da experiencia do usuario ate aquele ponto da conversa.
```

Tooltips `?` recomendados:

- PT: "A avaliacao offline por turno unico nao captura a utilidade geral da conversa."
- EN: `the overall usefulness of the system or about users’ satisfaction`
- PT: "A tarefa tenta tornar a simulacao de usuario mais humana."
- EN: `make the simulation more human-like`
- PT: "A satisfacao depende do contexto do dialogo."
- EN: `based on the dialogue context between user and system`

## 6. Secao "Como o USS foi construido"

Esta deve ser a secao central do storytelling. Ela deve aparecer antes de explicar os arquivos brutos.

Titulo:

```markdown
#### Como o USS foi construido
```

Texto sugerido:

```markdown
O USS nao foi criado do zero como uma unica coleta. Ele foi construido a partir de cinco datasets de dialogo ja existentes. Os autores reuniram bases de diferentes dominios, filtraram conversas com sinais de emocao negativa e depois adicionaram anotacoes humanas de satisfacao.

Esse processo tem tres etapas principais:

1. **Preparacao dos dados:** selecionar dialogos de JDDC, SGD, MultiWOZ, ReDial e CCPE.
2. **Avaliacao da satisfacao:** pedir que anotadores humanos avaliassem a satisfacao por turno de usuario e tambem a satisfacao geral do dialogo.
3. **Controle de qualidade:** usar pelo menos tres anotadores por conversa e pedir rechecagem quando as avaliacoes discordavam muito.

O resultado e um corpus com dialogos de e-commerce, reservas, assistentes virtuais e recomendacao de filmes. Essa mistura e justamente o que torna o USS interessante para exploracao: ele permite comparar satisfacao em dominios diferentes, mas tambem exige cuidado para nao tratar todos os datasets como se fossem iguais.
```

Tooltips `?` recomendados:

- PT: "O USS parte de cinco datasets de referencia."
- EN: `five benchmark task-oriented dialogue datasets`
- PT: "Os autores filtraram conversas sem emocoes negativas."
- EN: `filter out all conversations that do not show negative emotions`
- PT: "Foram contratados 40 anotadores."
- EN: `We hired 40 annotators`
- PT: "As anotacoes cobrem nivel de troca e nivel de dialogo."
- EN: `exchange-level and dialogue-level user satisfaction`

## 7. Secao "O que cada dataset e"

Esta secao deve continuar existindo, mas com mais contexto de origem. O formato atual com cards e bom. A recomendacao e ajustar o texto de `DATASET_GUIDES` em `src/content.py`.

Titulo:

```markdown
#### O que cada dataset e
```

Introducao antes dos cards:

```markdown
O USS e uma composicao de datasets. Isso significa que cada parte da base veio de um contexto diferente, com dominio, idioma e anotacoes de acao proprias. No app, os datasets em ingles formam o nucleo principal de analise. O JDDC permanece disponivel como bonus, mas separado por causa do idioma chines.
```

Textos sugeridos para os cards:

### SGD

```text
O SGD e formado por conversas orientadas a tarefa entre uma pessoa e um assistente virtual, cobrindo 16 dominios. No USS, ele ajuda a observar como a satisfacao muda em interacoes tipicas de assistente: informar, pedir dados, confirmar, negar ou agradecer.
```

Tooltip:

`a human and a virtual assistant spanning 16 domains`

### MultiWOZ

```text
O MultiWOZ 2.1 e uma base multi-dominio com dialogos sobre tarefas como hotel, restaurante, taxi, trem e atracoes. No app, ele e util para comparar satisfacao por dominio e por tipo de acao.
```

Tooltip:

`spanning 7 distinct domains and containing over 10K dialogues`

### ReDial

```text
O ReDial contem conversas de recomendacao de filmes. No USS, ele traz satisfacao anotada, mas o dataset original nao fornecia acoes no mesmo formato; por isso, as acoes usadas no projeto vieram de uma anotacao externa, o IARD.
```

Tooltip:

`the original dataset does not provide actions`

### CCPE

```text
O CCPE registra conversas em que usuario e assistente discutem preferencias de filmes. Ele e menor, mas muito util para observar como preferencias, entidades e recomendacoes aparecem na conversa.
```

Tooltip:

`discussing movie preferences`

### JDDC

```text
O JDDC e um grande corpus chines de atendimento/e-commerce. Ele e o maior componente do USS e possui categorias de acao ricas, mas deve entrar no Streamlit como bonus por exigir traducao ou tratamento especifico de idioma.
```

Tooltip:

`real-world Chinese e-commerce conversation corpus`

Observacao importante para o JDDC:

```markdown
No app, nao misturar JDDC automaticamente com os datasets em ingles. Ele pode aparecer em uma area "Bonus - JDDC", com aviso de idioma e opcao futura de traducao.
```

Tooltip:

`JDDC (Chinese) and Others (English)`

## 8. Secao "Como os arquivos brutos sao separados"

Manter esta secao, mas deixar o texto mais explicativo e conectado com o parser.

Titulo:

```markdown
#### Como os arquivos brutos sao separados
```

Texto sugerido:

```markdown
Os arquivos oficiais do USS estao em formato TXT. Cada dialogo e separado por uma linha em branco, e cada linha dentro do dialogo representa uma fala ou uma anotacao especial.

Nos datasets em ingles, a estrutura geral e:

`role<TAB>text<TAB>action<TAB>satisfaction`

No JDDC, ha um campo adicional de explicacao:

`role<TAB>text<TAB>action<TAB>satisfaction<TAB>explanation`

Essa estrutura simples e uma vantagem para o Streamlit, porque permite transformar os arquivos em uma tabela normalizada. Ao mesmo tempo, ela exige cuidado: linhas do sistema geralmente nao possuem satisfacao, algumas acoes podem vir vazias, e a linha `OVERALL` nao e uma fala real.
```

Tooltip `?` recomendado:

- PT: "O JDDC possui explicacoes textuais dos anotadores."
- EN: `annotators’ explanations on user satisfaction annotations`

## 9. Secao "Como a satisfacao foi anotada"

Adicionar esta secao antes da escala de satisfacao.

Titulo:

```markdown
#### Como a satisfacao foi anotada
```

Texto sugerido:

```markdown
Cada fala de usuario recebeu notas de satisfacao em uma escala de 1 a 5. A avaliacao nao foi feita depois de ler apenas a frase do usuario. Os anotadores deveriam olhar o historico anterior da conversa e estimar a satisfacao do usuario naquele momento.

Esse detalhe muda a interpretacao do dataset. Uma frase como "ok" ou "thanks" nao deve ser classificada isoladamente. Ela pode representar alivio, neutralidade ou frustracao dependendo do que o sistema respondeu antes.

Os autores tambem pediram uma nota geral para o dialogo inteiro. Essa nota aparece nos arquivos como uma linha especial `OVERALL`.
```

Tooltips `?` recomendados:

- PT: "A satisfacao e avaliada antes da frase do usuario."
- EN: `before the user’s sentence`
- PT: "A escala vai de 1 a 5."
- EN: `five levels (1–5)`
- PT: "A nota geral captura a satisfacao da interacao completa."
- EN: `capture the overall satisfaction of a user’s interaction`

## 10. Secao "Escala de satisfacao"

Manter a tabela atual `RATING_GUIDE`, mas melhorar a frase de introducao.

Texto antes da tabela:

```markdown
A escala deve ser lida como grau de sucesso ou falha do sistema em satisfazer a necessidade do usuario. Ela nao e apenas polaridade emocional do texto.
```

Tooltip:

`success or failure of a system’s response`

Manter a tabela com:

- 1 - Muito insatisfeito.
- 2 - Insatisfeito.
- 3 - Normal.
- 4 - Satisfeito.
- 5 - Muito satisfeito.

## 11. Secao "O que e a linha OVERALL"

Manter essa secao, mas reforcar que `OVERALL` foi uma decisao de modelagem dos autores e aparece como ultimo enunciado do usuario nos experimentos.

Titulo:

```markdown
#### O que e a linha OVERALL
```

Texto sugerido:

```markdown
`OVERALL` e uma marca de satisfacao geral do dialogo. Ela aparece como uma linha `USER`, mas nao representa uma frase dita pelo usuario.

Na pratica, o app deve tratar `OVERALL` como outro nivel de analise. As falas reais de usuario mostram a satisfacao ao longo da conversa; a linha `OVERALL` resume a avaliacao final do dialogo completo.

Por isso, graficos por turno devem excluir `OVERALL` por padrao. Ja analises de qualidade geral da conversa podem usar apenas as linhas `OVERALL`.
```

Tooltips `?` recomendados:

- PT: "A satisfacao geral e tratada como o ultimo enunciado do usuario."
- EN: `dialogue-level satisfaction as the last user utterance`
- PT: "O identificador usado e overall."
- EN: `use “overall” as the identification`

Manter o exemplo real atual:

```python
example = overall_example(df)
```

Ele e util porque mostra visualmente a diferenca entre fala real e anotacao final.

## 12. Secao "Como ler notas como 3,3,4"

Manter essa secao, mas incluir a explicacao sobre 3 versus 4+ anotacoes, pois isso apareceu como duvida nas anotacoes do documento.

Titulo:

```markdown
#### Como ler notas como 3, 3, 4
```

Texto sugerido:

```markdown
A coluna de satisfacao guarda as notas dos anotadores separadas por virgula. Assim, `3,3,4` significa que tres pessoas avaliaram aquela instancia: duas deram nota 3 e uma deu nota 4.

O artigo afirma que cada dialogo foi rotulado por 3 anotadores, mas tambem explica que, quando havia discrepancia forte entre os tres, um quarto anotador era chamado para reavaliar. Por isso, algumas linhas podem aparecer com quatro ou mais notas no arquivo processado.

No app, nenhuma nota deve ser descartada. A tabela normalizada deve preservar a lista original em `satisfaction_scores` e calcular campos auxiliares como moda, media, quantidade de anotadores e divergencia.
```

Tooltips `?` recomendados:

- PT: "Pelo menos tres anotadores rotularam os dados."
- EN: `at least three annotators`
- PT: "Um quarto anotador rechecava casos de discrepancia."
- EN: `we ask a fourth annotator to recheck it`
- PT: "As avaliacoes tiveram Fleiss Kappa 0,574."
- EN: `Fleiss Kappa score of 0.574`

## 13. Secao "Colunas normalizadas"

Manter essa secao, mas antes da tabela incluir uma explicacao mais narrativa sobre por que normalizar.

Titulo:

```markdown
#### Colunas normalizadas
```

Texto sugerido:

```markdown
Como o USS junta datasets diferentes, o app precisa transformar os arquivos brutos em uma tabela comum. Essa normalizacao nao apaga a origem dos dados; ela cria colunas padronizadas para permitir filtros, graficos e comparacoes.

O principio e preservar o maximo de informacao original e adicionar colunas derivadas apenas para facilitar a leitura. Por exemplo, a acao original fica em `action_raw`, enquanto agrupamentos como `action_group`, `action_type` e `action_target` ajudam a construir visualizacoes.
```

Colunas que devem aparecer no guia:

- `dataset`
- `dialogue_id`
- `turn_id`
- `role`
- `text`
- `action_raw`
- `action_group`
- `action_type`
- `action_target`
- `satisfaction_scores`
- `satisfaction_annotation_count`
- `satisfaction_mode`
- `satisfaction_mean`
- `satisfaction_interpretation`
- `satisfaction_disagreement`
- `is_overall`
- `language`
- `satisfaction_3_classes`
- `satisfaction_binary`

Adicionar estas colunas ao `COLUMN_GUIDE` se ainda nao existirem:

- `satisfaction_mode`: nota majoritaria na escala 1-5.
- `satisfaction_mean`: media das notas dos anotadores.
- `satisfaction_disagreement`: medida de discordancia entre anotadores.

## 14. Secao "Datasets carregados nesta execucao"

O usuario indicou que esta parte e legal, mas nao vale uma tabela so para isso. Recomendacao: substituir a tabela atual por um texto curto calculado dinamicamente.

Remover ou substituir este bloco atual:

```python
loaded = (
    df.groupby("dataset", as_index=False)["dialogue_id"]
    .nunique()
    .rename(columns={"dialogue_id": "Diálogos carregados", "dataset": "Dataset"})
)
st.markdown("#### Datasets carregados nesta execução")
st.dataframe(loaded, width="stretch", hide_index=True)
```

Substituir por uma frase dinamica:

```python
loaded = df.groupby("dataset")["dialogue_id"].nunique().sort_index()
loaded_text = ", ".join(
    f"{dataset}: {count:,}".replace(",", ".")
    for dataset, count in loaded.items()
)
st.markdown("#### Datasets carregados nesta execução")
st.markdown(
    f"Nesta execução, o app carregou **{len(loaded)} datasets**: {loaded_text}. "
    "Esse resumo serve apenas para confirmar a carga dos dados; as comparações "
    "detalhadas ficam nas páginas de visão geral e comparação entre datasets."
)
```

Se o JDDC estiver carregado, acrescentar:

```python
if "JDDC" in loaded.index:
    st.caption(
        "JDDC está disponível como corpus bônus em chinês. As análises principais "
        "continuam priorizando os datasets em inglês."
    )
```

## 15. Secao "Como navegar no app"

Substituir "Leitura recomendada dentro do app" por um roteiro mais conectado ao storytelling.

Titulo:

```markdown
#### Como navegar no app
```

Texto sugerido:

```markdown
Use esta pagina como mapa conceitual. Depois, siga para a visao geral para ver volume, distribuicao de notas e recortes por dataset. Em seguida, abra a inspecao de dialogo para ler conversas completas, porque a satisfacao depende do historico.

A pagina de dataset bruto ajuda a conferir a estrutura original normalizada. A analise de instancias mostra padroes por acao, nota e divergencia entre anotadores. Por fim, a preparacao para sentimentos e bot deve ser usada com cuidado: o USS mede satisfacao contextual, nao sentimento textual puro.
```

Tooltip:

`not only for user simulation`

## 16. Secao "Possiveis blocos de ARTICLE_NOTES"

O `guide.py` usa `ARTICLE_NOTES` com `source_badge`. A recomendacao e manter o mecanismo, mas atualizar o conteudo para uma sequencia de cards mais narrativa.

Sugestao de novos itens para `ARTICLE_NOTES`:

```python
ArticleNote(
    title="O problema: avaliar conversas inteiras",
    translated=(
        "O artigo argumenta que avaliar apenas um turno isolado nao captura "
        "a utilidade geral do sistema nem a satisfacao do usuario com o fluxo do dialogo."
    ),
    original_excerpt="the overall usefulness of the system or about users’ satisfaction",
)
```

```python
ArticleNote(
    title="A proposta: simular satisfacao do usuario",
    translated=(
        "A tarefa proposta combina simulacao de usuario com predicao de satisfacao, "
        "para tornar a avaliacao de sistemas de dialogo mais parecida com uma experiencia humana."
    ),
    original_excerpt="make the simulation more human-like",
)
```

```python
ArticleNote(
    title="A origem: cinco datasets de dialogo",
    translated=(
        "O USS e baseado em cinco datasets de dialogo orientados a tarefa, cobrindo "
        "e-commerce, assistentes virtuais, reservas e recomendacao de filmes."
    ),
    original_excerpt="five benchmark task-oriented dialogue datasets",
)
```

```python
ArticleNote(
    title="A anotacao: contexto antes da fala",
    translated=(
        "A satisfacao e avaliada antes da fala do usuario e depende do historico anterior, "
        "nao apenas do sentimento expresso na frase atual."
    ),
    original_excerpt="before the user utterance",
)
```

```python
ArticleNote(
    title="A qualidade: rechecagem quando ha divergencia",
    translated=(
        "O artigo explica que pelo menos tres anotadores avaliaram os dados e que um quarto "
        "podia ser chamado quando havia discrepancia entre as notas."
    ),
    original_excerpt="we ask a fourth annotator to recheck it",
)
```

```python
ArticleNote(
    title="O cuidado: classes desbalanceadas",
    translated=(
        "Como a classe 3 domina muitos recortes, as visualizacoes e modelos futuros precisam "
        "considerar o desbalanceamento das notas de satisfacao."
    ),
    original_excerpt="serious imbalance of the satisfaction label",
)
```

## 17. Conteudo para um pequeno glossario

As anotacoes do documento indicam interesse em uma "colinha" ou glossario. Inserir como secao curta, preferencialmente apos a escala de satisfacao.

Titulo:

```markdown
#### Glossario rapido
```

Itens:

- **Task-oriented dialogue:** conversa em que o sistema tenta ajudar o usuario a cumprir uma tarefa especifica.
- **User simulation:** metodo para simular comportamento de usuarios e avaliar sistemas de dialogo em larga escala.
- **Exchange-level satisfaction:** satisfacao em nivel de turno/troca, associada a um ponto especifico da conversa.
- **Dialogue-level satisfaction:** satisfacao geral do dialogo completo.
- **Before utterance:** a nota e atribuida antes da fala do usuario, considerando o contexto anterior.
- **Action:** ato/intencao associada a fala, como informar, pedir, recomendar, agradecer ou negar.
- **OVERALL:** identificador usado para registrar satisfacao geral do dialogo.
- **Fleiss Kappa:** medida de concordancia entre varios anotadores.

Evitar deixar o glossario longo. Ele deve ajudar o leitor a seguir a pagina, nao virar uma aula separada.

## 18. JDDC como bonus

Inserir uma nota especifica sobre JDDC na secao dos datasets e, se houver pagina propria no futuro, apontar para ela.

Texto sugerido:

```markdown
O JDDC aparece no USS como o maior corpus, mas sera tratado aqui como bonus. Ele esta em chines, veio de atendimento/e-commerce real e possui uma estrutura de acoes mais complexa. Para uma primeira versao do app, os datasets em ingles sao mais adequados para exploracao textual e para a preparacao do projeto de sentimentos/bot.

Quando o JDDC entrar na interface principal, a recomendacao e oferecer traducao sob demanda e manter o texto original sempre visivel, porque traducoes automaticas podem perder nuances importantes da satisfacao.
```

Tooltip:

`JDDC (Chinese) and Others (English)`

## 19. Fontes consultadas

Manter a secao de fontes, mas incluir tambem o documento traduzido como fonte interna de estudo.

Texto sugerido:

```markdown
#### Fontes consultadas

- Artigo original: [Simulating User Satisfaction for the Evaluation of Task-oriented Dialogue Systems](https://arxiv.org/pdf/2105.03748)
- Repositorio oficial: [sunnweiwei/user-satisfaction-simulation](https://github.com/sunnweiwei/user-satisfaction-simulation)
- Pasta oficial do dataset: [dataset](https://github.com/sunnweiwei/user-satisfaction-simulation/tree/master/dataset)
- Documento interno de estudo: `Tradução do Artigo - Simulando a Satisfação do Usuário.docx`
- Pagina atual usada como base: `pages_app/guide.py`
```

## 20. Resumo das mudancas recomendadas no codigo

Alterar principalmente:

- `pages_app/guide.py`: reorganizar ordem das secoes e substituir textos.
- `src/content.py`: atualizar `ARTICLE_NOTES`, enriquecer `DATASET_GUIDES` e completar `COLUMN_GUIDE`.

Nao e necessario mudar nesta etapa:

- loaders;
- graficos;
- estrutura de dados;
- paginas de analise;
- download dos arquivos.

Sequencia recomendada de implementacao:

1. Atualizar `ARTICLE_NOTES` com os novos titulos, textos em portugues e `original_excerpt` em ingles.
2. Atualizar `DATASET_GUIDES` para contar melhor a origem de cada dataset.
3. Completar `COLUMN_GUIDE` com `satisfaction_mode`, `satisfaction_mean` e `satisfaction_disagreement`, caso essas colunas existam no dataframe.
4. Reordenar as secoes em `guide.py` conforme este documento.
5. Trocar a tabela "Datasets carregados nesta execucao" por um resumo textual.
6. Manter o exemplo real de `OVERALL`.
7. Manter fontes consultadas no fim.

## 21. Checklist de aceitacao

A pagina inicial refinada deve cumprir estes criterios:

- Explica por que o USS existe antes de explicar colunas.
- Conta que o dataset veio de cinco bases diferentes.
- Deixa claro que SGD, MultiWOZ, ReDial e CCPE sao o foco em ingles.
- Deixa claro que JDDC e bonus por estar em chines.
- Explica a diferenca entre satisfacao por turno e satisfacao geral.
- Explica `OVERALL` como anotacao, nao fala real.
- Explica `3,3,4` como multiplas notas humanas.
- Explica por que podem existir mais de tres notas em alguns casos.
- Mantem os icones `?` com trechos curtos em ingles do artigo.
- Nao trata satisfacao como sentimento textual puro.
- Nao remove conteudos uteis que ja estavam no `guide.py`.
- Evita tabela separada apenas para informar datasets carregados.
