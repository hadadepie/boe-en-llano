/* El BOE en llano — la legislatura (legislatura.html): lo que pasó en toda la
   legislatura, no en una semana. Por ahora, los reales decretos-ley: resumen,
   tema y resultado, tamaño frente a apoyo y la tabla de votaciones.
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

window.PAGINA = {
  sinEdicion: true,
  preparar() {
    // Repintar con los colores del modo claro/oscuro cuando cambie.
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => pintarLegislatura());
  },
  pintar() {
    const L = estado.indice.legislatura;
    if (L) $("legislatura-etiqueta").textContent =
      `${L.legislatura} legislatura · desde el ${fechaMedia(L.desde)} hasta la disolución, el ${fechaMedia(L.hasta_pleno)}`;
    else $("legislatura-etiqueta").textContent = "Todavía no hay datos de la legislatura.";
    pintarLegislatura();
  },
};
