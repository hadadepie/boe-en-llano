/* El BOE en llano — el dinero público (dinero.html): gobernar sin Presupuestos (decretos-ley que
   conceden créditos, de datos/informe.json) y el dinero de los Presupuestos (Sankey con
   datos/presupuestos.json, de Hacienda). Estaba en «La legislatura» hasta el 25/11/2026.
   Usa lo común de app.js e informe.js. */

"use strict";

function pintarSinPresupuestos(I) {
  const S = I.sin_presupuestos;
  $("sin-presupuestos").hidden = !S;
  if (!S) return;
  const ultimo = S.por_anio[S.por_anio.length - 1];
  const conflicto = S.conflictos[0];
  $("lectura-sin-presupuestos").textContent =
    (S.leyes.length ? `En la legislatura se publicaron ${plural(S.leyes.length, "ley", "leyes")} de Presupuestos Generales del Estado. `
      : "En toda la legislatura no se publicó ninguna ley de Presupuestos Generales del Estado: siguieron prorrogados los de 2023. ") +
    (S.ordenes_elaboracion.length ? `Hacienda sí publicó ${S.ordenes_elaboracion.length === 1 ? "la orden" : `${S.ordenes_elaboracion.length} órdenes`} con las normas para elaborarlos (para ${lista(S.ordenes_elaboracion.map((o) => o.ejercicio))}). ` : "") +
    (conflicto ? `El ${fechaMedia(conflicto.fecha)}, el BOE publicó que el Tribunal Constitucional admitía a trámite el conflicto que el Senado planteó frente al Gobierno por lo que considera un incumplimiento del deber de presentar los Presupuestos de 2024, 2025 y 2026. ` : "") +
    `Sin Presupuestos nuevos, el gasto no previsto se aprueba norma a norma: ${miles(S.rdl_con_creditos)} de los ${miles(S.rdl)} reales decretos-ley conceden créditos extraordinarios o suplementos de crédito` +
    (ultimo ? `; en ${ultimo.anio}, ${miles(ultimo.con_creditos)} de ${miles(ultimo.rdl)}.` : ".");
  $("resumen-creditos").textContent = `Ver las ${miles(S.creditos.length)} normas que conceden créditos`;
  $("tabla-creditos").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Norma", "Publicada", "Tema", "Concede"].map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...S.creditos.map((x) => el("tr", {},
      el("td", {}, el("a", { href: `index.html#${x.id}`, texto: x.nombre })),
      el("td", { texto: `${fechaCorta(x.fecha)} ${x.fecha.slice(0, 4)}` }),
      el("td", { texto: x.tema || "—" }),
      el("td", { texto: x.tipos.map((t) => (t === "Crédito extraordinario" ? "créditos extraordinarios" : "suplementos de crédito")).join(" y ").replace(/^./, (c) => c.toUpperCase()) })))));
  $("sin-presupuestos-nota").textContent =
    "Las normas que conceden créditos se detectan con reglas sobre su texto oficial: un párrafo de la parte que manda que dice «se concede» o «se aprueba» un crédito extraordinario o un suplemento de crédito (el preámbulo solo lo explica y no cuenta). " +
    "No se suman los importes de normas distintas: muchos decretos-ley se derogaron o repiten lo de uno anterior, y un total los mezclaría. La ficha de cada norma dice el importe de cada crédito cuando se puede leer con seguridad, y enlaza a su texto oficial. " +
    "Datos: sección I del BOE.";
}

function pintarCreditos(I) {
  const S = I.sin_presupuestos;
  if (!S) return;
  const series = [
    { nombre: "Conceden créditos", datos: S.por_anio.map((x) => x.con_creditos), color: "--s1" },
    { nombre: "No conceden créditos", datos: S.por_anio.map((x) => x.rdl - x.con_creditos), color: "--voto-abst" },
  ];
  nuevoGrafico("creditos", $("grafico-creditos"), {
    type: "bar",
    data: { labels: S.por_anio.map((x) => x.anio),
      datasets: series.map((s) => ({ label: s.nombre, data: s.datos, backgroundColor: variable(s.color), borderColor: variable("--superficie"), borderWidth: 1, borderRadius: 4, maxBarThickness: 56 })) },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { x: { stacked: true, ticks: { color: variable("--tinta") }, grid: { display: false } }, y: { ...ejeValores(), stacked: true } },
      plugins: { legend: leyendaArriba(),
        tooltip: { callbacks: { footer: (items) => `Reales decretos-ley de ${S.por_anio[items[0].dataIndex].anio}: ${miles(S.por_anio[items[0].dataIndex].rdl)}` } } },
    },
  });
}

