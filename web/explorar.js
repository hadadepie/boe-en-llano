/* El BOE en llano — página de datos (datos.html): gráfico por día por sección y
   lista filtrable de las normas de la semana. Usa lo común de app.js.
   El mosaico de la portada ya cruza tema y a quién afecta; las votaciones están en
   la ficha de cada decreto-ley y en «La legislatura»; el método, en como.html. */

"use strict";

// «Cómo se ha hecho» estaba en esta página (datos.html#como): los enlaces antiguos van a su página.
if (location.hash === "#como") location.replace("como.html");

const explorar = {
  filtros: { fecha: "", tema: "", impacto: "", ambito: "", decision: "" },
  grafico: null,
};

// ---------- Frases de lectura ----------

function nombreCorto(seccion) {
  const nombres = { I: "normas generales", "II.A": "nombramientos", "II.B": "oposiciones y concursos",
    III: "otras disposiciones", IV: "decisiones de justicia", V: "anuncios",
    TC: "sentencias del Tribunal Constitucional" };
  return nombres[seccion.codigo] || seccion.nombre;
}

function fraseGrafico(dias) {
  if (!dias.length) return "";
  const totales = estado.indice.secciones.map((s) => ({ ...s, total: dias.reduce((a, d) => a + d.recuento[s.codigo], 0) }));
  const total = totales.reduce((a, s) => a + s.total, 0);
  const pct = (n) => {
    const v = (100 * n) / total;
    return `${v < 10 ? v.toFixed(1).replace(".", ",") : Math.round(v)} %`;
  };
  const [primera, segunda] = [...totales].sort((a, b) => b.total - a.total);
  const normas = totales.find((s) => s.codigo === "I");
  return `Lo que más publica el BOE son ${nombreCorto(primera)} (${pct(primera.total)}) y ${nombreCorto(segunda)} ` +
    `(${pct(segunda.total)}). Las normas generales son solo el ${pct(normas.total)}.`;
}

// ---------- Gráfico por día ----------

