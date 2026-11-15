# Dados brutos

Execute `python -m src.etl` na raiz do projeto para baixar a versão 1 de
[Leo Farhat, no Kaggle](https://www.kaggle.com/datasets/lfarhat/brasil-students-scholarship-prouni-20052019).
O ZIP tem aproximadamente 52 MB e contém `prouni_2005_2019.csv` (430.091.396 bytes).
O pipeline valida o SHA-256 do CSV dentro do arquivo:

```text
397fb45ec457e3e02d7cf4f1e59bfbd4bd6b9d0bc17e41f6eac640fc78da2540
```

O ZIP fica nesta pasta, ignorado pelo Git. As saídas disponibilizadas no
projeto são agregadas. Se precisar fazer o download pelo site, salve o ZIP
como `data/raw/prouni_kaggle.zip`.