// ---------- El dinero de los Presupuestos (Sankey, datos de Hacienda: boe.hacienda) ----------
const millones = (x) => Math.round(x).toLocaleString("es-ES", { useGrouping: "always" });
const porCiento = (parte, total) => `${(100 * parte / total).toLocaleString("es-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} %`;
let vistaPresupuestos = "quien";

// Nodos [nombre corto, importe, color, detalle] de cada columna, para la edición publicada.
function nodosPresupuestos(P) {
  const A = P.edicion, v = (fila) => fila[A], ing = P.ingresos, g = P.gastos, c1 = P.capitulo1_ingresos, tr = P.transferencias.total;
  const origen = [
    ["Impuestos directos del Estado", v(c1.estado_impuestos), "--s1", "IRPF, Sociedades y otros: solo la parte del Estado"],
    ["Impuestos indirectos del Estado", v(ing["Impuestos indirectos"]), "--s1", "IVA, impuestos especiales y otros: solo la parte del Estado"],
    ["Cotizaciones a la Seguridad Social", v(c1.seguridad_social_cotizaciones), "--s3", "Cotizaciones sociales del presupuesto de la Seguridad Social"],
    ["Organismos autónomos (capítulo 1)", v(c1.organismos_capitulo1), "--s3", "Impuestos directos y cotizaciones sociales de los organismos autónomos"],
    ["Transferencias recibidas", v(ing["Transferencias corrientes"]) + v(ing["Transferencias de capital"]), "--voto-abst", "Dinero que llega de fuera de estas administraciones (por ejemplo, de la Unión Europea), corriente y de capital"],
    ["Tasas, precios y otros", v(ing["Tasas, precios y otros ingresos"]), "--voto-abst", "Tasas, precios públicos y otros ingresos"],
    ["Rentas, ventas y préstamos devueltos", v(ing["Ingresos patrimoniales"]) + v(ing["Enajenación inversiones reales"]) + v(ing["Activos financieros"]), "--voto-abst", "Ingresos patrimoniales, venta de inversiones y activos financieros"],
    ["Deuda nueva (calculado)", P.deuda_calculada[A], "--s4", "Lo que no cubren los ingresos previstos: diferencia entre gastos e ingresos de los capítulos 1 a 8"],
  ];
  const destinatario = { "48": "Familias e instituciones sin fines de lucro", "45": "Comunidades autónomas", "46": "Entidades locales",
    "49": "Exterior", "47": "Empresas privadas", "44": "Empresas y entes públicos" };
  const detalle = { "48": "Transferencias: pensiones, prestaciones, becas, ayudas…", "49": "Transferencias al exterior, por ejemplo a la Unión Europea",
    "47": "Transferencias (subvenciones) a empresas privadas", "44": "Transferencias a sociedades, entidades públicas empresariales y fundaciones del sector público" };
  const quien = [
    ...["48", "45", "46", "49", "47", "44"].filter((k) => tr[k]).map((k) => [destinatario[k], v(tr[k]), "--s7", detalle[k] || `Transferencias a ${destinatario[k].toLowerCase()}`]),
    ["Intereses de la deuda", v(g["Gastos financieros"]), "--s5", "Gastos financieros (capítulo 3)"],
    ["Sueldos del personal público", v(g["Gastos de personal"]), "--s6", "Gastos de personal (capítulo 1)"],
    ["Compras por contrato", v(g["Gastos corrientes en bienes y servicios"]), "--s2", "Bienes y servicios (capítulo 2): pagos a empresas por contratos"],
    ["Inversiones por contrato", v(g["Inversiones reales"]), "--s2", "Obras y equipos (capítulo 6): pagos a empresas por contratos"],
    ["Préstamos y participaciones", v(g["Activos financieros"]), "--s5", "Activos financieros (capítulo 8): préstamos y compra de participaciones"],
    ["Fondo para imprevistos", v(g["Fondo de Contingencia"]), "--voto-abst", "Fondo de contingencia (capítulo 5)"],
  ];
  const total = v(P.politicas["CAPÍTULOS 1 a 8"]);
  const pol = Object.entries(P.politicas).filter(([k]) => !k.startsWith("CAPÍTULOS")).map(([k, x]) => [k, x[A]]).sort((a, b) => b[1] - a[1]);
  const grandes = pol.filter((p) => p[1] >= total * 0.02), resto = pol.filter((p) => p[1] < total * 0.02);
  const politicas = [...grandes.map(([k, x]) => [k, x, "--s1", "Política de gasto"]),
    [`Otras ${resto.length} políticas`, resto.reduce((s, p) => s + p[1], 0), "--voto-abst", resto.map((p) => `${p[0]}: ${millones(p[1])}`).join("\n")]];
  return { origen, quien, politicas, total };
}

