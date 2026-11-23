/* El BOE en llano — página de datos (datos.html): gráfico por día, matriz
   tema × a quién afecta, votaciones de la semana, lista filtrable, reales
   decretos-ley de la legislatura y «Cómo se ha hecho». Usa lo común de app.js. */

"use strict";

const explorar = {
  filtros: { fecha: "", tema: "", impacto: "", ambito: "" },
  grafico: null,
  graficoTemas: null,
  graficoTamano: null,
};

function luminancia(hex) {
  const c = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(c.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

// ---------- Frases de lectura ----------

function nombreCorto(seccion) {
  const nombres = { I: "normas generales", "II.A": "nombramientos", "II.B": "oposiciones y concursos",
    III: "otras disposiciones", IV: "decisiones de justicia", V: "anuncios" };
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

function fraseMatriz(base) {
  if (!base.length) return "No hay normas con estos filtros.";
  const porImpacto = (i) => base.filter((n) => n.impacto === i).length;
  const directas = porImpacto("Directo");
  const internas = porImpacto("Técnico");
  const temas = {};
  for (const n of base) temas[n.tema] = (temas[n.tema] || 0) + 1;
  const [temaTop, nTop] = Object.entries(temas).sort((a, b) => b[1] - a[1])[0];
  return [
    internas > base.length / 2
      ? `Más de la mitad de estas ${base.length} normas (${internas}) son de gestión interna.`
      : `De estas ${base.length} normas, ${internas} son de gestión interna.`,
    directas === 0 ? "Ninguna parece afectarte directamente."
      : directas === 1 ? "1 te puede afectar a ti." : `${directas} te pueden afectar a ti.`,
    `El tema más frecuente es «${temaTop}» (${nTop}).`,
  ].join(" ");
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
    (ignorar.includes("ambito") || !f.ambito || n.ambito === f.ambito));
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
}

function actualizar() {
  for (const [clave, valor] of Object.entries(explorar.filtros)) $(`f-${clave}`).value = valor;
  pintarMatriz();
  pintarLista();
}

// ---------- Matriz tema × impacto ----------

function pintarLeyendaImpacto() {
  // Se ve solo en pantallas estrechas, donde las cabeceras de la matriz no caben.
  $("leyenda-impacto").replaceChildren(...estado.indice.impactos.flatMap((i) => [
    el("dt", { texto: nombreImpacto(i) }),
    el("dd", { texto: IMPACTO[i] ? `${IMPACTO[i].explicacion} (${IMPACTO[i].ejemplo})` : "" }),
  ]));
}

function pintarMatriz() {
  const { temas, impactos } = estado.indice;
  const base = normasFiltradas({ ignorar: ["tema", "impacto"] }); // respeta día y ámbito
  $("lectura-matriz").textContent = fraseMatriz(base);
  const cuenta = (t, i) => base.filter((n) => n.tema === t && n.impacto === i).length;
  const maximo = Math.max(1, ...temas.flatMap((t) => impactos.map((i) => cuenta(t, i))));

  const celda = (tema, impacto) => {
    const n = cuenta(tema, impacto);
    const paso = n === 0 ? 0 : Math.max(1, Math.ceil((n / maximo) * 6));
    const fondo = variable(`--m${paso}`);
    const activa = explorar.filtros.tema === tema && explorar.filtros.impacto === impacto;
    const boton = el("button", {
      type: "button",
      clase: "celda" + (paso > 0 && luminancia(fondo) < 0.3 ? " clara" : ""),
      "aria-pressed": String(activa),
      "aria-label": `${n} ${n === 1 ? "norma" : "normas"} de ${tema} · ${nombreImpacto(impacto)}`,
      title: `${tema} · ${nombreImpacto(impacto)}: ${n}`,
      texto: String(n),
      onclick: () => {
        explorar.filtros.tema = activa ? "" : tema;
        explorar.filtros.impacto = activa ? "" : impacto;
        actualizar();
        if (!activa) $("normas").scrollIntoView({ behavior: "smooth", block: "start" });
      },
    });
    boton.style.background = fondo;
    if (n === 0) boton.disabled = true;
    return el("td", {}, boton);
  };

  $("matriz").replaceChildren(
    el("thead", {}, el("tr", {},
      el("th", { scope: "col", texto: "Tema" }),
      ...impactos.map((i) => el("th", { scope: "col", clase: "col-impacto" },
        el("span", { clase: "col-nombre", texto: nombreImpacto(i) }),
        el("span", { clase: "col-explica", texto: IMPACTO[i] ? IMPACTO[i].explicacion : "" }),
        el("span", { clase: "col-ejemplo", texto: IMPACTO[i] ? IMPACTO[i].ejemplo : "" }))),
      el("th", { scope: "col", texto: "Total" }))),
    el("tbody", {}, ...temas.map((t) => el("tr", {},
      el("th", { scope: "row", texto: t }),
      ...impactos.map((i) => celda(t, i)),
      el("td", { clase: "total", texto: String(base.filter((n) => n.tema === t).length) }),
    ))),
  );
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

// ---------- Votaciones de la semana ----------

function pintarVotacionesSemana() {
  const votaciones = edicionActual().votaciones || [];
  $("bloque-votaciones").hidden = votaciones.length === 0;
  $("votaciones-semana").replaceChildren(...votaciones.map((v) => {
    const c = v.convalidacion;
    const enlace = v.ids.length
      ? el("a", { href: `#${v.ids[0]}`, onclick: (e) => { e.preventDefault(); abrirArticulo(v.ids[0]); }, texto: "Ver la ficha" })
      : null;
    return el("article", { clase: "votacion-semana" },
      el("p", { clase: `resultado-votacion ${c.resultado}`, texto: `Real Decreto-ley ${v.rdl}: ${c.resultado.toUpperCase()}` }),
      el("p", { clase: "titulo-votacion", texto: v.titulo }),
      barraVotos(votosTotales(c.totales), { etiqueta: `Real Decreto-ley ${v.rdl}` }),
      el("p", { clase: "nota" }, resumenVotacion(c), " ", enlace),
      c.solo_totales ? el("p", { clase: "nota", texto: c.nota || "" })
        : el("details", {}, el("summary", { texto: "Ver el voto por grupos" }), leyendaVotos(), bloqueGrupos(c)));
  }));
}

// ---------- Legislatura ----------

function pintarLegislatura() {
  const L = estado.indice.legislatura;
  $("legislatura").hidden = !L;
  if (!L) return;
  const r = L.resumen;
  $("legislatura-resumen").textContent =
    `En la ${L.legislatura} legislatura se han convalidado ${r.convalidado} reales decretos-ley y derogado ${r.derogado}` +
    (r.empates ? ` (${r.empates === 1 ? "uno de ellos" : `${r.empates} de ellos`} por empate)` : "") + `. ` +
    `El Pleno votó ${r.pleno}; la Diputación Permanente, ${r.diputacion_permanente} que constan en el BOE. ` +
    `De otros ${r["sin votación publicada"]} no hay votación publicada todavía (pendientes o votados por la Diputación Permanente sin resolución en nuestros datos).`;
  const filas = L.decretos_ley.map((x) => el("tr", { clase: x.resultado === "derogado" ? "fila-derogado" : "" },
    el("td", { texto: x.rdl }),
    el("td", { clase: "celda-titular" }, x.titular ? enlaceBoe(x.id_boe, x.titular) : "—"),
    el("td", { texto: x.tema || "—" }),
    el("td", { texto: x.normas_modificadas != null ? String(x.normas_modificadas) : "—" }),
    el("td", { texto: x.fecha ? `${fechaCorta(x.fecha)} ${x.fecha.slice(0, 4)}` : x.organo === "Diputación Permanente" ? "Dip. Permanente" : "—" }),
    el("td", { texto: x.empate ? "derogado (empate)" : x.resultado }),
    el("td", { texto: x.afavor != null ? `${x.afavor} / ${x.enContra} / ${x.abstenciones}` : "—" }),
    el("td", { texto: x.margen != null ? (x.margen > 0 ? `+${x.margen}` : String(x.margen)) : "—" })));
  $("tabla-legislatura").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Real decreto-ley", "De qué trata", "Tema", "Normas que modifica", "Votación", "Resultado", "Sí / No / Abst.", "Margen"]
      .map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...filas));
  $("legislatura-nota").textContent = `${L.nota} Consultado el ${fechaMedia(L.consultado)} (${L.dias_consultados} días laborables revisados). ` +
    "Tema, título y normas que modifica: documento oficial de cada real decreto-ley en el BOE.";
  pintarTemasRdl(L);
  pintarTamanoRdl(L);
}

// Colores por resultado (los de sí y no de las votaciones; nunca colores de partido).
const COLORES_RESULTADO = { convalidado: "--voto-si", derogado: "--voto-no", "sin votación publicada": "--voto-abst" };
const NOMBRE_RESULTADO = { convalidado: "Convalidados", derogado: "Derogados", "sin votación publicada": "Sin votación publicada" };

function pintarTemasRdl(L) {
  const decretos = L.decretos_ley.filter((x) => x.tema);
  const caja = $("grafico-temas-rdl").closest(".grafico");
  if (!decretos.length) { caja.hidden = true; return; }
  const porTema = {};
  for (const x of decretos) {
    porTema[x.tema] = porTema[x.tema] || { total: 0, convalidado: 0, derogado: 0, "sin votación publicada": 0 };
    porTema[x.tema].total += 1;
    porTema[x.tema][x.resultado] += 1;
  }
  const temas = Object.keys(porTema).sort((a, b) => porTema[b].total - porTema[a].total);
  // Lectura: el tema con más decretos-ley y dónde más se derogaron (sobre los votados, con al menos 3).
  const votados = (t) => porTema[t].convalidado + porTema[t].derogado;
  const masDerogados = temas.filter((t) => votados(t) >= 3)
    .sort((a, b) => porTema[b].derogado / votados(b) - porTema[a].derogado / votados(a))[0];
  $("lectura-temas-rdl").textContent = `El tema con más reales decretos-ley es «${temas[0]}» (${porTema[temas[0]].total}).` +
    (masDerogados && porTema[masDerogados].derogado
      ? ` Donde más se derogaron, en proporción a los votados, es «${masDerogados}»: ${porTema[masDerogados].derogado} de ${votados(masDerogados)}.` : "");
  if (!window.Chart) return;
  if (explorar.graficoTemas) explorar.graficoTemas.destroy();
  // En pantallas estrechas, los nombres de tema largos se parten en líneas para que no se corten.
  const estrecho = caja.clientWidth < 520;
  const enLineas = (texto) => texto.split(" ").reduce((lineas, palabra) => {
    const ultima = lineas[lineas.length - 1];
    if (ultima && (ultima + " " + palabra).length <= 18) lineas[lineas.length - 1] = `${ultima} ${palabra}`;
    else lineas.push(palabra);
    return lineas;
  }, []);
  explorar.graficoTemas = new Chart($("grafico-temas-rdl"), {
    type: "bar",
    data: {
      labels: temas.map((t) => (estrecho ? enLineas(t) : t)),
      datasets: Object.keys(COLORES_RESULTADO).map((r) => ({
        label: NOMBRE_RESULTADO[r], data: temas.map((t) => porTema[t][r]),
        backgroundColor: variable(COLORES_RESULTADO[r]), maxBarThickness: 22,
      })),
    },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: {
        x: { stacked: true, beginAtZero: true, ticks: { precision: 0, color: variable("--tinta-2") }, grid: { color: variable("--linea") } },
        y: { stacked: true, ticks: { color: variable("--tinta"), autoSkip: false }, grid: { display: false } },
      },
      plugins: {
        legend: { position: "top", align: "start", labels: { color: variable("--tinta"), boxWidth: 12, boxHeight: 12 } },
        tooltip: { callbacks: { title: (items) => temas[items[0].dataIndex], footer: (items) => `Total: ${porTema[temas[items[0].dataIndex]].total}` } },
      },
    },
  });
}

