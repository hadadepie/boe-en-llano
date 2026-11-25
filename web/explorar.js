/* El BOE en llano — Explorar (datos.html): la semana de un vistazo (embudo en dos niveles),
   mosaico de las normas por tema, «La semana en datos», gráfico por día por sección y lista
   filtrable. Los tres primeros estaban en la portada hasta el 26/11/2026. Usa lo común de app.js.
   Las votaciones están en la ficha de cada decreto-ley y en «La legislatura»; el método, en como.html. */

"use strict";

// «Cómo se ha hecho» estaba en esta página (datos.html#como): los enlaces antiguos van a su página.
if (location.hash === "#como") location.replace("como.html");

const explorar = {
  filtros: { fecha: "", tema: "", impacto: "", ambito: "", decision: "" },
  grafico: null,
  piezaAbierta: null,
};

// ---------- La semana de un vistazo: embudo en dos niveles ----------
// 1) Una barra con todo lo publicado en la semana, con la astilla de las normas
//    generales iluminada. 2) Esa astilla ampliada: un cuadrado por norma general,
//    coloreado por a quién afecta. Las dos proporciones son exactas; el zoom solo
//    evita que las normas que afectan a mucha gente se pierdan entre las 1.500 publicaciones.

const SVG = "http://www.w3.org/2000/svg";
const ORDEN_IMPACTO = { Directo: 0, Colectivos: 1, Técnico: 2 };

function porcentaje(parte, total) {
  const v = (100 * parte) / (total || 1);
  return `${v < 10 ? v.toFixed(1).replace(".", ",") : Math.round(v)} %`;
}

function pintarEmbudo() {
  const r = edicionActual().resumen;
  const total = r.total_publicaciones;
  const normas = estado.normas;
  const resto = total - normas.length;
  const cuenta = (i) => normas.filter((n) => n.impacto === i).length;
  const afectan = cuenta("Directo");
  const proporcion = (100 * normas.length) / (total || 1);

  // Nivel 1: todo el BOE de la semana.
  const barra = el("div", { clase: "embudo-barra", role: "img",
    "aria-label": `${miles(total)} publicaciones en el BOE esta semana; ${miles(normas.length)} son normas generales (${porcentaje(normas.length, total)}).` });
  const astilla = el("span", { clase: "embudo-astilla" });
  astilla.style.width = `${proporcion}%`;
  barra.append(astilla);

  // Conector: de la astilla al ancho completo, para que se lea como una ampliación.
  const conector = document.createElementNS(SVG, "svg");
  conector.setAttribute("class", "embudo-conector");
  conector.setAttribute("viewBox", "0 0 100 24");
  conector.setAttribute("preserveAspectRatio", "none");
  conector.setAttribute("aria-hidden", "true");
  const forma = document.createElementNS(SVG, "polygon");
  forma.setAttribute("points", `0,0 ${Math.max(proporcion, 1.2)},0 100,24 0,24`);
  conector.append(forma);

  // Nivel 2: las normas generales, una a una.
  const ordenadas = [...normas].sort((a, b) => ORDEN_IMPACTO[a.impacto] - ORDEN_IMPACTO[b.impacto]);
  const cuadros = el("div", { clase: "embudo-zoom", role: "img",
    "aria-label": `De las ${miles(normas.length)} normas generales: ` +
      estado.indice.impactos.map((i) => `${miles(cuenta(i))} ${nombreImpacto(i).toLowerCase()}`).join(", ") + "." },
    ...ordenadas.map((n) => el("span", { clase: `embudo-cuadro tesela-${n.impacto}` })));

  // Cada fila de la leyenda filtra la lista de abajo por «A quién afecta».
  const fila = (impacto, cifra, texto) => el("li", {}, el("span", { clase: `muestra tesela-${impacto}` }),
    el("strong", { texto: miles(cifra) }), " ",
    el("button", { type: "button", clase: "enlace-boton", onclick: () => filtrarLista("impacto", impacto), texto }));
  $("embudo").replaceChildren(
    el("p", { clase: "embudo-titular" }, el("strong", { texto: miles(afectan) }),
      ` de ${miles(total)} publicaciones ${afectan === 1 ? "afecta" : "afectan"} a mucha gente.`),
    el("p", { clase: "embudo-etiqueta" }, el("strong", { texto: miles(total) }), " publicaciones en el BOE esta semana"),
    barra,
    el("p", { clase: "embudo-pie-barra" },
      el("span", { clase: "embudo-pie-normas", texto: `${miles(normas.length)} normas generales (${porcentaje(normas.length, total)})` }),
      el("span", { texto: `${miles(resto)} nombramientos, oposiciones, justicia y anuncios` })),
    conector,
    el("p", { clase: "embudo-etiqueta" }, "Ampliadas, las ", el("strong", { texto: miles(normas.length) }), " normas generales:"),
    cuadros,
    el("ul", { clase: "embudo-leyenda" },
      fila("Directo", afectan, afectan === 1 ? "afecta a mucha gente" : "afectan a mucha gente"),
      fila("Colectivos", cuenta("Colectivos"), "afectan a ciertos grupos"),
      fila("Técnico", cuenta("Técnico"), "son de gestión interna")),
    el("p", { clase: "nota", texto: "Gestión interna: trámites, organización de la Administración y subvenciones a entidades " +
      "concretas; no suelen afectar directamente a la ciudadanía. Pulsa una fila para ver esas normas en la lista." }));
}

