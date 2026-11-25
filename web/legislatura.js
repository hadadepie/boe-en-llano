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
  pintarSinPresupuestos(I);
  pintarTribunales(I);
  pintarSenado(I);
  pintarCorrecciones(I);
  $("informe-nota").textContent =
    "Falta por añadir qué pasó después con estas normas: cuántas se modificaron o se derogaron. " +
    `Datos: sumarios y textos oficiales del BOE del ${fechaMedia(I.desde)} al ${fechaMedia(I.hasta)}. ` +
    "Quién aprueba cada norma se deduce de su rango y su departamento en el BOE.";
  if (!window.Chart) return;
  pintarQuien(I);
  pintarMeses(I);
  pintarTemasVia(I);
  pintarVigencia(I);
  pintarVigenciaMinisterios(I);
  pintarPromotores(I);
  pintarCreditos(I);
  pintarGraficoSenado(I);
  pintarGraficoCorrecciones(I);
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

// Por ministerio (informe.vigencia_ministerios): reales decretos y órdenes, ordenados por cuántos publica.
function pintarVigenciaMinisterios(I) {
  const V = I.vigencia_ministerios;
  if (!V || !V.ministerios.length) return;
  const filas = V.ministerios.map((m) => ({ ...m, cuentas: m.tipos }));
  graficoPorcentajes("vigenciaMinisterios", $("grafico-vigencia-ministerios"), filas, (m) => organoCorto(m.ministerio), TIPOS_VIGOR,
    (m) => m.con_parrafo, (m) => `${m.ministerio}
Con párrafo de entrada en vigor: ${miles(m.con_parrafo)} de ${plural(m.total, "norma", "normas")}`);
  const enseguida = V.ministerios.reduce((s, m) => s + m.tipos.mismo_dia + m.tipos.dia_siguiente, 0);
  const con = V.ministerios.reduce((s, m) => s + m.con_parrafo, 0);
  const masPlazo = [...V.ministerios].sort((a, b) => b.tipos.plazo / b.con_parrafo - a.tipos.plazo / a.con_parrafo)[0];
  const sinPlazo = V.ministerios.filter((m) => !m.tipos.plazo).map((m) => organoCorto(m.ministerio));
  $("lectura-vigencia-ministerios").textContent =
    `En los ${V.ministerios.length} ministerios con más normas, el ${pct(enseguida, con)} % de sus reales decretos y órdenes se aplican el mismo día de publicarse o al siguiente. ` +
    (masPlazo.tipos.plazo ? `Donde más se deja un plazo de espera es en ${organoCorto(masPlazo.ministerio)}: ${miles(masPlazo.tipos.plazo)} de ${miles(masPlazo.con_parrafo)} (${pct(masPlazo.tipos.plazo, masPlazo.con_parrafo)} %). ` : "") +
    (sinPlazo.length ? `Sin ninguno con plazo de espera: ${sinPlazo.join("; ")}.` : ""); // «;»: hay nombres con comas
  $("nota-vigencia-ministerios").textContent =
    `Solo reales decretos y órdenes, que se pueden comparar entre sí: las resoluciones se aplican casi siempre el mismo día. ` +
    `El ministerio es el que propone la norma, con el nombre que le da el BOE (no se juntan los de antes y después de noviembre de 2023). ` +
    `Ministerios con al menos ${V.minimo} normas con párrafo de entrada en vigor, ordenados por cuántas publican, no por el resultado` +
    (V.fuera.ministerios ? `; quedan fuera ${V.fuera.ministerios} con menos (${plural(V.fuera.normas, "norma", "normas")}).` : ".") +
    ` Cuenta la regla general de cada norma, no sus excepciones.`;
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

const lista = (xs) => (xs.length > 1 ? `${xs.slice(0, -1).join(", ")} y ${xs[xs.length - 1]}` : xs.join(""));

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
    "No se suman los importes: vienen en euros, en miles o en millones de euros, a veces en tablas, y una suma automática podría dar cifras falsas; cada norma enlaza a su ficha y a su texto oficial. " +
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

const mayuscula = (t) => t.charAt(0).toUpperCase() + t.slice(1);

// ---------- Qué hizo el Senado con las leyes (informe.senado_leyes) ----------
// Cada fila: lo que hizo el Senado y, si la enmendó o vetó, lo que hizo después el Congreso.
const FILAS_SENADO = [
  { nombre: "Sin cambios", es: (x) => x.resultado === "sin_cambios", color: "--s3" },
  { nombre: "Con enmiendas: el Congreso aceptó todas", es: (x) => x.resultado === "con_enmiendas" && x.congreso === "todas", color: "--s1" },
  { nombre: "Con enmiendas: el Congreso aceptó una parte", es: (x) => x.resultado === "con_enmiendas" && x.congreso === "en_parte", color: "--s1" },
  { nombre: "Con enmiendas: el Congreso no aceptó ninguna", es: (x) => x.resultado === "con_enmiendas" && x.congreso === "ninguna", color: "--s1" },
  { nombre: "Vetada: el Congreso levantó el veto", es: (x) => x.resultado === "veto", color: "--s4" },
  { nombre: "Rechazada: el Senado lo registra como veto", es: (x) => x.resultado === "veto_por_rechazo", color: "--s4" },
  { nombre: "Caducada al disolverse las Cortes", es: (x) => x.resultado === "caducada", color: "--voto-abst" },
];
const filaSenado = (x) => (FILAS_SENADO.find((f) => f.es(x)) || { nombre: "Otro" }).nombre;

function pintarSenadoLeyes(I) {
  const L = I.senado_leyes;
  if (!L) return;
  const r = L.resultados, c = L.congreso;
  const enmendadas = r.con_enmiendas;
  const vetos = r.veto + r.veto_por_rechazo;
  $("lectura-senado-leyes").textContent =
    `Llegaron al Senado ${plural(L.n, "texto aprobado", "textos aprobados")} por el Congreso en la legislatura (proyectos y proposiciones de ley y reformas de la Constitución); ${miles(L.publicadas)} se publicaron en el BOE. ` +
    `El Senado no cambió ${miles(r.sin_cambios)}, enmendó ${miles(enmendadas)} y vetó o rechazó ${miles(vetos)}` +
    (r.caducada ? `; ${miles(r.caducada)} caducaron al disolverse las Cortes. ` : ". ") +
    (enmendadas ? `De las ${miles(enmendadas)} enmendadas, el Congreso aceptó todas las enmiendas en ${miles(c.todas)}, una parte en ${miles(c.en_parte)} y ninguna en ${miles(c.ninguna)}. ` : "") +
    (vetos ? `Ningún veto impidió que la ley se publicara.` : "");
  const filas = FILAS_SENADO.map((f) => ({ ...f, n: L.lista.filter(f.es).length })).filter((f) => f.n);
  nuevoGrafico("senadoLeyes", $("grafico-senado-leyes"), {
    type: "bar",
    data: { labels: filas.map((f) => enLineas(f.nombre, estrecho() ? 22 : 46)),
      datasets: [{ label: "Leyes", data: filas.map((f) => f.n), backgroundColor: filas.map((f) => variable(f.color)), borderRadius: 4, maxBarThickness: 24 }] },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: ejeValores(), y: ejeNombres() },
      plugins: { legend: { display: false }, tooltip: { callbacks: { title: (items) => filas[items[0].dataIndex].nombre,
        label: (item) => plural(item.raw, "ley", "leyes") } } },
    },
  });
  $("resumen-senado-leyes").textContent = `Ver los ${miles(L.n)} textos`;
  $("tabla-senado-leyes").replaceChildren(
    el("thead", {}, el("tr", {}, ...["En el BOE", "Texto", "Qué hizo el Senado", "Enmiendas presentadas"].map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...L.lista.map((x) => el("tr", {},
      el("td", { texto: x.fecha ? `${fechaCorta(x.fecha)} ${x.fecha.slice(0, 4)}` : "—" }),
      el("td", { clase: "celda-titular" }, x.id ? el("a", { href: `index.html#${x.id}`, texto: recortar(x.titulo, 160) }) : el("span", { texto: recortar(x.titulo, 160) })),
      el("td", { texto: filaSenado(x) }),
      el("td", { texto: x.enmiendas_presentadas != null ? miles(x.enmiendas_presentadas) : "—" })))));
  $("senado-leyes-nota").textContent =
    `Datos abiertos del Senado: la situación de cada iniciativa en el Senado y lo que hizo después el Congreso, que el Senado anota en texto y aquí se lee con reglas, por ley y no por enmienda. ` +
    `Incluye los proyectos de ley del Gobierno, las proposiciones de ley del Congreso, las reformas de la Constitución y las proposiciones de las comunidades autónomas; no las que nacen en el propio Senado. ` +
    `«Enmiendas presentadas» cuenta las que propusieron los grupos del Senado (en total, ${miles(L.enmiendas_presentadas)}), no las aprobadas. ` +
    (I.senado_leyes.resultados.veto_por_rechazo ? `En octubre de 2024 el Senado rechazó por mayoría absoluta una ley orgánica y lo registra como veto; en la tramitación que publica el Congreso no consta una votación para levantarlo y la ley se publicó en el BOE. ` : "") +
    `Las votaciones de cada ley todavía no se recogen.`;
}

