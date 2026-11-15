const figures = document.querySelectorAll(".chart");

function graphOptions(element) {
  const { data, layout } = window.prouniCharts[element.id];
  if (element.clientWidth < 480) {
    const indices = [0, 2, 4, 6, 7];
    layout.xaxis.tickvals = indices.map((index) => layout.xaxis.tickvals[index]);
    layout.xaxis.ticktext = indices.map((index) => layout.xaxis.ticktext[index]);
    layout.margin.l = 54;
    layout.margin.r = 12;
    layout.font.size = 11;
  }
  return { data, layout };
}

async function renderCharts() {
  try {
    await new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = new URL("plotly.min.js", window.prouniChartScript);
      script.onload = resolve;
      script.onerror = reject;
      document.head.append(script);
    });
    await document.fonts.ready;
    for (const element of figures) {
      const { data, layout } = graphOptions(element);
      await window.Plotly.newPlot(element, data, layout, {
        responsive: true,
        displayModeBar: false,
        scrollZoom: false,
      });
    }
  } catch {
    for (const element of figures) {
      element.classList.add("chart-failed");
      element.textContent = "Consulte os valores do gráfico na tabela anual.";
    }
  }
}

window.prouniChartScript = document.currentScript.src;
if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver((entries) => {
    if (entries.some((entry) => entry.isIntersecting)) {
      observer.disconnect();
      renderCharts();
    }
  }, { rootMargin: "250px" });
  for (const element of figures) observer.observe(element);
} else {
  renderCharts();
}