// ---------- Mosaico: todas las normas de la semana por tema ----------

function pintarMosaico(normas) {
  $("mosaico-seccion").hidden = normas.length === 0;
  $("t-mosaico").textContent = `Las ${normas.length} normas de la semana, por tema`;
  $("mosaico-leyenda").replaceChildren(...estado.indice.impactos.map((i) =>
    el("li", {}, el("span", { clase: `muestra tesela-${i}` }), nombreImpacto(i))));
  const pista = $("mosaico-pista");
  const textoPista = "Pasa el ratón o el foco por un cuadrado para ver de qué trata.";
  pista.textContent = textoPista;
  const temas = estado.indice.temas
    .map((tema) => ({ tema, normas: normas.filter((n) => n.tema === tema) }))
    .filter((t) => t.normas.length)
    .sort((a, b) => b.normas.length - a.normas.length);
  $("mosaico").replaceChildren(...temas.map(({ tema, normas: delTema }) => {
    const teselas = [...delTema]
      .sort((a, b) => ORDEN_IMPACTO[a.impacto] - ORDEN_IMPACTO[b.impacto] || porRelevancia(a, b))
      .map((n) => {
        const a = enlaceNorma(n, `tesela tesela-${n.impacto}`, []);
        const descripcion = `${nombreImpacto(n.impacto)}${n.ambito !== "Estatal" ? ` · ${n.ambito}` : ""}: ${titular(n)}`;
        a.setAttribute("aria-label", descripcion);
        a.setAttribute("title", titular(n));
        const mostrar = () => { pista.textContent = descripcion; };
        a.addEventListener("mouseenter", mostrar);
        a.addEventListener("focus", mostrar);
        return a;
      });
    return el("section", { clase: "mosaico-tema" },
      el("h3", { clase: "mosaico-titulo" }, iconoTema(tema), tema, el("span", { clase: "mosaico-cuenta", texto: ` ${delTema.length}` })),
      el("div", { clase: "mosaico-teselas" }, ...teselas));
  }));
}

// ---------- La semana en datos ----------

function pintarPiezas() {
  const piezas = edicionActual().piezas || [];
  const porId = Object.fromEntries(estado.normas.map((n) => [n.id, n]));
  $("piezas-seccion").hidden = piezas.length === 0;
  const detalle = $("pieza-detalle");
  const botones = piezas.map((p, i) => {
    const boton = el("button", {
      type: "button", clase: p.votaciones ? "pieza pieza-congreso" : "pieza", "aria-expanded": "false", "aria-controls": "pieza-detalle",
    }, el("span", { clase: "pieza-cifra", texto: miles(p.cifra) }), el("span", { clase: "pieza-texto", texto: p.texto }));
    boton.addEventListener("click", () => abrirPieza(i));
    return boton;
  });
  const abrirPieza = (i) => {
    const abierta = explorar.piezaAbierta === i ? null : i;
    explorar.piezaAbierta = abierta;
    botones.forEach((b, k) => b.setAttribute("aria-expanded", String(k === abierta)));
    detalle.hidden = abierta === null;
    if (abierta === null) return;
    const p = piezas[abierta];
    const normas = p.ids.map((id) => porId[id]).filter(Boolean);
    // Decretos-ley votados esta semana pero publicados antes: enlace a su ficha, con la votación por grupos.
    const otras = (p.otras || []).map((o) => el("li", {}, el("a", {
      href: `#${o.id}`, clase: "titular-lista", onclick: (e) => { e.preventDefault(); abrirArticulo(o.id); },
      texto: `Real Decreto-ley ${o.rdl} (${o.resultado}): ${o.titulo}`,
    })));
    detalle.replaceChildren(
      el("p", { clase: "pieza-detalle-titulo", texto: `${miles(p.cifra)} ${p.texto}` }),
      normas.length || otras.length
        ? el("ul", {}, ...normas.map((n) => el("li", {}, enlaceNorma(n, "titular-lista", [titular(n)]))), ...otras)
        : el("p", { clase: "nota", texto: "No hay más detalle de estas normas." }));
  };
  explorar.piezaAbierta = null;
  detalle.hidden = true;
  $("piezas").replaceChildren(...botones);
}


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

function filtrarLista(clave, valor) {
  for (const k of Object.keys(explorar.filtros)) explorar.filtros[k] = "";
  explorar.filtros[clave] = valor;
  actualizar();
  $("normas").scrollIntoView({ behavior: "smooth", block: "start" });
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
    pintarEmbudo();
    pintarMosaico(estado.normas);
    pintarPiezas();
    pintarGrafico();
    pintarTablaDias();
    rellenarFiltros();
    actualizar();
  },
};