const CORTE_TAMANO = 10; // solo para la frase de lectura; el gráfico muestra todos los tamaños

function pintarTamanoRdl(L) {
  const votados = L.decretos_ley.filter((x) => x.margen != null && x.normas_modificadas != null);
  const caja = $("grafico-tamano-rdl").closest(".grafico");
  if (!votados.length) { caja.hidden = true; return; }
  const grandes = votados.filter((x) => x.normas_modificadas >= CORTE_TAMANO);
  const resto = votados.filter((x) => x.normas_modificadas < CORTE_TAMANO);
  const derogados = (lista) => lista.filter((x) => x.resultado === "derogado").length;
  $("lectura-tamano-rdl").textContent =
    `De los ${grandes.length} reales decretos-ley votados en el Pleno que modifican ${CORTE_TAMANO} normas o más, ` +
    `se derogaron ${derogados(grandes)}; de los ${resto.length} que modifican menos, ${derogados(resto)}. ` +
    "Son pocos casos y el gráfico no explica por qué: solo muestra cómo se votaron.";
  if (!window.Chart) return;
  if (explorar.graficoTamano) explorar.graficoTamano.destroy();
  const puntos = (resultado) => votados.filter((x) => x.resultado === resultado)
    .map((x) => ({ x: x.normas_modificadas, y: x.margen, decreto: x }));
  explorar.graficoTamano = new Chart($("grafico-tamano-rdl"), {
    type: "scatter",
    data: {
      datasets: ["convalidado", "derogado"].map((r) => ({
        label: NOMBRE_RESULTADO[r], data: puntos(r),
        backgroundColor: variable(COLORES_RESULTADO[r]), pointRadius: 5, pointHoverRadius: 7,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { beginAtZero: true, title: { display: true, text: "Normas que modifica", color: variable("--tinta-2") },
          ticks: { precision: 0, color: variable("--tinta-2") }, grid: { color: variable("--linea") } },
        y: { title: { display: true, text: "Margen (sí − no)", color: variable("--tinta-2") },
          ticks: { color: variable("--tinta-2") },
          grid: { color: (c) => (c.tick && c.tick.value === 0 ? variable("--tinta-2") : variable("--linea")) } },
      },
      plugins: {
        legend: { position: "top", align: "start", labels: { color: variable("--tinta"), boxWidth: 12, boxHeight: 12 } },
        tooltip: {
          callbacks: {
            title: (items) => `Real Decreto-ley ${items[0].raw.decreto.rdl}`,
            label: (item) => {
              const d = item.raw.decreto;
              return [d.titular || "", `Modifica ${plural(d.normas_modificadas, "norma", "normas")} · ${d.afavor} sí, ${d.enContra} no (margen ${d.margen > 0 ? "+" : ""}${d.margen})`];
            },
          },
        },
      },
    },
  });
}

function pintarGlosario() {
  $("glosario").replaceChildren(...Object.values(GLOSARIO)
    .sort((a, b) => a[0].localeCompare(b[0], "es"))
    .flatMap(([t, d]) => [el("dt", { texto: t }), el("dd", { texto: d })]));
}

function pintarEstadoFichas() {
  const n = estado.indice.num_normas;
  const ok = estado.indice.resumen.fichas_verificadas;
  $("estado-fichas").textContent = ok === 0
    ? `Ahora mismo las ${n} fichas están pendientes.`
    : `Ahora mismo ${ok} de ${n} fichas tienen resumen automático experimental; el resto están pendientes porque el resumen no superó las comprobaciones.`;
}

window.PAGINA = {
  preparar() {
    for (const clave of Object.keys(explorar.filtros)) {
      $(`f-${clave}`).addEventListener("change", (e) => { explorar.filtros[clave] = e.target.value; actualizar(); });
    }
    $("filtros").addEventListener("reset", () => {
      setTimeout(() => { for (const k of Object.keys(explorar.filtros)) explorar.filtros[k] = ""; actualizar(); });
    });
    pintarLeyendaImpacto();
    pintarGlosario();
    pintarLegislatura();
    pintarEstadoFichas();
    // Repintar con los colores del modo claro/oscuro cuando cambie.
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { pintarGrafico(); pintarMatriz(); pintarLegislatura(); });
  },
  pintar() {
    for (const k of Object.keys(explorar.filtros)) explorar.filtros[k] = "";
    pintarGrafico();
    pintarTablaDias();
    pintarVotacionesSemana();
    rellenarFiltros();
    actualizar();
  },
};
