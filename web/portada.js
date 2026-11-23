/* El BOE en llano — portada (index.html): titulares, la semana de un vistazo
   (embudo de puntos), mosaico de las normas por tema, «La semana en datos»
   y breves. Usa lo común de app.js. Sin Chart.js: los
   gráficos son SVG y HTML con CSS. */

"use strict";

const NUM_SECUNDARIOS = 3;
const MAX_BREVES = 8;
const portadaEstado = { brevesAbiertos: false, piezaAbierta: null };

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

// ---------- La semana de un vistazo: embudo de puntos ----------
// Un punto por publicación del BOE de la semana. Arriba, encendidas, las normas
// que te pueden afectar; después, el resto de normas generales; el resto, en gris.

const SVG = "http://www.w3.org/2000/svg";
// Con sitio (móvil a todo el ancho) se usan más columnas para que el bloque no sea tan alto.
const columnasEmbudo = () => ($("embudo").clientWidth > 300 ? 60 : 40);

function pintarEmbudo() {
  const COLUMNAS_EMBUDO = columnasEmbudo();
  $("embudo").dataset.columnas = COLUMNAS_EMBUDO;
  const r = edicionActual().resumen;
  const total = r.total_publicaciones;
  const afectan = r.impacto_directo;
  const otrasNormas = r.normas_generales - afectan;
  const resto = total - r.normas_generales;
  const filas = Math.ceil(total / COLUMNAS_EMBUDO);
  const svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("viewBox", `0 0 ${COLUMNAS_EMBUDO * 10} ${filas * 10}`);
  svg.setAttribute("class", "embudo-puntos");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", `${miles(total)} puntos, uno por publicación del BOE de la semana: ` +
    `${miles(afectan)} son normas que te pueden afectar, ${miles(otrasNormas)} otras normas generales ` +
    `y ${miles(resto)} nombramientos, oposiciones, decisiones de justicia y anuncios.`);
  for (let i = 0; i < total; i++) {
    const p = document.createElementNS(SVG, "rect");
    p.setAttribute("x", (i % COLUMNAS_EMBUDO) * 10 + 1);
    p.setAttribute("y", Math.floor(i / COLUMNAS_EMBUDO) * 10 + 1);
    p.setAttribute("width", 8);
    p.setAttribute("height", 8);
    p.setAttribute("rx", 2);
    p.setAttribute("class", i < afectan ? "punto-afecta" : i < r.normas_generales ? "punto-norma" : "punto-resto");
    svg.append(p);
  }
  const fila = (clase, cifra, texto) => el("li", {}, el("span", { clase: `muestra ${clase}` }),
    el("strong", { texto: miles(cifra) }), ` ${texto}`);
  $("embudo").replaceChildren(
    el("p", { clase: "embudo-titular" }, el("strong", { texto: miles(afectan) }),
      ` de ${miles(total)} publicaciones te pueden afectar directamente.`),
    svg,
    el("ul", { clase: "embudo-leyenda" },
      fila("punto-afecta", afectan, "te pueden afectar directamente"),
      fila("punto-norma", otrasNormas, "normas más: afectan a grupos concretos o son de gestión interna"),
      fila("punto-resto", resto, "nombramientos, oposiciones, justicia y anuncios")),
    el("p", { clase: "nota", texto: "Cada punto es una publicación del BOE de esta semana." }));
}

// ---------- Mosaico: todas las normas de la semana por tema ----------

const ORDEN_IMPACTO = { Directo: 0, Colectivos: 1, Técnico: 2 };

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
      el("h3", { clase: "mosaico-titulo" }, tema, el("span", { clase: "mosaico-cuenta", texto: ` ${delTema.length}` })),
      el("div", { clase: "mosaico-teselas" }, ...teselas));
  }));
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

// ---------- Breves ----------

function pintarBreves() {
  const breves = estado.normas.filter((n) => n.impacto === "Técnico").sort(porRelevancia);
  const visibles = portadaEstado.brevesAbiertos ? breves : breves.slice(0, MAX_BREVES);
  $("breves").replaceChildren(...visibles.map((n) => el("li", {}, enlaceNorma(n, "breve", [titular(n)]))));
  const boton = $("ver-breves");
  boton.hidden = breves.length <= MAX_BREVES;
  boton.textContent = portadaEstado.brevesAbiertos ? "Ver menos" : `Ver las ${breves.length} normas de gestión interna`;
}

window.PAGINA = {
  preparar() {
    // Repintar el embudo si al cambiar el ancho de la ventana cambia el número de columnas.
    window.addEventListener("resize", () => {
      if (estado.edicion && String(columnasEmbudo()) !== $("embudo").dataset.columnas) pintarEmbudo();
    });
    $("ver-breves").addEventListener("click", () => { portadaEstado.brevesAbiertos = !portadaEstado.brevesAbiertos; pintarBreves(); });
  },
  pintar() {
    portadaEstado.brevesAbiertos = false;
    const portada = elegirPortada(estado.normas);
    pintarPortada(portada);
    pintarEmbudo();
    pintarMosaico(estado.normas);
    pintarPiezas();
    pintarBreves();
  },
};