function pintarSenado(I) {
  const S = I.senado;
  $("senado").hidden = !S && !I.senado_leyes;
  pintarSenadoLeyes(I);
  if (!S) return;
  const p = S.parejas;
  const delSenado = S.por_quien["el Senado"] || 0;
  const [motivo, nMotivo] = Object.entries(S.motivos)[0];
  $("lectura-senado").textContent =
    `El BOE publicó ${plural(S.n, "conflicto", "conflictos")} entre órganos constitucionales que el Tribunal Constitucional admitió a trámite en la legislatura. ` +
    (delSenado ? `${miles(delSenado)} los planteó el Senado (${miles(p["el Senado frente a el Gobierno"] || 0)} frente al Gobierno y ${miles(p["el Senado frente a el Congreso"] || 0)} frente al Congreso)` : "") +
    (p["el Gobierno frente a el Senado"] ? ` y ${miles(p["el Gobierno frente a el Senado"])} el Gobierno frente al Senado. ` : ". ") +
    (motivo.startsWith("Enmiendas con gasto")
      ? `En ${miles(nMotivo)} de los ${miles(S.n)}, la discusión es sobre enmiendas o proposiciones que aumentan el gasto o reducen los ingresos, a las que el Gobierno puede oponerse (artículo 134.6 de la Constitución).`
      : `El motivo más repetido (${miles(nMotivo)} de ${miles(S.n)}): «${motivo}».`);
  $("resumen-senado").textContent = `Ver los ${miles(S.n)} conflictos`;
  $("tabla-senado").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Publicado", "Lo plantea", "Frente a", "Motivo", "Sobre"].map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...S.lista.map((x) => el("tr", {},
      el("td", { texto: `${fechaCorta(x.fecha)} ${x.fecha.slice(0, 4)}` }),
      el("td", { texto: x.quien ? mayuscula(x.quien) : "—" }),
      el("td", { texto: x.frente_a ? mayuscula(x.frente_a) : "—" }),
      el("td", { texto: x.motivo }),
      el("td", { clase: "celda-titular" }, el("a", { href: `index.html#${x.id}`, texto: mayuscula(recortar(x.sobre, 160)) }))))));
  $("senado-nota").textContent =
    "Son las admisiones a trámite que publica la sección I del BOE: dicen quién plantea el conflicto, frente a quién y sobre qué, no quién tiene razón. " +
    "Las sentencias del Tribunal Constitucional van en un suplemento aparte del BOE que aún no recogemos. " +
    "El motivo se asigna con reglas sobre el título oficial; quién lo plantea y frente a quién, del propio texto.";
}

