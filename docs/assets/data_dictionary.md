# Dicionário de dados · ProUni 2005–2019

**Autoria:** Wikten Alves. **Instituição e curso:** Unilasalle-RJ, Bacharelado em Sistemas de Informação.  
**Disciplina:** Linguagem de Programação (Análise e Visualização de Dados com Python), 6º período, 2026.2.

**Distribuição analisada:** [Leo Farhat, Kaggle, versão 1](https://www.kaggle.com/datasets/lfarhat/brasil-students-scholarship-prouni-20052019).  
**Fonte institucional e documentação:** [Ministério da Educação, Portal de Dados Abertos](https://dadosabertos.mec.gov.br/prouni).

## Arquivo de origem

`prouni_2005_2019.csv` em UTF-8, separado por vírgulas, com cabeçalho. Cada linha é um registro de bolsa na distribuição analisada. Os tipos abaixo descrevem a representação semântica dos campos no CSV. O ETL lê inicialmente como texto somente as cinco variáveis indicadas.

| Variável original | Tipo primitivo e formato | Significado | Uso no ETL |
| --- | --- | --- | --- |
| `ANO_CONCESSAO_BOLSA` | Inteiro, AAAA | Ano de concessão da bolsa. | Convertido e validado no intervalo 2005–2019. |
| `CODIGO_EMEC_IES_BOLSA` | Texto de código, dígitos | Identificador e-MEC da instituição de educação superior (IES). | Excluído da seleção. |
| `NOME_IES_BOLSA` | Texto livre | Nome da instituição de educação superior vinculada à bolsa. | Excluído da seleção. |
| `TIPO_BOLSA` | Texto categórico | Tipo cadastrado da bolsa. | Normalizado para Integral, Parcial 50% ou Complementar 25%. |
| `MODALIDADE_ENSINO_BOLSA` | Texto categórico | Modalidade de ensino do curso vinculado à bolsa. | Normalizada para Presencial ou EaD. |
| `NOME_CURSO_BOLSA` | Texto livre | Nome cadastrado do curso vinculado à bolsa. | Excluído da seleção. |
| `NOME_TURNO_CURSO_BOLSA` | Texto categórico | Turno cadastrado do curso. | Excluído da seleção. |
| `CPF_BENEFICIARIO_BOLSA` | Texto, identificador mascarado | Campo de CPF do beneficiário com máscara na distribuição original. A máscara não serve como identificador único. | Excluído da seleção. |
| `SEXO_BENEFICIARIO_BOLSA` | Texto categórico | Sexo cadastrado do beneficiário. | Excluído da seleção. |
| `RACA_BENEFICIARIO_BOLSA` | Texto categórico | Categoria de raça/cor cadastrada do beneficiário. | Excluído da seleção. |
| `DT_NASCIMENTO_BENEFICIARIO` | Data como texto, AAAA-MM-DD ou AAAA-MM-DD hh:mm:ss | Data de nascimento cadastrada do beneficiário. | Excluído da seleção. |
| `BENEFICIARIO_DEFICIENTE_FISICO` | Texto categórico | Indicador cadastral de deficiência física conforme a nomenclatura da fonte. | Excluído da seleção. |
| `REGIAO_BENEFICIARIO_BOLSA` | Texto categórico | Região geográfica declarada no registro do beneficiário. | Comparada à região derivada da UF. |
| `SIGLA_UF_BENEFICIARIO_BOLSA` | Texto categórico, sigla de duas letras | UF associada ao beneficiário no cadastro. | Padronizada e validada, com `NI` para registros sem UF. |
| `MUNICIPIO_BENEFICIARIO_BOLSA` | Texto livre | Nome do município associado ao beneficiário no cadastro. | Excluído da seleção. |
| `idade` | Número decimal ou vazio, em anos | Idade disponibilizada pelo compilador da distribuição. A referência temporal não é definida aqui como o ano da concessão. | Excluído da seleção. |

## Saídas tratadas

`data/processed/bolsas_agregadas.csv.gz` é um CSV UTF-8 com vírgulas, compactado com gzip.
Cada linha agrega os registros de uma combinação de ano, UF, região, modalidade e tipo. Só aparecem combinações observadas e as contagens somam o número de linhas lidas.

| Variável | Tipo e formato | Significado |
| --- | --- | --- |
| `ano` | Inteiro, AAAA | Ano de concessão, de 2005 a 2019. |
| `uf` | Texto, 2 letras maiúsculas | Sigla da UF associada ao beneficiário ou `NI` (não informada). |
| `regiao` | Texto categórico | Região brasileira derivada da UF. `Não informada` quando a UF não está disponível. |
| `modalidade` | Texto categórico | `Presencial` ou `EaD`. |
| `tipo_bolsa` | Texto categórico | `Integral`, `Parcial 50%` ou `Complementar 25%`. A última denominação é a categoria histórica do CSV. |
| `bolsas` | Inteiro positivo | Contagem de registros no grupo. |

`data/processed/qualidade.json` preserva a proveniência e a auditoria.

| Chave | Tipo | Significado |
| --- | --- | --- |
| `dataset` | Texto | Identificador da distribuição no Kaggle. |
| `versao` | Inteiro | Versão utilizada no Kaggle. |
| `csv_sha256` | Texto hexadecimal | SHA-256 dos bytes do CSV descompactado. |
| `linhas_lidas` | Inteiro | Registros lidos, excluído o cabeçalho. |
| `ausentes_ano`, `ausentes_tipo_bolsa`, `ausentes_modalidade`, `ausentes_regiao_origem`, `ausentes_uf` | Inteiro | Campos vazios entre as cinco colunas lidas, após remover espaços nas extremidades. |
| `regioes_declaradas_divergentes` | Inteiro | Regiões preenchidas no CSV que divergem da derivação a partir da UF. |
| `bolsas_processadas` | Inteiro | Soma da coluna `bolsas` após agregação. |
| `grupos_processados` | Inteiro | Número de linhas da tabela agregada. |

## Indicadores analíticos

- **Participação por UF ou região** = bolsas no território ÷ bolsas com UF conhecida × 100.
- **Participação EaD anual** = bolsas EaD no ano ÷ todas as bolsas no mesmo ano × 100.
- **Participação EaD acumulada** = bolsas EaD no período ÷ todas as bolsas do período × 100.
- **Variação anual** = (bolsas no ano ÷ bolsas no ano anterior − 1) × 100. Indefinida no primeiro ano.
- **Variação de participação em pontos percentuais** = participação final − inicial.
- **Intervalo interquartil (IQR)** = Q3 − Q1 da contagem anual, com percentis calculados por interpolação linear. Anos abaixo de Q1 − 1,5 × IQR ou acima de Q3 + 1,5 × IQR são sinalizados.
- **Spearman** = correlação de Pearson entre os postos do ano e os postos da participação anual da EaD.
