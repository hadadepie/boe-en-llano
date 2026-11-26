/* El BOE en llano — el dinero de las comunidades autónomas (dinero.html, datos/autonomicas.json de
   boe.autonomicas): de cuánto disponen, a qué lo dedican y cuánto gastaron de verdad. Usa lo común de app.js. */

"use strict";

const ccMill = (x) => Math.round(x).toLocaleString("es-ES", { useGrouping: "always" });
const ccPct = (parte, total) => (total ? `${(100 * parte / total).toLocaleString("es-ES", { maximumFractionDigits: 0 })} %` : "—");
const ccHab = (millones, personas) => Math.round(millones * 1e6 / personas).toLocaleString("es-ES", { useGrouping: "always" });

// Capítulos agrupados para «¿De cuánto dispone?» (clasificación económica de ingresos).
const GRUPOS_INGRESOS = [
  ["Impuestos", ["1", "2"], "Impuestos directos e indirectos: los cedidos por el Estado (parte del IRPF, el IVA y los especiales) y los propios"],
  ["Transferencias recibidas", ["4", "7"], "Del sistema de financiación, del Estado con destino fijado y de la Unión Europea"],
  ["Tasas, rentas y ventas", ["3", "5", "6"], "Tasas, precios públicos, ingresos del patrimonio y venta de inversiones"],
  ["Préstamos devueltos", ["8"], "Activos financieros: préstamos que le devuelven y venta de participaciones"],
  ["Deuda nueva", ["9"], "Pasivos financieros: lo que pide prestado"],
];
const CAPITULOS_GASTO = {
  "1": "Sueldos del personal", "2": "Compras de bienes y servicios", "3": "Intereses de la deuda",
  "4": "Transferencias corrientes", "5": "Fondo para imprevistos", "6": "Inversiones",
  "7": "Transferencias de capital", "8": "Préstamos y participaciones", "9": "Devolución de deuda",
};

let comunidadElegida = "00";

// Las claves «10»…«17» parecen números y JavaScript las pone delante: se ordena por nombre, el total primero.
const ordenComunidades = (D) => Object.entries(D.comunidades)
  .sort(([a, x], [b, y]) => (a !== "00") - (b !== "00") || x.nombre.localeCompare(y.nombre, "es"));

function pintarComunidades(D) {
  $("comunidades").hidden = !D;
  if (!D) return;
  const AP = D.año_presupuesto, AL = D.año_liquidacion, T = D.comunidades["00"];
  const tp = T.presupuestado[AP], tg = T.gastado[AL], tl = T.presupuestado[AL];
  const inv = tg.gastos["6"];
  $("lectura-comunidades").textContent =
    `Las 17 comunidades autónomas presupuestan para ${AP} ${ccMill(tp.total)} millones de euros. Lo que más: sanidad, ${ccMill(tp.politicas["31"])} millones (${ccPct(tp.politicas["31"], tp.total)}), y educación, ${ccMill(tp.politicas["32"])} (${ccPct(tp.politicas["32"], tp.total)}). ` +
    `Lo gastado de verdad se conoce con unos dos años de retraso: en ${AL} gastaron ${ccMill(tg.total)} millones, el ${ccPct(tg.total, tl.total)} de lo presupuestado al empezar el año. ` +
    `En sanidad gastaron el ${ccPct(tg.politicas["31"], tl.politicas["31"])} de lo presupuestado; en inversiones, el ${ccPct(inv[2], inv[0])}.`;

  const sel = $("elegir-comunidad");
  if (!sel.options.length) {
    for (const [c, x] of ordenComunidades(D)) sel.append(el("option", { value: c, texto: x.nombre }));
    sel.onchange = () => { comunidadElegida = sel.value; pintarComunidad(D); };
  }
  sel.value = comunidadElegida;
  pintarComunidad(D);
  pintarComparacion(D);
  const pr = (a) => (D.prorrogados[a] || []).map((c) => D.comunidades[c].nombre);
  $("comunidades-nota").textContent =
    `Presupuestos iniciales y liquidaciones (obligaciones reconocidas: lo que la comunidad se compromete a pagar por lo ya recibido) de cada comunidad, consolidados: administración general, organismos y entes con presupuesto limitativo, sin contar lo que se pasan entre ellos. ` +
    `Con presupuesto prorrogado: en ${AP}, ${lista(pr(AP)) || "ninguna"}; en ${AL}, ${lista(pr(AL)) || "ninguna"}. ` +
    "Lo que cada comunidad incluye en una política (por ejemplo, sanidad) no es idéntico en todas: las diferencias pequeñas no significan mucho. " +
    "Navarra y el País Vasco tienen régimen foral: recaudan casi todos sus impuestos y pagan al Estado una aportación o un cupo, por eso su total no se compara con el de las demás. " +
    "Ceuta y Melilla no están: Hacienda no publica sus datos aquí y su sanidad y su educación las gestiona el Estado. " +
    `Por habitante: población a 1 de enero de cada año (INE, Estadística Continua de Población). Datos: ${D.fuente.organismo}.`;
}