function pintarGraficoSenado(I) {
  const S = I.senado;
  if (!S) return;
  const motivos = Object.keys(S.motivos);
  const parejas = [
    { clave: "el Senado frente a el Gobierno", nombre: "El Senado frente al Gobierno", color: "--s1" },
    { clave: "el Senado frente a el Congreso", nombre: "El Senado frente al Congreso", color: "--s2" },
    { clave: "el Gobierno frente a el Senado", nombre: "El Gobierno frente al Senado", color: "--s3" },
  ].filter((x) => S.parejas[x.clave]);
  const pareja = (x) => (x.frente_a ? `${x.quien} frente a ${x.frente_a}` : x.quien);
  nuevoGrafico("senado", $("grafico-senado"), {
    type: "bar",
    data: { labels: motivos.map((m) => (estrecho() ? enLineas(m, 18) : enLineas(m, 40))),
      datasets: parejas.map((pp) => ({ label: pp.nombre, backgroundColor: variable(pp.color), borderColor: variable("--superficie"), borderWidth: 1, borderRadius: 4, maxBarThickness: 26,
        data: motivos.map((m) => S.lista.filter((x) => x.motivo === m && pareja(x) === pp.clave).length) })) },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { ...ejeValores(), stacked: true }, y: { ...ejeNombres(), stacked: true } },
      plugins: { legend: leyendaArriba(), tooltip: { callbacks: { title: (items) => motivos[items[0].dataIndex] } } },
    },
  });
}

