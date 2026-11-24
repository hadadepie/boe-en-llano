/* El BOE en llano — la legislatura (legislatura.html): lo que pasó en toda la
   legislatura, no en una semana. Primero el informe «Quién decidió» (datos/informe.json):
   quién aprobó las normas, mes a mes, por tema y su entrada en vigor; después, los
   reales decretos-ley: resumen, tema y resultado, tamaño frente a apoyo y votaciones.
   Usa lo común de app.js; no depende de la edición semanal. */

"use strict";

const graficosLegislatura = { temas: null, tamano: null };

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
    el("td", { texto: x.discrepancia ? `${x.resultado} (según el BOE)` : x.empate ? "derogado (empate)" : x.resultado,
      title: x.discrepancia || "" }),
    el("td", { texto: x.afavor != null ? `${x.afavor} / ${x.enContra} / ${x.abstenciones}` : "—" }),
    el("td", { texto: x.margen != null ? (x.margen > 0 ? `+${x.margen}` : String(x.margen)) : "—" })));
  $("tabla-legislatura").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Real decreto-ley", "De qué trata", "Tema", "Normas que modifica", "Votación", "Resultado", "Sí / No / Abst.", "Margen"]
      .map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...filas));
  const discrepancias = L.decretos_ley.filter((x) => x.discrepancia).map((x) => `Real Decreto-ley ${x.rdl}: ${x.discrepancia}`);
  $("legislatura-nota").textContent = `${L.nota} Consultado el ${fechaMedia(L.consultado)} (${L.dias_consultados} días laborables revisados). ` +
    "Tema, título y normas que modifica: documento oficial de cada real decreto-ley en el BOE." +
    (discrepancias.length ? ` ${discrepancias.join(" ")}` : "");
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
  if (graficosLegislatura.temas) graficosLegislatura.temas.destroy();
  // En pantallas estrechas, los nombres de tema largos se parten en líneas para que no se corten.
  const estrecho = window.matchMedia("(max-width: 560px)").matches; // el mismo corte que estilos.css
  const enLineas = (texto) => texto.split(" ").reduce((lineas, palabra) => {
    const ultima = lineas[lineas.length - 1];
    if (ultima && (ultima + " " + palabra).length <= 18) lineas[lineas.length - 1] = `${ultima} ${palabra}`;
    else lineas.push(palabra);
    return lineas;
  }, []);
  graficosLegislatura.temas = new Chart($("grafico-temas-rdl"), {
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
  if (graficosLegislatura.tamano) graficosLegislatura.tamano.destroy();
  const puntos = (resultado) => votados.filter((x) => x.resultado === resultado)
    .map((x) => ({ x: x.normas_modificadas, y: x.margen, decreto: x }));
  graficosLegislatura.tamano = new Chart($("grafico-tamano-rdl"), {
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

// ---------- Informe: quién decidió (datos/informe.json, boe.informe) ----------

const graficosInforme = {};
const VIAS = [
  { clave: "cortes", nombre: "Leyes de las Cortes", color: "--s1" },
  { clave: "rdl", nombre: "Reales decretos-ley", color: "--s2" },
  { clave: "rd", nombre: "Reales decretos", color: "--s3" },
];
const TIPOS_VIGOR = [
  { clave: "mismo_dia", nombre: "El mismo día", color: "--s1" },
  { clave: "dia_siguiente", nombre: "Al día siguiente", color: "--s3" },
  { clave: "plazo", nombre: "Tras un plazo (días o meses)", color: "--s4" },
  { clave: "fecha", nombre: "En una fecha concreta", color: "--s7" },
  { clave: "otro", nombre: "Otro (mes siguiente, depende de otro hecho, sin clasificar)", color: "--voto-abst" },
];
const pct = (parte, total) => (total ? Math.round((100 * parte) / total) : 0);
const nombreMes = (m) => aFecha(`${m}-01`).toLocaleDateString("es-ES", { month: "long", year: "numeric" });
const unos = (x) => (Number.isInteger(x) ? miles(x) : `unos ${miles(Math.round(x))}`);

function nuevoGrafico(clave, lienzo, config) {
  if (graficosInforme[clave]) graficosInforme[clave].destroy();
  graficosInforme[clave] = new Chart(lienzo, config);
}

const leyendaArriba = () => ({ position: "top", align: "start", labels: { color: variable("--tinta"), boxWidth: 12, boxHeight: 12 } });
const ejeValores = (extra = {}) => ({ beginAtZero: true, ticks: { precision: 0, color: variable("--tinta-2"), ...extra }, grid: { color: variable("--linea") } });
const ejeNombres = () => ({ ticks: { color: variable("--tinta"), autoSkip: false }, grid: { display: false } });
const estrecho = () => window.matchMedia("(max-width: 560px)").matches; // el mismo corte que estilos.css
const enLineas = (texto, ancho = 18) => texto.split(" ").reduce((lineas, palabra) => {
  const ultima = lineas[lineas.length - 1];
  if (ultima && (ultima + " " + palabra).length <= ancho) lineas[lineas.length - 1] = `${ultima} ${palabra}`;
  else lineas.push(palabra);
  return lineas;
}, []);

function pintarInforme(I) {
  $("informe").hidden = !I;
  if (!I) return;
  const cat = Object.fromEntries(I.categorias.map((c) => [c.clave, c]));
  const leyes = cat.cortes.n;
  const sd = I.subvenciones_directas;
  $("informe-resumen").textContent =
    `Entre el ${fechaMedia(I.desde)} y el ${fechaMedia(I.hasta)}, la sección I del BOE («Disposiciones generales») publicó ${miles(I.total)} textos. ` +
    `Quitadas ${miles(I.correcciones)} correcciones de errores y ${miles(I.convalidaciones_publicadas)} publicaciones de convalidaciones de decretos-ley, ` +
    `${miles(I.estatales)} son normas y decisiones del Estado y ${miles(I.autonomicas)}, normas autonómicas que también se publican en el BOE. ` +
    (leyes ? `Por cada ley de las Cortes (${miles(leyes)} en total), el Gobierno aprobó ${unos(cat.rdl.n / leyes)} reales decretos-ley y ${unos(cat.rd.n / leyes)} reales decretos. ` : "") +
    (sd.de ? `De los ${miles(sd.de)} reales decretos, ${miles(sd.n)} (${pct(sd.n, sd.de)} %) regulan la concesión directa de una subvención.` : "");
  $("informe-categorias").replaceChildren(...I.categorias.flatMap((c) => [
    el("dt", { texto: `${c.etiqueta}: ${miles(c.n)}` }), el("dd", { texto: c.explicacion })]));
  pintarLeyes(I);
  pintarLecturas(I);
  pintarGrupos(I);
  pintarTramitados(I);
  pintarTribunales(I);
  $("informe-nota").textContent =
    "Falta por añadir qué pasó después con estas normas: cuántas se modificaron o se derogaron. " +
    `Datos: sumarios y textos oficiales del BOE del ${fechaMedia(I.desde)} al ${fechaMedia(I.hasta)}. ` +
    "Quién aprueba cada norma se deduce de su rango y su departamento en el BOE.";
  if (!window.Chart) return;
  pintarQuien(I);
  pintarMeses(I);
  pintarTemasVia(I);
  pintarVigencia(I);
  pintarPromotores(I);
}

function pintarLecturas(I) {
  const r = I.ritmo;
  const m = I.por_mes;
  const maxRd = m.rd.indexOf(Math.max(...m.rd));
  $("lectura-meses").textContent = (r
    ? `Con el Gobierno en funciones, hasta que el nuevo reorganizó los ministerios el ${fechaMedia(I.nuevo_gobierno.fecha)} ` +
      `(${I.nuevo_gobierno.titulo.split(",")[0]}), se publicaron ${plural(r.en_funciones.rd, "real decreto", "reales decretos")} en ${miles(r.en_funciones.dias)} días ` +
      `(${unos(r.en_funciones.rd_cada_30_dias)} cada 30 días), ${r.en_funciones.rdl ? plural(r.en_funciones.rdl, "real decreto-ley", "reales decretos-ley") : "ningún real decreto-ley"} ` +
      `y ${r.en_funciones.cortes ? plural(r.en_funciones.cortes, "ley", "leyes") : "ninguna ley"}. ` +
      `Desde entonces y hasta ${I.disolucion ? `la disolución de las Cortes, el ${fechaMedia(I.disolucion)}` : "hoy"}: ${unos(r.con_gobierno.rd_cada_30_dias)} reales decretos cada 30 días. `
    : "") + `El mes con más reales decretos fue ${nombreMes(m.meses[maxRd])} (${miles(m.rd[maxRd])})` +
    (I.disolucion && m.meses[maxRd] >= I.disolucion.slice(0, 7) ? ", con las Cortes ya disueltas." : ".");

  const conVia = I.por_tema.filter((t) => t.cortes + t.rdl + t.rd >= 10)
    .map((t) => ({ ...t, total: t.cortes + t.rdl + t.rd, conLey: t.cortes + t.rdl }))
    .sort((a, b) => b.conLey / b.total - a.conLey / a.total);
  if (conVia.length >= 2) {
    const mas = conVia[0], menos = conVia[conVia.length - 1];
    $("lectura-temas-via").textContent =
      `En «${mas.tema}», el ${pct(mas.conLey, mas.total)} % de las normas fueron leyes o decretos-ley (${miles(mas.conLey)} de ${miles(mas.total)}). ` +
      `En «${menos.tema}», el ${pct(menos.conLey, menos.total)} %: casi todo se decidió por real decreto (${miles(menos.rd)}).`;
  }

  const g = Object.fromEntries(I.vigencia.map((x) => [x.grupo, x]));
  const conParrafo = (x) => x.total - x.sin_parrafo;
  const total = I.vigencia.reduce((s, x) => s + conParrafo(x), 0);
  const enseguida = I.vigencia.reduce((s, x) => s + x.tipos.mismo_dia + x.tipos.dia_siguiente, 0);
  const rdl = g["Reales decretos-ley"];
  const masPlazo = I.vigencia.filter((x) => conParrafo(x) >= 10)
    .sort((a, b) => b.tipos.plazo / conParrafo(b) - a.tipos.plazo / conParrafo(a))[0];
  $("lectura-vigencia").textContent =
    `El ${pct(enseguida, total)} % de las normas con párrafo de entrada en vigor se aplican el mismo día de publicarse o al siguiente. ` +
    (rdl ? `Reales decretos-ley: ${miles(rdl.tipos.mismo_dia + rdl.tipos.dia_siguiente)} de ${miles(conParrafo(rdl))}, ${rdl.tipos.plazo ? `y ${miles(rdl.tipos.plazo)} con plazo de espera` : "y ninguno con plazo de espera"}. ` : "") +
    (masPlazo && masPlazo.tipos.plazo ? `Donde más se da un plazo de espera es en las ${masPlazo.grupo.toLowerCase()}: ` +
      `${miles(masPlazo.tipos.plazo)} de ${miles(conParrafo(masPlazo))} (${pct(masPlazo.tipos.plazo, conParrafo(masPlazo))} %).` : "");
}

function pintarQuien(I) {
  const datos = [...I.categorias].sort((a, b) => b.n - a.n);
  nuevoGrafico("quien", $("grafico-quien"), {
    type: "bar",
    data: { labels: datos.map((c) => (estrecho() ? enLineas(c.etiqueta, 16) : c.etiqueta)),
      datasets: [{ label: "Normas", data: datos.map((c) => c.n), backgroundColor: variable("--s1"), borderRadius: 4, maxBarThickness: 22 }] },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: ejeValores(), y: ejeNombres() },
      plugins: { legend: { display: false },
        tooltip: { callbacks: { title: (items) => datos[items[0].dataIndex].etiqueta,
          label: (item) => `${miles(item.raw)} (${pct(item.raw, I.estatales)} % de las normas del Estado)`,
          afterLabel: (item) => enLineas(datos[item.dataIndex].explicacion, 50) } } },
    },
  });
}

function pintarMeses(I) {
  const m = I.por_mes;
  nuevoGrafico("meses", $("grafico-meses"), {
    type: "bar",
    data: { labels: m.meses.map((x) => aFecha(`${x}-01`).toLocaleDateString("es-ES", { month: "short", year: "2-digit" })),
      datasets: VIAS.map((v) => ({ label: v.nombre, data: m[v.clave], backgroundColor: variable(v.color),
        borderColor: variable("--fondo"), borderWidth: { top: 1 } })) },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { x: { stacked: true, ticks: { color: variable("--tinta-2"), maxRotation: 0, autoSkipPadding: 8 }, grid: { display: false } },
        y: { stacked: true, ...ejeValores() } },
      plugins: { legend: leyendaArriba(),
        tooltip: { mode: "index", callbacks: { title: (items) => nombreMes(m.meses[items[0].dataIndex]) } } },
    },
  });
}

// Barras al 100 %: cada tramo guarda también su cuenta para el tooltip.
function graficoPorcentajes(clave, lienzo, filas, nombreFila, series, totalDe, pie) {
  nuevoGrafico(clave, lienzo, {
    type: "bar",
    data: { labels: filas.map((f) => (estrecho() ? enLineas(nombreFila(f), 16) : nombreFila(f))),
      datasets: series.map((s) => ({ label: s.nombre, data: filas.map((f) => (100 * f.cuentas[s.clave]) / totalDe(f)),
        cuentas: filas.map((f) => f.cuentas[s.clave]),
        backgroundColor: variable(s.color), borderColor: variable("--fondo"), borderWidth: { right: 2 }, maxBarThickness: 22 })) },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { stacked: true, max: 100, ...ejeValores({ callback: (v) => `${v} %` }) }, y: { stacked: true, ...ejeNombres() } },
      plugins: { legend: leyendaArriba(),
        tooltip: { callbacks: { title: (items) => nombreFila(filas[items[0].dataIndex]),
          label: (item) => `${item.dataset.label}: ${miles(item.dataset.cuentas[item.dataIndex])} (${Math.round(item.raw)} %)`,
          footer: (items) => pie(filas[items[0].dataIndex]) } } },
    },
  });
}