function pintarComunidad(D) {
  const AP = D.año_presupuesto, AL = D.año_liquidacion, C = D.comunidades[comunidadElegida];
  const p = C.presupuestado[AP], pl = C.presupuestado[AL], g = C.gastado[AL], hab = C.poblacion[AP], habL = C.poblacion[AL];
  const foral = D.forales.includes(comunidadElegida);

  // ¿De cuánto dispone?
  const ingresos = GRUPOS_INGRESOS.map(([nombre, caps, detalle]) => ({
    nombre, detalle,
    previsto: caps.reduce((s, k) => s + (p.ingresos[k] || 0), 0),
    entrado: caps.reduce((s, k) => s + (g.ingresos[k] ? g.ingresos[k][2] : 0), 0),
  }));
  const totalIng = ingresos.reduce((s, x) => s + x.previsto, 0), totalEnt = ingresos.reduce((s, x) => s + x.entrado, 0);
  $("cc-dispone").textContent =
    `${C.nombre === D.comunidades["00"].nombre ? "Entre todas prevén" : "Prevé"} ingresar en ${AP} ${ccMill(totalIng)} millones de euros${foral ? "" : `, ${ccHab(totalIng, hab)} € por habitante`}; ` +
    `el ${ccPct(ingresos[4].previsto, totalIng)} es deuda nueva. En ${AL} entraron de verdad ${ccMill(totalEnt)} millones.` +
    (foral ? " Régimen foral: recauda casi todos sus impuestos y paga al Estado una parte, así que estas cifras no se comparan con las de las demás." : "") +
    (ingresos[1].previsto < 0 || ingresos[1].entrado < 0
      ? " Las transferencias salen negativas: en el sistema de financiación, esta comunidad aporta a los fondos comunes (sobre todo al Fondo de Garantía de los Servicios Públicos Fundamentales) más de lo que recibe de ellos, y Hacienda lo anota como un ingreso negativo. Por eso los porcentajes de las demás filas pueden pasar del 100 %."
      : "");
  $("tabla-cc-ingresos").replaceChildren(
    el("thead", {}, el("tr", {}, ...["De dónde sale", `Previsto ${AP}`, "%", `Entró en ${AL}`].map((t, i) => el("th", { texto: t, clase: i ? "numero" : "" })))),
    el("tbody", {}, ...ingresos.map((x) => el("tr", { title: x.detalle },
      el("td", { texto: x.nombre }), el("td", { clase: "numero", texto: ccMill(x.previsto) }),
      el("td", { clase: "numero", texto: ccPct(x.previsto, totalIng) }), el("td", { clase: "numero", texto: ccMill(x.entrado) })))));

  // ¿A qué lo dedica? (por políticas, presupuestado y gastado)
  const codigos = Object.keys(D.politicas).filter((k) => p.politicas[k] || g.politicas[k])
    .sort((a, b) => (p.politicas[b] || 0) - (p.politicas[a] || 0));
  const s = p.politicas["31"] || 0, e = p.politicas["32"] || 0;
  $("cc-dedica").textContent =
    `En ${AP}: sanidad, ${ccMill(s)} millones (${ccHab(s, hab)} € por habitante); educación, ${ccMill(e)} millones (${ccHab(e, hab)} € por habitante). ` +
    `El gráfico compara lo presupuestado y lo gastado en ${AL} en las políticas con más gasto; las cifras de todas están en la tabla.`;
  $("tabla-cc-politicas").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Política de gasto", `${AP}, millones`, "€ por habitante", `${AL}, presupuestado`, `${AL}, gastado`, "Gastado / presupuestado"]
      .map((t, i) => el("th", { texto: t, clase: i ? "numero" : "" })))),
    el("tbody", {}, ...codigos.map((k) => el("tr", {},
      el("td", { texto: D.politicas[k] }),
      el("td", { clase: "numero", texto: p.politicas[k] ? ccMill(p.politicas[k]) : "—" }),
      el("td", { clase: "numero", texto: p.politicas[k] ? ccHab(p.politicas[k], hab) : "—" }),
      el("td", { clase: "numero", texto: pl.politicas[k] ? ccMill(pl.politicas[k]) : "—" }),
      el("td", { clase: "numero", texto: g.politicas[k] ? ccMill(g.politicas[k]) : "—" }),
      el("td", { clase: "numero", texto: pl.politicas[k] && g.politicas[k] ? ccPct(g.politicas[k], pl.politicas[k]) : "—" })))),
    el("tfoot", {}, el("tr", {}, el("th", { texto: "Total" }), el("th", { clase: "numero", texto: ccMill(p.total) }),
      el("th", { clase: "numero", texto: foral ? "—" : ccHab(p.total, hab) }), el("th", { clase: "numero", texto: ccMill(pl.total) }),
      el("th", { clase: "numero", texto: ccMill(g.total) }), el("th", { clase: "numero", texto: ccPct(g.total, pl.total) }))));

  // ¿Cuánto gastó de verdad? (por capítulos, presupuesto inicial, definitivo y obligaciones)
  const caps = Object.keys(CAPITULOS_GASTO).filter((k) => g.gastos[k] && (g.gastos[k][0] || g.gastos[k][2]));
  const inv = g.gastos["6"] || [0, 0, 0, 0];
  $("cc-gasto").textContent =
    `En ${AL} presupuestó al empezar el año ${ccMill(pl.total)} millones, el presupuesto se amplió durante el año hasta ${ccMill(Object.values(g.gastos).reduce((t, v) => t + v[1], 0))} y gastó ${ccMill(g.total)} ` +
    `(${ccHab(g.total, habL)} € por habitante${foral ? ", no comparable por el régimen foral" : ""}). De las inversiones previstas se gastó el ${ccPct(inv[2], inv[0])}.`;
  $("tabla-cc-capitulos").replaceChildren(
    el("thead", {}, el("tr", {}, ...["En qué tipo de gasto", "Presupuesto inicial", "Presupuesto final", "Gastado", "Gastado / inicial"]
      .map((t, i) => el("th", { texto: t, clase: i ? "numero" : "" })))),
    el("tbody", {}, ...caps.map((k) => el("tr", {},
      el("td", { texto: CAPITULOS_GASTO[k] }), el("td", { clase: "numero", texto: ccMill(g.gastos[k][0]) }),
      el("td", { clase: "numero", texto: ccMill(g.gastos[k][1]) }), el("td", { clase: "numero", texto: ccMill(g.gastos[k][2]) }),
      el("td", { clase: "numero", texto: ccPct(g.gastos[k][2], g.gastos[k][0]) })))));
  graficosComunidad(D, C, ingresos);
  graficoComparacion(D);
  pintarQuienPresta(D);
}

