/* El BOE en llano — portada (index.html): titulares, «En cifras» con la
   semana de un vistazo, «La semana en datos», secciones por tema y breves.
   Usa lo común de app.js. Sin gráficos de Chart.js: la barra es HTML y CSS. */

"use strict";

const NUM_SECUNDARIOS = 3;
const MAX_POR_TEMA = 3;
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

// ---------- En cifras y la semana de un vistazo ----------

const NOMBRE_CORTO = { I: "Normas generales", "II.A": "Nombramientos", "II.B": "Oposiciones y concursos",
  III: "Otras disposiciones", IV: "Justicia", V: "Anuncios" };

function pintarCifras() {
  const r = edicionActual().resumen;
  $("c-total").textContent = miles(r.total_publicaciones);
  $("c-normas").textContent = miles(r.normas_generales);
  $("c-directo").textContent = miles(r.impacto_directo);
  $("frase").textContent = r.frase;

  // Una sola barra: qué parte del BOE de la semana es cada sección.
  const dias = diasEdicion();
  const secciones = estado.indice.secciones.map((s, i) => ({
    ...s, color: `var(--s${i + 1})`, total: dias.reduce((a, d) => a + d.recuento[s.codigo], 0),
  }));
  const total = secciones.reduce((a, s) => a + s.total, 0) || 1;
  const pct = (n) => {
    const v = (100 * n) / total;
    return `${v < 10 ? v.toFixed(1).replace(".", ",") : Math.round(v)} %`;
  };
  const barra = el("div", { clase: "barra-semana", role: "img",
    "aria-label": `Publicaciones de la semana por sección: ${secciones.map((s) => `${NOMBRE_CORTO[s.codigo] || s.nombre}, ${pct(s.total)}`).join("; ")}` });
  for (const s of secciones) {
    if (!s.total) continue;
    const seg = el("span", { clase: "segmento", title: `${s.nombre}: ${miles(s.total)} (${pct(s.total)})` });
    seg.style.width = `${(100 * s.total) / total}%`;
    seg.style.background = s.color;
    barra.append(seg);
  }
  const leyenda = el("ul", { clase: "leyenda-semana" }, ...secciones.filter((s) => s.total).map((s) => {
    const muestra = el("span", { clase: "muestra" });
    muestra.style.background = s.color;
    return el("li", { clase: s.codigo === "I" ? "destacada" : "" }, muestra, `${NOMBRE_CORTO[s.codigo] || s.nombre} ${pct(s.total)}`);
  }));
  $("vistazo").replaceChildren(barra, leyenda);
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

// ---------- Secciones por tema y breves ----------

function pintarSecciones(normas, portada) {
  const enPortada = new Set([portada.principal, ...portada.secundarios].filter(Boolean).map((n) => n.id));
  const bloques = estado.indice.temas.map((tema) => {
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
    $("ver-breves").addEventListener("click", () => { portadaEstado.brevesAbiertos = !portadaEstado.brevesAbiertos; pintarBreves(); });
  },
  pintar() {
    portadaEstado.brevesAbiertos = false;
    const portada = elegirPortada(estado.normas);
    pintarPortada(portada);
    pintarCifras();
    pintarPiezas();
    pintarSecciones(estado.normas, portada);
    pintarBreves();
  },
};