function pintarTemasVia(I) {
  const temas = I.por_tema.map((t) => ({ tema: t.tema, cuentas: t, total: t.cortes + t.rdl + t.rd })).filter((t) => t.total);
  graficoPorcentajes("temasVia", $("grafico-temas-via"), temas, (t) => t.tema, VIAS, (t) => t.total,
    (t) => `Total: ${miles(t.total)}`);
}

function pintarVigencia(I) {
  const grupos = I.vigencia.map((g) => ({ ...g, cuentas: g.tipos, con: g.total - g.sin_parrafo })).filter((g) => g.con);
  graficoPorcentajes("vigencia", $("grafico-vigencia"), grupos, (g) => g.grupo, TIPOS_VIGOR, (g) => g.con,
    (g) => `Con párrafo de entrada en vigor: ${miles(g.con)} de ${miles(g.total)}`);
}

// ---------- Cómo votó cada grupo (informe.votos_grupos) ----------
// Colores de sí, no y abstención de las votaciones (nunca colores de partido).
const POSICIONES_GRUPO = [
  { clave: "Sí", nombre: "Sí", color: "--voto-si" },
  { clave: "No", nombre: "No", color: "--voto-no" },
  { clave: "Abstención", nombre: "Abstención", color: "--voto-abst" },
  { clave: "No vota", nombre: "No vota (todo el grupo)", color: "--voto-nv" },
  { clave: "Dividido", nombre: "Dividido", color: "--s7" },
];