function pintarComparacion(D) {
  const AP = D.año_presupuesto, AL = D.año_liquidacion;
  const filas = ordenComunidades(D).filter(([c]) => c !== "00");
  const cab = ["Comunidad", `Sanidad ${AP}`, `Educación ${AP}`, `Servicios sociales ${AP}`, `Deuda ${AP}`, `Sanidad gastada ${AL}`, `Sanidad: gastado / presupuestado ${AL}`];
  const fila = (c, x, cabecera) => {
    const p = x.presupuestado[AP].politicas, gl = x.gastado[AL].politicas, pl = x.presupuestado[AL].politicas;
    const h = x.poblacion[AP], hl = x.poblacion[AL];
    const marca = [(D.prorrogados[AP] || []).includes(c) ? "*" : "", (D.prorrogados[AL] || []).includes(c) ? "†" : ""].join("");
    const celda = cabecera ? "th" : "td";
    return el("tr", {}, el(celda, { texto: x.nombre + (marca ? ` ${marca}` : "") }),
      ...["31", "32", "23", "95"].map((k) => el(celda, { clase: "numero", texto: p[k] ? ccHab(p[k], h) : "—" })),
      el(celda, { clase: "numero", texto: gl["31"] ? ccHab(gl["31"], hl) : "—" }),
      el(celda, { clase: "numero", texto: ccPct(gl["31"], pl["31"]) }));
  };
  $("tabla-cc-comparar").replaceChildren(
    el("thead", {}, el("tr", {}, ...cab.map((t, i) => el("th", { texto: t, clase: i ? "numero" : "" })))),
    el("tbody", {}, ...filas.map(([c, x]) => fila(c, x))),
    el("tfoot", {}, fila("00", D.comunidades["00"], true)));
  $("cc-comparar-nota").textContent =
    `Euros por habitante. * Presupuesto de ${AP} prorrogado. † Presupuesto de ${AL} prorrogado.`;
  graficoComparacion(D);
}

