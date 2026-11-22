/* El BOE en llano — código común a la portada (index.html) y a la página de
   datos (datos.html).
   Carga los datos por partes (generados por `python -m boe.exportar`):
   - datos/indice.json al empezar (ediciones, recuentos, legislatura),
   - datos/semanas/<semana>.json para la edición que se ve,
   - datos/normas/<id>.json solo al abrir una ficha (preámbulo completo y el
     antes y el después).
   Cada página define window.PAGINA = { pintar() } y este archivo hace el resto:
   cabecera, cambio de edición y la ficha en cuatro preguntas.
   Todo texto que viene de los datos se inserta con textContent (nunca innerHTML). */

"use strict";

const estado = {
  indice: null,
  edicion: null,     // id de la semana elegida, p. ej. "2026-S47"
  normas: [],        // normas de la edición elegida
};
const cache = { semanas: {}, detalles: {} };
const $ = (id) => document.getElementById(id);

// Nombres que se muestran para el impacto (en los datos: Directo / Colectivos / Técnico).
const IMPACTO = {
  Directo: { nombre: "Te afecta a ti", explicacion: "Cambia algo para mucha gente", ejemplo: "p. ej., salario mínimo, impuestos, precios regulados" },
  Colectivos: { nombre: "Afecta a ciertos grupos", explicacion: "Un sector, una profesión o un colectivo", ejemplo: "p. ej., pesca, profesorado, funcionarios" },
  Técnico: { nombre: "Gestión interna", explicacion: "Trámites y organización de la Administración", ejemplo: "p. ej., subvenciones a una entidad, correcciones" },
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
  "caducar": ["Caducar (un proyecto de ley)", "Cuando se disuelven las Cortes, por ejemplo al convocarse elecciones, las iniciativas que no han terminado su tramitación decaen: si se quieren aprobar, tienen que empezar de nuevo en la siguiente legislatura. Si venía de un real decreto-ley ya convalidado, este sigue en vigor tal como lo aprobó el Gobierno."],
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
  return el("span", { clase: "termino" }, texto, texto ? " " : "", boton, caja);
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
const fechaMedia = (iso) => aFecha(iso).toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" });

function variable(nombre) {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
}

const titular = (n) => (n.ficha && n.ficha.titulo_llano) || n.titulo;
const porRelevancia = (a, b) => b.relevancia - a.relevancia || b.fecha.localeCompare(a.fecha) || a.id.localeCompare(b.id);
const plural = (k, uno, varios) => `${miles(k)} ${k === 1 ? uno : varios}`;

function primeraFrase(texto, max = 230) {
  const t = (texto || "").replace(/\s+/g, " ").trim();
  const fin = t.search(/\.\s/);
  const frase = fin > 40 ? t.slice(0, fin + 1) : t;
  return frase.length > max ? `${frase.slice(0, max).replace(/\s\S*$/, "")}…` : frase;
}

// ---------- Carga de datos ----------

async function cargarJson(ruta) {
  const respuesta = await fetch(`datos/${ruta}`, { cache: "no-cache" });
  if (!respuesta.ok) throw new Error(`${ruta}: ${respuesta.status}`);
  return respuesta.json();
}

const edicionPorId = (id) => estado.indice.ediciones.find((e) => e.id === id);
const edicionActual = () => edicionPorId(estado.edicion);
const diasEdicion = () => {
  const e = edicionActual();
  return estado.indice.dias.filter((d) => d.fecha >= e.desde && d.fecha <= e.hasta);
};

function cargarSemana(id) {
  if (!cache.semanas[id]) {
    cache.semanas[id] = cargarJson(edicionPorId(id).archivo).then((d) => d.normas)
      .catch((error) => { delete cache.semanas[id]; throw error; });
  }
  return cache.semanas[id];
}

function cargarDetalle(id) {
  if (!cache.detalles[id]) {
    cache.detalles[id] = cargarJson(`normas/${id}.json`).catch((error) => { delete cache.detalles[id]; throw error; });
  }
  return cache.detalles[id];
}

// ---------- Enlaces entre páginas ----------

function urlPagina(pagina, extra = "") {
  // La edición viaja en ?e= (salvo la más reciente, para que la URL quede limpia).
  const e = estado.edicion && estado.edicion !== estado.indice.ediciones[0].id ? `?e=${estado.edicion}` : "";
  return `${pagina}${e}${extra}`;
}

function actualizarEnlaces() {
  for (const a of document.querySelectorAll("[data-pagina]")) {
    a.href = urlPagina(a.dataset.pagina, a.dataset.ancla ? `#${a.dataset.ancla}` : "");
  }
}

function enlaceNorma(n, clase, contenido) {
  return el("a", {
    clase, href: `#${n.id}`,
    onclick: (e) => { e.preventDefault(); abrirArticulo(n.id); },
  }, ...contenido);
}

function etiquetas(n) {
  // Antetítulo de texto: a quién afecta, tema y, si no es estatal, el ámbito.
  const partes = [n.tema];
  if (n.ambito && n.ambito !== "Estatal") partes.push(n.ambito);
  return el("p", { clase: "antetitulo" },
    el("span", { clase: `antetitulo-impacto impacto-${n.impacto}`, texto: nombreImpacto(n.impacto) }),
    ` · ${partes.join(" · ")}`);
}

// ---------- Cabecera ----------

function pintarMancheta() {
  const e = edicionActual();
  $("edicion-etiqueta").textContent = e.etiqueta;
  $("edicion-estado").hidden = !e.en_curso;
  $("edicion-estado").textContent = e.en_curso ? "Edición en curso: se completa cada día" : "";
  const sel = $("f-edicion");
  sel.replaceChildren(...estado.indice.ediciones.map((x) => el("option", { value: x.id, texto: x.etiqueta })));
  sel.value = e.id;
  sel.closest("label").hidden = estado.indice.ediciones.length < 2;
  const generado = new Date(estado.indice.generado);
  $("generado").textContent = `Actualizado el ${generado.toLocaleString("es-ES", { dateStyle: "long", timeStyle: "short" })}.`;
  actualizarEnlaces();
}

async function cambiarEdicion(id, { historial = true } = {}) {
  if (!edicionPorId(id)) id = estado.indice.ediciones[0].id;
  const normas = await cargarSemana(id);
  estado.edicion = id;
  estado.normas = normas;
  pintarMancheta();
  window.PAGINA.pintar();
  if (historial) {
    const url = new URL(location.href);
    if (id === estado.indice.ediciones[0].id) url.searchParams.delete("e"); else url.searchParams.set("e", id);
    if (url.href !== location.href) history.replaceState(null, "", url);
  }
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

const votosTotales = (t) => ({ "Sí": t.afavor, "No": t.enContra, "Abstención": t.abstenciones, "No vota": t.noVotan });

function leyendaVotos() {
  return el("p", { clase: "leyenda-votos" }, ...OPCIONES_VOTO.map(([k, color]) => {
    const muestra = el("span", { clase: "muestra" });
    muestra.style.background = `var(${color})`;
    return el("span", {}, muestra, k);
  }));
}

function resumenVotacion(c) {
  const t = c.totales;
  return `${c.resultado === "convalidado" ? "Convalidado" : "Derogado (rechazado)"} por el Pleno el ${fechaMedia(c.fecha)}: ` +
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

function margen(c) {
  const d = c.totales.afavor - c.totales.enContra;
  const votos = (k) => `${k} ${k === 1 ? "voto" : "votos"}`;
  return d > 0 ? `Salió adelante por ${votos(d)} de diferencia.` : d < 0 ? `Fue rechazado por ${votos(-d)} de diferencia.` : "Empate.";
}

function gruposPorVoto(c) {
  // Qué grupos votaron mayoritariamente sí y cuáles no (dato agregado, sin nombres de personas).
  const r = { "Sí": [], "No": [], "Abstención": [] };
  for (const g of c.grupos || []) {
    const emitidos = Object.entries(g.votos).filter(([k]) => k !== "No vota");
    if (!emitidos.length) continue;
    const [voto] = emitidos.sort((a, b) => b[1] - a[1])[0];
    if (r[voto]) r[voto].push(g.nombre);
  }
  return r;
}

function ordinal(n, femenino = false) { return `${n}.${femenino ? "ª" : "º"}`; }

function contextoLegislatura(rdl) {
  // "En la XV legislatura se convalidaron 49 reales decretos-ley y se derogaron 14. Fue la 12.ª derogación."
  const L = estado.indice.legislatura;
  if (!L) return null;
  const r = L.resumen;
  let texto = `En la ${L.legislatura} legislatura se convalidaron ${r.convalidado} reales decretos-ley y se derogaron ${r.derogado}.`;
  const derogados = L.decretos_ley.filter((x) => x.resultado === "derogado").sort((a, b) => a.fecha.localeCompare(b.fecha));
  const k = derogados.findIndex((x) => x.rdl === rdl);
  if (k >= 0) texto += ` Fue la ${ordinal(k + 1, true)} derogación de la legislatura.`;
  return el("p", { clase: "nota" }, texto, " ", el("a", { href: urlPagina("datos.html", "#legislatura"), texto: "Ver todos" }));
}

// ---------- Vida de la norma, tramitación y antes y después ----------

const URL_DOC = (id) => `https://www.boe.es/buscar/doc.php?id=${id}`;

function enlaceBoe(id, texto) {
  return id ? el("a", { href: URL_DOC(id), target: "_blank", rel: "noopener", texto }) : el("span", { texto });
}

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
  // Lo que esta norma cambia en otras: antes y después de cada artículo, y la lista del resto.
  const cambios = (n.cambios || []).filter((c) => c.bloques && c.bloques.length);
  const conComparacion = new Set(cambios.map((c) => c.norma));
  const resto = ((n.vida || {}).modifica || []).filter((m) => !conComparacion.has(m.id));
  if (!cambios.length && !resto.length) return null;
  const sec = el("section", { clase: "cambios" }, el("h4", {}, "Qué cambia en otras normas ", termino("", "legislación consolidada")));
  if (cambios.length) {
    sec.append(el("p", { clase: "nota", texto: "El texto de los artículos que cambia, antes y después, según las versiones de la legislación consolidada del BOE." }),
      leyendaCambios());
    for (const c of cambios) {
      sec.append(el("details", { clase: "cambio-norma" },
        el("summary", { texto: `${c.relacion} ${c.referencia} (${plural(c.bloques.length, "artículo", "artículos")})` }),
        ...c.bloques.map(vistaBloque),
        c.recortado ? el("p", { clase: "nota", texto: "Hay más cambios: consulta el texto consolidado completo en el BOE." }) : null));
    }
  }
  if (resto.length) {
    sec.append(el("details", { clase: "modifica" },
      el("summary", { texto: cambios.length ? `Otros cambios (${resto.length})` : `Ver la lista (${resto.length})` }),
      el("ul", {}, ...resto.map((m) => el("li", {}, el("strong", { texto: `${m.relacion} ` }), enlaceBoe(m.id, m.texto))))));
  }
  return sec;
}

function lineaTiempoVida(n) {
  const v = n.vida;
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
    }
    hitos.push(hito);
  }
  const bloque = el("div", { clase: "vida" }, el("ol", { clase: "linea-tiempo" }, ...hitos));
  if (!(v.despues || []).length) {
    bloque.append(el("p", { clase: "nota", texto: "Por ahora, el BOE no registra cambios posteriores en esta norma." }));
  }
  const otrasNotas = (v.notas || []).filter((t) => t !== v.entrada_en_vigor);
  if (otrasNotas.length) {
    bloque.append(el("ul", { clase: "notas-boe" }, ...otrasNotas.map((t) => el("li", { texto: `Nota del BOE: ${t}` }))));
  }
  bloque.append(el("p", { clase: "nota" }, "Según el análisis de la legislación consolidada del BOE (solo relaciones expresas), consultado el ",
    fechaMedia(v.consultado), ". ", el("a", { href: v.enlace, target: "_blank", rel: "noopener", texto: "Texto consolidado" }), " ", termino("", "legislación consolidada")));
  return bloque;
}

