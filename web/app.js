/* El BOE en llano — edición semanal.
   Lee datos.json (generado por `python -m boe.exportar`) y pinta, para la
   edición (semana) elegida: portada con titulares, «En cifras», «La semana en
   datos», secciones por tema, breves y, al final, los datos (gráfico, matriz y
   lista filtrable). Las fichas se abren como un artículo superpuesto.
   Todo texto que viene de los datos se inserta con textContent (nunca innerHTML). */

"use strict";

const estado = {
  datos: null,
  edicion: null,                 // id de la semana elegida, p. ej. "2026-S47"
  filtros: { fecha: "", tema: "", impacto: "", ambito: "" },
  filtroIds: null,               // { texto, ids } al pulsar una pieza de «La semana en datos»
  graficos: {},
  brevesAbiertos: false,
};
const $ = (id) => document.getElementById(id);
const MAX_BREVES = 8;
const NUM_SECUNDARIOS = 3;
const MAX_POR_TEMA = 3;

// Nombres que se muestran para el impacto (en los datos: Directo / Colectivos / Técnico).
const IMPACTO = {
  Directo: {
    nombre: "Te afecta a ti",
    explicacion: "Cambia algo para mucha gente",
    ejemplo: "p. ej., salario mínimo, impuestos, precios regulados",
  },
  Colectivos: {
    nombre: "Afecta a ciertos grupos",
    explicacion: "Un sector, una profesión o un colectivo",
    ejemplo: "p. ej., pesca, profesorado, funcionarios",
  },
  Técnico: {
    nombre: "Gestión interna",
    explicacion: "Trámites y organización de la Administración",
    ejemplo: "p. ej., subvenciones a una entidad, correcciones",
  },
};
const nombreImpacto = (i) => (IMPACTO[i] ? IMPACTO[i].nombre : i);

// ---------- Glosario ----------
// Definiciones breves y neutrales de los términos que aparecen en las fichas.
const GLOSARIO = {
  "ley": ["Ley", "Norma aprobada por un parlamento: las Cortes Generales (Congreso y Senado) o el parlamento de una comunidad autónoma. Solo una ley puede regular ciertas materias, como los impuestos o los derechos de las personas."],
  "ley orgánica": ["Ley orgánica", "Ley sobre materias que la Constitución reserva a este tipo (derechos fundamentales, Estatutos de Autonomía, régimen electoral…). Necesita mayoría absoluta del Congreso en una votación final sobre el conjunto."],
  "real decreto-ley": ["Real decreto-ley", "Norma con fuerza de ley que aprueba el Gobierno, sin pasar antes por las Cortes, en casos de «extraordinaria y urgente necesidad» (artículo 86 de la Constitución). Se aplica desde que se publica, pero el Congreso tiene 30 días para convalidarlo o derogarlo."],
  "real decreto": ["Real decreto", "Norma que aprueba el Gobierno (el Consejo de Ministros) para desarrollar o aplicar las leyes. Está por debajo de la ley y no puede contradecirla."],
  "orden": ["Orden ministerial", "Norma que dicta un ministerio sobre asuntos de su competencia. Está por debajo de los reales decretos."],
  "resolución": ["Resolución", "Decisión de un órgano público sobre un asunto concreto: fijar un precio regulado, convocar ayudas, publicar un acuerdo del Congreso…"],
  "corrección de errores": ["Corrección de errores", "Publicación que corrige erratas o errores materiales de una norma ya publicada. No cambia su contenido de fondo."],
  "acuerdo internacional": ["Acuerdo internacional", "Pacto entre España y otros Estados u organizaciones internacionales. Se publica en el BOE para que forme parte del ordenamiento español."],
  "convalidar": ["Convalidar", "El Congreso vota a favor de que un real decreto-ley siga en vigor. Gana la convalidación si hay más votos a favor que en contra."],
  "derogar": ["Derogar (un real decreto-ley)", "El Congreso vota en contra de mantenerlo: deja de aplicarse desde ese momento, aunque lo que se hizo mientras estuvo en vigor sigue siendo válido."],
  "tramitar como proyecto de ley": ["Tramitar como proyecto de ley", "Tras convalidar un real decreto-ley, el Congreso puede decidir tramitarlo como una ley: los grupos pueden presentar enmiendas y el texto puede cambiar antes de aprobarse definitivamente."],
  "diputación permanente": ["Diputación Permanente", "Órgano reducido del Congreso (unos 60 diputados, en proporción a los grupos) que actúa cuando las Cortes están disueltas o fuera de los periodos de sesiones. Entre otras cosas, convalida o deroga reales decretos-ley."],
  "votación por llamamiento": ["Votación pública por llamamiento", "Votación en la que se nombra a cada diputado y responde de viva voz «sí», «no» o «abstención», en lugar de usar el sistema electrónico."],
  "voto telemático": ["Voto telemático", "Voto a distancia que la Mesa del Congreso autoriza en casos tasados (por ejemplo, embarazo, maternidad o paternidad, o enfermedad grave). Cuenta como voto emitido."],
  "entrada en vigor": ["Entrada en vigor", "Momento a partir del cual una norma se aplica. Puede ser el día siguiente a su publicación, una fecha concreta o distinta para cada parte de la norma."],
  "preámbulo": ["Preámbulo o exposición de motivos", "Texto con el que empieza una norma, donde quien la aprueba explica por qué y para qué. Ayuda a interpretarla, pero no contiene obligaciones."],
  "legislación consolidada": ["Legislación consolidada", "Versión actualizada de una norma que elabora el BOE incorporando todos los cambios posteriores, con su historial de versiones."],
  "grupo mixto": ["Grupo Mixto", "Grupo parlamentario que reúne a diputados de partidos que no tienen grupo propio. Sus miembros suelen votar de forma distinta entre sí."],
};
const TIPO_A_TERMINO = {
  "Ley": "ley", "Ley Orgánica": "ley orgánica", "Real Decreto-ley": "real decreto-ley", "Decreto-ley": "real decreto-ley",
  "Real Decreto": "real decreto", "Orden": "orden", "Resolución": "resolución",
  "Corrección (errores o erratas)": "corrección de errores", "Acuerdo Internacional": "acuerdo internacional",
};
let contadorTerminos = 0;

