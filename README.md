# Explorador USS em Streamlit

Este projeto é uma interface em Streamlit para estudar o dataset **User Satisfaction Simulation**, também chamado de **USS**. O objetivo é explorar o dataset, suas anotações de satisfação e os padrões presentes nas conversas, sem reproduzir os modelos do artigo.

A ferramenta permite visualizar os datasets em inglês, inspecionar diálogos completos, entender as colunas normalizadas, analisar distribuições de satisfação, comparar anotações e verificar a concordância entre anotadores.

## Como executar

```bash
uv run streamlit run app.py
```

Na primeira execução, o app tenta usar os arquivos presentes em `data/raw`. Se algum arquivo oficial estiver ausente, ele tenta baixá-lo automaticamente.

Também é possível baixar os dados manualmente:

```bash
uv run python scripts/download_data.py
```

## Dados usados

Os arquivos em `data/raw` vieram do repositório oficial do projeto USS:

https://github.com/sunnweiwei/user-satisfaction-simulation/tree/master/dataset

Eles são mantidos dentro deste projeto para evitar perda de reprodutibilidade caso os arquivos originais deixem de estar disponíveis no futuro. A fonte original continua referenciada aqui e na própria análise.

Arquivos principais usados na análise:

- `SGD.txt`
- `MWOZ.txt`
- `ReDial.txt`
- `CCPE.txt`

Arquivos auxiliares mantidos para estudo futuro:

- `ReDial-action.txt`
- `JDDC.txt`
- `JDDC-ActionList.txt`

## Referência principal

Sun, Weiwei, Shuo Zhang, Krisztian Balog, Zhaochun Ren, Pengjie Ren, Zhumin Chen e Maarten de Rijke. **Simulating User Satisfaction for the Evaluation of Task-oriented Dialogue Systems**. SIGIR, 2021.

Artigo:

https://arxiv.org/pdf/2105.03748

Repositório oficial:

https://github.com/sunnweiwei/user-satisfaction-simulation

## Estrutura da aplicação

- `app.py`: interface Streamlit.
- `src/loaders.py`: leitura e normalização dos datasets.
- `src/preprocessing.py`: parsing e tradução textual das notas de satisfação.
- `src/charts.py`: gráficos Plotly.
- `src/content.py`: textos explicativos exibidos no guia do app.
- `src/downloads.py`: download automático dos arquivos oficiais.
- `pages_app/overview.py`: panorama analítico, distribuição de notas, cobertura e concordância.
- `pages_app/dataset_annotations.py`: glossário, exemplos e gráficos de anotações por dataset.
- `pages_app/dialogue_inspection.py`: busca, paginação e inspeção de conversas completas.
- `data/raw`: arquivos TXT originais do dataset.
- `data/processed`: cache Parquet normalizado.

## Observação analítica

A nota de satisfação do USS é contextual. Ela deve ser lida com o histórico da conversa em mente. Uma fala aparentemente neutra pode ter nota baixa se o sistema falhou antes, e uma fala curta pode ter nota alta se a tarefa foi resolvida bem.