function tramitacionVista(t) {
  // Pasos de un real decreto-ley tramitado como proyecto de ley (datos de iniciativas del Congreso).
  const hitos = [el("li", { clase: "hito hito-inicio" },
    el("span", { clase: "hito-fecha", texto: t.presentado ? fechaMedia(t.presentado) : "" }),
    el("span", { clase: "hito-texto" }, `El Congreso acuerda tramitarlo como proyecto de ley (expediente ${t.expediente}). `,
      termino("", "tramitar como proyecto de ley")))];
  for (const p of t.pasos || []) {
    const caducado = /caducad/i.test(p.fase);
    const periodo = p.hasta && p.hasta !== p.desde ? `del ${fechaMedia(p.desde)} al ${fechaMedia(p.hasta)}` : fechaMedia(p.desde);
    const texto = caducado
      ? el("span", { clase: "hito-texto" }, el("strong", { texto: "La tramitación termina sin aprobarse: caduca. " }), termino("", "caducar"))
      : el("span", { clase: "hito-texto", texto: `${p.fase}${p.organo ? ` (${p.organo})` : ""}` });
    hitos.push(el("li", { clase: "hito" }, el("span", { clase: "hito-fecha", texto: caducado ? `Desde el ${fechaMedia(p.desde)}` : periodo }), texto));
  }
  const caja = el("div", { clase: "tramitacion" },
    el("h4", { texto: "Su tramitación como proyecto de ley" }),
    el("ol", { clase: "linea-tiempo" }, ...hitos));
  if (t.resultado) caja.append(el("p", { clase: "nota", texto: `Resultado oficial: ${t.resultado}.` }));
  if ((t.enlaces_bocg || []).length) {
    caja.append(el("p", { clase: "nota" }, "Boletín Oficial de las Cortes: ",
      ...t.enlaces_bocg.flatMap((u, i) => [i ? " · " : "", el("a", { href: u, target: "_blank", rel: "noopener", texto: `documento ${i + 1}` })])));
  }
  return caja;
}