// «Ministerio de Asuntos Exteriores, …» → «Asuntos Exteriores, …» en el eje (el nombre entero va en la tabla y el tooltip).
const organoCorto = (o) => mayuscula(o.replace(/^Ministerio (?:para la |de la |del |de |para )/, ""));
const decimal = (x) => x.toLocaleString("es-ES", { maximumFractionDigits: 1 });

function pintarCorrecciones(I) {
  const C = I.correcciones_por_organo;
  $("correcciones").hidden = !C;
  if (!C) return;
  const mayor = C.organos.reduce((a, o) => (o.tasa > a.tasa ? o : a), C.organos[0]);
  const exteriores = C.organos.find((o) => o.organo.startsWith("Ministerio de Asuntos Exteriores"));
  $("lectura-correcciones").textContent =
    `Entre el ${fechaMedia(I.desde)} y el ${fechaMedia(I.hasta)}, la sección I del BOE publicó ${plural(C.total, "corrección de errores", "correcciones de errores")}: ` +
    `${miles(C.estatales)} de órganos del Estado y ${miles(C.autonomicas)} de comunidades autónomas. ` +
    `Son unas ${decimal((100 * C.estatales) / C.normas_estatales)} por cada 100 normas del Estado (${miles(C.normas_estatales)}). ` +
    (mayor ? `La proporción más alta, entre los órganos con al menos ${miles(C.minimo_normas)} normas, es la de ${mayor.organo === "Jefatura del Estado" ? "la Jefatura del Estado, que publica las leyes, los decretos-ley y los tratados que firma el Rey" : mayor.organo}: ` +
      `${miles(mayor.correcciones)} correcciones de ${miles(mayor.normas)} normas (${decimal(mayor.tasa)} por cada 100). ` : "") +
    (exteriores && exteriores.de_acuerdos_internacionales ? `De las ${miles(exteriores.correcciones)} de Exteriores, ${miles(exteriores.de_acuerdos_internacionales)} corrigen tratados, enmiendas a convenios y otros textos internacionales. ` : "") +
    (C.dias ? `La mitad de las correcciones llegan en ${plural(C.dias.mediana, "día", "días")} o menos desde la norma; ${miles(C.dias.hasta_7)} en la primera semana y ${miles(C.dias.mas_de_180)} más de seis meses después.` : "");
  const conVarias = C.ejemplos.filter((e) => e.correcciones.length > 1).length;
  $("resumen-correcciones").textContent = conVarias
    ? `Ver normas corregidas (${plural(conVarias, "norma del Estado corregida dos veces o más", "normas del Estado corregidas dos veces o más")} y las últimas corregidas)`
    : "Ver las últimas normas del Estado corregidas";
  $("tabla-correcciones").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Norma corregida", "Órgano", "Publicada", "Corrección"].map((t) => el("th", { texto: t })))),
    el("tbody", {}, ...C.ejemplos.map((x) => el("tr", {},
      el("td", { clase: "celda-titular" }, el("a", { href: `index.html#${x.id}`, texto: recortar(x.titulo, 160) })),
      el("td", { texto: x.organo }),
      el("td", { texto: `${fechaCorta(x.fecha)} ${x.fecha.slice(0, 4)}` }),
      el("td", {}, ...x.correcciones.flatMap((c, i) => [i ? el("br") : "",
        el("a", { href: `index.html#${c.id}`, texto: `${fechaCorta(c.fecha)} ${c.fecha.slice(0, 4)} (${plural(c.dias, "día", "días")} después)` })]))))));
  $("correcciones-nota").textContent =
    `Solo se muestran los órganos con al menos ${miles(C.minimo_normas)} normas propias en el periodo (sin contar sus correcciones), ordenados por cuántas publican: con menos, una sola corrección mueve mucho la proporción. ` +
    "Los ministerios llevan el nombre que les da el BOE; los anteriores a la reestructuración de noviembre de 2023 se cuentan aparte, porque no siempre son el mismo ministerio con otro nombre. " +
    "Una corrección puede ser de una norma anterior al periodo, así que la proporción compara lo que cada órgano publicó y corrigió en estos años, no qué parte de sus normas tuvo errores. " +
    `${miles(C.enlazadas)} de las ${miles(C.total)} correcciones se han enlazado con la norma que corrigen (mismo título oficial y mismo órgano); el resto corrige normas anteriores o de otras secciones del BOE, o su título no coincide exactamente. ` +
    "Datos: sección I del BOE, rango «Corrección (errores o erratas)».";
}