let autonomicasCargadas;
async function cargarAutonomicas() {
  if (autonomicasCargadas === undefined) {
    try { autonomicasCargadas = await cargarJson("autonomicas.json"); } catch (e) { autonomicasCargadas = null; }
  }
  return autonomicasCargadas;
}

// --- Gráficos (Chart.js, como los demás de la página; las tablas quedan en «Ver las cifras») ---

// Etiqueta larga del eje en varias líneas, para que quepa en el móvil.
function ccLineas(texto, max = 22) {
  const lineas = [];
  for (const palabra of texto.split(" ")) {
    const ultima = lineas[lineas.length - 1];
    if (ultima && (ultima + " " + palabra).length <= max) lineas[lineas.length - 1] = ultima + " " + palabra;
    else lineas.push(palabra);
  }
  return lineas;
}

function ccBarras(clave, lienzo, etiquetas, series, unidad, extra = {}) {
  if (!window.Chart) return;
  nuevoGrafico(clave, lienzo, {
    type: "bar",
    data: { labels: etiquetas.map((e) => ccLineas(e)),
      datasets: series.map((s) => ({ label: s.nombre, data: s.datos, backgroundColor: s.colores || variable(s.color),
        borderColor: variable("--superficie"), borderWidth: 1, borderRadius: 4, maxBarThickness: 22 })) },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { ...ejeValores(), ticks: { color: variable("--tinta-2"), callback: (v) => ccMill(v) } }, y: ejeNombres() },
      plugins: {
        legend: series.length > 1 ? leyendaArriba() : { display: false },
        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${ccMill(c.parsed.x)} ${unidad}`, ...(extra.pie ? { footer: extra.pie } : {}) } },
      },
    },
  });
}

function graficosComunidad(D, C, ingresos) {
  const AP = D.año_presupuesto, AL = D.año_liquidacion, pl = C.presupuestado[AL], g = C.gastado[AL];
  ccBarras("cc-ingresos", $("grafico-cc-ingresos"), ingresos.map((x) => x.nombre),
    [{ nombre: `Previsto para ${AP}`, datos: ingresos.map((x) => x.previsto), color: "--s1" }], "millones de euros");

  // Las 8 políticas con más gasto y el resto junto; presupuestado (gris, la referencia) y gastado (azul).
  const codigos = Object.keys(D.politicas).filter((k) => pl.politicas[k] || g.politicas[k])
    .sort((a, b) => (g.politicas[b] || 0) - (g.politicas[a] || 0));
  const grandes = codigos.slice(0, 8), resto = codigos.slice(8);
  const suma = (obj, ks) => ks.reduce((s, k) => s + (obj[k] || 0), 0);
  const etiquetas = [...grandes.map((k) => D.politicas[k]), `Otras ${resto.length} políticas`];
  ccBarras("cc-politicas", $("grafico-cc-politicas"), etiquetas, [
    { nombre: `Presupuestado ${AL}`, datos: [...grandes.map((k) => pl.politicas[k] || 0), suma(pl.politicas, resto)], color: "--voto-abst" },
    { nombre: `Gastado ${AL}`, datos: [...grandes.map((k) => g.politicas[k] || 0), suma(g.politicas, resto)], color: "--s1" },
  ], "millones de euros", { pie: (items) => {
    const i = items[0].dataIndex, ks = i < grandes.length ? [grandes[i]] : resto;
    const pre = suma(pl.politicas, ks), gas = suma(g.politicas, ks);
    return pre ? `Gastado: el ${ccPct(gas, pre)} de lo presupuestado` : "";
  } });

  const caps = Object.keys(CAPITULOS_GASTO).filter((k) => k !== "5" && g.gastos[k] && (g.gastos[k][0] || g.gastos[k][2]));
  ccBarras("cc-capitulos", $("grafico-cc-capitulos"), caps.map((k) => CAPITULOS_GASTO[k]), [
    { nombre: `Presupuesto inicial ${AL}`, datos: caps.map((k) => g.gastos[k][0]), color: "--voto-abst" },
    { nombre: `Gastado ${AL}`, datos: caps.map((k) => g.gastos[k][2]), color: "--s1" },
  ], "millones de euros", { pie: (items) => {
    const v = g.gastos[caps[items[0].dataIndex]];
    return `Gastado: el ${ccPct(v[2], v[0])} del presupuesto inicial`;
  } });
}

const POLITICAS_COMPARAR = { "31": "Sanidad", "32": "Educación", "23": "Servicios sociales", "95": "Deuda" };
let politicaComparada = "31";

function graficoComparacion(D) {
  const AP = D.año_presupuesto, k = politicaComparada;
  const filas = ordenComunidades(D)
    .map(([c, x]) => ({ c, nombre: c === "00" ? "Media de las 17" : x.nombre, valor: (x.presupuestado[AP].politicas[k] || 0) * 1e6 / x.poblacion[AP] }))
    .sort((a, b) => b.valor - a.valor);
  // La comunidad elegida arriba se resalta; la media, en tinta; las demás, en gris.
  const color = (f) => variable(f.c === "00" ? "--tinta" : f.c === comunidadElegida ? "--s1" : "--voto-abst");
  ccBarras("cc-comparar", $("grafico-cc-comparar"), filas.map((f) => f.nombre),
    [{ nombre: `${POLITICAS_COMPARAR[k]} ${AP}`, datos: filas.map((f) => f.valor), colores: filas.map(color) }], "€ por habitante");
  for (const [codigo] of Object.entries(POLITICAS_COMPARAR)) {
    const b = $(`cc-vista-${codigo}`);
    b.setAttribute("aria-pressed", String(codigo === k));
    b.onclick = () => { politicaComparada = codigo; graficoComparacion(D); };
  }
}

// --- ¿Quién presta el servicio? (sanidad y educación: estadísticas de los ministerios; el resto: Hacienda) ---

const QUIEN_PRESTA = {
  sanidad: { titulo: "Sanidad", destacar: "conciertos", partes: [
    ["personal", "Personal propio", "--s1"], ["compras", "Compras y suministros", "--s4"],
    ["conciertos", "Conciertos con centros ajenos", "--s2"], ["otros", "Otros (recetas, inversiones…)", "--voto-abst"]] },
  educacion: { titulo: "Educación", destacar: "privada", partes: [
    ["personal", "Personal propio", "--s1"], ["compras", "Compras y suministros", "--s4"],
    ["privada", "A centros privados (conciertos y subvenciones)", "--s2"], ["otras_transferencias", "Otras transferencias", "--s7"],
    ["inversiones", "Inversiones", "--s3"], ["otros", "Otros", "--voto-abst"]] },
  "23": { titulo: "Servicios sociales", destacar: "transferencias" },
  "45": { titulo: "Infraestructuras", destacar: "inversiones" },
};
const PARTES_HACIENDA = [["personal", "Personal propio", "--s1"], ["compras", "Compras de bienes y servicios", "--s4"],
  ["transferencias", "Transferencias (a familias, entidades y otras administraciones)", "--s7"], ["inversiones", "Inversiones", "--s3"], ["otros", "Otros", "--voto-abst"]];
let vistaQuien = "sanidad";

// % de cada parte para una comunidad, según la fuente de la vista.
function repartoQuien(D, vista, c) {
  if (vista === "sanidad") return D.quien_presta.sanidad.comunidades[c];
  if (vista === "educacion") {
    const x = D.quien_presta.educacion.comunidades[c], t = Object.values(x).reduce((s, v) => s + v, 0);
    return Object.fromEntries(Object.entries(x).map(([k, v]) => [k, 100 * v / t]));
  }
  const v = D.comunidades[c].gastado[D.año_liquidacion].capitulos_politica[vista];
  if (!v) return null;
  const t = v.reduce((s, x) => s + x, 0);
  const r = { personal: v[0], compras: v[1], transferencias: v[3] + v[6], inversiones: v[5], otros: v[2] + v[4] };
  return Object.fromEntries(Object.entries(r).map(([k, x]) => [k, t ? 100 * x / t : 0]));
}

function pintarQuienPresta(D) {
  const V = QUIEN_PRESTA[vistaQuien], partes = V.partes || PARTES_HACIENDA, AL = D.año_liquidacion;
  const filas = ordenComunidades(D)
    .map(([c, x]) => ({ c, nombre: c === "00" ? (vistaQuien === "sanidad" ? "España (17 comunidades)" : "Total de las 17") : x.nombre, r: repartoQuien(D, vistaQuien, c) }))
    .filter((f) => f.r).sort((a, b) => (b.r[V.destacar] || 0) - (a.r[V.destacar] || 0));
  const fmt = (v) => `${v.toLocaleString("es-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} %`;
  const resaltada = (i) => filas[i] && (filas[i].c === comunidadElegida || filas[i].c === "00");
  if (window.Chart) {
    nuevoGrafico("cc-quien", $("grafico-cc-quien"), {
      type: "bar",
      data: { labels: filas.map((f) => (f.c === comunidadElegida && f.c !== "00" ? `▸ ${f.nombre}` : f.nombre)),
        datasets: partes.map(([k, nombre, color]) => ({ label: nombre, data: filas.map((f) => f.r[k] || 0), backgroundColor: variable(color),
          borderColor: variable("--superficie"), borderWidth: 1, maxBarThickness: 22 })) },
      options: {
        indexAxis: "y", responsive: true, maintainAspectRatio: false,
        scales: { x: { ...ejeValores(), stacked: true, max: 100, ticks: { color: variable("--tinta-2"), callback: (v) => `${v} %` } },
          y: { ...ejeNombres(), stacked: true, ticks: { color: variable("--tinta"), autoSkip: false, font: (ctx) => ({ weight: resaltada(ctx.index) ? "bold" : "normal" }) } } },
        plugins: { legend: leyendaArriba(), tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${fmt(c.parsed.x)}` } } },
      },
    });
  }
  for (const k of Object.keys(QUIEN_PRESTA)) {
    const b = $(`cc-quien-${k}`);
    b.setAttribute("aria-pressed", String(k === vistaQuien));
    b.onclick = () => { vistaQuien = k; pintarQuienPresta(D); };
  }
  const elegida = filas.find((f) => f.c === comunidadElegida), media = filas.find((f) => f.c === "00");
  const parte = partes.find(([k]) => k === V.destacar)[1].toLowerCase();
  $("cc-quien-texto").textContent = elegida && elegida.c !== "00"
    ? `En ${elegida.nombre}, «${parte}» es el ${fmt(elegida.r[V.destacar])} del gasto; en el conjunto de las 17, el ${fmt(media.r[V.destacar])}.`
    : `En el conjunto de las 17, «${parte}» es el ${fmt(media.r[V.destacar])} del gasto. Elige una comunidad arriba para verla marcada.`;
  const S = D.quien_presta.sanidad, E = D.quien_presta.educacion;
  const notas = {
    sanidad: `Gasto sanitario público gestionado por cada comunidad en ${S.año}, en porcentaje (${S.fuente}). Los conciertos son la atención que paga la sanidad pública y prestan centros que no son suyos: hospitales, pruebas, rehabilitación, transporte sanitario… «Concierto» no quiere decir siempre empresa con ánimo de lucro: en Cataluña, buena parte de la red hospitalaria pública son consorcios y fundaciones concertados. Las compras también van a empresas (medicamentos de hospital, material, limpieza), pero para centros públicos. Las recetas se pagan a farmacias y van en «Otros». No incluye los cuidados de larga duración en residencias.`,
    educacion: `Gasto de la consejería de educación de cada comunidad en ${E.año} (${E.fuente}). «A centros privados» son los conciertos y subvenciones a centros educativos de titularidad privada. «Otras transferencias» incluye, por ejemplo, lo que se pasa a universidades públicas, becas o ayuntamientos. No coincide exactamente con la política de educación de Hacienda: son fuentes y ámbitos distintos.`,
    "23": `Lo gastado en ${AL} en la política de servicios sociales, por tipo de gasto (liquidación de Hacienda). No hay una estadística oficial que separe la gestión directa de la concertada: las transferencias mezclan prestaciones a familias, ayudas a entidades sociales y plazas concertadas, y las compras incluyen contratos de servicios.`,
    "45": `Lo gastado en ${AL} en la política de infraestructuras, por tipo de gasto (liquidación de Hacienda). Las inversiones son sobre todo obras y equipos contratados a empresas; Hacienda no publica a cuáles (eso está en los contratos).`,
  };
  $("cc-quien-nota").textContent = notas[vistaQuien];
}