function termino(texto, clave) {
  // Texto con un botón ⓘ que abre la definición (popover nativo; accesible con teclado).
  const def = GLOSARIO[clave];
  if (!def) return el("span", { texto });
  const id = `def-${++contadorTerminos}`;
  const boton = el("button", { type: "button", clase: "boton-termino", popovertarget: id, "aria-label": `Qué significa «${def[0]}»`, texto: "ⓘ" });
  const caja = el("div", { id, popover: "auto", clase: "definicion", role: "note" },
    el("strong", { texto: def[0] }), el("p", { texto: def[1] }));
  return el("span", { clase: "termino" }, texto, " ", boton, caja);
}

function pintarGlosario() {
  const destino = $("glosario");
  if (!destino) return;
  destino.replaceChildren(...Object.values(GLOSARIO)
    .sort((a, b) => a[0].localeCompare(b[0], "es"))
    .flatMap(([t, d]) => [el("dt", { texto: t }), el("dd", { texto: d })]));
}

// ---------- Utilidades ----------

function el(etiqueta, props = {}, ...hijos) {
  const nodo = document.createElement(etiqueta);
  for (const [clave, valor] of Object.entries(props)) {
    if (clave === "texto") nodo.textContent = valor;
    else if (clave === "clase") nodo.className = valor;
    else if (clave.startsWith("on")) nodo.addEventListener(clave.slice(2), valor);
    else nodo.setAttribute(clave, valor);
  }
  for (const hijo of hijos) if (hijo != null) nodo.append(hijo);
  return nodo;
}

const miles = (n) => n.toLocaleString("es-ES", { useGrouping: "always" });

function aFecha(iso) {
  const [a, m, d] = iso.split("-").map(Number);
  return new Date(a, m - 1, d);
}
const fechaCorta = (iso) => aFecha(iso).toLocaleDateString("es-ES", { day: "numeric", month: "short" });
const diaSemana = (iso) => aFecha(iso).toLocaleDateString("es-ES", { weekday: "long", day: "numeric" });
const fechaLarga = (iso) => aFecha(iso).toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

function variable(nombre) {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
}

