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
    `La tabla compara además lo presupuestado y lo gastado en ${AL}, política a política.`;
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
}

let autonomicasCargadas;
async function cargarAutonomicas() {
  if (autonomicasCargadas === undefined) {
    try { autonomicasCargadas = await cargarJson("autonomicas.json"); } catch (e) { autonomicasCargadas = null; }
  }
  return autonomicasCargadas;
}