// ---------- Ficha en cuatro preguntas ----------
// Cada pregunta tiene una línea de respuesta y, al desplegarla, el detalle.

function pregunta(texto, respuesta, detalle, extra = null) {
  const cabeza = [el("span", { clase: "pregunta-q", texto }), el("span", { clase: "pregunta-r" }, ...[].concat(respuesta)), extra];
  const hijos = (detalle || []).filter(Boolean);
  if (!hijos.length) return el("div", { clase: "pregunta sin-detalle" }, el("div", { clase: "pregunta-cabeza" }, ...cabeza));
  return el("details", { clase: "pregunta" }, el("summary", { clase: "pregunta-cabeza" }, ...cabeza),
    el("div", { clase: "pregunta-detalle" }, ...hijos));
}

function lineaTipo(n) {
  // "Real decreto-ley ⓘ · Jefatura del Estado · Es el 22.º real decreto-ley de 2026"
  const partes = [];
  const clave = TIPO_A_TERMINO[n.rango];
  if (n.rango) partes.push(clave ? termino(n.rango, clave) : el("span", { texto: n.rango }));
  if (n.organo) partes.push(el("span", { texto: n.organo }));
  const m = (n.numero_oficial || "").match(/^(\d+)\/(\d{4})$/);
  if (m && ["Real Decreto-ley", "Ley", "Ley Orgánica"].includes(n.rango) && n.ambito === "Estatal") {
    const tipo = n.rango === "Real Decreto-ley" ? "real decreto-ley" : n.rango === "Ley" ? "ley estatal" : "ley orgánica";
    partes.push(el("span", { texto: `Es ${n.rango === "Real Decreto-ley" ? "el" : "la"} ${ordinal(Number(m[1]))} ${tipo} de ${m[2]}` }));
  }
  const linea = el("p", { clase: "linea-tipo" });
  partes.forEach((p, i) => { if (i) linea.append(" · "); linea.append(p); });
  return linea;
}