function luminancia(hex) {
  const c = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(c.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

const titular = (n) => (n.ficha && n.ficha.titulo_llano) || n.titulo;
const porRelevancia = (a, b) => b.relevancia - a.relevancia || b.fecha.localeCompare(a.fecha) || a.id.localeCompare(b.id);

// ---------- Datos de la edición elegida ----------

const edicionActual = () => estado.datos.ediciones.find((e) => e.id === estado.edicion);
const diasEdicion = () => {
  const e = edicionActual();
  return estado.datos.dias.filter((d) => d.fecha >= e.desde && d.fecha <= e.hasta);
};
const normasEdicion = () => estado.datos.normas.filter((n) => n.semana === estado.edicion);

function enlaceNorma(n, clase, contenido) {
  return el("a", {
    clase, href: `#${n.id}`,
    onclick: (e) => { e.preventDefault(); abrirArticulo(n.id); },
  }, ...contenido);
}

function etiquetas(n) {
  // Antetítulo de texto (sin cápsulas): a quién afecta, tema y, si no es estatal, el ámbito.
  const partes = [n.tema];
  if (n.ambito && n.ambito !== "Estatal") partes.push(n.ambito);
  return el("p", { clase: "antetitulo" },
    el("span", { clase: `antetitulo-impacto impacto-${n.impacto}`, texto: nombreImpacto(n.impacto) }),
    ` · ${partes.join(" · ")}`);
}

function primeraFrase(texto, max = 230) {
  const t = (texto || "").replace(/\s+/g, " ").trim();
  const fin = t.search(/\.\s/);
  const frase = fin > 40 ? t.slice(0, fin + 1) : t;
  return frase.length > max ? `${frase.slice(0, max).replace(/\s\S*$/, "")}…` : frase;
}

// ---------- Cabecera y «En cifras» ----------

function pintarMancheta() {
  const e = edicionActual();
  $("edicion-etiqueta").textContent = e.etiqueta;
  $("edicion-estado").hidden = !e.en_curso;
  $("edicion-estado").textContent = e.en_curso ? "Edición en curso: se completa cada día" : "";
  const sel = $("f-edicion");
  sel.replaceChildren(...estado.datos.ediciones.map((x) => el("option", { value: x.id, texto: x.etiqueta })));
  sel.value = e.id;
  sel.closest("label").hidden = estado.datos.ediciones.length < 2;

  const r = e.resumen;
  $("frase").textContent = r.frase;
  $("c-total").textContent = miles(r.total_publicaciones);
  $("c-normas").textContent = miles(r.normas_generales);
  $("c-pct").textContent = r.porcentaje_normas;
  $("c-directo").textContent = miles(r.impacto_directo);

  const generado = new Date(estado.datos.generado);
  $("generado").textContent = `Actualizado el ${generado.toLocaleString("es-ES", { dateStyle: "long", timeStyle: "short" })}.`;
  const n = estado.datos.normas.length;
  const ok = estado.datos.resumen.fichas_verificadas;
  $("estado-fichas").textContent = ok === 0
    ? `Ahora mismo las ${n} fichas están pendientes.`
    : `Ahora mismo ${ok} de ${n} fichas tienen resumen automático experimental; el resto están pendientes porque el resumen no superó las comprobaciones.`;
}

// ---------- Portada ----------

function elegirPortada(normas) {
  const candidatas = normas.filter((n) => n.impacto !== "Técnico").sort(porRelevancia);
  if (!candidatas.length) return { principal: null, secundarios: [] };
  const [principal, ...resto] = candidatas;
  // Secundarios: los más relevantes, procurando no repetir tema.
  const secundarios = [];
  const temasUsados = new Set([principal.tema]);
  for (const n of resto) {
    if (secundarios.length === NUM_SECUNDARIOS) break;
    if (!temasUsados.has(n.tema)) { secundarios.push(n); temasUsados.add(n.tema); }
  }
  for (const n of resto) {
    if (secundarios.length === NUM_SECUNDARIOS) break;
    if (!secundarios.includes(n)) secundarios.push(n);
  }
  return { principal, secundarios };
}

function entradilla(n) {
  const f = n.ficha || {};
  if (f.estado === "ok") return el("p", { clase: "entradilla", texto: f.que_cambia });
  const porque = n.preambulo && n.preambulo.parrafos && n.preambulo.parrafos[0];
  if (porque) {
    return el("p", { clase: "entradilla" },
      el("span", { clase: "entradilla-fuente", texto: "Según su preámbulo: " }), `«${primeraFrase(porque)}»`);
  }
  return null;
}

function pintarPortada(portada) {
  const { principal, secundarios } = portada;
  if (!principal) {
    $("principal").replaceChildren(el("p", { clase: "ayuda", texto: "Esta semana no hay normas que afecten a la ciudadanía o a grupos concretos: todo es gestión interna." }));
    $("secundarios").replaceChildren();
    return;
  }
  $("principal").replaceChildren(...[
    etiquetas(principal),
    el("h2", { clase: "titular-principal" }, enlaceNorma(principal, "", [titular(principal)])),
    entradilla(principal),
    enlaceNorma(principal, "leer-mas", ["Leer la ficha →"]),
  ].filter(Boolean));
  $("secundarios").replaceChildren(...secundarios.map((n) => el("article", { clase: "secundario" },
    etiquetas(n),
    el("h3", { clase: "titular-secundario" }, enlaceNorma(n, "", [titular(n)])),
  )));
}

// ---------- La semana en datos ----------

function pintarPiezas() {
  const piezas = edicionActual().piezas || [];
  $("piezas-seccion").hidden = piezas.length === 0;
  $("piezas").replaceChildren(...piezas.map((p) => el("button", {
    type: "button", clase: p.votaciones ? "pieza pieza-congreso" : "pieza",
    onclick: () => {
      estado.filtroIds = { texto: `${p.cifra} ${p.texto}`, ids: p.ids };
      for (const k of Object.keys(estado.filtros)) estado.filtros[k] = "";
      actualizar();
      $("normas").scrollIntoView({ behavior: "smooth", block: "start" });
    },
  }, el("span", { clase: "pieza-cifra", texto: miles(p.cifra) }), el("span", { clase: "pieza-texto", texto: p.texto }))));
}

// ---------- Secciones por tema y breves ----------

function pintarSecciones(normas, portada) {
  const enPortada = new Set([portada.principal, ...portada.secundarios].filter(Boolean).map((n) => n.id));
  const bloques = estado.datos.temas.map((tema) => {
    const delTema = normas.filter((n) => n.tema === tema && n.impacto !== "Técnico" && !enPortada.has(n.id)).sort(porRelevancia);
    if (!delTema.length) return null;
    const item = (n) => el("li", {},
      enlaceNorma(n, "titular-lista", [titular(n)]),
      el("span", { clase: "meta-lista", texto: nombreImpacto(n.impacto) + (n.ambito !== "Estatal" ? ` · ${n.ambito}` : "") }));
    const lista = el("ul", {}, ...delTema.slice(0, MAX_POR_TEMA).map(item));
    const seccion = el("section", { clase: "seccion-tema" }, el("h3", { clase: "seccion-titulo", texto: tema }), lista);
    if (delTema.length > MAX_POR_TEMA) {
      const boton = el("button", { type: "button", clase: "boton-enlace ver-mas", texto: `Ver ${delTema.length - MAX_POR_TEMA} más` });
      boton.addEventListener("click", () => { lista.append(...delTema.slice(MAX_POR_TEMA).map(item)); boton.remove(); });
      seccion.append(boton);
    }
    return seccion;
  }).filter(Boolean);
  $("secciones").replaceChildren(...(bloques.length ? bloques
    : [el("p", { clase: "ayuda", texto: "El resto de normas de esta semana ya están en portada o son de gestión interna." })]));
}

function pintarBreves(normas) {
  const breves = normas.filter((n) => n.impacto === "Técnico").sort(porRelevancia);
  const visibles = estado.brevesAbiertos ? breves : breves.slice(0, MAX_BREVES);
  $("breves").replaceChildren(...visibles.map((n) => el("li", {}, enlaceNorma(n, "breve", [titular(n)]))));
  const boton = $("ver-breves");
  boton.hidden = breves.length <= MAX_BREVES;
  boton.textContent = estado.brevesAbiertos ? "Ver menos" : `Ver las ${breves.length} normas de gestión interna`;
}

// ---------- Frases de lectura ----------

function nombreCorto(seccion) {
  const nombres = { I: "normas generales", "II.A": "nombramientos", "II.B": "oposiciones y concursos",
    III: "otras disposiciones", IV: "decisiones de justicia", V: "anuncios" };
  return nombres[seccion.codigo] || seccion.nombre;
}

function fraseGrafico(dias) {
  if (!dias.length) return "";
  const totales = estado.datos.secciones.map((s) => ({ ...s, total: dias.reduce((a, d) => a + d.recuento[s.codigo], 0) }));
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

// ---------- Gráficos ----------

function seriesSecciones(dias, mini) {
  const superficie = variable("--superficie");
  return estado.datos.secciones.map((s, i) => ({
    label: s.nombre,
    data: dias.map((d) => d.recuento[s.codigo]),
    backgroundColor: variable(`--s${i + 1}`),
    borderColor: superficie,
    borderWidth: { top: mini ? 1 : 2 },
    borderSkipped: "start",
    borderRadius: i === estado.datos.secciones.length - 1 ? { topLeft: 3, topRight: 3 } : 0,
    maxBarThickness: mini ? 14 : 24,
  }));
}

function pintarGraficos() {
  const dias = diasEdicion();
  if (!window.Chart) {
    $("grafico").replaceWith(el("p", { clase: "ayuda", texto: "No se ha podido cargar la librería del gráfico. Los datos están en la tabla de abajo." }));
    if ($("grafico-mini")) $("grafico-mini").closest(".grafico-mini").hidden = true;
    return;
  }
  for (const g of Object.values(estado.graficos)) g.destroy();
  const ejes = (mini) => ({
    x: { stacked: true, grid: { display: false }, ticks: { color: variable("--tinta-2"), font: { size: mini ? 10 : 12 } }, border: { color: variable("--linea") } },
    y: { stacked: true, beginAtZero: true, display: !mini, grid: { color: variable("--linea") }, ticks: { color: variable("--tinta-2"), precision: 0 }, border: { display: false } },
  });
  const tooltip = {
    callbacks: {
      title: (items) => fechaLarga(dias[items[0].dataIndex].fecha),
      label: (item) => ` ${miles(item.raw)}  ${item.dataset.label}`,
      footer: (items) => `Total: ${miles(items.reduce((s, i) => s + i.raw, 0))}`,
    },
  };
  const etiquetasDias = dias.map((d) => aFecha(d.fecha).toLocaleDateString("es-ES", { weekday: "short", day: "numeric" }));
  estado.graficos.grande = new Chart($("grafico"), {
    type: "bar",
    data: { labels: etiquetasDias, datasets: seriesSecciones(dias, false) },
    options: {
      responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
      scales: ejes(false),
      plugins: {
        legend: { position: "top", align: "start", labels: { color: variable("--tinta"), boxWidth: 12, boxHeight: 12, useBorderRadius: true, borderRadius: 2 } },
        tooltip,
      },
    },
  });
  if (!$("grafico-mini")) return;
  estado.graficos.mini = new Chart($("grafico-mini"), {
    type: "bar",
    data: { labels: etiquetasDias, datasets: seriesSecciones(dias, true) },
    options: {
      responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
      scales: ejes(true), plugins: { legend: { display: false }, tooltip },
    },
  });
}

function pintarTablaDias() {
  const { secciones } = estado.datos;
  $("tabla-dias").replaceChildren(
    el("thead", {}, el("tr", {}, el("th", { texto: "Día" }), ...secciones.map((s) => el("th", { texto: s.codigo })), el("th", { texto: "Total" }))),
    el("tbody", {}, ...diasEdicion().map((d) => el("tr", {},
      el("td", { texto: fechaCorta(d.fecha) }),
      ...secciones.map((s) => el("td", { texto: miles(d.recuento[s.codigo]) })),
      el("td", { texto: miles(Object.values(d.recuento).reduce((a, b) => a + b, 0)) }),
    ))),
  );
}

function pintarLeyendaImpacto() {
  // Se ve solo en pantallas estrechas, donde las cabeceras de la matriz no caben.
  $("leyenda-impacto").replaceChildren(...estado.datos.impactos.flatMap((i) => [
    el("dt", { texto: nombreImpacto(i) }),
    el("dd", { texto: IMPACTO[i] ? `${IMPACTO[i].explicacion} (${IMPACTO[i].ejemplo})` : "" }),
  ]));
}

// ---------- Filtros ----------

function normasFiltradas({ ignorar = [] } = {}) {
  const f = estado.filtros;
  const ids = estado.filtroIds && !ignorar.includes("ids") ? new Set(estado.filtroIds.ids) : null;
  return normasEdicion().filter((n) =>
    (!ids || ids.has(n.id)) &&
    (ignorar.includes("fecha") || !f.fecha || n.fecha === f.fecha) &&
    (ignorar.includes("tema") || !f.tema || n.tema === f.tema) &&
    (ignorar.includes("impacto") || !f.impacto || n.impacto === f.impacto) &&
    (ignorar.includes("ambito") || !f.ambito || n.ambito === f.ambito));
}

function rellenarSelect(select, todas, opciones, formato = (x) => x) {
  select.replaceChildren(el("option", { value: "", texto: todas }), ...opciones.map((o) => el("option", { value: o, texto: formato(o) })));
}

function rellenarFiltros() {
  const normas = normasEdicion();
  const fechas = [...new Set(normas.map((n) => n.fecha))].sort().reverse();
  const ambitos = [...new Set(normas.map((n) => n.ambito))].sort((a, b) => (a === "Estatal" ? -1 : b === "Estatal" ? 1 : a.localeCompare(b, "es")));
  rellenarSelect($("f-fecha"), "Todos los días", fechas, diaSemana);
  rellenarSelect($("f-tema"), "Todos los temas", estado.datos.temas);
  rellenarSelect($("f-impacto"), "Todos", estado.datos.impactos, nombreImpacto);
  rellenarSelect($("f-ambito"), "Todos", ambitos);
}

function prepararControles() {
  for (const clave of Object.keys(estado.filtros)) {
    $(`f-${clave}`).addEventListener("change", (e) => { estado.filtros[clave] = e.target.value; estado.filtroIds = null; actualizar(); });
  }
  $("filtros").addEventListener("reset", () => {
    setTimeout(() => { for (const k of Object.keys(estado.filtros)) estado.filtros[k] = ""; estado.filtroIds = null; actualizar(); });
  });
  $("f-edicion").addEventListener("change", (e) => cambiarEdicion(e.target.value));
  $("ver-breves").addEventListener("click", () => { estado.brevesAbiertos = !estado.brevesAbiertos; pintarBreves(normasEdicion()); });
}

function sincronizarSelects() {
  for (const [clave, valor] of Object.entries(estado.filtros)) $(`f-${clave}`).value = valor;
}

// ---------- Matriz tema × impacto ----------

function pintarMatriz() {
  const { temas, impactos } = estado.datos;
  const base = normasFiltradas({ ignorar: ["tema", "impacto", "ids"] }); // respeta día y ámbito
  $("lectura-matriz").textContent = fraseMatriz(base);
  const cuenta = (t, i) => base.filter((n) => n.tema === t && n.impacto === i).length;
  const maximo = Math.max(1, ...temas.flatMap((t) => impactos.map((i) => cuenta(t, i))));

  const celda = (tema, impacto) => {
    const n = cuenta(tema, impacto);
    const paso = n === 0 ? 0 : Math.max(1, Math.ceil((n / maximo) * 6));
    const fondo = variable(`--m${paso}`);
    const activa = !estado.filtroIds && estado.filtros.tema === tema && estado.filtros.impacto === impacto;
    const boton = el("button", {
      type: "button",
      clase: "celda" + (paso > 0 && luminancia(fondo) < 0.3 ? " clara" : ""),
      "aria-pressed": String(activa),
      "aria-label": `${n} ${n === 1 ? "norma" : "normas"} de ${tema} · ${nombreImpacto(impacto)}`,
      title: `${tema} · ${nombreImpacto(impacto)}: ${n}`,
      texto: String(n),
      onclick: () => {
        estado.filtroIds = null;
        estado.filtros.tema = activa ? "" : tema;
        estado.filtros.impacto = activa ? "" : impacto;
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

function etiquetaEstado(ficha) {
  const ok = ficha && ficha.estado === "ok";
  return el("span", {
    clase: `etiqueta ${ok ? "experimental" : "pendiente"}`,
    texto: ok ? "⚠ Resumen automático (experimental)" : "⏳ Resumen pendiente",
  });
}

function pintarLista() {
  const normas = normasFiltradas().sort((a, b) => b.fecha.localeCompare(a.fecha) || porRelevancia(a, b));
  const total = normasEdicion().length;
  const contador = $("contador");
  if (estado.filtroIds) {
    contador.replaceChildren(`Mostrando: ${estado.filtroIds.texto}. `,
      el("button", { type: "button", clase: "boton-enlace", texto: "Ver todas", onclick: () => { estado.filtroIds = null; actualizar(); } }));
  } else {
    contador.textContent = normas.length === total
      ? `${total} normas generales esta semana.`
      : `${normas.length} de ${total} normas con estos filtros.`;
  }

  const lista = $("lista");
  if (normas.length === 0) {
    lista.replaceChildren(el("li", {}, el("p", { clase: "ayuda", texto: "No hay normas con estos filtros." })));
    return;
  }
  lista.replaceChildren(...normas.map((n) => el("li", {}, el("button", {
    type: "button",
    onclick: () => abrirArticulo(n.id),
  },
  el("span", { clase: "t", texto: titular(n) }),
  el("span", { clase: "m", texto: `${fechaCorta(n.fecha)} · ${n.rango || ""} · ${n.ambito}` }),
  el("span", { clase: "m", texto: `${n.tema} · ${nombreImpacto(n.impacto)}${n.ficha && n.ficha.estado === "ok" ? " · resumen automático" : ""}` }),
  ))));
}

// ---------- Votaciones del Congreso ----------
// Colores: polaridad sí/no (azul/rojo) con neutros para abstención y no vota.
const OPCIONES_VOTO = [
  ["Sí", "--voto-si"], ["No", "--voto-no"], ["Abstención", "--voto-abst"], ["No vota", "--voto-nv"],
];

function barraVotos(votos, { etiqueta = "" } = {}) {
  const total = OPCIONES_VOTO.reduce((a, [k]) => a + (votos[k] || 0), 0) || 1;
  const texto = OPCIONES_VOTO.filter(([k]) => votos[k]).map(([k]) => `${k}: ${votos[k]}`).join(", ");
  const barra = el("div", { clase: "barra-votos", role: "img", "aria-label": `${etiqueta} ${texto}`.trim(), title: texto });
  for (const [k, color] of OPCIONES_VOTO) {
    if (!votos[k]) continue;
    const seg = el("span", { clase: "segmento" });
    seg.style.width = `${(100 * votos[k]) / total}%`;
    seg.style.background = `var(${color})`;
    barra.append(seg);
  }
  return barra;
}

function leyendaVotos() {
  return el("p", { clase: "leyenda-votos" }, ...OPCIONES_VOTO.map(([k, color]) => {
    const muestra = el("span", { clase: "muestra" });
    muestra.style.background = `var(${color})`;
    return el("span", {}, muestra, k);
  }));
}

function resumenVotacion(c) {
  const t = c.totales;
  const fecha = aFecha(c.fecha).toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" });
  return `${c.resultado === "convalidado" ? "Convalidado" : "Derogado (rechazado)"} por el Pleno el ${fecha}: ` +
    `${t.afavor} sí, ${t.enContra} no` + (t.noVotan == null ? ` y ${t.abstenciones} abstenciones` : `, ${t.abstenciones} abstenciones y ${t.noVotan} no votan`) +
    (c.telematicos ? ` (${c.telematicos} votos telemáticos).` : ".");
}

const PLURAL_VOTO = { "Sí": "sí", "No": "no", "Abstención": "abstenciones", "No vota": "no votan" };
const cifrasVotos = (votos) => OPCIONES_VOTO.filter(([k]) => votos[k])
  .map(([k]) => `${votos[k]} ${votos[k] === 1 ? k.toLowerCase() : PLURAL_VOTO[k]}`);

function bloqueGrupos(c) {
  const filas = c.grupos.map((g) => {
    const fila = el("div", { clase: "fila-grupo" },
      el("span", { clase: "nombre-grupo", title: g.nombre_completo, texto: g.nombre }),
      barraVotos(g.votos, { etiqueta: g.nombre }),
      el("span", { clase: "cifras-grupo", texto: cifrasVotos(g.votos).join(" · ") }));
    if (!g.por_lista) return fila;
    const listas = Object.entries(g.por_lista).map(([lista, votos]) => `${lista}: ${cifrasVotos(votos).join(", ")}`);
    return el("div", {}, fila, el("p", { clase: "detalle-listas", texto: `Por lista electoral: ${listas.join(" · ")}` }));
  });
  return el("div", { clase: "grupos-votacion" }, ...filas);
}

function seccionCongreso(congreso) {
  const hijos = [el("h3", { texto: "Cómo votó el Congreso" })];
  const c = congreso.convalidacion;
  if (!c) {
    hijos.push(el("p", { clase: "ayuda", texto: congreso.estado === "pendiente de votación"
      ? `Pendiente de votación en el Congreso. ${congreso.nota || ""}`
      : `No hay datos de la votación. ${congreso.nota || ""}` }));
    hijos.push(el("p", { clase: "nota" }, "El Congreso debe ", termino("convalidarlo", "convalidar"), " o ",
      termino("derogarlo", "derogar"), " en 30 días; con las Cortes disueltas lo hace la ", termino("Diputación Permanente", "diputación permanente"), "."));
    return el("section", { clase: "congreso" }, ...hijos);
  }
  hijos.push(el("p", { clase: `resultado-votacion ${c.resultado}`, texto: resumenVotacion(c) }));
  hijos.push(el("p", { clase: "nota" }, margen(c), " ",
    c.resultado === "convalidado" ? termino("¿Qué es convalidar?", "convalidar") : termino("¿Qué es derogar?", "derogar")));
  if (c.solo_totales) {
    const t = c.totales;
    hijos.push(leyendaVotos(), barraVotos({ "Sí": t.afavor, "No": t.enContra, "Abstención": t.abstenciones }, { etiqueta: "Total" }),
      el("p", { clase: "nota" }, c.nota || "", " ", /llamamiento/.test(c.nota || "") ? termino("", "votación por llamamiento") : ""));
  } else {
    hijos.push(leyendaVotos(), bloqueGrupos(c));
  }
  if (congreso.tramitacion) {
    const t = congreso.tramitacion;
    hijos.push(el("p", { clase: "nota" }, `Además, ${t.resultado} (${t.totales.afavor} sí, ${t.totales.enContra} no): ` +
      (t.resultado.startsWith("se tramita") ? "el Congreso podrá modificarlo con enmiendas. " : "queda tal como lo aprobó el Gobierno. "),
      termino("", "tramitar como proyecto de ley")));
  }
  const enlaces = [];
  if (c.fuente_pdf) enlaces.push(el("a", { href: c.fuente_pdf, target: "_blank", rel: "noopener", texto: "Votación oficial (PDF)" }));
  hijos.push(el("p", { clase: "nota" },
    ...(c.solo_totales ? [] : ["Voto por grupo parlamentario; el ", termino("voto telemático", "voto telemático"),
      " cuenta como voto. En el ", termino("Grupo Mixto", "grupo mixto"), " se desglosa por lista cuando votan distinto. No se muestran votos individuales. "]),
    ...enlaces));
  return el("section", { clase: "congreso" }, ...hijos);
}

function pintarVotacionesSemana() {
  const votaciones = edicionActual().votaciones || [];
  $("bloque-votaciones").hidden = votaciones.length === 0;
  $("votaciones-semana").replaceChildren(...votaciones.map((v) => {
    const c = v.convalidacion;
    const t = c.totales;
    return el("article", { clase: "votacion-semana" },
      el("p", { clase: `resultado-votacion ${c.resultado}`, texto: `Real Decreto-ley ${v.rdl}: ${c.resultado.toUpperCase()}` }),
      el("p", { clase: "titulo-votacion", texto: v.titulo }),
      barraVotos({ "Sí": t.afavor, "No": t.enContra, "Abstención": t.abstenciones, "No vota": t.noVotan },
        { etiqueta: `Real Decreto-ley ${v.rdl}` }),
      el("p", { clase: "nota", texto: resumenVotacion(c) }),
      c.solo_totales ? el("p", { clase: "nota", texto: c.nota || "" })
        : el("details", {}, el("summary", { texto: "Ver el voto por grupos" }), leyendaVotos(), bloqueGrupos(c)));
  }));
}

// ---------- Vida de la norma (legislación consolidada del BOE) ----------

const URL_DOC = (id) => `https://www.boe.es/buscar/doc.php?id=${id}`;
const fechaMedia = (iso) => aFecha(iso).toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" });

function enlaceBoe(id, texto) {
  return id ? el("a", { href: URL_DOC(id), target: "_blank", rel: "noopener", texto }) : el("span", { texto });
}

function seccionVida(n) {
  const v = n.vida;
  if (!v || !v.consolidada) return null;
  const hitos = [el("li", { clase: "hito hito-inicio" },
    el("span", { clase: "hito-fecha", texto: fechaMedia(n.fecha) }),
    el("span", { clase: "hito-texto", texto: "Se publica en el BOE." }))];
  const recibidos = Object.fromEntries((n.cambios_recibidos || []).map((c) => [c.por, c.bloques]));
  for (const h of v.despues || []) {
    const hito = el("li", { clase: "hito" },
      el("span", { clase: "hito-fecha", texto: h.fecha ? fechaMedia(h.fecha) : "Después" }),
      el("span", { clase: "hito-texto" }, el("strong", { texto: `${h.relacion} ` }), enlaceBoe(h.id, h.texto)));
    if (recibidos[h.id]) {
      hito.append(el("details", { clase: "cambio-norma" }, el("summary", { texto: "Ver el antes y el después" }),
        leyendaCambios(), ...recibidos[h.id].map(vistaBloque)));
      delete recibidos[h.id];
    }
    hitos.push(hito);
  }
  const bloque = el("section", { clase: "vida" },
    el("h3", { texto: "Qué ha pasado después" }),
    el("ol", { clase: "linea-tiempo" }, ...hitos));
  if (!(v.despues || []).length) {
    bloque.append(el("p", { clase: "nota", texto: "Por ahora, el BOE no registra cambios posteriores en esta norma." }));
  }
  const otrasNotas = (v.notas || []).filter((t) => t !== v.entrada_en_vigor);
  if (otrasNotas.length) {
    bloque.append(el("ul", { clase: "notas-boe" }, ...otrasNotas.map((t) => el("li", { texto: `Nota del BOE: ${t}` }))));
  }
  const conComparacion = new Set((n.cambios || []).filter((c) => c.bloques && c.bloques.length).map((c) => c.norma));
  const resto = (v.modifica || []).filter((m) => !conComparacion.has(m.id));
  if (resto.length) {
    bloque.append(el("details", { clase: "modifica" },
      el("summary", { texto: conComparacion.size ? `Otros cambios en otras normas (${resto.length})` : `Qué cambia en otras normas (${resto.length})` }),
      el("ul", {}, ...resto.map((m) => el("li", {}, el("strong", { texto: `${m.relacion} ` }), enlaceBoe(m.id, m.texto))))));
  }
  bloque.append(el("p", { clase: "nota" }, "Según el análisis de la legislación consolidada del BOE (solo relaciones expresas), consultado el ",
    fechaMedia(v.consultado), ". ", el("a", { href: v.enlace, target: "_blank", rel: "noopener", texto: "Texto consolidado" }), " ", termino("", "legislación consolidada")));
  return bloque;
}

// ---------- Antes y después (versiones del texto consolidado) ----------

function leyendaCambios() {
  return el("p", { clase: "leyenda-cambios" },
    el("del", { texto: "Tachado" }), ": texto que desaparece · ", el("ins", { texto: "Subrayado" }), ": texto nuevo");
}

function vistaBloque(b) {
  const filas = b.comparacion.map((x) => {
    if ("iguales" in x) {
      return el("p", { clase: "cambio-iguales", texto: `… ${x.iguales} ${x.iguales === 1 ? "párrafo sin cambios" : "párrafos sin cambios"} …` });
    }
    if ("añadido" in x) return el("p", { clase: "cambio-parrafo" }, el("ins", { texto: x["añadido"] }));
    if ("eliminado" in x) return el("p", { clase: "cambio-parrafo" }, el("del", { texto: x.eliminado }));
    const p = el("p", { clase: "cambio-parrafo" });
    x.cambiado.forEach(([op, t], i) => {
      if (i) p.append(" ");
      p.append(op === "=" ? t : el(op === "+" ? "ins" : "del", { texto: t }));
    });
    return p;
  });
  const cabecera = [el("strong", { texto: b.titulo }), b.nuevo ? " (nuevo)" : ""];
  if (b.en_vigor_desde) cabecera.push(` · en vigor desde el ${fechaMedia(b.en_vigor_desde)}`);
  const bloque = el("div", { clase: "cambio-bloque" }, el("p", { clase: "cambio-titulo" }, ...cabecera), ...filas);
  if (b.hasta) {
    bloque.append(el("p", { clase: "nota" }, `Esta redacción estuvo en vigor hasta el ${fechaMedia(b.hasta)}: después la cambió `,
      enlaceBoe(b.cambiado_despues_por, "otra norma"), "."));
  }
  return bloque;
}

function seccionCambios(n) {
  const cambios = (n.cambios || []).filter((c) => c.bloques && c.bloques.length);
  if (!cambios.length) return null;
  const sec = el("section", { clase: "cambios" },
    el("h3", {}, "Qué cambia en concreto ", termino("", "legislación consolidada")),
    el("p", { clase: "nota", texto: "El texto de los artículos que esta norma cambia en otras, antes y después, según las versiones de la legislación consolidada del BOE." }),
    leyendaCambios());
  for (const c of cambios) {
    sec.append(el("details", { clase: "cambio-norma" },
      el("summary", { texto: `${c.relacion} ${c.referencia} (${c.bloques.length} ${c.bloques.length === 1 ? "artículo" : "artículos"})` }),
      ...c.bloques.map(vistaBloque),
      c.recortado ? el("p", { clase: "nota", texto: "Hay más cambios: consulta el texto consolidado completo en el BOE." }) : null));
  }
  return sec;
}

// ---------- Contexto ----------

function ordinal(n) { return `${n}.º`; }

function lineaTipo(n) {
  // "Real decreto-ley ⓘ · Jefatura del Estado · Es el 22.º real decreto-ley de 2026."
  const partes = [];
  const clave = TIPO_A_TERMINO[n.rango];
  if (n.rango) partes.push(clave ? termino(n.rango, clave) : el("span", { texto: n.rango }));
  if (n.organo) partes.push(el("span", { texto: n.organo }));
  const m = (n.numero_oficial || "").match(/^(\d+)\/(\d{4})$/);
  if (m && ["Real Decreto-ley", "Ley", "Ley Orgánica"].includes(n.rango) && n.ambito === "Estatal") {
    const tipo = n.rango === "Real Decreto-ley" ? "real decreto-ley" : n.rango === "Ley" ? "ley estatal" : "ley orgánica";
    partes.push(el("span", { texto: `Es ${n.rango === "Ley" ? "la" : n.rango === "Ley Orgánica" ? "la" : "el"} ${ordinal(Number(m[1]))} ${tipo} de ${m[2]}` }));
  }
  const linea = el("p", { clase: "linea-tipo" });
  partes.forEach((p, i) => { if (i) linea.append(" · "); linea.append(p); });
  return linea;
}

function margen(c) {
  const d = c.totales.afavor - c.totales.enContra;
  const votos = (k) => `${k} ${k === 1 ? "voto" : "votos"}`;
  return d > 0 ? `Salió adelante por ${votos(d)} de diferencia.` : d < 0 ? `Fue rechazado por ${votos(-d)} de diferencia.` : "Empate.";
}

// ---------- Ficha (artículo) ----------

function pintarFicha(n) {
  const ficha = n.ficha || {};
  const ok = ficha.estado === "ok";
  const hijos = [etiquetas(n), el("h2", { id: "ficha-titulo", clase: "articulo-titular", texto: titular(n) })];
  if (ok) hijos.push(etiquetaEstado(ficha));
  hijos.push(lineaTipo(n));
  if (n.vida && n.vida.entrada_en_vigor) {
    hijos.push(el("p", { clase: "dato-clave" }, el("strong", {}, termino("Desde cuándo", "entrada en vigor"), " (según el BOE): "), n.vida.entrada_en_vigor));
  }

  if (ok) {
    hijos.push(el("p", { clase: "aviso-ia", role: "note" },
      el("strong", { texto: "Puede contener errores. " }),
      ficha.aviso_ia || "Resumen automático experimental: compruébalo siempre en el texto oficial."));
    const apartados = [
      ["Qué cambia", "que_cambia"],
      ["A quién afecta", "a_quien_afecta"],
      ["Desde cuándo", "desde_cuando"],
      ["Qué tienes que hacer", "que_hacer"],
    ];
    const citas = ficha.citas || {};
    hijos.push(el("dl", {}, ...apartados.flatMap(([titulo, campo]) => {
      const dd = el("dd", {}, el("span", { texto: ficha[campo] }));
      const fuentes = Array.isArray(citas[campo]) ? citas[campo] : [];
      if (fuentes.length) {
        const etiqueta = fuentes.length === 1 ? `párrafo ${fuentes[0].parrafo}` : `párrafos ${fuentes.map((c) => c.parrafo).join(", ")}`;
        dd.append(el("details", { clase: "cita" },
          el("summary", { texto: `De dónde sale (${etiqueta} del texto oficial)` }),
          ...fuentes.map((c) => el("blockquote", { texto: c.texto }))));
      }
      return [el("dt", { texto: titulo }), dd];
    })));
  } else {
    hijos.push(el("p", { clase: "ayuda", texto: "Todavía no hay un resumen de esta norma que haya superado las comprobaciones. El titular es una versión simplificada del título oficial." }));
  }

  if (n.preambulo && n.preambulo.parrafos && n.preambulo.parrafos.length) {
    const [primero, ...resto] = n.preambulo.parrafos;
    const bloque = el("section", { clase: "porque" },
      el("h3", {}, "Por qué se aprueba, según el propio texto ", termino("", "preámbulo")),
      el("p", { clase: "nota", texto: "Párrafos copiados literalmente del preámbulo, donde quien aprueba la norma explica sus motivos." }),
      el("blockquote", { texto: primero }));
    if (resto.length) {
      bloque.append(el("details", {}, el("summary", { texto: `Seguir leyendo (${resto.length} ${resto.length === 1 ? "párrafo" : "párrafos"} más)` }),
        ...resto.map((p) => el("blockquote", { texto: p }))));
    }
    if (n.preambulo.recortado) bloque.append(el("p", { clase: "nota", texto: "El preámbulo completo sigue en el texto oficial." }));
    hijos.push(bloque);
  }

  hijos.push(el("p", { clase: "oficial" }, el("strong", { texto: "Título oficial: " }), n.titulo));
  hijos.push(el("a", { clase: "enlace", href: ficha.enlace || n.url_html, target: "_blank", rel: "noopener", texto: "Leer el texto oficial en boe.es →" }));

  const datos = [
    ["Publicada", fechaLarga(n.fecha)],
    ["Tipo", n.rango],
    ["Órgano", n.organo],
    ["Ámbito", n.ambito],
    ["Tema", n.tema],
    ["A quién afecta", nombreImpacto(n.impacto)],
    ["Identificador", n.id],
  ];
  const cambios = seccionCambios(n);
  if (cambios) hijos.push(cambios);
  const vida = seccionVida(n);
  if (vida) hijos.push(vida);
  if (n.congreso) hijos.push(seccionCongreso(n.congreso));

  const detalles = el("details", { clase: "mas-detalles" }, el("summary", { texto: "Más detalles de la norma" }),
    el("dl", { clase: "datos" }, ...datos.filter(([, v]) => v).flatMap(([t, v]) => [el("dt", { texto: t }), el("dd", { texto: v })])));
  const c = n.clasificacion || {};
  if (c.metodo === "reglas") {
    const motivos = [...(c.motivos_tema || []), ...(c.motivos_impacto || [])].join(" · ");
    detalles.append(el("p", { clase: "motivos", texto: `Clasificada con reglas automáticas: ${motivos}.` }));
  } else if (c.metodo === "ia") {
    detalles.append(el("p", { clase: "motivos", texto: `Clasificada con IA (${c.modelo}): ${c.motivo || ""}` }));
  }
  hijos.push(detalles);

  hijos.push(el("p", { clase: "aviso", texto: ficha.aviso || "Resumen orientativo, no es asesoramiento jurídico. Consulta el texto oficial." }));
  $("ficha").replaceChildren(...hijos);
}

function abrirArticulo(id, actualizarUrl = true) {
  const n = estado.datos.normas.find((x) => x.id === id);
  if (!n) return;
  if (n.semana !== estado.edicion) cambiarEdicion(n.semana);
  pintarFicha(n);
  const dialogo = $("articulo");
  if (!dialogo.open) dialogo.showModal();
  dialogo.scrollTop = 0;
  if (actualizarUrl && location.hash !== `#${id}`) history.pushState(null, "", `#${id}`);
}

function prepararArticulo() {
  const dialogo = $("articulo");
  dialogo.addEventListener("close", () => {
    if (location.hash.startsWith("#BOE-")) history.pushState(null, "", location.pathname + location.search);
  });
  // Cerrar al pulsar fuera del artículo.
  dialogo.addEventListener("click", (e) => { if (e.target === dialogo) dialogo.close(); });
  const desdeUrl = () => {
    const id = location.hash.slice(1);
    if (id.startsWith("BOE-")) abrirArticulo(id, false);
    else if (dialogo.open) dialogo.close();
  };
  window.addEventListener("hashchange", desdeUrl);
  window.addEventListener("popstate", desdeUrl);
  desdeUrl();
}

// ---------- Arranque ----------

function actualizar() {
  sincronizarSelects();
  pintarMatriz();
  pintarLista();
}

function cambiarEdicion(id) {
  estado.edicion = id;
  estado.filtroIds = null;
  estado.brevesAbiertos = false;
  for (const k of Object.keys(estado.filtros)) estado.filtros[k] = "";
  const normas = normasEdicion();
  const portada = elegirPortada(normas);
  pintarMancheta();
  pintarPortada(portada);
  pintarPiezas();
  pintarSecciones(normas, portada);
  pintarBreves(normas);
  $("lectura-grafico").textContent = fraseGrafico(diasEdicion());
  pintarVotacionesSemana();
  pintarTablaDias();
  pintarGraficos();
  rellenarFiltros();
  actualizar();
}

async function iniciar() {
  try {
    const respuesta = await fetch("datos.json", { cache: "no-cache" });
    if (!respuesta.ok) throw new Error(respuesta.status);
    estado.datos = await respuesta.json();
  } catch (error) {
    $("edicion-etiqueta").textContent = "No se han podido cargar los datos. Genera web/datos.json con «python -m boe.exportar» y abre la página con un servidor local.";
    return;
  }
  if (!estado.datos.ediciones || !estado.datos.ediciones.length) {
    $("edicion-etiqueta").textContent = "Todavía no hay ninguna edición.";
    return;
  }
  pintarLeyendaImpacto();
  pintarGlosario();
  prepararControles();
  cambiarEdicion(estado.datos.ediciones[0].id);
  prepararArticulo();
  const bloqueGrafico = $("grafico").closest("details");
  if (bloqueGrafico) bloqueGrafico.addEventListener("toggle", () => { if (bloqueGrafico.open && estado.graficos.grande) estado.graficos.grande.resize(); });

  // Repintar con los colores del modo claro/oscuro cuando cambie.
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { pintarGraficos(); pintarMatriz(); });
}

document.addEventListener("DOMContentLoaded", iniciar);