function pintarGrafico() {
  const dias = diasEdicion();
  $("lectura-grafico").textContent = fraseGrafico(dias);
  if (!window.Chart) {
    $("grafico").closest(".grafico").replaceChildren(el("p", { clase: "ayuda", texto: "No se ha podido cargar la librería del gráfico. Los datos están en la tabla de abajo." }));
    return;
  }
  if (explorar.grafico) explorar.grafico.destroy();
  const superficie = variable("--superficie");
  const secciones = estado.indice.secciones;
  explorar.grafico = new Chart($("grafico"), {
    type: "bar",
    data: {
      labels: dias.map((d) => aFecha(d.fecha).toLocaleDateString("es-ES", { weekday: "short", day: "numeric" })),
      datasets: secciones.map((s, i) => ({
        label: s.nombre,
        data: dias.map((d) => d.recuento[s.codigo]),
        backgroundColor: variable(`--s${i + 1}`),
        borderColor: superficie, borderWidth: { top: 2 }, borderSkipped: "start",
        borderRadius: i === secciones.length - 1 ? { topLeft: 3, topRight: 3 } : 0,
        maxBarThickness: 24,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { color: variable("--tinta-2") }, border: { color: variable("--linea") } },
        y: { stacked: true, beginAtZero: true, grid: { color: variable("--linea") }, ticks: { color: variable("--tinta-2"), precision: 0 }, border: { display: false } },
      },
      plugins: {
        legend: { position: "top", align: "start", labels: { color: variable("--tinta"), boxWidth: 12, boxHeight: 12, useBorderRadius: true, borderRadius: 2 } },
        tooltip: {
          callbacks: {
            title: (items) => fechaLarga(dias[items[0].dataIndex].fecha),
            label: (item) => ` ${miles(item.raw)}  ${item.dataset.label}`,
            footer: (items) => `Total: ${miles(items.reduce((s, i) => s + i.raw, 0))}`,
          },
        },
      },
    },
  });
}

function pintarTablaDias() {
  const { secciones } = estado.indice;
  $("tabla-dias").replaceChildren(
    el("thead", {}, el("tr", {}, el("th", { texto: "Día" }), ...secciones.map((s) => el("th", { texto: s.codigo })), el("th", { texto: "Total" }))),
    el("tbody", {}, ...diasEdicion().map((d) => el("tr", {},
      el("td", { texto: fechaCorta(d.fecha) }),
      ...secciones.map((s) => el("td", { texto: miles(d.recuento[s.codigo]) })),
      el("td", { texto: miles(Object.values(d.recuento).reduce((a, b) => a + b, 0)) }),
    ))),
  );
}

// ---------- Filtros ----------

function normasFiltradas({ ignorar = [] } = {}) {
  const f = explorar.filtros;
  return estado.normas.filter((n) =>
    (ignorar.includes("fecha") || !f.fecha || n.fecha === f.fecha) &&
    (ignorar.includes("tema") || !f.tema || n.tema === f.tema) &&
    (ignorar.includes("impacto") || !f.impacto || n.impacto === f.impacto) &&
    (ignorar.includes("ambito") || !f.ambito || n.ambito === f.ambito) &&
    (ignorar.includes("decision") || !f.decision || n.decision === f.decision));
}

function rellenarSelect(select, todas, opciones, formato = (x) => x) {
  select.replaceChildren(el("option", { value: "", texto: todas }), ...opciones.map((o) => el("option", { value: o, texto: formato(o) })));
}

function rellenarFiltros() {
  const normas = estado.normas;
  const fechas = [...new Set(normas.map((n) => n.fecha))].sort().reverse();
  const ambitos = [...new Set(normas.map((n) => n.ambito))].sort((a, b) => (a === "Estatal" ? -1 : b === "Estatal" ? 1 : a.localeCompare(b, "es")));
  rellenarSelect($("f-fecha"), "Todos los días", fechas, diaSemana);
  rellenarSelect($("f-tema"), "Todos los temas", estado.indice.temas);
  rellenarSelect($("f-impacto"), "Todos", estado.indice.impactos, nombreImpacto);
  rellenarSelect($("f-ambito"), "Todos", ambitos);
  rellenarSelect($("f-decision"), "Todas", estado.indice.decisiones, nombreDecision);
}

function actualizar() {
  for (const [clave, valor] of Object.entries(explorar.filtros)) $(`f-${clave}`).value = valor;
  pintarLista();
}

// ---------- Lista ----------

function pintarLista() {
  const normas = normasFiltradas().sort((a, b) => b.fecha.localeCompare(a.fecha) || porRelevancia(a, b));
  const total = estado.normas.length;
  $("contador").textContent = normas.length === total
    ? `${total} normas generales esta semana.`
    : `${normas.length} de ${total} normas con estos filtros.`;
  const lista = $("lista");
  if (normas.length === 0) {
    lista.replaceChildren(el("li", {}, el("p", { clase: "ayuda", texto: "No hay normas con estos filtros." })));
    return;
  }
  lista.replaceChildren(...normas.map((n) => el("li", {}, el("button", { type: "button", onclick: () => abrirArticulo(n.id) },
    el("span", { clase: "t", texto: titular(n) }),
    el("span", { clase: "m", texto: `${fechaCorta(n.fecha)} · ${n.rango || ""} · ${n.ambito}` }),
    el("span", { clase: "m", texto: `${n.tema} · ${nombreImpacto(n.impacto)}${n.ficha && n.ficha.estado === "ok" ? " · resumen automático" : ""}` }),
  ))));
}

window.PAGINA = {
  preparar() {
    for (const clave of Object.keys(explorar.filtros)) {
      $(`f-${clave}`).addEventListener("change", (e) => { explorar.filtros[clave] = e.target.value; actualizar(); });
    }
    $("filtros").addEventListener("reset", () => {
      setTimeout(() => { for (const k of Object.keys(explorar.filtros)) explorar.filtros[k] = ""; actualizar(); });
    });
    // Repintar con los colores del modo claro/oscuro cuando cambie.
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => pintarGrafico());
  },
  pintar() {
    for (const k of Object.keys(explorar.filtros)) explorar.filtros[k] = "";
    // Al llegar con un filtro en la URL (p. ej. ?impacto=Técnico desde la portada), se aplica una vez.
    if (!explorar.filtroUrlAplicado) {
      explorar.filtroUrlAplicado = true;
      const params = new URLSearchParams(location.search);
      if (estado.indice.impactos.includes(params.get("impacto"))) explorar.filtros.impacto = params.get("impacto");
      if (estado.indice.temas.includes(params.get("tema"))) explorar.filtros.tema = params.get("tema");
      if (estado.indice.decisiones.includes(params.get("decision"))) explorar.filtros.decision = params.get("decision");
    }
    pintarGrafico();
    pintarTablaDias();
    rellenarFiltros();
    actualizar();
  },
};