function pintarGrupos(I) {
  const G = I.votos_grupos;
  $("bloque-grupos").hidden = !G;
  if (!G) return;
  const describir = (g) => POSICIONES_GRUPO.filter((p) => g.posiciones[p.clave])
    .map((p) => `${miles(g.posiciones[p.clave])} ${{ "Sí": "sí", "No": "no", "Abstención": g.posiciones[p.clave] === 1 ? "abstención" : "abstenciones",
      "No vota": "sin votar", "Dividido": g.posiciones[p.clave] === 1 ? "dividido" : "divididos" }[p.clave]}`).join(", ");
  const siempre = G.grupos.filter((g) => g.posiciones["Sí"] === g.votaciones).map((g) => g.nombre);
  const reparto = (g) => 1 - Math.max(...Object.values(g.posiciones)) / g.votaciones;
  const repartidos = G.grupos.filter((g) => reparto(g) > 0.25).sort((a, b) => reparto(b) - reparto(a)).slice(0, 2);
  const divididos = G.grupos.filter((g) => g.posiciones.Dividido);
  $("lectura-grupos").textContent =
    `En las ${miles(G.votaciones)} votaciones del Pleno con voto por grupos, ` +
    (siempre.length ? `${siempre.join(" y ")} votaron sí en todas. ` : "ningún grupo votó sí en todas. ") +
    (repartidos.length ? `Los grupos con el voto más repartido: ${repartidos.map((g) => `${g.nombre} (${describir(g)})`).join("; ")}. ` : "") +
    divididos.map((g) => `El ${g.nombre} se dividió en ${plural(g.posiciones.Dividido, "votación", "votaciones")}: sus diputados votaron distinto a partes iguales.`).join(" ");
  $("nota-grupos").textContent =
    "La posición de un grupo es lo que votó la mayoría de sus diputados en cada convalidación; los grupos van por número de diputados. " +
    `No incluye ${plural(G.solo_totales, "votación", "votaciones")} por llamamiento (el Congreso solo publica los totales) ni lo que acordó la Diputación Permanente, que no publica sus votaciones. ` +
    "Las listas del Grupo Mixto votan a menudo distinto: su desglose está en la ficha de cada decreto-ley. La composición de los grupos cambió durante la legislatura; cada votación usa la de su día.";
  $("tabla-grupos").replaceChildren(
    el("thead", {}, el("tr", {}, el("th", { texto: "Grupo" }), ...POSICIONES_GRUPO.map((p) => el("th", { texto: p.nombre })))),
    el("tbody", {}, ...G.grupos.map((g) => el("tr", {},
      el("td", { texto: g.nombre_completo }), ...POSICIONES_GRUPO.map((p) => el("td", { texto: miles(g.posiciones[p.clave]) }))))));
  if (!window.Chart) return;
  const grupos = G.grupos.map((g) => ({ ...g, cuentas: g.posiciones }));
  graficoPorcentajes("grupos", $("grafico-grupos"), grupos, (g) => g.nombre, POSICIONES_GRUPO.filter((p) => grupos.some((g) => g.posiciones[p.clave])),
    (g) => g.votaciones, (g) => `${g.nombre_completo} · ${miles(g.votaciones)} votaciones`);
}

