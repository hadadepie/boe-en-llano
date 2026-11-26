/* El BOE en llano — los tribunales (tribunales.html): qué publicó el BOE de los tribunales sobre
   normas (sección I) y qué decidió el Tribunal Constitucional (sección T), de datos/informe.json.
   Estaba en «La legislatura» hasta el 25/11/2026. Usa lo común de app.js e informe.js. */

"use strict";

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
  pintarSentenciasTc(I);
  $("tribunales-nota").textContent =
    "El BOE no publica todo lo que deciden los tribunales. Del Constitucional, la sección I publica sobre todo las admisiones a trámite y sus sentencias van en la sección «T»; " +
    "del Supremo se publican sobre todo las sentencias que anulan una norma, porque la ley obliga a publicar su fallo para que tenga efectos para todos, " +
    "y por eso casi todas dan la razón a quien recurre. " +
    `En ${plural(T.sin_norma, "publicación", "publicaciones")} no se ha podido leer qué norma se recurre. ` +
    "Datos: sección I del BOE; tipo de asunto, decisión y quién recurre se leen con reglas sobre el texto, sin IA, y pueden fallar.";
}

// ---------- Qué decidió el Tribunal Constitucional (informe.sentencias_tc) ----------
const NOMBRE_RESULTADO_TC = {
  nulidad: "Nulidad (en todo o en parte)", inconstitucional_sin_nulidad: "Inconstitucional sin nulidad", desestima: "Desestima",
  pierde_objeto: "Pérdida de objeto", extinguido: "Extinción", inadmite: "Inadmisión", constitucional: "Constitucional",
};

function pintarSentenciasTc(I) {
  const S = I.sentencias_tc;
  $("bloque-sentencias-tc").hidden = !S;
  if (!S) return;
  const r = S.resultados, d = S.dias;
  const sinFondo = r.pierde_objeto + r.extinguido + r.inadmite;
  const otros = (r.inconstitucional_sin_nulidad || 0) + (r.constitucional || 0);
  const decisiones = Object.values(r).reduce((s, v) => s + v, 0);
  $("lectura-sentencias-tc").textContent =
    `Entre el ${fechaMedia(S.desde)} y el ${fechaMedia(S.hasta)}, el BOE publicó ${plural(S.sentencias, "sentencia", "sentencias")} del Tribunal Constitucional sobre normas. ` +
    // Se cuenta por norma juzgada: una sentencia puede decidir sobre varias normas (por eso salen más decisiones que sentencias).
    `Una sentencia puede decidir sobre varias normas, así que se cuenta cada norma juzgada: ${plural(decisiones, "decisión", "decisiones")} en total. ` +
    `Declararon la nulidad en todo o en parte ${plural(r.nulidad, "vez", "veces")}, desestimaron el recurso o la cuestión ${plural(r.desestima, "vez", "veces")}, ` +
    `${plural(sinFondo, "vez", "veces")} lo dieron por terminado sin entrar en el fondo` +
    (otros ? ` y ${plural(otros, "vez", "veces")} decidieron otra cosa (inconstitucional sin anularla o constitucional)` : "") + ". " +
    `De los ${miles(S.admisiones)} recursos y cuestiones de inconstitucionalidad que el BOE publicó como admitidos en la legislatura, ${miles(S.admisiones_resueltas)} tienen ya sentencia` +
    (d.n ? `: la mitad tardó ${plural(d.mediana, "día", "días")} o menos entre la admisión y la sentencia (el más rápido, ${miles(d.min)}; el más lento, ${miles(d.max)})` : "") +
    `; ${miles(S.admisiones - S.admisiones_resueltas)} siguen sin sentencia publicada. Solo ${plural(S.normas_juzgadas.length, "norma publicada", "normas publicadas")} en la legislatura tiene${S.normas_juzgadas.length === 1 ? "" : "n"} ya sentencia; las demás sentencias juzgan normas anteriores.`;
  $("resumen-sentencias-tc").textContent = `Ver las ${plural(S.normas_juzgadas.length, "norma", "normas")} de la legislatura con sentencia`;
  $("tabla-sentencias-tc").replaceChildren(
    el("thead", {}, el("tr", {}, ...["Norma", "Sentencias", "Qué decidieron"].map((x) => el("th", { texto: x })))),
    el("tbody", {}, ...S.normas_juzgadas.map((x) => el("tr", {},
      el("td", { clase: "celda-titular" }, el("a", { href: `index.html#${x.id}`, texto: recortar(x.titulo, 160) })),
      el("td", { texto: miles(x.sentencias) }),
      el("td", { texto: Object.entries(x.resultados).map(([k, v]) => `${NOMBRE_RESULTADO_TC[k] || k}${x.sentencias > 1 ? ` (${v})` : ""}`).join(", ") })))));
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

function pintarPaginaTribunales(I) {
  if (!I) return;
  pintarTribunales(I);
  if (window.Chart) pintarPromotores(I);
}

window.PAGINA = {
  sinEdicion: true,
  preparar() { repintarAlCambiar(() => cargarInforme().then(pintarPaginaTribunales)); },
  pintar() {
    pintarEtiquetaLegislatura();
    cargarInforme().then(pintarPaginaTribunales).then(irAlAncla);
  },
};
