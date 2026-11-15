# Bolsas do ProUni no Brasil (2005–2019)

**Autoria:** Wikten Alves.  
**Filiação:** Centro Universitário La Salle do Rio de Janeiro (Unilasalle-RJ), Bacharelado em Sistemas de Informação.  
**Disciplina:** Linguagem de Programação (Análise e Visualização de Dados com Python), 6º período, semestre 2026.2.

![Python 3.12](https://img.shields.io/badge/Python-3.12-28607b)
![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a%20do%20c%C3%B3digo-MIT-14655f)

## Resumo executivo

Estudo descritivo de 2.692.540 registros de concessão de bolsas do ProUni. O volume anual aumentou de 95.629 em 2005 para 225.555 em 2019, com pico de 252.650 em 2015. Entre os registros com UF identificada, 47,89% estavam associados ao Sudeste. A participação da educação a distância (EaD) passou de 4,99% para 29,82%.

**Palavras-chave:** ProUni, bolsas de estudo, ensino superior, educação a distância, análise exploratória.

- **RQ1** — Como evoluiu o total anual de bolsas registradas entre 2005 e 2019?
- **RQ2** — Como as bolsas se distribuíram entre regiões e UFs associadas aos beneficiários?
- **RQ3** — Como variou a participação da EaD no total anual de concessões?

**Dados analisados:** [Leo Farhat, Kaggle, versão 1](https://www.kaggle.com/datasets/lfarhat/brasil-students-scholarship-prouni-20052019). A fonte institucional é o [Portal de Dados Abertos do MEC](https://dadosabertos.mec.gov.br/prouni). O indicador-base é a contagem de registros de concessões na distribuição analisada.

## Como ver o trabalho

[Artigo no GitHub Pages](https://wikten1.github.io/teste_manuzinha/).

Abra `docs/index.html` no navegador, mantendo `docs/assets/` ao lado dele. O artigo já vem gerado, com seus gráficos e tabelas. O notebook, com resultados da execução, pode ser visto no GitHub ou no JupyterLab local.

## Estrutura

```text
prouni-2005-2019/
├── README.md
├── LICENSE e LICENCAS.md
├── requirements.txt
├── .gitignore
├── projeto.toml
├── data/
│   ├── raw/README.md
│   ├── processed/
│   │   ├── bolsas_agregadas.csv.gz
│   │   └── qualidade.json
│   └── data_dictionary.md
├── notebooks/analise_exploratoria.ipynb
├── src/
│   ├── __init__.py
│   ├── etl.py
│   ├── analise.py
│   ├── publicar.py
│   └── artigo.html
└── docs/
    ├── .nojekyll
    ├── index.html
    └── assets/
```

## Reprodução do zero

Clone o repositório público, ou extraia o ZIP, e execute os comandos na raiz. Use Python 3.12.

**Windows · PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.etl
.\.venv\Scripts\python.exe -m src.publicar
.\.venv\Scripts\python.exe -m jupyterlab
```

**Linux, macOS ou WSL**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.etl
python -m src.publicar
python -m jupyterlab
```

1. Abra `notebooks/analise_exploratoria.ipynb` no JupyterLab e execute todas as células.
2. Confira `data/processed/qualidade.json`. O ETL registra a origem, as ausências e a conservação da contagem.
3. Abra `docs/index.html`. `src/publicar.py` gera o artigo e os dados dos gráficos a partir da tabela processada. O ETL só precisa acessar o Kaggle quando o ZIP de origem ainda não está em `data/raw/`.

O ETL lê cinco dos 16 campos em blocos de 150 mil linhas. Os 402 registros sem UF permanecem nas contagens nacionais. As participações por estado e região usam os 2.692.138 registros com UF conhecida. As análises da EaD incluem todos os registros e usam o total de cada ano no denominador. O [dicionário de dados](data/data_dictionary.md) descreve as variáveis e os indicadores.

## Publicação no GitHub Pages

1. Crie um repositório público no GitHub. Em `projeto.toml`, preencha `repositorio` com o endereço HTTPS real, como `https://github.com/USUARIO/REPOSITORIO`. Confirme a equipe e o semestre. Se houver ajustes, sincronize os cabeçalhos do README, do dicionário e do notebook.
2. Execute novamente `python -m src.publicar` com o ambiente configurado para gravar o link no artigo. Envie o conteúdo da pasta do projeto à branch `main`. O ZIP baixado pelo ETL permanece ignorado pelo Git.
3. No GitHub, abra **Settings → Pages**. Em **Build and deployment**, selecione **Deploy from a branch**, escolha **main** e **/docs**, e salve.
4. Quando o GitHub mostrar a URL pública, abra-a e confira o botão do repositório, os gráficos, os downloads e a navegação em tela pequena. Acrescente a URL pública ao README do repositório.

[Documentação oficial do GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## FAIR e licenças

| Princípio | Implementação |
| --- | --- |
| Localizável | Fonte, versão, palavras-chave, identificação acadêmica e assuntos de pesquisa. |
| Acessível | Ingestão via endpoint público sem credenciais. Artigo estático pronto para GitHub Pages. |
| Interoperável | CSV gzip e JSON em UTF-8, com [dicionário para as variáveis de origem e processadas](data/data_dictionary.md). |
| Reutilizável | Instruções de reprodução, dependências congeladas e [licenças por tipo de material](LICENCAS.md). |
