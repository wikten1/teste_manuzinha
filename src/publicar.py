"""Gera o artigo e os ativos estáticos a partir da tabela processada."""

import json
import shutil
import tomllib
from html import escape
from importlib.resources import files
from string import Template
from urllib.parse import urlparse

import matplotlib

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from .analise import analisar, carregar_dados
from .etl import PROCESSED, ROOT

DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
BLUE = "#204e65"
TEAL = "#0e655c"
INK = "#172a35"


def pt(value, places=0):
    return f"{value:,.{places}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def tabela(caption, headers, rows):
    head = "".join(f'<th scope="col">{escape(str(header))}</th>' for header in headers)
    body = []
    for label, *values in rows:
        cells = "".join(f"<td>{escape(str(value))}</td>" for value in values)
        body.append(f'<tr><th scope="row">{escape(str(label))}</th>{cells}</tr>')
    return (
        f"<table><caption>{escape(caption)}</caption>"
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"
    )


def grafico_ranking(estados, *, mobile=False):
    top = estados.head(8).iloc[::-1]
    size = (4.4, 4.25) if mobile else (9.2, 4.8)
    fig, ax = plt.subplots(figsize=size)
    fig.subplots_adjust(left=.12, right=.97, bottom=.16 if mobile else .20, top=.97)
    colors = [TEAL if uf == "SP" else "#39637b" for uf in top["uf"]]
    bars = ax.barh(top["uf"], top["bolsas"], color=colors, height=.66)
    ax.bar_label(bars, labels=[pt(value) for value in top["bolsas"]], padding=8, fontsize=13, color=INK)
    ax.set_xlim(0, 1_060_000 if mobile else 955_000)
    ticks = [0, 200_000, 400_000, 600_000, 800_000]
    labels = [pt(value) for value in ticks]
    if mobile:
        labels = ["0", "200 mil", "400 mil", "600 mil", "800 mil"]
    ax.set_xticks(ticks, labels)
    ax.set_xlabel("Registros de bolsas", color=BLUE, fontsize=13, labelpad=12)
    ax.tick_params(axis="both", length=0, labelsize=12, colors=INK, pad=8)
    ax.xaxis.grid(True, color="#dce7e9")
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig


def grafico_anual(annual, column, color, tick_values, tick_labels, label):
    chart = go.Figure(
        go.Scatter(
            x=annual.index.tolist(),
            y=annual[column].round(4).tolist(),
            mode="lines+markers",
            line={"color": color, "width": 3},
            marker={"size": 7, "line": {"color": "white", "width": 1}},
            hovertemplate="%{customdata}<extra></extra>",
            customdata=[f"{year}<br>{label(value)}" for year, value in annual[column].items()],
        )
    )
    chart.update_layout(
        template="none",
        autosize=True,
        margin={"l": 60, "r": 20, "t": 16, "b": 45},
        font={"family": "Source Sans 3, system-ui, sans-serif", "size": 13, "color": INK},
        xaxis={
            "type": "linear", "range": [2004.6, 2019.4], "tickmode": "array",
            "tickvals": [2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019],
            "ticktext": ["2005", "2007", "2009", "2011", "2013", "2015", "2017", "2019"],
            "fixedrange": True, "showgrid": False,
        },
        yaxis={
            "range": [0, tick_values[-1] * 1.06], "fixedrange": True,
            "tickmode": "array", "tickvals": tick_values, "ticktext": tick_labels,
            "gridcolor": "#dce7e9", "zeroline": False,
        },
        showlegend=False,
        hoverlabel={"bgcolor": INK, "font_color": "white"},
    )
    return json.loads(chart.to_json())


