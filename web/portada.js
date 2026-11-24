/* El BOE en llano — portada (index.html): titulares, la semana de un vistazo
   (embudo en dos niveles), mosaico de las normas por tema, qué ha pasado con
   normas anteriores, «La semana en datos» y el enlace a la gestión interna. Usa lo común de app.js. Sin Chart.js: los
   gráficos son SVG y HTML con CSS. */

"use strict";

const NUM_SECUNDARIOS = 3;
const portadaEstado = { piezaAbierta: null };

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
    el("span", { clase: "entradilla-fuente", texto: "Según su preámbulo: " }), `«${primeraFrase(porque)}»`);
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
    el("h3", { clase: "titular-secundario" }, enlaceNorma(n, "", [titular(n)])))));
}

// ---------- La semana de un vistazo: embudo en dos niveles ----------
// 1) Una barra con todo lo publicado en la semana, con la astilla de las normas
//    generales iluminada. 2) Esa astilla ampliada: un cuadrado por norma general,
//    coloreado por a quién afecta. Las dos proporciones son exactas; el zoom solo
//    evita que las normas que te afectan se pierdan entre las 1.500 publicaciones.

const SVG = "http://www.w3.org/2000/svg";
const ORDEN_IMPACTO = { Directo: 0, Colectivos: 1, Técnico: 2 };

function porcentaje(parte, total) {
  const v = (100 * parte) / (total || 1);
  return `${v < 10 ? v.toFixed(1).replace(".", ",") : Math.round(v)} %`;
}

function pintarEmbudo() {
  const r = edicionActual().resumen;
  const total = r.total_publicaciones;
  const normas = estado.normas;
  const resto = total - normas.length;
  const cuenta = (i) => normas.filter((n) => n.impacto === i).length;
  const afectan = cuenta("Directo");
  const proporcion = (100 * normas.length) / (total || 1);

  // Nivel 1: todo el BOE de la semana.
  const barra = el("div", { clase: "embudo-barra", role: "img",
    "aria-label": `${miles(total)} publicaciones en el BOE esta semana; ${miles(normas.length)} son normas generales (${porcentaje(normas.length, total)}).` });
  const astilla = el("span", { clase: "embudo-astilla" });
  astilla.style.width = `${proporcion}%`;
  barra.append(astilla);

  // Conector: de la astilla al ancho completo, para que se lea como una ampliación.
  const conector = document.createElementNS(SVG, "svg");
  conector.setAttribute("class", "embudo-conector");
  conector.setAttribute("viewBox", "0 0 100 24");
  conector.setAttribute("preserveAspectRatio", "none");
  conector.setAttribute("aria-hidden", "true");
  const forma = document.createElementNS(SVG, "polygon");
  forma.setAttribute("points", `0,0 ${Math.max(proporcion, 1.2)},0 100,24 0,24`);
  conector.append(forma);

  // Nivel 2: las normas generales, una a una.
  const ordenadas = [...normas].sort((a, b) => ORDEN_IMPACTO[a.impacto] - ORDEN_IMPACTO[b.impacto]);
  const cuadros = el("div", { clase: "embudo-zoom", role: "img",
    "aria-label": `De las ${miles(normas.length)} normas generales: ` +
      estado.indice.impactos.map((i) => `${miles(cuenta(i))} ${nombreImpacto(i).toLowerCase()}`).join(", ") + "." },
    ...ordenadas.map((n) => el("span", { clase: `embudo-cuadro tesela-${n.impacto}` })));

  const fila = (clase, cifra, texto) => el("li", {}, el("span", { clase: `muestra ${clase}` }),
    el("strong", { texto: miles(cifra) }), ` ${texto}`);
  $("embudo").replaceChildren(
    el("p", { clase: "embudo-titular" }, el("strong", { texto: miles(afectan) }),
      ` de ${miles(total)} publicaciones te pueden afectar directamente.`),
    el("p", { clase: "embudo-etiqueta" }, el("strong", { texto: miles(total) }), " publicaciones en el BOE esta semana"),
    barra,
    el("p", { clase: "embudo-pie-barra" },
      el("span", { clase: "embudo-pie-normas", texto: `${miles(normas.length)} normas generales (${porcentaje(normas.length, total)})` }),
      el("span", { texto: `${miles(resto)} nombramientos, oposiciones, justicia y anuncios` })),
    conector,
    el("p", { clase: "embudo-etiqueta" }, "Ampliadas, las ", el("strong", { texto: miles(normas.length) }), " normas generales:"),
    cuadros,
    el("ul", { clase: "embudo-leyenda" },
      fila("tesela-Directo", afectan, "te pueden afectar directamente"),
      fila("tesela-Colectivos", cuenta("Colectivos"), "afectan a ciertos grupos"),
      fila("tesela-Técnico", cuenta("Técnico"), "son de gestión interna")));
}

// ---------- Mosaico: todas las normas de la semana por tema ----------