function dibujarSankey(caja, izquierda, derecha, total, titulo) {
  const NS = "http://www.w3.org/2000/svg";
  const nodo = (n, a, padre) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); padre.append(e); return e; };
  const W = Math.max(caja.clientWidth, 320), angosto = W < 640;
  const M = Math.min(300, Math.max(112, Math.round(W * (angosto ? 0.36 : 0.29)))), ancho = angosto ? 10 : 14, hueco = 10;
  const H = angosto ? 900 : 620, cx = W / 2 - ancho / 2;
  const caben = Math.max(12, Math.floor((M - 12) / (angosto ? 6 : 6.6)));
  const k = Math.min((H - hueco * (izquierda.length - 1)) / total, (H - hueco * (derecha.length - 1)) / total);
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H + 28}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", titulo);
  const yc = (H - total * k) / 2;
  const columna = (nodos, x, lado) => {
    let y = (H - (nodos.reduce((s, n) => s + n[1], 0) * k + hueco * (nodos.length - 1))) / 2, yCentro = yc;
    // Etiquetas: centradas en su bloque, pero empujadas hacia abajo (y luego hacia arriba si no caben) para no pisarse.
    const etiquetas = [];
    let yb0 = y;
    for (const n of nodos) {
      const lineas = enLineas(n[0], caben), alto = 13 * (lineas.length + 1);
      etiquetas.push({ lineas, alto, centro: yb0 + (n[1] * k) / 2 });
      yb0 += n[1] * k + hueco;
    }
    let fin = -Infinity;
    for (const e of etiquetas) { e.arriba = Math.max(e.centro - e.alto / 2, fin + 2); fin = e.arriba + e.alto; }
    let tope = H + 4;
    for (const e of [...etiquetas].reverse()) { if (e.arriba + e.alto > tope) e.arriba = tope - e.alto; tope = e.arriba - 2; }
    for (const [i, [nombre, valor, tono, detalle]] of nodos.entries()) {
      const h = valor * k, x0 = lado < 0 ? x + ancho : cx + ancho, x1 = lado < 0 ? cx : x;
      const ya = lado < 0 ? y : yCentro, yb = lado < 0 ? yCentro : y, m = (x0 + x1) / 2, hb = Math.max(h, 1);
      const texto = `${nombre}: ${millones(valor)} millones de euros (${porCiento(valor, total)})${detalle ? `\n${detalle}` : ""}`;
      // Banda rellena (borde de arriba y de abajo con la misma curva): no se deforma aunque sea muy ancha.
      const d = `M${x0},${ya} C${m},${ya} ${m},${yb} ${x1},${yb} L${x1},${yb + hb} C${m},${yb + hb} ${m},${ya + hb} ${x0},${ya + hb} Z`;
      nodo("title", {}, nodo("path", { d, fill: variable(tono) }, svg)).textContent = texto;
      nodo("title", {}, nodo("rect", { x, y, width: ancho, height: Math.max(h, 1), fill: variable(tono), rx: 2 }, svg)).textContent = texto;
      const { lineas, arriba } = etiquetas[i], tx = lado < 0 ? x - 6 : x + ancho + 6, anc = lado < 0 ? "end" : "start";
      const t = nodo("text", { x: tx, y: arriba + 10, "text-anchor": anc }, svg);
      lineas.forEach((l, i) => { nodo("tspan", { x: tx, dy: i ? 13 : 0 }, t).textContent = l; });
      nodo("tspan", { x: tx, dy: 13, class: "cifra" }, t).textContent = `${millones(valor)} · ${porCiento(valor, total)}`;
      y += h + hueco; yCentro += h;
    }
  };
  columna(izquierda, M - ancho, -1);
  columna(derecha, W - M, 1);
  nodo("title", {}, nodo("rect", { x: cx, y: yc, width: ancho, height: total * k, fill: variable("--tinta"), rx: 2 }, svg)).textContent = `Gasto previsto (capítulos 1 a 8): ${millones(total)} millones de euros`;
  nodo("text", { x: W / 2, y: H + 20, "text-anchor": "middle" }, svg).textContent = `Gasto previsto: ${millones(total)} millones de euros`;
  caja.replaceChildren(svg);
}