function pintarTramitados(I) {
  const T = I.tramitados_como_ley;
  $("bloque-tramitados").hidden = !T;
  if (!T) return;
  const caducados = T.resultados.Caducado || 0;
  const fechas = [...new Set(T.lista.filter((x) => x.resultado?.startsWith("Caducado")).map((x) => x.fecha_resultado))];
  const [faseMas, nFase] = Object.entries(T.fases)[0];
  $("lectura-tramitados").textContent =
    (T.convalidados ? `De los ${miles(T.convalidados)} decretos-ley convalidados, ${miles(T.n)} se tramitaron además como proyecto de ley. `
      : `${miles(T.n)} decretos-ley se tramitaron además como proyecto de ley. `) +
    (caducados === T.n ? `Ninguno terminó: ${T.n === 1 ? "caducó" : `caducaron los ${miles(T.n)}`}` : `${miles(caducados)} caducaron`) +
    (fechas.length === 1 ? `, con fecha ${fechaMedia(fechas[0])}. ` : ". ") +
    `${miles(nFase)} no pasaron de la fase «${faseMas.toLowerCase()}». ` +
    (T.dias ? `Estuvieron en trámite una mediana de ${miles(T.dias.mediana)} días (de ${miles(T.dias.min)} a ${miles(T.dias.max)}).` : "");
  $("resumen-tramitados").textContent = `Ver los ${miles(T.n)} decretos-ley tramitados como ley`;
  $("tabla-tramitados").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Decreto-ley", "Tema", "Presentado", "Se quedó en", "Días", "Comisión"].map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...T.lista.map((x) => el("tr", {},
      el("td", {}, el("a", { href: `index.html#${x.id}`, texto: x.nombre })),
      el("td", { texto: x.tema || "—" }),
      el("td", { texto: x.presentado ? `${fechaCorta(x.presentado)} ${x.presentado.slice(0, 4)}` : "—" }),
      el("td", { texto: x.fase || "—" }),
      el("td", { texto: x.dias == null ? "—" : miles(x.dias) }),
      el("td", { texto: (x.comision || "—").replace(/^Comisión de /, "") })))));
}

