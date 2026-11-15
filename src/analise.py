"""Calcula as estatísticas descritivas usadas no notebook e no artigo."""

import json

import numpy as np
import pandas as pd

from .etl import PROCESSED


def carregar_dados():
    dados = pd.read_csv(PROCESSED / "bolsas_agregadas.csv.gz")
    qualidade = json.loads((PROCESSED / "qualidade.json").read_text(encoding="utf-8"))
    if dados["bolsas"].sum() != qualidade["linhas_lidas"]:
        raise ValueError("Contagens divergentes entre os dados agregados e a auditoria.")
    return dados, qualidade


def analisar(dados):
    anual = dados.groupby("ano")["bolsas"].sum().rename("total").to_frame()
    por_tipo = dados.pivot_table(
        index="ano", columns="tipo_bolsa", values="bolsas", aggfunc="sum", fill_value=0
    )
    por_modo = dados.pivot_table(
        index="ano", columns="modalidade", values="bolsas", aggfunc="sum", fill_value=0
    )
    anual["ead"] = por_modo["EaD"]
    anual["presencial"] = por_modo["Presencial"]
    anual["ead_pct"] = 100 * anual["ead"] / anual["total"]
    anual["variacao_pct"] = anual["total"].pct_change() * 100

    estados = (
        dados.loc[dados["uf"] != "NI"]
        .groupby(["uf", "regiao"], as_index=False)["bolsas"].sum()
        .sort_values(["bolsas", "uf"], ascending=[False, True], ignore_index=True)
    )
    conhecido = int(estados["bolsas"].sum())
    estados["participacao_pct"] = 100 * estados["bolsas"] / conhecido
    regioes = estados.groupby("regiao")["bolsas"].sum().sort_values(ascending=False)
    regioes = regioes.to_frame()
    regioes["participacao_pct"] = 100 * regioes["bolsas"] / conhecido

    total = int(anual["total"].sum())
    q1, mediana, q3 = np.percentile(anual["total"], [25, 50, 75])
    iqr = q3 - q1
    atipicos = (anual["total"] < q1 - 1.5 * iqr) | (anual["total"] > q3 + 1.5 * iqr)
    ano_rank = pd.Series(anual.index, index=anual.index).rank()
    ead_rank = anual["ead_pct"].rank()
    inicio = anual.iloc[0]
    fim = anual.iloc[-1]
    stats = {
        "total": total,
        "media": float(anual["total"].mean()),
        "mediana": float(mediana),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "anos_atipicos": anual.index[atipicos].tolist(),
        "pico_ano": int(anual["total"].idxmax()),
        "pico": int(anual["total"].max()),
        "inicio": int(inicio["total"]),
        "fim": int(fim["total"]),
        "crescimento_pct": 100 * (fim["total"] / inicio["total"] - 1),
        "mudanca_final": float(anual.iloc[-1]["variacao_pct"]),
        "integral_pct": 100 * int(por_tipo["Integral"].sum()) / total,
        "complementar": int(por_tipo["Complementar 25%"].sum()),
        "uf_conhecida": conhecido,
        "uf_ausente": total - conhecido,
        "sudeste_pct": float(regioes.loc["Sudeste", "participacao_pct"]),
        "sp_pct": float(estados.loc[estados["uf"] == "SP", "participacao_pct"].iloc[0]),
        "sp_total": int(estados.loc[estados["uf"] == "SP", "bolsas"].iloc[0]),
        "top3_pct": 100 * int(estados.head(3)["bolsas"].sum()) / conhecido,
        "ead_total": int(anual["ead"].sum()),
        "ead_pct": 100 * int(anual["ead"].sum()) / total,
        "ead_pct_inicio": float(inicio["ead_pct"]),
        "ead_pct_fim": float(fim["ead_pct"]),
        "ead_aumento_pp": float(fim["ead_pct"] - inicio["ead_pct"]),
        "ead_pico_ano": int(anual["ead_pct"].idxmax()),
        "ead_pico_pct": float(anual["ead_pct"].max()),
        "spearman": float(ano_rank.corr(ead_rank)),
    }
    return anual, por_tipo, estados, regioes, stats