function pintarMosaico(normas) {
  $("mosaico-seccion").hidden = normas.length === 0;
  $("t-mosaico").textContent = `Las ${normas.length} normas de la semana`;
  $("mosaico-leyenda").replaceChildren(...estado.indice.impactos.map((i) =>
    el("li", {}, el("span", { clase: `muestra tesela-${i}` }), nombreImpacto(i))));
  const pista = $("mosaico-pista");
  const textoPista = "Pasa el ratón o el foco por un cuadrado para ver de qué trata.";
  pista.textContent = textoPista;
  const temas = estado.indice.temas
    .map((tema) => ({ tema, normas: normas.filter((n) => n.tema === tema) }))
    .filter((t) => t.normas.length)
    .sort((a, b) => b.normas.length - a.normas.length);
  $("mosaico").replaceChildren(...temas.map(({ tema, normas: delTema }) => {
    const teselas = [...delTema]
      .sort((a, b) => ORDEN_IMPACTO[a.impacto] - ORDEN_IMPACTO[b.impacto] || porRelevancia(a, b))
      .map((n) => {
        const a = enlaceNorma(n, `tesela tesela-${n.impacto}`, []);
        const descripcion = `${nombreImpacto(n.impacto)}${n.ambito !== "Estatal" ? ` · ${n.ambito}` : ""}: ${titular(n)}`;
        a.setAttribute("aria-label", descripcion);
        a.setAttribute("title", titular(n));
        const mostrar = () => { pista.textContent = descripcion; };
        a.addEventListener("mouseenter", mostrar);
        a.addEventListener("focus", mostrar);
        return a;
      });
    return el("section", { clase: "mosaico-tema" },
      el("h3", { clase: "mosaico-titulo" }, iconoTema(tema), tema, el("span", { clase: "mosaico-cuenta", texto: ` ${delTema.length}` })),
      el("div", { clase: "mosaico-teselas" }, ...teselas));
  }));
}

// ---------- Qué ha pasado con normas anteriores ----------
// Lo repetido se agrupa («La Diputación Permanente convalidó 7 decretos-ley» y la lista
// de títulos al desplegar) y solo se ven MAX_SEGUIMIENTO elementos; el resto, tras «Ver todos».

const MAX_SEGUIMIENTO = 4;
const seguimientoEstado = { todos: false };

function enlaceHecho(h) {
  // Si la norma está en nuestros datos, se abre su ficha; si no, el texto oficial en el BOE.
  const enlace = h.en_web && estado.indice.semana_de_norma[h.id]
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

// ---------- La semana en datos ----------

function pintarPiezas() {
  const piezas = edicionActual().piezas || [];
  const porId = Object.fromEntries(estado.normas.map((n) => [n.id, n]));
  $("piezas-seccion").hidden = piezas.length === 0;
  const detalle = $("pieza-detalle");
  const botones = piezas.map((p, i) => {
    const boton = el("button", {
      type: "button", clase: p.votaciones ? "pieza pieza-congreso" : "pieza", "aria-expanded": "false", "aria-controls": "pieza-detalle",
    }, el("span", { clase: "pieza-cifra", texto: miles(p.cifra) }), el("span", { clase: "pieza-texto", texto: p.texto }));
    boton.addEventListener("click", () => abrirPieza(i));
    return boton;
  });
  const abrirPieza = (i) => {
    const abierta = portadaEstado.piezaAbierta === i ? null : i;
    portadaEstado.piezaAbierta = abierta;
    botones.forEach((b, k) => b.setAttribute("aria-expanded", String(k === abierta)));
    detalle.hidden = abierta === null;
    if (abierta === null) return;
    const p = piezas[abierta];
    const normas = p.ids.map((id) => porId[id]).filter(Boolean);
    detalle.replaceChildren(
      el("p", { clase: "pieza-detalle-titulo", texto: `${miles(p.cifra)} ${p.texto}` }),
      normas.length
        ? el("ul", {}, ...normas.map((n) => el("li", {}, enlaceNorma(n, "titular-lista", [titular(n)]))))
        : el("p", { clase: "nota", texto: "Son votaciones de normas publicadas en otras semanas: se ven en «Explorar los datos»." }));
  };
  portadaEstado.piezaAbierta = null;
  detalle.hidden = true;
  $("piezas").replaceChildren(...botones);
}

// ---------- Gestión interna ----------
// Trámites y subvenciones a entidades concretas: interesan a poca gente, así que en la
// portada solo se cuentan y se enlaza a «Explorar», ya filtrado (también están en el mosaico).

function pintarBreves() {
  const n = estado.normas.filter((x) => x.impacto === "Técnico").length;
  $("breves-seccion").hidden = n === 0;
  $("breves-texto").textContent = `Además, ${plural(n, "norma es", "normas son")} de gestión interna: trámites, ` +
    "organización de la Administración y subvenciones a entidades concretas. No suelen afectar directamente a la ciudadanía.";
  const url = new URL(urlPagina("datos.html"), location.href);
  url.searchParams.set("impacto", "Técnico");
  url.hash = "normas";
  $("ver-breves").href = `${url.pathname.split("/").pop()}${url.search}${url.hash}`;
}

window.PAGINA = {
  preparar: prepararBienvenida,
  pintar() {
    const portada = elegirPortada(estado.normas);
    pintarPortada(portada);
    pintarEmbudo();
    pintarMosaico(estado.normas);
    pintarSeguimiento();
    pintarPiezas();
    pintarBreves();
  },
};