function preguntaQueEs(n) {
  const ficha = n.ficha || {};
  const ok = ficha.estado === "ok";
  const rc = n.resumen_cambios || {};
  const cambia = rc.articulos ? ` Cambia ${plural(rc.articulos, "artículo", "artículos")} de ${plural(rc.normas, "norma", "normas")}.`
    : ((n.vida || {}).modifica || []).length ? ` Modifica ${plural(n.vida.modifica.length, "norma", "normas")}.` : "";
  const respuesta = ok
    ? [el("span", { clase: "etiqueta experimental", texto: "IA experimental" }), " ", ficha.que_cambia]
    : `${n.rango || "Norma"}${n.organo ? ` (${n.organo})` : ""}.${cambia}`;

  const detalle = [lineaTipo(n)];
  if (n.vida && n.vida.entrada_en_vigor) {
    detalle.push(el("p", { clase: "dato-clave" }, el("strong", {}, termino("Desde cuándo", "entrada en vigor"), " (según el BOE): "), n.vida.entrada_en_vigor));
  }
  if (ok) {
    detalle.push(el("p", { clase: "aviso-ia", role: "note" }, el("strong", { texto: "Puede contener errores. " }),
      ficha.aviso_ia || "Resumen automático experimental: compruébalo siempre en el texto oficial."));
    const citas = ficha.citas || {};
    detalle.push(el("dl", { clase: "apartados" }, ...[
      ["Qué cambia", "que_cambia"], ["A quién afecta", "a_quien_afecta"], ["Desde cuándo", "desde_cuando"], ["Qué tienes que hacer", "que_hacer"],
    ].flatMap(([titulo, campo]) => {
      const dd = el("dd", {}, el("span", { texto: ficha[campo] }));
      const fuentes = Array.isArray(citas[campo]) ? citas[campo] : [];
      if (fuentes.length) {
        const etiqueta = fuentes.length === 1 ? `párrafo ${fuentes[0].parrafo}` : `párrafos ${fuentes.map((c) => c.parrafo).join(", ")}`;
        dd.append(el("details", { clase: "cita" }, el("summary", { texto: `De dónde sale (${etiqueta} del texto oficial)` }),
          ...fuentes.map((c) => el("blockquote", { texto: c.texto }))));
      }
      return [el("dt", { texto: titulo }), dd];
    })));
  } else {
    detalle.push(el("p", { clase: "nota", texto: "Todavía no hay un resumen de esta norma que haya superado las comprobaciones. El titular es una versión simplificada del título oficial." }));
  }
  detalle.push(el("p", { clase: "oficial" }, el("strong", { texto: "Título oficial: " }), n.titulo));
  if (n.detalle_error) detalle.push(el("p", { clase: "nota", texto: "No se ha podido cargar el antes y el después de esta norma." }));
  else detalle.push(seccionCambios(n));

  const c = n.clasificacion || {};
  const datos = [["Publicada", fechaLarga(n.fecha)], ["Ámbito", n.ambito], ["Tema", n.tema], ["A quién afecta", nombreImpacto(n.impacto)], ["Identificador", n.id]];
  const mas = el("details", { clase: "mas-detalles" }, el("summary", { texto: "Datos y clasificación" }),
    el("dl", { clase: "datos" }, ...datos.filter(([, v]) => v).flatMap(([t, v]) => [el("dt", { texto: t }), el("dd", { texto: v })])));
  if (c.metodo === "reglas") {
    mas.append(el("p", { clase: "motivos", texto: `Clasificada con reglas automáticas: ${[...(c.motivos_tema || []), ...(c.motivos_impacto || [])].join(" · ")}.` }));
  } else if (c.metodo === "ia") {
    mas.append(el("p", { clase: "motivos", texto: `Clasificada con IA (${c.modelo}): ${c.motivo || ""}` }));
  }
  detalle.push(mas);
  return pregunta("¿Qué es?", respuesta, detalle);
}