function pintarPresupuestos(P) {
  $("presupuestos").hidden = !P;
  if (!P) return;
  const A = P.edicion, N = nodosPresupuestos(P), derecha = vistaPresupuestos === "quien" ? N.quien : N.politicas;
  const ingresos = N.origen.slice(0, -1).reduce((s, n) => s + n[1], 0);
  const familias = N.quien[0];
  $("lectura-presupuestos").textContent =
    `Siguen vigentes los Presupuestos de 2023, prorrogados. En la prórroga para ${A.slice(0, 4)} (las cifras más recientes que publica Hacienda) se prevé gastar ${millones(N.total)} millones de euros. ` +
    `Los ingresos previstos cubren ${millones(ingresos)}; el resto, ${millones(P.deuda_calculada[A])}, se cubre con deuda. ` +
    `${familias[0]} reciben el ${porCiento(familias[1], N.total)} del gasto, sobre todo en pensiones.`;
  for (const [id, vista] of [["vista-quien", "quien"], ["vista-politicas", "politicas"]]) {
    $(id).setAttribute("aria-pressed", String(vista === vistaPresupuestos));
    $(id).onclick = () => { vistaPresupuestos = vista; pintarPresupuestos(P); };
  }
  dibujarSankey($("sankey-presupuestos"), N.origen, derecha, N.total,
    `Diagrama de flujo: de dónde sale el dinero de los Presupuestos (${N.origen.map((n) => `${n[0]}, ${millones(n[1])}`).join("; ")}) y ` +
    `${vistaPresupuestos === "quien" ? "a quién llega" : "a qué se dedica"} (${derecha.map((n) => `${n[0]}, ${millones(n[1])}`).join("; ")}). Millones de euros. Las cifras están también en la tabla «Ver las cifras».`);
  const fila = (parte, n) => el("tr", {}, el("td", { texto: parte }), el("td", { texto: n[0] }),
    el("td", { clase: "numero", texto: millones(n[1]) }), el("td", { clase: "numero", texto: porCiento(n[1], N.total) }));
  $("tabla-presupuestos").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Parte", "Concepto", "Millones de euros", "Del gasto"].map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...N.origen.map((n) => fila("De dónde sale", n)), ...N.quien.map((n) => fila("A quién llega", n)),
      ...N.politicas.map((n) => fila("A qué se dedica", n))));
  $("presupuestos-nota").textContent =
    "Es lo presupuestado, no lo gastado. Cifras consolidadas: Estado, Seguridad Social, organismos autónomos y demás entidades con presupuesto limitativo, sin contar el dinero que se pasan entre ellos. " +
    "Una parte del IRPF, el IVA y los impuestos especiales va directamente a las comunidades autónomas y a los ayuntamientos y no aparece aquí. " +
    "«A quién llega» separa lo que se transfiere (sin nada a cambio) de lo que se paga por un contrato. Sanidad y Educación salen pequeñas porque las gestionan las comunidades: su dinero va en «Transferencias a otras Administraciones Públicas». " +
    `Datos: Secretaría de Estado de Presupuestos y Gastos (Ministerio de Hacienda), Estadísticas de los Presupuestos Generales del Estado, edición ${A}.`;
}

let presupuestosCargados;
async function cargarPresupuestos() {
  if (presupuestosCargados === undefined) {
    try { presupuestosCargados = await cargarJson("presupuestos.json"); } catch (e) { presupuestosCargados = null; }
  }
  return presupuestosCargados;
}

window.PAGINA = {
  sinEdicion: true,
  preparar() {
    repintarAlCambiar(() => { cargarInforme().then(pintarDinero); cargarPresupuestos().then(pintarPresupuestos); });
    // El Sankey se dibuja al ancho real de su caja: se vuelve a dibujar si cambia.
    let espera;
    window.addEventListener("resize", () => { clearTimeout(espera); espera = setTimeout(() => cargarPresupuestos().then(pintarPresupuestos), 200); });
  },
  pintar() {
    pintarEtiquetaLegislatura();
    Promise.all([cargarInforme().then(pintarDinero), cargarPresupuestos().then(pintarPresupuestos)]).then(irAlAncla);
  },
};

function pintarDinero(I) {
  if (!I) return;
  pintarSinPresupuestos(I);
  if (window.Chart) pintarCreditos(I);
}