const recortar = (texto, n = 140) => (texto.length > n ? `${texto.slice(0, n).replace(/\s+\S*$/, "")}…` : texto);

function pintarTribunales(I) {
  const T = I.tribunales;
  $("tribunales").hidden = !T;
  if (!T) return;
  const tc = T.tipos_tc, ts = T.decisiones_ts;
  const estima = (ts.Estima || 0) + (ts["Estima en parte"] || 0);
  $("lectura-tribunales").textContent =
    `La sección I del BOE publicó ${miles(T.total)} decisiones de tribunales sobre normas: ${miles(T.constitucional)} del Tribunal Constitucional y ${miles(T.supremo)} del Tribunal Supremo. ` +
    `Del Constitucional son sobre todo admisiones a trámite: ${miles(tc["Recurso de inconstitucionalidad"] || 0)} recursos de inconstitucionalidad y ${miles(tc["Cuestión de inconstitucionalidad"] || 0)} cuestiones de inconstitucionalidad` +
    (T.suspension_161_2 ? `; en ${miles(T.suspension_161_2)}, el Gobierno de España invocó el artículo 161.2 de la Constitución, que suspende la norma autonómica recurrida hasta que el Tribunal ratifique o levante la suspensión (en un plazo de cinco meses). ` : ". ") +
    (estima ? `Del Supremo, ${miles(estima)} sentencias dan la razón, en todo o en parte, a quien recurrió una norma.` : "") +
    (T.mas_recurridas.length ? ` La norma más citada: ${recortar(T.mas_recurridas[0].norma, 90)} (${plural(T.mas_recurridas[0].n, "publicación", "publicaciones")}).` : "");
  $("tabla-recurridas").replaceChildren(
    el("thead", {}, el("tr", {}, el("th", { texto: "Norma" }), el("th", { texto: "Publicaciones" }))),
    el("tbody", {}, ...T.mas_recurridas.map((x) => el("tr", {},
      el("td", { clase: "celda-titular", texto: recortar(x.norma) }), el("td", { texto: miles(x.n) })))));
  $("tribunales-nota").textContent =
    "El BOE no publica todo lo que deciden los tribunales. Las sentencias del Constitucional van en un suplemento aparte del BOE que aún no recogemos; " +
    "del Supremo se publican sobre todo las sentencias que anulan una norma, porque la ley obliga a publicar su fallo para que tenga efectos para todos, " +
    "y por eso casi todas dan la razón a quien recurre. " +
    `En ${plural(T.sin_norma, "publicación", "publicaciones")} no se ha podido leer qué norma se recurre. ` +
    "Datos: sección I del BOE; tipo de asunto, decisión y quién recurre se leen con reglas sobre el texto, sin IA, y pueden fallar.";
}

