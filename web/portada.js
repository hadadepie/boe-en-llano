/* El BOE en llano — portada (index.html): titulares, «¿Quién decidió?», qué ha pasado con
   normas anteriores y enlaces a los informes. El embudo, el mosaico por tema y «La semana en
   datos» están en «Explorar» (explorar.js) desde el 25/11/2026. Usa lo común de app.js. */

"use strict";

const NUM_SECUNDARIOS = 3;

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
  if (!porque) return null;
  return el("p", { clase: "entradilla" },
    el("span", { clase: "entradilla-fuente", texto: "Por qué, según su preámbulo: " }), `«${primeraFrase(porque)}»`);
}

function pintarPortada(portada) {
  const { principal, secundarios } = portada;
  if (!principal) {
    $("principal").replaceChildren(el("p", { clase: "ayuda", texto: "Esta semana no hay normas que afecten a la ciudadanía o a grupos concretos: todo es gestión interna." }));
    $("secundarios").replaceChildren();
    return;
  }
  $("principal").className = `principal ${claseTema(principal)}`;
  $("principal").replaceChildren(...[
    etiquetas(principal),
    el("h2", { clase: "titular-principal" }, enlaceNorma(principal, "", [titular(principal)])),
    entradilla(principal),
    enlaceNorma(principal, "leer-mas", ["Leer la ficha →"]),
  ].filter(Boolean));
  $("secundarios").replaceChildren(...secundarios.map((n) => el("article", { clase: `secundario ${claseTema(n)}` },
    etiquetas(n),
    el("h3", { clase: "titular-secundario" }, enlaceNorma(n, "", [titular(n)])))));
}

// ---------- ¿Quién decidió? ----------
// Cuántas normas de la semana se votaron en el Parlamento y cuántas decidió el Gobierno u otro
// órgano; cada fila enlaza a «Explorar» con ese filtro.

function pintarDecisiones() {
  const normas = estado.normas;
  const filas = estado.indice.decisiones
    .map((d) => ({ d, n: normas.filter((x) => x.decision === d).length }))
    .filter((f) => f.n > 0 || f.d === "votada"); // «0 se votaron» también es una respuesta
  $("decisiones").hidden = !normas.length;
  if (!normas.length) return;
  $("decisiones").replaceChildren(
    el("p", { clase: "embudo-etiqueta" }, "De las ", el("strong", { texto: miles(normas.length) }), " normas generales de la semana:"),
    el("ul", { clase: "embudo-leyenda decisiones-lista" }, ...filas.map(({ d, n }) => {
      const url = new URL(urlPagina("datos.html"), location.href);
      url.searchParams.set("decision", d);
      url.hash = "normas";
      return el("li", {}, el("strong", { texto: miles(n) }), " ",
        el("a", { href: `${url.pathname.split("/").pop()}${url.search}${url.hash}`, texto: DECISION[d].corto[n === 1 ? 0 : 1] }));
    })));
}

// ---------- Qué ha pasado con normas anteriores ----------
// Lo repetido se agrupa («La Diputación Permanente convalidó 7 decretos-ley» y la lista
// de títulos al desplegar) y solo se ven MAX_SEGUIMIENTO elementos; el resto, tras «Ver todos».

const MAX_SEGUIMIENTO = 4;
const seguimientoEstado = { todos: false };

function enlaceHecho(h) {
  // Si la norma está en nuestros datos, se abre su ficha; si no, el texto oficial en el BOE.
  const enlace = h.en_web
    ? enlaceNorma({ id: h.id, titular: h.titular, titulo: h.titular }, "titular-lista", [h.titular])
    : enlaceBoe(h.id, h.titular);
  enlace.classList.add("titular-lista");
  return enlace;
}