function preguntaPorQue(n) {
  const p = n.preambulo;
  if (!p || !p.parrafos || !p.parrafos.length) {
    return pregunta("¿Por qué?", "No hemos encontrado un preámbulo que explique sus motivos. Consulta el texto oficial.", []);
  }
  const detalle = [
    el("p", { clase: "nota" }, "Párrafos copiados literalmente del preámbulo, donde quien aprueba la norma explica sus motivos. ", termino("", "preámbulo")),
    ...p.parrafos.map((t) => el("blockquote", { texto: t })),
  ];
  if (p.parrafos.length < (p.total_parrafos || 0)) detalle.push(el("p", { clase: "nota", texto: "No se ha podido cargar el resto del preámbulo." }));
  if (p.recortado) detalle.push(el("p", { clase: "nota", texto: "El preámbulo completo sigue en el texto oficial." }));
  return pregunta("¿Por qué?", [el("span", { clase: "fuente-respuesta", texto: "Según su preámbulo: " }), `«${primeraFrase(p.parrafos[0], 200)}»`], detalle);
}

const RANGOS_DE_GOBIERNO = ["Real Decreto", "Decreto", "Orden", "Resolución", "Circular", "Instrucción", "Corrección (errores o erratas)"];

function preguntaQuienApoyo(n) {
  const titulo = "¿Quién la apoyó?";
  const congreso = n.congreso;
  if (congreso && congreso.convalidacion) {
    const c = congreso.convalidacion;
    const t = c.totales;
    const g = gruposPorVoto(c);
    let linea = `${c.resultado === "convalidado" ? "Convalidado" : "Derogado"} en el Congreso: ${t.afavor} sí, ${t.enContra} no.`;
    if (!c.solo_totales) {
      if (g["Sí"].length) linea += ` A favor: ${g["Sí"].join(", ")}.`;
      if (g["No"].length) linea += ` En contra: ${g["No"].join(", ")}.`;
    }
    const detalle = [
      el("p", { clase: `resultado-votacion ${c.resultado}`, texto: resumenVotacion(c) }),
      el("p", { clase: "nota" }, margen(c), " ",
        c.resultado === "convalidado" ? termino("¿Qué es convalidar?", "convalidar") : termino("¿Qué es derogar?", "derogar")),
      contextoLegislatura(congreso.rdl),
      leyendaVotos(),
    ];
    if (c.solo_totales) {
      detalle.push(barraVotos(votosTotales(t), { etiqueta: "Total" }),
        el("p", { clase: "nota" }, c.nota || "", " ", /llamamiento/.test(c.nota || "") ? termino("", "votación por llamamiento") : ""));
    } else {
      detalle.push(bloqueGrupos(c), el("p", { clase: "nota" }, "Voto por grupo parlamentario; el ", termino("voto telemático", "voto telemático"),
        " cuenta como voto. En el ", termino("Grupo Mixto", "grupo mixto"), " se desglosa por lista cuando votan distinto. No se muestran votos individuales."));
    }
    if (c.fuente_pdf) detalle.push(el("p", { clase: "nota" }, el("a", { href: c.fuente_pdf, target: "_blank", rel: "noopener", texto: "Votación oficial (PDF)" })));
    return pregunta(titulo, linea, detalle, barraVotos(votosTotales(t), { etiqueta: "Votación en el Congreso:" }));
  }
  if (congreso || n.rango === "Real Decreto-ley") {
    const linea = congreso && congreso.estado === "pendiente de votación" ? "Pendiente de votación en el Congreso."
      : "No tenemos datos de su votación de convalidación.";
    return pregunta(titulo, linea, [
      congreso && congreso.nota ? el("p", { texto: congreso.nota }) : null,
      el("p", { clase: "nota" }, "El Congreso debe ", termino("convalidarlo", "convalidar"), " o ", termino("derogarlo", "derogar"),
        " en 30 días; con las Cortes disueltas lo hace la ", termino("Diputación Permanente", "diputación permanente"), ", cuyas votaciones no están en los datos abiertos."),
    ]);
  }
  if (n.ambito !== "Estatal" && /^(Ley|Ley Foral|Decreto-ley)$/.test(n.rango || "")) {
    return pregunta(titulo, `Es una norma de ${n.ambito}: no recogemos las votaciones de los parlamentos autonómicos.`, []);
  }
  if (n.rango === "Ley" || n.rango === "Ley Orgánica") {
    return pregunta(titulo, "La aprobaron las Cortes Generales. Todavía no recogemos las votaciones de las leyes.", []);
  }
  if (n.rango === "Sentencia" || n.rango === "Providencia") {
    return pregunta(titulo, "Es una decisión de un tribunal: no hay votación política.", []);
  }
  if (RANGOS_DE_GOBIERNO.includes(n.rango)) {
    return pregunta(titulo, `No se vota en el Parlamento: es una norma del Gobierno o la Administración${n.organo ? ` (${n.organo})` : ""}.`, []);
  }
  return pregunta(titulo, "No recogemos votaciones de este tipo de norma.", []);
}

