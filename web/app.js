/* El BOE en llano — código común a la portada (index.html) y a la página de
   datos (datos.html).
   Carga los datos por partes (generados por `python -m boe.exportar`):
   - datos/indice.json al empezar (ediciones, recuentos, legislatura),
   - datos/semanas/<semana>.json para la edición que se ve,
   - datos/normas/<id>.json solo al abrir una ficha (preámbulo completo y el
     antes y el después).
   Cada página define window.PAGINA = { pintar() } y este archivo hace el resto:
   cabecera, cambio de edición y la ficha en cuatro preguntas. Una página con
   PAGINA.sinEdicion (la legislatura) solo carga el índice y se pinta.
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
  Directo: { nombre: "Afecta a mucha gente", explicacion: "Cambia algo para mucha gente", ejemplo: "p. ej., salario mínimo, impuestos, precios regulados" },
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

// Titular largo (ficha): el título simplificado completo. Corto (portada y listas):
// el mismo recortado por reglas en boe.exportar, que puede acabar en «…».
const titularLargo = (n) => (n.ficha && n.ficha.titulo_llano) || n.titulo;
const titular = (n) => n.titular || titularLargo(n);
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
    ...(titular(n) !== titularLargo(n) ? { title: titularLargo(n) } : {}),
    onclick: (e) => { e.preventDefault(); abrirArticulo(n.id); },
  }, ...contenido);
}

// Iconos de los temas: Lucide (https://lucide.dev, licencia ISC), trazos de 24×24.
const ICONOS_TEMA = {
  "Trabajo y empleo": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
  "Impuestos y dinero": '<path d="M4 10h12"/><path d="M4 14h9"/><path d="M19 6a7.7 7.7 0 0 0-5.2-2A7.9 7.9 0 0 0 6 12c0 4.4 3.5 8 7.8 8 2 0 3.8-.8 5.2-2"/>',
  "Vivienda y urbanismo": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  "Salud, consumo y animales": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
  "Movilidad, energía y medio ambiente": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
  "Derechos e igualdad": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
  "Educación, cultura y ciencia": '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
  "Instituciones, ayudas e internacional": '<path d="M10 18v-7"/><path d="M11.12 2.198a2 2 0 0 1 1.76.006l7.866 3.847c.476.233.31.949-.22.949H3.474c-.53 0-.695-.716-.22-.949z"/><path d="M14 18v-7"/><path d="M18 18v-7"/><path d="M3 22h18"/><path d="M6 18v-7"/>',
};

function iconoTema(tema) {
  // Icono decorativo (el nombre del tema siempre va escrito al lado). null si el tema no tiene.
  const trazos = ICONOS_TEMA[tema];
  if (!trazos) return null;
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "icono-tema");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  svg.innerHTML = trazos; // constante del código, no viene de los datos
  return svg;
}

function etiquetas(n) {
  // Antetítulo de texto: a quién afecta, tema (con su icono) y, si no es estatal, el ámbito.
  const partes = [n.ambito && n.ambito !== "Estatal" ? n.ambito : null].filter(Boolean);
  return el("p", { clase: "antetitulo" },
    el("span", { clase: `antetitulo-impacto impacto-${n.impacto}`, texto: nombreImpacto(n.impacto) }),
    " · ", iconoTema(n.tema), n.tema, partes.length ? ` · ${partes.join(" · ")}` : "");
}

// ---------- Cabecera ----------

function claseTema(n) {
  // «tema-1»…«tema-8»: color del tema (variables --tema-N en estilos.css); vacío si el tema no está en el índice.
  const i = estado.indice.temas.indexOf(n.tema);
  return i >= 0 ? `tema-${i + 1}` : "";
}

function prepararCabeceraFija() {
  // La cabecera se queda fija al bajar, pero solo con lo útil (navegación y semana): el lema y
  // el título grande salen de la pantalla. La cabecera sube justo lo que miden esos dos elementos.
  const cabecera = document.querySelector(".mancheta");
  const nav = cabecera && cabecera.querySelector(".navegacion");
  if (!nav) return;
  const ajustar = () => {
    const oculto = Math.max(0, nav.offsetTop - 6);
    cabecera.style.top = `-${oculto}px`;
    // Altura que queda a la vista al bajar: para que los enlaces a #ancla no queden tapados.
    document.documentElement.style.setProperty("--alto-cabecera", `${cabecera.offsetHeight - oculto}px`);
  };
  ajustar();
  window.addEventListener("resize", ajustar);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(ajustar);
  if (window.ResizeObserver) new ResizeObserver(ajustar).observe(cabecera);
}

function etiquetaCorta(e) {
  // "28 sep – 3 oct 2026" (o "23 nov 2026" si la edición es de un solo día).
  const dia = (iso) => aFecha(iso).toLocaleDateString("es-ES", { day: "numeric", month: "short" }).replace(".", "");
  const anio = e.hasta.slice(0, 4);
  return e.desde === e.hasta ? `${dia(e.desde)} ${anio}` : `${dia(e.desde)} – ${dia(e.hasta)} ${anio}`;
}

function pintarMancheta() {
  const e = edicionActual();
  const ediciones = estado.indice.ediciones; // de la más reciente a la más antigua
  const varias = ediciones.length > 1;
  // Con varias ediciones, el propio selector hace de título; si no, se muestra el texto.
  $("edicion-etiqueta").textContent = e.etiqueta;
  $("edicion-etiqueta").hidden = varias;
  $("navegador-semanas").hidden = !varias;
  $("edicion-estado").hidden = !e.en_curso;
  $("edicion-estado").textContent = e.en_curso ? "Edición en curso: se completa cada día" : "";
  const sel = $("f-edicion");
  // En pantallas estrechas, formato corto para que el nombre de la semana quepa entero.
  const corto = window.matchMedia("(max-width: 560px)").matches;
  sel.replaceChildren(...ediciones.map((x) => el("option", { value: x.id, texto: corto ? etiquetaCorta(x) : x.etiqueta })));
  sel.value = e.id;
  const k = ediciones.findIndex((x) => x.id === e.id);
  $("semana-anterior").disabled = k >= ediciones.length - 1;
  $("semana-siguiente").disabled = k <= 0;
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
  return el("p", { clase: "nota" }, texto, " ", el("a", { href: "legislatura.html", texto: "Ver todos" }));
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

// ---------- Compartir ----------

function enlaceFicha(id) {
  // Enlace limpio a la ficha: la página actual sin parámetros y con #BOE-… (la semana se deduce del id).
  const url = new URL(location.href);
  url.search = "";
  url.hash = id;
  return url.href;
}

async function compartirNorma(n, aviso) {
  const url = enlaceFicha(n.id);
  const datos = { title: `${titular(n)} · El BOE en llano`, text: titular(n), url };
  try {
    if (navigator.share) { await navigator.share(datos); return; }
    await navigator.clipboard.writeText(url);
    aviso.textContent = "Enlace copiado";
  } catch (error) {
    if (error && error.name === "AbortError") return; // la persona cerró el menú de compartir
    // Sin portapapeles (p. ej. página sin HTTPS): se enseña el enlace para copiarlo a mano.
    aviso.textContent = url;
  }
  setTimeout(() => { aviso.textContent = ""; }, 4000);
}

function botonCompartir(n) {
  const aviso = el("span", { clase: "compartir-aviso", role: "status" });
  const boton = el("button", { type: "button", clase: "boton-compartir", onclick: () => compartirNorma(n, aviso) },
    el("span", { "aria-hidden": "true", texto: "↗ " }), "Compartir");
  return el("p", { clase: "compartir" }, boton, aviso);
}

function pintarFicha(n) {
  const ficha = n.ficha || {};
  $("ficha").replaceChildren(
    etiquetas(n),
    el("h2", { id: "ficha-titulo", clase: "articulo-titular", texto: titularLargo(n) }),
    botonCompartir(n),
    el("div", { clase: "preguntas" }, preguntaQueEs(n), preguntaPorQue(n), preguntaQuienApoyo(n), preguntaDespues(n)),
    el("a", { clase: "enlace", href: ficha.enlace || n.url_html, target: "_blank", rel: "noopener", texto: "Leer el texto oficial en boe.es →" }),
    el("p", { clase: "aviso", texto: ficha.aviso || "Resumen orientativo, no es asesoramiento jurídico. Consulta el texto oficial." }),
  );
}

const TITULO_BASE = document.title;
let aperturaEnCurso = 0;
// true si la ficha abierta añadió su propia entrada al historial (#BOE-…):
// al cerrarla se vuelve atrás en lugar de añadir otra, para que «Atrás» no la reabra.
let fichaEmpujada = false;

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
  $("ficha").replaceChildren(etiquetas(n), el("h2", { id: "ficha-titulo", clase: "articulo-titular", texto: titularLargo(n) }),
    el("p", { clase: "nota", texto: "Cargando la ficha…" }));
  document.title = `${titular(n)} · El BOE en llano`;
  const yaAbierta = dialogo.open;
  if (!yaAbierta) dialogo.showModal();
  dialogo.scrollTop = 0;
  if (!actualizarUrl) {
    fichaEmpujada = false;
  } else if (location.hash !== `#${id}`) {
    const url = `${location.pathname}${location.search}#${id}`;
    // Pasar de una ficha a otra sin cerrar reutiliza la entrada ya añadida.
    if (yaAbierta && fichaEmpujada) history.replaceState(null, "", url);
    else { history.pushState(null, "", url); fichaEmpujada = true; }
  }
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
    document.title = TITULO_BASE;
    const empujada = fichaEmpujada;
    fichaEmpujada = false;
    if (!location.hash.startsWith("#BOE-")) return; // ya se cerró con «Atrás»
    if (empujada) history.back();
    else history.replaceState(null, "", location.pathname + location.search);
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
    ($("edicion-etiqueta") || $("legislatura-etiqueta")).textContent = "No se han podido cargar los datos. Genera web/datos/ con «python -m boe.exportar» y abre la página con un servidor local.";
    return;
  }
  // Páginas que no dependen de la edición semanal (p. ej. la legislatura).
  if (window.PAGINA.sinEdicion) {
    if (window.PAGINA.preparar) window.PAGINA.preparar();
    $("generado").textContent = `Actualizado el ${new Date(estado.indice.generado).toLocaleString("es-ES", { dateStyle: "long", timeStyle: "short" })}.`;
    window.PAGINA.pintar();
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
  const irA = async (id) => {
    try {
      await cambiarEdicion(id);
    } catch (error) {
      // Si la semana no se carga, el selector vuelve a la edición que se está viendo.
      console.warn(error);
      $("f-edicion").value = estado.edicion;
      $("edicion-estado").hidden = false;
      $("edicion-estado").textContent = "No se ha podido cargar esa edición.";
    }
  };
  const vecina = (paso) => {
    const lista = estado.indice.ediciones;
    const k = lista.findIndex((x) => x.id === estado.edicion) + paso;
    if (k >= 0 && k < lista.length) irA(lista[k].id);
  };
  $("f-edicion").addEventListener("change", (e) => irA(e.target.value));
  $("semana-anterior").addEventListener("click", () => vecina(1)); // más antigua
  $("semana-siguiente").addEventListener("click", () => vecina(-1)); // más reciente
  try {
    await cambiarEdicion(pedida || estado.indice.ediciones[0].id);
  } catch (error) {
    console.warn(error);
    $("edicion-etiqueta").textContent = "No se ha podido cargar esta edición.";
    return;
  }
  prepararArticulo();
}

document.addEventListener("DOMContentLoaded", () => { prepararCabeceraFija(); iniciar(); });