function agruparSeguimiento(hechos) {
  // Votaciones de la Diputación Permanente (mismo órgano y mismo verbo): se juntan si son 3 o más.
  const clave = (h) => {
    const m = h.texto.match(/^La Diputación Permanente del Congreso (convalidó|derogó) /);
    return m ? `${h.tipo}|${m[1]}` : null;
  };
  const grupos = new Map();
  for (const h of hechos) {
    const k = clave(h);
    if (k) grupos.set(k, [...(grupos.get(k) || []), h]);
  }
  const elementos = [];
  const yaPuestos = new Set();
  for (const h of hechos) {
    const k = clave(h);
    if (k && grupos.get(k).length >= 3) {
      if (yaPuestos.has(k)) continue;
      yaPuestos.add(k);
      const g = grupos.get(k);
      const fechas = g.map((x) => x.fecha).sort();
      elementos.push({ grupo: g, tipo: h.tipo, etiqueta: h.etiqueta, verbo: k.split("|")[1],
        fecha: fechas[0], hasta: fechas[fechas.length - 1] });
    } else {
      elementos.push({ hecho: h });
    }
  }
  return elementos;
}

function elementoSeguimiento(e) {
  if (e.hecho) {
    const h = e.hecho;
    return el("li", { clase: "hecho" },
      el("p", { clase: "hecho-cabeza" },
        el("span", { clase: `hecho-etiqueta hecho-${h.tipo}`, texto: h.etiqueta }),
        el("span", { clase: "hecho-fecha", texto: fechaMedia(h.fecha) })),
      enlaceHecho(h),
      el("p", { clase: "hecho-texto", texto: `${h.texto} Publicada el ${fechaMedia(h.publicada)}.` }));
  }
  const n = e.grupo.length;
  return el("li", { clase: "hecho hecho-grupo" },
    el("p", { clase: "hecho-cabeza" },
      el("span", { clase: `hecho-etiqueta hecho-${e.tipo}`, texto: e.etiqueta }),
      el("span", { clase: "hecho-fecha", texto: e.fecha === e.hasta ? fechaMedia(e.fecha) : `del ${fechaMedia(e.fecha)} al ${fechaMedia(e.hasta)}` })),
    el("p", { clase: "hecho-resumen", texto: `La Diputación Permanente del Congreso ${e.verbo} ${n} reales decretos-ley.` }),
    el("details", { clase: "hecho-lista" }, el("summary", { texto: `Ver los ${n}` }),
      el("ul", {}, ...e.grupo.map((h) => el("li", {}, enlaceHecho(h))))));
}

function pintarSeguimiento() {
  const hechos = edicionActual().seguimiento || [];
  $("seguimiento-seccion").hidden = hechos.length === 0;
  const elementos = agruparSeguimiento(hechos).map((e) => ({ e, nodo: elementoSeguimiento(e) }));
  const lista = $("seguimiento");
  seguimientoEstado.todos = false;
  const boton = el("button", { type: "button", clase: "ver-todos", "aria-controls": "seguimiento" });
  const aplicar = () => {
    elementos.forEach(({ nodo }, i) => { nodo.hidden = !seguimientoEstado.todos && i >= MAX_SEGUIMIENTO; });
    boton.textContent = seguimientoEstado.todos ? "Ver menos" : `Ver todos (${elementos.length})`;
    boton.setAttribute("aria-expanded", String(seguimientoEstado.todos));
  };
  boton.addEventListener("click", () => { seguimientoEstado.todos = !seguimientoEstado.todos; aplicar(); });
  lista.replaceChildren(...elementos.map(({ nodo }) => nodo));
  aplicar();
  const anterior = $("seguimiento-seccion").querySelector(".ver-todos");
  if (anterior) anterior.remove();
  if (elementos.length > MAX_SEGUIMIENTO) lista.after(boton);
}

// ---------- Buscador ----------
// Busca palabras del titular en todas las normas de todas las semanas (datos/buscar.json,
// que solo se descarga al empezar a escribir). Sin tildes ni mayúsculas; todas las palabras
// deben aparecer. Los resultados salen de la más reciente a la más antigua.

const MAX_RESULTADOS = 25;
let busquedaDatos = null; // promesa de [{ fila, texto }]

const sinTildes = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