function pintarPromotores(I) {
  const T = I.tribunales;
  if (!T) return;
  const datos = T.promotores;
  nuevoGrafico("promotores", $("grafico-promotores"), {
    type: "bar",
    data: { labels: datos.map((p) => (estrecho() ? enLineas(p.categoria, 16) : p.categoria)),
      datasets: [{ label: "Asuntos", data: datos.map((p) => p.n), backgroundColor: variable("--s1"), borderRadius: 4, maxBarThickness: 22 }] },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: ejeValores(), y: ejeNombres() },
      plugins: { legend: { display: false },
        tooltip: { callbacks: { title: (items) => datos[items[0].dataIndex].categoria,
          label: (item) => `${plural(item.raw, "publicación", "publicaciones")} (${pct(item.raw, T.total)} %)` } } },
    },
  });
}

function pintarLeyes(I) {
  $("resumen-leyes").textContent = `Ver las ${miles(I.leyes.length)} leyes y reformas de la Constitución de la legislatura`;
  $("tabla-leyes").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Publicada", "Rango", "Ley", "Tema"].map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...I.leyes.map((x) => el("tr", {},
      el("td", { texto: `${fechaCorta(x.fecha)} ${x.fecha.slice(0, 4)}` }),
      el("td", { texto: x.rango === "Reforma" ? "Reforma de la Constitución" : x.rango }),
      el("td", { clase: "celda-titular" }, el("a", { href: `index.html#${x.id}`, texto: x.titulo })),
      el("td", { texto: x.tema || "—" })))));
}

let informeCargado;
async function cargarInforme() {
  if (informeCargado === undefined) {
    try { informeCargado = await cargarJson("informe.json"); } catch (e) { informeCargado = null; }
  }
  return informeCargado;
}

window.PAGINA = {
  sinEdicion: true,
  preparar() {
    // Repintar con los colores del modo claro/oscuro, o con otro ancho, cuando cambie.
    const repintar = () => { pintarLegislatura(); cargarInforme().then(pintarInforme); };
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", repintar);
    // Al cruzar el corte de pantalla estrecha, los nombres largos pasan a partirse en líneas (o dejan de hacerlo).
    window.matchMedia("(max-width: 560px)").addEventListener("change", repintar);
  },
  pintar() {
    const L = estado.indice.legislatura;
    if (L) $("legislatura-etiqueta").textContent =
      `${L.legislatura} legislatura · desde el ${fechaMedia(L.desde)} hasta la disolución, el ${fechaMedia(L.hasta_pleno)}`;
    else $("legislatura-etiqueta").textContent = "Todavía no hay datos de la legislatura.";
    pintarLegislatura();
    cargarInforme().then(pintarInforme);
  },
};