function preguntaDespues(n) {
  const v = n.vida;
  const t = n.tramitacion;
  const partes = [];
  const detalle = [];
  if (v && v.consolidada) {
    const despues = v.despues || [];
    partes.push(despues.length
      ? despues.map((h) => `${h.relacion}${h.fecha ? ` (${fechaCorta(h.fecha)})` : ""}`).join(" · ") + "."
      : "Nada por ahora, según el BOE.");
    detalle.push(lineaTiempoVida(n));
  } else if (!t) {
    partes.push("Sin datos: el BOE no tiene (todavía) una versión consolidada de esta norma.");
  }
  if (t) {
    partes.push(/caducad/i.test(t.resultado || "") ? "Su tramitación como proyecto de ley caducó." : `Se tramita como proyecto de ley${t.resultado ? ` (${t.resultado})` : ""}.`);
    detalle.push(tramitacionVista(t));
  }
  const tc = n.congreso && n.congreso.tramitacion;
  if (tc && !t) partes.push(`El Congreso votó también: ${tc.resultado}.`);
  return pregunta("¿Qué ha pasado después?", partes.join(" "), detalle);
}

function pintarFicha(n) {
  const ficha = n.ficha || {};
  $("ficha").replaceChildren(
    etiquetas(n),
    el("h2", { id: "ficha-titulo", clase: "articulo-titular", texto: titular(n) }),
    el("div", { clase: "preguntas" }, preguntaQueEs(n), preguntaPorQue(n), preguntaQuienApoyo(n), preguntaDespues(n)),
    el("a", { clase: "enlace", href: ficha.enlace || n.url_html, target: "_blank", rel: "noopener", texto: "Leer el texto oficial en boe.es →" }),
    el("p", { clase: "aviso", texto: ficha.aviso || "Resumen orientativo, no es asesoramiento jurídico. Consulta el texto oficial." }),
  );
}