function cargarBusqueda() {
  if (!busquedaDatos) {
    busquedaDatos = cargarIndiceBusqueda()
      .then((filas) => filas.map((fila) => ({ fila, texto: sinTildes(fila[2]) })))
      .catch((error) => { busquedaDatos = null; throw error; });
  }
  return busquedaDatos;
}

function buscarNormas(lista, consulta) {
  const palabras = sinTildes(consulta).split(/\s+/).filter((p) => p.length >= 2);
  if (!palabras.length) return null;
  return lista.filter((x) => palabras.every((p) => x.texto.includes(p))).map((x) => x.fila);
}

function filaResultado([id, fecha, titularNorma, indiceTema, impacto]) {
  const tema = estado.indice.temas[indiceTema];
  const enlace = enlaceNorma({ id, titular: titularNorma, titulo: titularNorma }, "titular-lista", [titularNorma]);
  return el("li", { clase: `resultado ${indiceTema >= 0 ? `tema-${indiceTema + 1}` : ""}` },
    el("p", { clase: "antetitulo" },
      fechaCorta(fecha), " · ", el("span", { clase: `antetitulo-impacto impacto-${impacto}`, texto: nombreImpacto(impacto) }),
      ...(tema ? [" · ", iconoTema(tema), tema] : [])),
    enlace);
}

function prepararBuscador() {
  const campo = $("q");
  const panel = $("resultados");
  let turno = 0;
  const buscar = async () => {
    const consulta = campo.value.trim();
    const mio = ++turno;
    if (consulta.length < 2) { panel.hidden = true; return; }
    let lista;
    try {
      lista = await cargarBusqueda();
    } catch (error) {
      console.warn(error);
      panel.hidden = false;
      $("resultados-cuenta").textContent = "No se ha podido cargar el buscador. Inténtalo de nuevo más tarde.";
      $("resultados-lista").replaceChildren();
      return;
    }
    if (mio !== turno) return; // ya se ha escrito otra cosa
    const encontradas = buscarNormas(lista, consulta);
    if (encontradas === null) { panel.hidden = true; return; }
    panel.hidden = false;
    $("resultados-cuenta").textContent = !encontradas.length
      ? "Ninguna norma coincide. Prueba con otra palabra (solo se busca en los titulares)."
      : encontradas.length > MAX_RESULTADOS
        ? `${miles(encontradas.length)} normas coinciden; se muestran las ${MAX_RESULTADOS} más recientes. Añade otra palabra para afinar.`
        : `${plural(encontradas.length, "norma coincide", "normas coinciden")}.`;
    $("resultados-lista").replaceChildren(...encontradas.slice(0, MAX_RESULTADOS).map(filaResultado));
  };
  campo.addEventListener("input", buscar);
  campo.addEventListener("focus", () => { cargarBusqueda().catch(() => {}); }, { once: true });
  campo.addEventListener("keydown", (e) => { if (e.key === "Escape") { campo.value = ""; buscar(); } });
  $("buscador").addEventListener("submit", (e) => e.preventDefault());
}

// ---------- Bienvenida ----------
// Una línea para quien llega por primera vez; al cerrarla no vuelve (preferencia en el navegador).

const CLAVE_BIENVENIDA = "boe-en-llano:bienvenida-cerrada";

function prepararBienvenida() {
  const caja = $("bienvenida");
  let cerrada = false;
  try { cerrada = localStorage.getItem(CLAVE_BIENVENIDA) === "1"; } catch (error) { /* sin almacenamiento: se muestra siempre */ }
  caja.hidden = cerrada;
  $("cerrar-bienvenida").addEventListener("click", () => {
    caja.hidden = true;
    try { localStorage.setItem(CLAVE_BIENVENIDA, "1"); } catch (error) { /* no se pudo recordar */ }
  });
}

window.PAGINA = {
  preparar() { prepararBienvenida(); prepararBuscador(); },
  pintar() {
    const portada = elegirPortada(estado.normas);
    pintarPortada(portada);
    pintarDecisiones();
    pintarSeguimiento();
  },
};
