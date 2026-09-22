# REVIEW - Estudo do Projeto USS com Foco nos Datasets em Ingles

## 1. Visao geral

Este documento analisa o projeto **User Satisfaction Simulation (USS)**, disponibilizado no repositorio [sunnweiwei/user-satisfaction-simulation](https://github.com/sunnweiwei/user-satisfaction-simulation), associado ao artigo [Simulating User Satisfaction for the Evaluation of Task-oriented Dialogue Systems](https://arxiv.org/pdf/2105.03748).

O projeto propoe uma base anotada para estudar **satisfacao do usuario em sistemas de dialogo orientados a tarefa**. Em vez de avaliar apenas se o sistema respondeu algo correto em um turno isolado, o trabalho tenta modelar como a satisfacao do usuario muda ao longo da conversa e como essa satisfacao se relaciona com a proxima acao do usuario.

Para o objetivo deste estudo, o ponto mais importante e o dataset. A ideia e preparar uma base conceitual para, depois, construir um projeto em **Streamlit** capaz de explorar os dados, visualizar distribuicoes, inspecionar dialogos, entender anotacoes humanas e preparar o material para um projeto posterior de analise de sentimentos ou interacao com bot.

O foco pratico do MVP em Streamlit deve ser nos datasets em ingles:

- **SGD** - Schema Guided Dialogue.
- **MultiWOZ 2.1** - Multi-domain Wizard-of-Oz.
- **ReDial** - Recommendation Dialogues.
- **CCPE** - Coached Conversational Preference Elicitation.

O dataset **JDDC** tambem faz parte do USS e e o maior corpus do projeto, mas esta em chines. Por isso, neste estudo ele deve ser tratado como um **dataset adicional/bonus** para implementacao futura no Streamlit, com suporte opcional a traducao quando necessario.

## 2. O que o projeto faz

O projeto USS busca apoiar a avaliacao de sistemas de dialogo orientados a tarefa por meio da simulacao de satisfacao do usuario. Em um sistema de dialogo tradicional, a avaliacao pode ficar limitada a metricas pontuais, como acuracia de uma resposta, sucesso de tarefa ou avaliacao offline por turno. O artigo argumenta que isso nao captura completamente a experiencia do usuario durante uma conversa.

A proposta central e modelar duas coisas:

1. **Satisfacao do usuario** em um determinado momento da conversa.
2. **Proxima acao do usuario**, considerando o historico do dialogo e, conceitualmente, o estado de satisfacao.

Formalmente, o artigo descreve a tarefa como aprender uma funcao:

```text
P(action, satisfaction | context)
```

Onde:

- `context` e o historico do dialogo ate aquele ponto.
- `action` e a proxima acao do usuario.
- `satisfaction` e o nivel de satisfacao associado ao usuario naquele ponto.

Na pratica, o dataset permite responder perguntas como:

- O usuario parece satisfeito ou frustrado depois da resposta do sistema?
- Que tipos de respostas do sistema antecedem quedas de satisfacao?
- Certas acoes do usuario aparecem mais quando a satisfacao e baixa?
- O comportamento do usuario muda quando o sistema falha, demora ou nao entende o pedido?
- Um bot poderia usar sinais de satisfacao para decidir quando pedir esclarecimento, corrigir rota ou transferir para atendimento humano?

Esse tipo de dado e especialmente util para um projeto de analise de sentimentos porque a satisfacao anotada nao e apenas uma emocao expressa no texto. Ela e uma avaliacao contextual: os anotadores observaram o que aconteceu antes da fala do usuario e avaliaram como o usuario provavelmente se sentiria naquele momento.

## 3. Relacao com o artigo

O artigo apresenta tres contribuicoes principais:

- A formulacao da tarefa de **simulacao de satisfacao do usuario**.
- A construcao do dataset **USS**, com 6.800 dialogos anotados.
- A implementacao de baselines para prever satisfacao e acao do usuario.

Segundo o artigo, o USS foi construido a partir de cinco datasets de dialogo orientado a tarefa:

| Dataset | Idioma | Dominio geral | Papel neste estudo |
|---|---:|---|---|
| JDDC | Chines | E-commerce / atendimento ao cliente | Bonus no Streamlit |
| SGD | Ingles | Assistente virtual multi-dominio | Foco principal |
| MultiWOZ 2.1 | Ingles | Tarefas urbanas, hotel, restaurante, taxi etc. | Foco principal |
| ReDial | Ingles | Recomendacao de filmes | Foco principal |
| CCPE | Ingles | Elicitacao de preferencias sobre filmes | Foco principal |

O artigo enfatiza que a satisfacao e anotada em dois niveis:

- **Exchange-level**: satisfacao por turno/fala do usuario.
- **Dialogue-level**: satisfacao geral da conversa.

Um detalhe fundamental: a satisfacao por turno e avaliada **antes da fala do usuario**, com base no contexto anterior. Assim, se uma linha `USER` tem uma nota `2,3,3`, essa nota representa como anotadores avaliaram a satisfacao do usuario naquele momento da conversa, considerando o que o sistema ja tinha feito.

## 4. Estrutura do repositorio

O repositorio e pequeno, mas contem tres partes importantes:

```text
user-satisfaction-simulation/
  README.md
  dataset/
  baselines/
  imgs/
```

### 4.1 README.md

O `README.md` apresenta o projeto, aponta para o artigo, descreve o formato dos dados e informa estatisticas gerais. Ele tambem explica que:

- Os arquivos do dataset estao em formato TXT.
- As colunas sao separadas por tabulacao.
- As sessoes/dialogos sao separados por linhas em branco.
- A satisfacao tem anotacoes repetidas separadas por virgula.
- O JDDC possui explicacoes textuais em algumas linhas.
- As acoes do ReDial foram adicionadas a partir do IARD, pois o ReDial original nao tinha esse tipo de anotacao.
- As acoes do JDDC foram comprimidas de 234 categorias para grupos maiores.

### 4.2 dataset/

A pasta `dataset/` e a parte mais importante para este estudo. Ela contem:

```text
dataset/
  CCPE.txt
  JDDC-ActionList.txt
  JDDC.txt
  MWOZ.txt
  README.md
  ReDial-action.txt
  ReDial.txt
  SGD.txt
```

Arquivos principais:

- `SGD.txt`: dialogos do Schema Guided Dialogue.
- `MWOZ.txt`: dialogos do MultiWOZ 2.1.
- `ReDial.txt`: dialogos do ReDial com anotacoes de satisfacao, mas sem acoes preenchidas no arquivo principal.
- `ReDial-action.txt`: versao auxiliar com acoes do ReDial.
- `CCPE.txt`: dialogos do CCPE.
- `JDDC.txt`: dialogos do JDDC em chines.
- `JDDC-ActionList.txt`: mapeamento manual de acoes detalhadas do JDDC para grupos maiores.

### 4.3 baselines/

A pasta `baselines/` contem scripts de treinamento e avaliacao. Ela mostra como os autores usam o dataset para treinar modelos de:

- Predicao de satisfacao.
- Predicao de acao do usuario.

Os principais scripts incluem:

- `train_sat.py`: treinamento de satisfacao para datasets em ingles.
- `train_act.py`: treinamento de acao para datasets em ingles.
- `train_jddc_sat.py`: treinamento de satisfacao para JDDC.
- `train_jddc_act.py`: treinamento de acao para JDDC.
- `models.py`: arquiteturas GRU, HiGRU, HiGRU+ATTN e BERT.
- `svm.py`: abordagem baseada em features tradicionais.
- `jddc_config.py`: configuracao/mapeamento de dominios de acao do JDDC.

### 4.4 imgs/

A pasta `imgs/` contem imagens de resultados dos experimentos, especialmente tabelas/figuras relacionadas a desempenho em predicao de satisfacao e acao.

## 5. Como o dataset foi construido

O USS foi construido a partir de datasets ja existentes. Os autores selecionaram dialogos de diferentes dominios, filtraram conversas, organizaram acoes e pediram que anotadores humanos avaliassem a satisfacao do usuario.

O processo geral descrito no artigo foi:

1. Selecionar dialogos de bases de dialogo orientado a tarefa.
2. Identificar conversas com potenciais sinais emocionais, especialmente emocoes negativas.
3. Anotar a satisfacao do usuario em escala de 1 a 5.
4. Anotar tanto turnos individuais quanto a satisfacao geral do dialogo.
5. Usar pelo menos tres anotadores por instancia.
6. Solicitar rechecagem quando havia grande divergencia.
7. Para o JDDC, coletar tambem explicacoes textuais dos anotadores.

Escala de satisfacao usada no artigo:

| Valor | Significado | Interpretacao pratica |
|---:|---|---|
| 1 | Very dissatisfied | Sistema nao entende nem atende a solicitacao |
| 2 | Dissatisfied | Sistema entende, mas nao satisfaz adequadamente |
| 3 | Normal | Sistema entende e atende parcialmente ou orienta o usuario |
| 4 | Satisfied | Sistema atende, mas com excesso de informacao ou turnos extras |
| 5 | Very satisfied | Sistema entende e resolve de forma completa e eficiente |

Essa escala e importante porque nao representa apenas polaridade de sentimento. Um texto educado pode receber nota baixa se o sistema falhou antes. Da mesma forma, uma fala curta como "thanks" pode aparecer em contexto de satisfacao alta ou apenas normal, dependendo do historico.

## 6. Estrutura bruta dos arquivos TXT

Cada arquivo principal representa varias sessoes/dialogos. A separacao e:

- Cada linha representa uma fala ou uma anotacao especial.
- Campos sao separados por tabulacao (`\t`).
- Dialogos diferentes sao separados por uma linha em branco.

Formato geral dos datasets em ingles:

```text
role<TAB>text<TAB>action<TAB>satisfaction
```

Formato do JDDC:

```text
role<TAB>text<TAB>action<TAB>satisfaction<TAB>explanation
```

Exemplo simplificado inspirado no formato do SGD:

```text
USER	I would like to find a place to eat.	INFORM_INTENT	3,4,3
SYSTEM	In which city? What kind of food would you like?	REQUEST
USER	I'd like Sichuan in San Jose.	INFORM	3,3,3
SYSTEM	Chef Li in San Jose is nice.	OFFER
USER	OVERALL		3,4,3
```

### 6.1 Campo `role`

Indica quem falou:

- `USER`: fala do usuario.
- `SYSTEM`: fala do sistema.

As linhas `USER` sao as que possuem anotacao de satisfacao. As linhas `SYSTEM` normalmente nao possuem satisfacao, porque o objetivo e avaliar a satisfacao do usuario diante do historico do dialogo.

### 6.2 Campo `text`

Contem o texto da fala. Para linhas normais, e a frase dita pelo usuario ou sistema.

Existe um caso especial:

```text
USER	OVERALL
```

Nesse caso, `OVERALL` nao e uma fala real do usuario. E uma linha especial que registra a satisfacao geral do dialogo.

### 6.3 Campo `action`

Representa a acao/dialog act associada a fala. Exemplos:

- `INFORM`
- `REQUEST`
- `SELECT`
- `THANK_YOU`
- `AFFIRM`
- `Restaurant-Inform`
- `Hotel-Request`
- `ENTITY_PREFERENCE+MOVIE_OR_SERIES`

Nem todos os datasets possuem acoes igualmente completas. O caso mais importante e o ReDial: no arquivo `ReDial.txt`, a coluna de acao aparece vazia nas falas de usuario. O repositorio inclui `ReDial-action.txt` para suprir essa informacao a partir de anotacoes externas do IARD.

### 6.4 Campo `satisfaction`

Este campo aparece principalmente nas linhas `USER` e contem uma lista de notas humanas separadas por virgula.

Exemplo:

```text
2,3,3
```

Isso significa:

- Anotador 1 deu nota 2.
- Anotador 2 deu nota 3.
- Anotador 3 deu nota 3.

Portanto, `2,3,3` nao deve ser lido como uma categoria unica. Ele deve ser convertido para uma lista de inteiros:

```python
[2, 3, 3]
```

Para reproduzir a logica dos baselines, essa lista pode virar uma classe final por voto majoritario:

```text
mode([2, 3, 3]) = 3
```

Tambem e util calcular a media:

```text
mean([2, 3, 3]) = 2.67
```

No Streamlit, a recomendacao e manter os dois:

- `satisfaction_scores`: lista original dos anotadores.
- `satisfaction_mode`: classe agregada por maioria.
- `satisfaction_mean`: valor medio para analises exploratorias.

### 6.5 Campo `explanation`

Esse campo aparece no JDDC. Ele traz explicacoes textuais dos anotadores, especialmente para avaliacoes em nivel de dialogo.

Exemplo conceitual:

```text
system nao resolveu o problema; system nao entendeu a intencao do usuario
```

Como o JDDC esta em chines, essas explicacoes tambem podem exigir traducao para uso em apresentacao ou interface.

## 7. Estatisticas gerais dos arquivos

As contagens abaixo foram organizadas a partir das estatisticas do artigo/README e da leitura estrutural dos arquivos do repositorio. Para o Streamlit, e importante diferenciar:

- Total de dialogos.
- Falas reais de usuario.
- Linhas `OVERALL`.
- Falas do sistema.
- Quantidade de acoes.

| Dataset | Idioma | Dialogos | Linhas USER reais | Linhas OVERALL | Linhas SYSTEM | Papel no Streamlit |
|---|---:|---:|---:|---:|---:|---|
| SGD | Ingles | 1.000 | 12.833 | 1.000 | 12.833 | Principal |
| MultiWOZ | Ingles | 1.000 | 11.553 | 1.000 | 10.555 | Principal |
| ReDial | Ingles | 1.000 | 10.806 | 1.000 | 10.652 | Principal |
| CCPE | Ingles | 500 | 6.360 | 500 | 5.576 | Principal |
| JDDC | Chines | 3.300 | 54.517 | 3.300 | 51.991 | Bonus |

Observacao importante: a linha `OVERALL` e contada como `USER` no arquivo, mas nao e uma fala real. Para analise exploratoria, ela deve ser separada com `is_overall = true`.

### 7.1 Distribuicao de satisfacao por turnos reais

As distribuicoes abaixo consideram a classe majoritaria das notas de satisfacao por turno real de usuario, sem contar `OVERALL`.

| Dataset | Rating 1 | Rating 2 | Rating 3 | Rating 4 | Rating 5 |
|---|---:|---:|---:|---:|---:|
| SGD | 3 | 710 | 10.728 | 1.336 | 56 |
| MultiWOZ | 9 | 661 | 10.317 | 559 | 7 |
| ReDial | 17 | 629 | 8.915 | 1.211 | 34 |
| CCPE | 6 | 432 | 5.614 | 306 | 2 |
| JDDC | 120 | 4.820 | 45.005 | 4.151 | 421 |

O padrao mais visivel e o forte desbalanceamento para a classe 3. Isso significa que, se no futuro houver treinamento de modelos, sera necessario lidar com desbalanceamento. O proprio artigo faz up-sampling das classes diferentes de 3 durante o treinamento.

## 8. Datasets em ingles - foco principal

### 8.1 SGD

O **Schema Guided Dialogue (SGD)** contem conversas entre humanos e um assistente virtual em multiplos dominios. Ele e adequado para o MVP do Streamlit porque:

- Esta em ingles.
- Tem acoes de dialogo relativamente claras.
- Possui variedade de dominios.
- Tem dialogos longos o suficiente para visualizar evolucao de satisfacao.

Exemplos de acoes encontradas:

- `INFORM`
- `AFFIRM`
- `SELECT`
- `THANK_YOU`
- `REQUEST`
- `INFORM_INTENT`
- `NEGATE_INTENT`
- `REQUEST_ALTS`
- `AFFIRM_INTENT`
- `NEGATE`

Uso recomendado no Streamlit:

- Visualizar sequencias de conversa.
- Comparar satisfacao antes e depois de falhas do sistema.
- Filtrar por acoes como `REQUEST`, `INFORM`, `THANK_YOU`.
- Exibir distribuicao de notas por acao.

### 8.2 MultiWOZ 2.1

O **MultiWOZ 2.1** e um dataset multi-dominio usado em dialogos orientados a tarefa, com dominios como hotel, restaurante, taxi, trem e atracoes.

Ele e util porque traz acoes que ja indicam dominio e tipo de acao:

- `Hotel-Inform`
- `Restaurant-Inform`
- `Train-Inform`
- `Attraction-Request`
- `Restaurant-Request`
- `Taxi-Inform`
- `general-thank`

Ha tambem acoes vazias em algumas linhas. Para o Streamlit, elas nao devem ser descartadas. A recomendacao e normalizar acao vazia como:

```text
UNKNOWN
```

Uso recomendado:

- Comparar satisfacao por dominio (`Hotel`, `Restaurant`, `Train`, etc.).
- Avaliar se certos dominios concentram mais insatisfacao.
- Gerar heatmap de `domain-action` versus satisfacao.

### 8.3 ReDial

O **ReDial** e um dataset de recomendacao de filmes em dialogo. No arquivo principal `ReDial.txt`, as acoes aparecem vazias. Isso ocorre porque o ReDial original nao fornecia acoes no mesmo formato usado pelos demais datasets.

O repositorio inclui o arquivo auxiliar:

```text
ReDial-action.txt
```

Esse arquivo adiciona acoes provenientes do IARD, como:

- `AskForRec`
- `Recommend`
- `GiveFeedback`
- `AddDetails`
- `Respond`

Para o Streamlit, existem duas possibilidades:

1. MVP simples: carregar `ReDial.txt` com `action_raw = UNKNOWN`.
2. MVP enriquecido: alinhar `ReDial.txt` com `ReDial-action.txt` para preencher as acoes.

A recomendacao e implementar primeiro a versao simples e documentar a versao enriquecida como melhoria. Como o objetivo inicial e estudo do dataset e analise de satisfacao, ReDial ainda e util mesmo sem acao preenchida, pois possui textos e anotacoes de satisfacao.

Uso recomendado:

- Explorar recomendacoes de filmes.
- Analisar como feedback negativo ou rejeicao de recomendacao afeta satisfacao.
- Separar futuramente acoes de recomendacao quando `ReDial-action.txt` for integrado.

### 8.4 CCPE

O **CCPE** envolve conversas sobre preferencias de filmes. Ele e menor que os demais datasets em ingles, mas tem acoes mais especificas e compostas.

Exemplos:

- `ENTITY_PREFERENCE+MOVIE_OR_SERIES`
- `ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY`
- `ENTITY_NAME+MOVIE_OR_SERIES`
- `ENTITY_OTHER+MOVIE_OR_SERIES`
- `ENTITY_DESCRIPTION+MOVIE_OR_SERIES`
- `ENTITY_PREFERENCE+PERSON`

Essas acoes podem ser quebradas em duas partes:

```text
ENTITY_PREFERENCE + MOVIE_OR_SERIES
```

Para o Streamlit, isso abre uma boa oportunidade:

- `action_raw`: valor completo original.
- `action_type`: parte antes do `+`.
- `action_target`: parte depois do `+`.

Uso recomendado:

- Visualizar preferencias por tipo de entidade.
- Comparar satisfacao quando o bot pergunta sobre preferencias versus quando cita entidades especificas.
- Usar como dataset de exploracao para projetos de recomendacao/sentimento.

## 9. JDDC como dataset bonus

O **JDDC** deve ser documentado no `REVIEW.md`, mas tratado como bonus na implementacao do Streamlit.

Motivos:

- Esta em chines, diferente dos demais datasets.
- E o maior dataset do projeto.
- Tem dominio especifico de e-commerce/atendimento ao cliente.
- Possui acoes originais muito numerosas.
- Pode exigir traducao para apresentacao, leitura e interpretacao por usuarios que nao leem chines.

### 9.1 Importancia do JDDC

Apesar de ser bonus para o MVP, o JDDC e muito relevante:

- Tem 3.300 dialogos.
- Tem 54.517 turnos reais de usuario.
- Tem 51.991 falas de sistema.
- Possui anotacoes de satisfacao em escala 1-5.
- Possui explicacoes textuais de anotadores, especialmente uteis para interpretabilidade.

### 9.2 Acoes do JDDC

O JDDC possui 234 categorias originais de acao do usuario. O projeto comprime essas categorias em grupos maiores via `JDDC-ActionList.txt`.

Grupos principais listados:

- `配送` - entrega/logistica.
- `退换` - devolucao, troca, reembolso.
- `发票` - nota fiscal/fatura.
- `客服` - atendimento ao cliente.
- `产品咨询` - consulta de produto.
- `价保` - protecao de preco.
- `支付` - pagamento.
- `bug` - falhas ou problemas de sistema.
- `维修` - manutencao/reparo.
- `评价` - avaliacoes/comentarios.
- `预定` - reservas.
- `other` - categoria usada pelo codigo para o que nao mapeia diretamente.

O artigo menciona compressao para 12 categorias; na pratica, isso corresponde aos grupos mapeados mais a categoria `other` usada no codigo.

### 9.3 Como tratar no Streamlit

O JDDC deve aparecer como um modulo bonus:

- Um filtro separado: **Dataset chines - JDDC**.
- Um aviso visual de idioma.
- Uma opcao futura de traducao sob demanda.
- Analise propria de acoes comprimidas.
- Carregamento independente, para nao bloquear o uso dos datasets em ingles.

Regra importante:

```text
Se a biblioteca de traducao nao estiver instalada ou se a API externa falhar,
o app deve continuar funcionando normalmente para SGD, MultiWOZ, ReDial e CCPE.
```

Campos extras sugeridos para JDDC:

- `translated_text`
- `translated_explanation`
- `translation_provider`
- `translation_status`

Esses campos devem ser opcionais e nao devem ser exigidos para o MVP.

## 10. Como os baselines processam os dados

Os scripts em `baselines/` ajudam a entender como os autores transformam os arquivos brutos em dados para modelos.

### 10.1 Conversao da satisfacao

Nos arquivos TXT, a satisfacao vem como valores separados por virgula:

```text
3,3,4
```

Os scripts convertem esses valores para inteiros e subtraem 1:

```text
[3, 3, 4] -> [2, 2, 3]
```

Isso acontece porque os modelos trabalham internamente com classes de `0` a `4`, enquanto a escala humana e de `1` a `5`.

Depois, o codigo usa uma funcao equivalente ao voto majoritario:

```text
get_main_score([2, 2, 3]) = 2
```

Interpretacao:

- Classe interna `2`.
- Nota humana correspondente `3`.

Para documentacao e Streamlit, e melhor exibir a escala original `1-5`, porque e a escala humana e interpretavel.

### 10.2 Empate entre anotadores

O codigo conta quantas vezes cada classe aparece e escolhe o indice com maior contagem. Em caso de empate, a implementacao tende a escolher a menor classe, porque usa uma logica equivalente a `argmax` sobre uma lista ordenada.

Exemplo:

```text
[2, 3, 4]
```

Cada nota aparece uma vez. A classe majoritaria fica ambigua. No codigo, a menor entre as empatadas tende a vencer.

Para o Streamlit, a recomendacao e mostrar:

- Classe majoritaria.
- Media.
- Grau de discordancia.
- Lista original de anotadores.

Assim, o usuario consegue perceber quando a nota agregada e estavel ou controversa.

### 10.3 Entrada dos modelos

Para cada fala do usuario, os baselines usam o historico anterior do dialogo como entrada. Em termos simples:

```text
Historico ate agora -> prever satisfacao do usuario e/ou proxima acao
```

Isso reforca um ponto importante para a interface:

> A satisfacao anotada nao deve ser interpretada olhando apenas a frase atual do usuario; ela depende do contexto anterior.

Por isso, a pagina de inspecao de dialogo no Streamlit deve sempre mostrar a conversa em sequencia, nao apenas linhas isoladas.

### 10.4 Modelos usados

O artigo compara tres familias de modelos:

| Familia | Modelos | Ideia |
|---|---|---|
| Feature-based | LR, SVM, XGBoost | Usam TF-IDF, tamanho da fala e posicao do turno |
| RNN-based | GRU, HiGRU, HiGRU+ATTN | Representam o historico com redes recorrentes |
| BERT-based | BERT | Usa representacao contextual pre-treinada |

Resultados gerais relatados:

- Modelos neurais superam abordagens baseadas em features para satisfacao.
- HiGRU tem bom desempenho em predicao in-domain de satisfacao.
- BERT tende a generalizar melhor em cenarios cross-domain.
- Para predicao de acao, BERT apresenta desempenho forte em varios datasets.

## 11. Schema normalizado recomendado para o Streamlit

Para facilitar analise e visualizacao, os arquivos TXT devem ser convertidos para uma tabela normalizada. Sugestao:

| Coluna | Tipo sugerido | Descricao |
|---|---|---|
| `dataset` | string | Nome do dataset: `SGD`, `MWOZ`, `ReDial`, `CCPE`, `JDDC` |
| `dialogue_id` | int/string | Identificador do dialogo dentro do dataset |
| `turn_id` | int | Posicao da linha dentro do dialogo |
| `role` | string | `USER` ou `SYSTEM` |
| `text` | string | Texto original da fala |
| `action_raw` | string | Acao original do arquivo |
| `action_group` | string | Grupo normalizado de acao, quando aplicavel |
| `satisfaction_scores` | list[int] | Notas originais dos anotadores |
| `satisfaction_mode` | int/null | Nota majoritaria na escala 1-5 |
| `satisfaction_mean` | float/null | Media das notas |
| `satisfaction_disagreement` | float/int | Medida simples de divergencia, como amplitude ou desvio |
| `is_overall` | bool | `true` para linha `USER OVERALL` |
| `explanation` | string/null | Explicacao textual, especialmente no JDDC |
| `language` | string | `en` ou `zh` |
| `translated_text` | string/null | Traducao opcional para JDDC |

### 11.1 Regras de conversao

Regras recomendadas:

- Preservar `satisfaction_scores` como lista original.
- Calcular `satisfaction_mode` em escala `1-5`.
- Calcular `satisfaction_mean` para analise.
- Separar `is_overall = true` quando `role = USER` e `text = OVERALL`.
- Nao misturar `OVERALL` com falas reais do usuario em graficos por turno.
- Tratar acao vazia como `UNKNOWN`.
- Definir `language = en` para SGD, MultiWOZ, ReDial e CCPE.
- Definir `language = zh` para JDDC.
- Manter `translated_text = null` por padrao.

### 11.2 Funcoes conceituais de parsing

O futuro projeto Streamlit pode ter funcoes como:

```python
parse_dataset_file(path, dataset_name, language)
parse_satisfaction_scores(raw_value)
compute_satisfaction_mode(scores)
compute_satisfaction_mean(scores)
normalize_action(dataset_name, action_raw)
split_ccpe_action(action_raw)
load_jddc_action_groups(path)
```

Para o MVP, a prioridade deve ser:

1. Parser generico para os quatro datasets em ingles.
2. Tratamento de `OVERALL`.
3. Normalizacao de notas.
4. Visualizacoes basicas.
5. JDDC bonus, carregado separadamente.

## 12. Planejamento do Streamlit

O Streamlit deve ser organizado como uma ferramenta de exploracao do dataset USS, nao como uma landing page. A primeira tela deve ja mostrar dados, filtros e indicadores.

### 12.1 Principio do MVP

O MVP deve ser:

- Geral o suficiente para lidar com os cinco datasets.
- Focado operacionalmente nos quatro datasets em ingles.
- Preparado para receber o JDDC como bonus.
- Capaz de separar dados brutos, dados normalizados e analises.

### 12.2 Pagina 1 - Visao geral

Objetivo: apresentar o corpus e permitir uma leitura rapida.

Elementos:

- Cards metricos:
  - total de datasets carregados;
  - total de dialogos;
  - total de turnos de usuario;
  - total de linhas `OVERALL`;
  - distribuicao de idiomas.
- Filtros:
  - dataset;
  - idioma;
  - faixa de satisfacao;
  - incluir/excluir `OVERALL`;
  - incluir/excluir `SYSTEM`.
- Graficos:
  - barras de quantidade de dialogos por dataset;
  - histograma geral de satisfacao;
  - proporcao de ratings 1-5.

### 12.3 Pagina 2 - Dataset bruto

Objetivo: permitir inspecao tabular.

Elementos:

- Tabela filtravel com colunas principais.
- Busca textual.
- Filtro por `role`.
- Filtro por `action_raw`.
- Filtro por `satisfaction_mode`.
- Toggle para mostrar/ocultar linhas `OVERALL`.
- Download do recorte filtrado em CSV.

Essa pagina ajuda a entender o material antes de qualquer modelagem.

### 12.4 Pagina 3 - Inspecao de dialogo

Objetivo: mostrar uma conversa inteira.

Fluxo:

1. Usuario escolhe dataset.
2. Usuario escolhe `dialogue_id`.
3. App exibe a conversa em ordem.
4. Falas de `USER` e `SYSTEM` aparecem visualmente diferenciadas.
5. Ao lado das falas de usuario, aparecem:
   - notas dos anotadores;
   - moda;
   - media;
   - divergencia;
   - acao.
6. Ao final, aparece a nota `OVERALL`.

Essa pagina e essencial porque a satisfacao depende do historico do dialogo.

### 12.5 Pagina 4 - Analise de instancias

Objetivo: analisar padroes estatisticos.

Visualizacoes:

- Distribuicao de satisfacao por dataset.
- Distribuicao de satisfacao por acao.
- Quantidade de anotadores por linha.
- Divergencia entre anotadores.
- Tamanho dos dialogos.
- Quantidade de turnos ate a nota geral.
- Top acoes por dataset.
- Percentual de satisfacao baixa (`rating < 3`) por dataset.

Essa pagina deve ajudar a preparar explicacoes para apresentacao.

### 12.6 Pagina 5 - Comparacao entre datasets em ingles

Objetivo: comparar SGD, MultiWOZ, ReDial e CCPE.

Comparacoes:

- Total de dialogos.
- Total de turnos.
- Distribuicao de ratings.
- Acoes mais frequentes.
- Media de satisfacao por dataset.
- Percentual de discordancia entre anotadores.
- Presenca de acoes vazias.

Essa pagina deve deixar claro que, embora todos estejam no USS, cada dataset tem estrutura e dominio diferente.

### 12.7 Pagina 6 - Visualizacoes interativas

Graficos recomendados:

- Histograma de satisfacao.
- Grafico de barras por acao.
- Heatmap `action_raw x satisfaction_mode`.
- Linha temporal de satisfacao dentro de um dialogo.
- Boxplot de satisfacao por dataset.
- Scatter ou strip plot de posicao do turno versus satisfacao.

Ferramentas possiveis:

- `plotly` para graficos interativos.
- `pandas` para transformacao.
- `streamlit` para interface.

### 12.8 Pagina 7 - Preparacao para analise de sentimentos/bot

Objetivo: conectar o estudo do USS com o projeto futuro de sentimentos.

Conteudos:

- Exportar dataset normalizado.
- Escolher target:
  - classificacao 5 classes: `1,2,3,4,5`;
  - classificacao 3 classes: insatisfeito, neutro, satisfeito;
  - classificacao binaria: insatisfeito (`<3`) versus nao insatisfeito (`>=3`).
- Mostrar exemplos por classe.
- Mostrar classes desbalanceadas.
- Alertar que satisfacao nao e exatamente sentimento textual.
- Permitir separar treino/teste por dataset.

Mapeamento sugerido para classificacao em 3 classes:

| Nota | Classe |
|---:|---|
| 1-2 | Insatisfeito |
| 3 | Neutro/normal |
| 4-5 | Satisfeito |

Esse mapeamento pode ser util para o projeto futuro, mas o app deve preservar a escala original de 5 pontos.

### 12.9 Modulo bonus - JDDC

O JDDC deve ficar em uma area separada:

- Nome: **Bonus - Dataset chines JDDC**.
- Aviso: "Este dataset esta em chines e pode exigir traducao externa para analise textual em portugues/ingles."
- Filtros por grupo de acao comprimida.
- Graficos proprios.
- Opcao futura de traducao por demanda.

Bibliotecas/estrategias possiveis para traducao:

- API externa de traducao.
- Modelo local de traducao, se viavel.
- Cache de traducoes para evitar custo e repeticao.

Regras:

- Traducao nao deve ser requisito para carregar o app.
- Se a traducao falhar, exibir texto original.
- O app deve informar que traducoes automaticas podem alterar nuances de satisfacao.

## 13. Cuidados analiticos

### 13.1 Satisfacao nao e sentimento puro

Um projeto de analise de sentimentos geralmente classifica o texto como positivo, neutro ou negativo. No USS, a nota e mais contextual:

- Uma fala pode parecer neutra, mas vir apos uma falha grave do sistema.
- Uma fala pode parecer educada, mas indicar frustracao no contexto.
- A nota mede a experiencia do usuario com o sistema, nao apenas a emocao expressa.

Portanto, para um projeto de sentimentos com bot, o ideal e tratar USS como dataset de **satisfacao contextual**, nao como dataset simples de polaridade textual.

### 13.2 Desbalanceamento

A maioria das instancias esta na classe 3. Isso afeta:

- Graficos.
- Interpretacao.
- Treinamento de modelos.
- Metricas.

Um modelo ingenuo pode acertar muitas instancias simplesmente prevendo sempre classe 3. Por isso, metricas como UAR, macro F1 e analise por classe sao mais informativas que acuracia simples.

### 13.3 Diferenca entre turno e dialogo

As linhas `OVERALL` representam satisfacao geral. Elas nao devem ser misturadas com falas reais em analises de sequencia.

Recomendacao:

- Analises por turno: `is_overall = false`.
- Analises de qualidade geral do dialogo: `is_overall = true`.

### 13.4 Acoes vazias

Alguns datasets possuem acoes vazias. Isso nao significa que a linha e invalida. Pode significar:

- anotacao inexistente;
- acao nao fornecida;
- acao nao aplicavel;
- diferenca de formato do dataset original.

No Streamlit, usar `UNKNOWN` e manter a linha.

### 13.5 Diferenca de idioma

JDDC tem caracteristicas proprias:

- idioma chines;
- dominio e-commerce;
- explicacoes textuais;
- acoes muito numerosas;
- necessidade de mapeamento de acoes.

Por isso, nao deve bloquear o MVP em ingles.

## 14. Plano de implementacao futuro do Streamlit

### 14.1 Organizacao sugerida de arquivos

```text
streamlit_app/
  app.py
  data/
    raw/
      SGD.txt
      MWOZ.txt
      ReDial.txt
      ReDial-action.txt
      CCPE.txt
      JDDC.txt
      JDDC-ActionList.txt
    processed/
      uss_normalized.parquet
  src/
    loaders.py
    preprocessing.py
    metrics.py
    charts.py
    translation.py
  pages/
    1_Visao_Geral.py
    2_Dataset_Bruto.py
    3_Inspecao_Dialogo.py
    4_Analise_Instancias.py
    5_Comparacao_Datasets.py
    6_Preparacao_Sentimentos.py
    7_Bonus_JDDC.py
```

### 14.2 Ordem recomendada de desenvolvimento

1. Criar parser para SGD, MultiWOZ, ReDial e CCPE.
2. Gerar dataframe normalizado.
3. Implementar metricas basicas.
4. Criar pagina de visao geral.
5. Criar pagina de dataset bruto.
6. Criar pagina de inspecao de dialogo.
7. Criar graficos interativos.
8. Adicionar exportacao de recortes.
9. Adicionar JDDC como bonus sem traducao.
10. Adicionar traducao opcional para JDDC, se necessario.

### 14.3 MVP minimo

O MVP deve conter:

- Carregamento dos quatro datasets em ingles.
- Conversao de satisfacao para lista, moda e media.
- Separacao de `OVERALL`.
- Visualizacao tabular.
- Filtros basicos.
- Grafico de distribuicao de satisfacao.
- Inspecao de dialogo completo.

JDDC nao deve ser requisito do MVP. Ele entra como bonus.

## 15. Validacoes recomendadas

Antes de considerar o Streamlit correto, validar:

- SGD tem 1.000 dialogos.
- MultiWOZ tem 1.000 dialogos.
- ReDial tem 1.000 dialogos.
- CCPE tem 500 dialogos.
- JDDC tem 3.300 dialogos, mas esta marcado como bonus.
- Linhas `SYSTEM` nao quebram o parser por nao terem satisfacao.
- Linhas `OVERALL` sao detectadas corretamente.
- `2,3,3` vira `[2, 3, 3]`.
- `satisfaction_mode` de `[2, 3, 3]` vira `3`.
- `satisfaction_mean` de `[2, 3, 3]` vira `2.67`.
- Acoes vazias viram `UNKNOWN`.
- JDDC com 5 colunas e datasets em ingles com 4 colunas sao tratados corretamente.
- O app funciona sem traducao.
- O app funciona mesmo se JDDC nao for carregado.

## 16. Conclusao

O projeto USS e uma base rica para estudar satisfacao em dialogos orientados a tarefa. Seu maior valor esta no fato de combinar:

- multiplos datasets;
- multiplos dominios;
- anotacao por turno;
- anotacao geral por dialogo;
- multiplos anotadores;
- tarefas de predicao de satisfacao e acao.

Para o projeto em Streamlit, a melhor estrategia e construir primeiro uma interface robusta para os datasets em ingles: **SGD, MultiWOZ, ReDial e CCPE**. Esses datasets permitem trabalhar com exploracao textual, visualizacoes, filtros, distribuicao de satisfacao e preparacao para analise de sentimentos sem a complexidade adicional de traducao.

O **JDDC** deve ser mantido como um modulo bonus. Ele e valioso por tamanho e riqueza de anotacao, mas exige cuidado por estar em chines e por ter um esquema de acoes mais complexo. A decisao correta e nao remove-lo do estudo, mas tambem nao deixar que ele bloqueie o MVP.

Em resumo:

- MVP: datasets em ingles.
- Bonus: JDDC com suporte opcional a traducao.
- Estrutura principal: parser normalizado, filtros, graficos e inspecao contextual de dialogos.
- Uso futuro: preparacao para analise de sentimentos contextual e avaliacao de bots.

## 17. Fontes consultadas

- Repositorio oficial: [sunnweiwei/user-satisfaction-simulation](https://github.com/sunnweiwei/user-satisfaction-simulation)
- README do repositorio: [README.md](https://raw.githubusercontent.com/sunnweiwei/user-satisfaction-simulation/master/README.md)
- README do dataset: [dataset/README.md](https://github.com/sunnweiwei/user-satisfaction-simulation/tree/master/dataset)
- Artigo: [Simulating User Satisfaction for the Evaluation of Task-oriented Dialogue Systems](https://arxiv.org/pdf/2105.03748)
- Arquivo de grupos de acao JDDC: [JDDC-ActionList.txt](https://raw.githubusercontent.com/sunnweiwei/user-satisfaction-simulation/master/dataset/JDDC-ActionList.txt)