let aperturaEnCurso = 0;

async function abrirArticulo(id, actualizarUrl = true) {
  const semana = estado.indice.semana_de_norma[id];
  if (!semana) return;
  const turno = ++aperturaEnCurso;
  const dialogo = $("articulo");
  try {
    if (semana !== estado.edicion) await cambiarEdicion(semana);
  } catch (error) {
    console.warn(error);
    return;
  }
  const n = estado.normas.find((x) => x.id === id);
  if (!n || turno !== aperturaEnCurso) return;
  $("ficha").replaceChildren(etiquetas(n), el("h2", { id: "ficha-titulo", clase: "articulo-titular", texto: titular(n) }),
    el("p", { clase: "nota", texto: "Cargando la ficha…" }));
  if (!dialogo.open) dialogo.showModal();
  dialogo.scrollTop = 0;
  if (actualizarUrl && location.hash !== `#${id}`) history.pushState(null, "", `${location.pathname}${location.search}#${id}`);
  let detalle;
  try {
    detalle = await cargarDetalle(id);
  } catch (error) {
    console.warn(error);
    detalle = { detalle_error: true };
  }
  if (turno !== aperturaEnCurso || !dialogo.open) return;
  pintarFicha({ ...n, ...detalle });
  dialogo.scrollTop = 0;
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

async function iniciar() {
  try {
    estado.indice = await cargarJson("indice.json");
  } catch (error) {
    $("edicion-etiqueta").textContent = "No se han podido cargar los datos. Genera web/datos/ con «python -m boe.exportar» y abre la página con un servidor local.";
    return;
  }
  if (!estado.indice.ediciones || !estado.indice.ediciones.length) {
    $("edicion-etiqueta").textContent = "Todavía no hay ninguna edición.";
    return;
  }
  // Edición: la de ?e=, la de la norma enlazada (#BOE-…) o la más reciente.
  const hash = location.hash.slice(1);
  const pedida = new URLSearchParams(location.search).get("e") || estado.indice.semana_de_norma[hash];
  if (window.PAGINA.preparar) window.PAGINA.preparar();
  $("f-edicion").addEventListener("change", (e) => cambiarEdicion(e.target.value));
  try {
    await cambiarEdicion(pedida || estado.indice.ediciones[0].id);
  } catch (error) {
    console.warn(error);
    $("edicion-etiqueta").textContent = "No se ha podido cargar esta edición.";
    return;
  }
  prepararArticulo();
}

document.addEventListener("DOMContentLoaded", iniciar);