def gerar_visualizacoes(annual, estados):
    figures = {
        "chart-anual": grafico_anual(
            annual, "total", BLUE,
            [0, 50_000, 100_000, 150_000, 200_000, 250_000, 275_000],
            ["0", "50 mil", "100 mil", "150 mil", "200 mil", "250 mil", ""],
            lambda value: f"{pt(value)} bolsas",
        ),
        "chart-ead": grafico_anual(
            annual, "ead_pct", TEAL, [0, 5, 10, 15, 20, 25, 30, 35],
            ["0%", "5%", "10%", "15%", "20%", "25%", "30%", ""],
            lambda value: f"{pt(value, 2)}% em EaD",
        ),
    }
    fig = grafico_ranking(estados)
    fig.savefig(ASSETS / "ranking-ufs.png", dpi=180, facecolor="white")
    plt.close(fig)
    mobile = grafico_ranking(estados, mobile=True)
    mobile.savefig(ASSETS / "ranking-ufs-mobile.png", dpi=180, facecolor="white")
    plt.close(mobile)
    (ASSETS / "dados-graficos.js").write_text(
        "window.prouniCharts = " + json.dumps(figures, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    plotly_js = files("plotly").joinpath("package_data", "plotly.min.js")
    (ASSETS / "plotly.min.js").write_bytes(plotly_js.read_bytes())


def montar_artigo(annual, estados, regioes, stats, qualidade):
    meta = tomllib.loads((ROOT / "projeto.toml").read_text(encoding="utf-8"))
    repo = meta["repositorio"].strip().rstrip("/")
    parsed = urlparse(repo)
    if repo and (
        parsed.scheme != "https" or parsed.netloc != "github.com"
        or len(parsed.path.strip("/").split("/")) != 2 or parsed.query or parsed.fragment
    ):
        raise ValueError("Use https://github.com/usuario/repositorio no campo repositorio.")
    repo_url = escape(repo, quote=True)
    autor = ", ".join(meta["autores"])
    dados = {key: escape(meta[key]) for key in ("instituicao", "curso", "disciplina", "periodo", "semestre")}
    dados["autores"] = escape(autor)
    if repo:
        dados["link_repo"] = f'<a class="repo" href="{repo_url}">Ver repositório no GitHub ↗</a>'
        dados["link_dicionario"] = (
            f'<a href="{repo_url}/blob/HEAD/data/data_dictionary.md">Consultar dicionário de dados</a>'
        )
        clone = f"git clone {repo}\ncd {parsed.path.split('/')[-1]}\n"
    else:
        dados["link_repo"] = '<span class="repo" aria-disabled="true">Link do GitHub pendente</span>'
        dados["link_dicionario"] = '<a href="assets/data_dictionary.md" download>Baixar dicionário de dados</a>'
        clone = "git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO\ncd SEU-REPOSITORIO\n"
    dados["comandos"] = escape(clone + (
        "python -m venv .venv\n"
        "source .venv/bin/activate\n"
        "python -m pip install -r requirements.txt\n"
        "python -m src.etl\n"
        "python -m src.publicar"
    ))

    for key, value in stats.items():
        if isinstance(value, (int, float)):
            places = 2 if key.endswith(("_pct", "_pp")) or key.startswith("ead_pct_") else 0
            dados[key] = pt(value, places)
    for key in ("pico_ano", "ead_pico_ano"):
        dados[key] = str(stats[key])
    for key in ("q1", "q3", "iqr"):
        dados[key] = pt(stats[key], 1 if stats[key] % 1 else 0)
    dados["mismatch"] = pt(qualidade["regioes_declaradas_divergentes"])
    dados["grupos"] = pt(qualidade["grupos_processados"])
    dados["atipicos"] = "nenhum ano foi sinalizado como atípico"
    if stats["anos_atipicos"]:
        anos = ", ".join(str(ano) for ano in stats["anos_atipicos"])
        dados["atipicos"] = f"os anos sinalizados como atípicos foram {anos}"
    dados["spearman"] = pt(stats["spearman"], 3)
    dados["queda_final"] = pt(abs(stats["mudanca_final"]), 2)
    dados["sul_pct"] = pt(regioes.loc["Sul", "participacao_pct"], 2)
    dados["nordeste_pct"] = pt(regioes.loc["Nordeste", "participacao_pct"], 2)
    for ano in (2018, 2019):
        dados[f"ead_{ano}"] = pt(annual.loc[ano, "ead"])
        dados[f"presencial_{ano}"] = pt(annual.loc[ano, "presencial"])

    dados["tabela_anual"] = tabela(
        "Bolsas anuais por modalidade, 2005–2019", ["Ano", "Total", "Presencial", "EaD", "% EaD"],
        (
            (ano, pt(row.total), pt(row.presencial), pt(row.ead), pt(row.ead_pct, 2) + "%")
            for ano, row in annual.iterrows()
        ),
    )
    dados["tabela_regioes"] = tabela(
        "Registros com UF identificada, por região", ["Região", "Bolsas", "Participação"],
        ((regiao, pt(row.bolsas), pt(row.participacao_pct, 2) + "%") for regiao, row in regioes.iterrows()),
    )
    dados["tabela_estados"] = tabela(
        "Registros por UF", ["UF", "Região", "Bolsas", "Participação"],
        (
            (row.uf, row.regiao, pt(row.bolsas), pt(row.participacao_pct, 2) + "%")
            for row in estados.itertuples(index=False)
        ),
    )
    template = Template(ROOT.joinpath("src", "artigo.html").read_text(encoding="utf-8"))
    return template.substitute(dados)


def main():
    matplotlib.use("Agg")
    input_data, qualidade = carregar_dados()
    annual, _, estados, regioes, stats = analisar(input_data)
    ASSETS.mkdir(parents=True, exist_ok=True)
    gerar_visualizacoes(annual, estados)
    for name in ("bolsas_agregadas.csv.gz", "qualidade.json"):
        shutil.copyfile(PROCESSED / name, ASSETS / name)
    shutil.copyfile(ROOT / "data" / "data_dictionary.md", ASSETS / "data_dictionary.md")
    (DOCS / "index.html").write_text(montar_artigo(annual, estados, regioes, stats, qualidade), encoding="utf-8")
    print("Artigo gerado em docs/index.html.")


if __name__ == "__main__":
    main()