function pintarGraficoCorrecciones(I) {
  const C = I.correcciones_por_organo;
  if (!C) return;
  const O = C.organos;
  const tasa = (n, o) => Math.round((1000 * n) / o.normas) / 10;
  const series = [
    { label: "De acuerdos internacionales", color: "--s2", n: (o) => o.de_acuerdos_internacionales },
    { label: "De otras normas", color: "--s1", n: (o) => o.correcciones - o.de_acuerdos_internacionales },
  ].filter((x) => O.some((o) => x.n(o)));
  nuevoGrafico("correcciones", $("grafico-correcciones"), {
    type: "bar",
    data: { labels: O.map((o) => enLineas(organoCorto(o.organo), estrecho() ? 22 : 52)),
      datasets: series.map((x) => ({ label: x.label, backgroundColor: variable(x.color), borderColor: variable("--superficie"), borderWidth: 1,
        borderRadius: 4, maxBarThickness: 20, data: O.map((o) => tasa(x.n(o), o)), cuantas: O.map(x.n) })) },
    options: {
      indexAxis: "y", responsive: true, maintainAspectRatio: false,
      scales: { x: { ...ejeValores(), stacked: true, title: { display: true, text: "Correcciones por cada 100 normas", color: variable("--tinta-2") } },
        y: { ...ejeNombres(), stacked: true } },
      plugins: { legend: series.length > 1 ? leyendaArriba() : { display: false },
        tooltip: { callbacks: {
          title: (items) => O[items[0].dataIndex].organo,
          label: (item) => `${item.dataset.label}: ${plural(item.dataset.cuantas[item.dataIndex], "corrección", "correcciones")} (${decimal(item.raw)} por cada 100)`,
          footer: (items) => { const o = O[items[0].dataIndex]; return `En total: ${miles(o.correcciones)} de ${plural(o.normas, "norma", "normas")} (${decimal(o.tasa)} por cada 100)`; },
        } } },
    },
  });
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
