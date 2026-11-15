"""Adquire a base ProUni do Kaggle e gera sua versão analítica agregada."""

import gzip
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "prouni_kaggle.zip"
PROCESSED = ROOT / "data" / "processed"
DATASET = "lfarhat/brasil-students-scholarship-prouni-20052019"
URL = f"https://www.kaggle.com/api/v1/datasets/download/{DATASET}?datasetVersionNumber=1"
MEMBER = "prouni_2005_2019.csv"
SHA256 = "397fb45ec457e3e02d7cf4f1e59bfbd4bd6b9d0bc17e41f6eac640fc78da2540"
YEARS = set(range(2005, 2020))
COLUMNS = {
    "ANO_CONCESSAO_BOLSA": "ano",
    "TIPO_BOLSA": "tipo_bolsa",
    "MODALIDADE_ENSINO_BOLSA": "modalidade",
    "REGIAO_BENEFICIARIO_BOLSA": "regiao_origem",
    "SIGLA_UF_BENEFICIARIO_BOLSA": "uf",
}
REGIONS = {
    "Norte": "AC AM AP PA RO RR TO",
    "Nordeste": "AL BA CE MA PB PE PI RN SE",
    "Centro-Oeste": "DF GO MS MT",
    "Sudeste": "ES MG RJ SP",
    "Sul": "PR RS SC",
}
UF_REGION = {
    uf: region for region, codes in REGIONS.items() for uf in codes.split()
}
TYPES = {
    "BOLSA INTEGRAL": "Integral",
    "BOLSA PARCIAL 50%": "Parcial 50%",
    "BOLSA COMPLEMENTAR 25%": "Complementar 25%",
}
MODES = {"PRESENCIAL": "Presencial", "EAD": "EaD"}
KEYS = ["ano", "uf", "regiao", "modalidade", "tipo_bolsa"]
UNKNOWN = "Não informada"


def verify_archive(path):
    with ZipFile(path) as archive, archive.open(MEMBER) as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if digest != SHA256:
        raise ValueError(f"SHA-256 inesperado para {MEMBER}: {digest}")


def acquire():
    if RAW.exists():
        verify_archive(RAW)
        return RAW

    RAW.parent.mkdir(parents=True, exist_ok=True)
    request = Request(URL, headers={"User-Agent": "ProUni-EDA/1.0"})
    with TemporaryDirectory(dir=RAW.parent) as directory:
        candidate = Path(directory) / RAW.name
        with urlopen(request, timeout=90) as response, candidate.open("wb") as target:
            shutil.copyfileobj(response, target)
        verify_archive(candidate)
        candidate.replace(RAW)
    return RAW


def normalize(chunk, audit):
    chunk = chunk.rename(columns=COLUMNS)
    for column in COLUMNS.values():
        chunk[column] = chunk[column].str.strip().replace("", pd.NA)
        audit[f"ausentes_{column}"] += int(chunk[column].isna().sum())

    year = pd.to_numeric(chunk["ano"], errors="coerce")
    if not year.isin(YEARS).all():
        raise ValueError("Há ano ausente ou fora da janela de 2005 a 2019.")
    chunk["ano"] = year.astype("int16")

    for column, labels in (("tipo_bolsa", TYPES), ("modalidade", MODES)):
        normalized = chunk[column].str.upper().map(labels)
        if normalized.isna().any():
            raise ValueError(f"{column} contém categoria desconhecida ou ausente.")
        chunk[column] = normalized

    uf = chunk["uf"].str.upper()
    if (uf.notna() & ~uf.isin(UF_REGION)).any():
        raise ValueError("Há UF preenchida que não corresponde a uma sigla válida.")
    region = uf.map(UF_REGION).fillna(UNKNOWN)
    declared = chunk["regiao_origem"].str.upper()
    mismatch = declared.notna() & declared.ne(region.str.upper()).fillna(False)
    audit["regioes_declaradas_divergentes"] += int(mismatch.sum())
    chunk["uf"] = uf.fillna("NI")
    chunk["regiao"] = region
    return chunk


def aggregate(path, chunksize=150_000):
    audit = Counter()
    totals = Counter()
    with ZipFile(path) as archive, archive.open(MEMBER) as source:
        reader = pd.read_csv(
            source,
            usecols=list(COLUMNS),
            dtype="string",
            encoding="utf-8-sig",
            sep=",",
            keep_default_na=False,
            chunksize=chunksize,
        )
        for chunk in reader:
            audit["linhas_lidas"] += len(chunk)
            normal = normalize(chunk, audit)
            totals.update(normal.groupby(KEYS, sort=False).size().to_dict())

    rows = [(*key, count) for key, count in totals.items()]
    table = pd.DataFrame(rows, columns=[*KEYS, "bolsas"]).sort_values(KEYS)
    audit["bolsas_processadas"] = int(table["bolsas"].sum())
    audit["grupos_processados"] = len(table)
    if audit["linhas_lidas"] != audit["bolsas_processadas"] or set(table["ano"]) != YEARS:
        raise ValueError("A agregação não preservou a contagem ou a série de anos.")
    return table, dict(audit)


def main():
    path = acquire()
    table, audit = aggregate(path)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with (PROCESSED / "bolsas_agregadas.csv.gz").open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as output:
            table.to_csv(output, index=False, encoding="utf-8", lineterminator="\n")
    metadata = {"dataset": DATASET, "versao": 1, "csv_sha256": SHA256, **audit}
    (PROCESSED / "qualidade.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{audit['bolsas_processadas']:,} registros em {len(table):,} grupos.")


if __name__ == "__main__":
    main()
