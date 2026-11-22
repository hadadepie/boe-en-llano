/* El BOE en llano — lógica de la página.
   Lee datos.json (generado por `python -m boe.exportar`) y pinta:
   cabecera, gráfico por secciones, matriz tema × impacto, lista filtrable y ficha.
   Todo texto que viene de los datos se inserta con textContent (nunca innerHTML). */

"use strict";

const estado = { datos: null, filtros: { fecha: "", tema: "", impacto: "", ambito: "" }, seleccion: null, grafico: null };
const $ = (id) => document.getElementById(id);

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

// ---------- Cabecera ----------

function pintarCabecera() {
  const r = estado.datos.resumen;
  $("frase").textContent = r.frase;
  $("c-total").textContent = miles(r.total_publicaciones);
  $("c-normas").textContent = miles(r.normas_generales);
  $("c-pct").textContent = r.porcentaje_normas;
  $("c-directo").textContent = miles(r.impacto_directo);
  const generado = new Date(estado.datos.generado);
  $("generado").textContent = `Actualizado el ${generado.toLocaleString("es-ES", { dateStyle: "long", timeStyle: "short" })}.`;
  const n = estado.datos.normas.length;
  const ok = r.fichas_verificadas;
  $("estado-fichas").textContent = ok === 0
    ? `Ahora mismo las ${n} fichas están pendientes: no hay ningún modelo de IA configurado.`
    : `Ahora mismo ${ok} de ${n} fichas tienen resumen verificado; el resto están pendientes.`;
}

// ---------- Gráfico de barras apiladas ----------

function pintarGrafico() {
  if (!window.Chart) {
    $("grafico").replaceWith(el("p", { clase: "ayuda", texto: "No se ha podido cargar la librería del gráfico. Los datos están en la tabla de abajo." }));
    return;
  }
  const { dias, secciones } = estado.datos;
  const superficie = variable("--superficie");
  const series = secciones.map((s, i) => ({
    label: s.nombre,
    data: dias.map((d) => d.recuento[s.codigo]),
    backgroundColor: variable(`--s${i + 1}`),
    borderColor: superficie,
    borderWidth: { top: 2 },   // hueco de 2 px entre segmentos
    borderSkipped: "start",
    borderRadius: i === secciones.length - 1 ? { topLeft: 4, topRight: 4 } : 0,
    maxBarThickness: 24,
  }));

  if (estado.grafico) estado.grafico.destroy();
  estado.grafico = new Chart($("grafico"), {
    type: "bar",
    data: { labels: dias.map((d) => fechaCorta(d.fecha)), datasets: series },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: { stacked: true, grid: { display: false }, ticks: { color: variable("--tinta-2") }, border: { color: variable("--linea") } },
        y: { stacked: true, beginAtZero: true, grid: { color: variable("--linea") }, ticks: { color: variable("--tinta-2"), precision: 0 }, border: { display: false } },
      },
      plugins: {
        legend: { position: "top", align: "start", labels: { color: variable("--tinta"), boxWidth: 12, boxHeight: 12, useBorderRadius: true, borderRadius: 2 } },
        tooltip: {
          callbacks: {
            title: (items) => fechaLarga(dias[items[0].dataIndex].fecha),
            label: (item) => ` ${miles(item.raw)}  ${item.dataset.label}`,
            footer: (items) => `Total: ${miles(items.reduce((s, i) => s + i.raw, 0))}`,
          },
        },
      },
    },
  });
}

function pintarTablaDias() {
  const { dias, secciones } = estado.datos;
  const tabla = $("tabla-dias");
  tabla.replaceChildren(
    el("thead", {}, el("tr", {}, el("th", { texto: "Fecha" }), ...secciones.map((s) => el("th", { texto: s.codigo })), el("th", { texto: "Total" }))),
    el("tbody", {}, ...dias.map((d) => el("tr", {},
      el("td", { texto: fechaCorta(d.fecha) }),
      ...secciones.map((s) => el("td", { texto: miles(d.recuento[s.codigo]) })),
      el("td", { texto: miles(Object.values(d.recuento).reduce((a, b) => a + b, 0)) }),
    ))),
  );
}

// ---------- Filtros ----------

function normasFiltradas({ ignorar = [] } = {}) {
  const f = estado.filtros;
  return estado.datos.normas.filter((n) =>
    (ignorar.includes("fecha") || !f.fecha || n.fecha === f.fecha) &&
    (ignorar.includes("tema") || !f.tema || n.tema === f.tema) &&
    (ignorar.includes("impacto") || !f.impacto || n.impacto === f.impacto) &&
    (ignorar.includes("ambito") || !f.ambito || n.ambito === f.ambito));
}

function rellenarSelect(select, todas, opciones, formato = (x) => x) {
  select.replaceChildren(el("option", { value: "", texto: todas }), ...opciones.map((o) => el("option", { value: o, texto: formato(o) })));
}

function prepararFiltros() {
  const { normas, temas, impactos } = estado.datos;
  const fechas = [...new Set(normas.map((n) => n.fecha))].sort().reverse();
  const ambitos = [...new Set(normas.map((n) => n.ambito))].sort((a, b) => (a === "Estatal" ? -1 : b === "Estatal" ? 1 : a.localeCompare(b, "es")));
  rellenarSelect($("f-fecha"), "Todas las fechas", fechas, fechaCorta);
  rellenarSelect($("f-tema"), "Todos los temas", temas);
  rellenarSelect($("f-impacto"), "Todos", impactos);
  rellenarSelect($("f-ambito"), "Todos", ambitos);

  for (const clave of Object.keys(estado.filtros)) {
    $(`f-${clave}`).addEventListener("change", (e) => { estado.filtros[clave] = e.target.value; actualizar(); });
  }
  $("filtros").addEventListener("reset", () => {
    setTimeout(() => { for (const k of Object.keys(estado.filtros)) estado.filtros[k] = ""; actualizar(); });
  });
}

function sincronizarSelects() {
  for (const [clave, valor] of Object.entries(estado.filtros)) $(`f-${clave}`).value = valor;
}

// ---------- Matriz tema × impacto ----------

function pintarMatriz() {
  const { temas, impactos } = estado.datos;
  const base = normasFiltradas({ ignorar: ["tema", "impacto"] }); // la matriz respeta fecha y ámbito
  const cuenta = (t, i) => base.filter((n) => n.tema === t && n.impacto === i).length;
  const maximo = Math.max(1, ...temas.flatMap((t) => impactos.map((i) => cuenta(t, i))));

  const celda = (tema, impacto) => {
    const n = cuenta(tema, impacto);
    const paso = n === 0 ? 0 : Math.max(1, Math.ceil((n / maximo) * 6));
    const fondo = variable(`--m${paso}`);
    const activa = estado.filtros.tema === tema && estado.filtros.impacto === impacto;
    const boton = el("button", {
      type: "button",
      clase: "celda" + (paso > 0 && luminancia(fondo) < 0.3 ? " clara" : ""),
      "aria-pressed": String(activa),
      "aria-label": `${n} normas de ${tema} con impacto ${impacto}`,
      title: `${tema} · ${impacto}: ${n}`,
      texto: String(n),
      onclick: () => {
        const quitar = activa;
        estado.filtros.tema = quitar ? "" : tema;
        estado.filtros.impacto = quitar ? "" : impacto;
        actualizar();
        if (!quitar) $("normas").scrollIntoView({ behavior: "smooth", block: "start" });
      },
    });
    boton.style.background = fondo;
    if (n === 0) boton.disabled = true;
    return el("td", {}, boton);
  };

  $("matriz").replaceChildren(
    el("thead", {}, el("tr", {}, el("th", { scope: "col", texto: "Tema" }), ...impactos.map((i) => el("th", { scope: "col", texto: i })), el("th", { scope: "col", texto: "Total" }))),
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
  return el("span", { clase: `etiqueta ${ok ? "ok" : "pendiente"}`, texto: ok ? "✓ Resumen verificado" : "⏳ Resumen pendiente" });
}

function pintarLista() {
  const normas = normasFiltradas();
  const total = estado.datos.normas.length;
  $("contador").textContent = normas.length === total
    ? `${total} normas generales.`
    : `${normas.length} de ${total} normas con estos filtros.`;

  const lista = $("lista");
  if (normas.length === 0) {
    lista.replaceChildren(el("li", {}, el("p", { clase: "ayuda", texto: "No hay normas con estos filtros." })));
    return;
  }
  lista.replaceChildren(...normas.map((n) => {
    const titulo = (n.ficha && n.ficha.titulo_llano) || n.titulo;
    return el("li", {}, el("button", {
      type: "button",
      "aria-current": String(estado.seleccion === n.id),
      onclick: () => seleccionar(n.id, true),
    },
    el("span", { clase: "t", texto: titulo }),
    el("span", { clase: "m", texto: `${fechaCorta(n.fecha)} · ${n.rango || ""} · ${n.ambito}` }),
    el("span", { clase: "m" }, el("span", { clase: "etiqueta", texto: n.tema }), el("span", { clase: "etiqueta", texto: n.impacto }), etiquetaEstado(n.ficha)),
    ));
  }));
}

// ---------- Ficha ----------

function pintarFicha(n) {
  const ficha = n.ficha || {};
  const ok = ficha.estado === "ok";
  const hijos = [
    etiquetaEstado(ficha),
    el("h3", { texto: ficha.titulo_llano || n.titulo }),
  ];

  if (ok) {
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
    hijos.push(el("p", { clase: "ayuda", texto: "Todavía no hay un resumen verificado de esta norma. Arriba tienes su título simplificado; para saber qué dice, consulta el texto oficial." }));
  }

  hijos.push(el("p", { clase: "oficial" }, el("strong", { texto: "Título oficial: " }), n.titulo));
  hijos.push(el("a", { clase: "enlace", href: ficha.enlace || n.url_html, target: "_blank", rel: "noopener", texto: "Leer el texto oficial en boe.es →" }));

  const datos = [
    ["Publicada", fechaLarga(n.fecha)],
    ["Tipo", n.rango],
    ["Órgano", n.organo],
    ["Ámbito", n.ambito],
    ["Tema", n.tema],
    ["Impacto", n.impacto],
    ["Identificador", n.id],
  ];
  hijos.push(el("dl", { clase: "datos" }, ...datos.filter(([, v]) => v).flatMap(([t, v]) => [el("dt", { texto: t }), el("dd", { texto: v })])));

  const c = n.clasificacion || {};
  if (c.metodo === "reglas") {
    const motivos = [...(c.motivos_tema || []), ...(c.motivos_impacto || [])].join(" · ");
    hijos.push(el("p", { clase: "motivos", texto: `Clasificada con reglas automáticas: ${motivos}.` }));
  } else if (c.metodo === "ia") {
    hijos.push(el("p", { clase: "motivos", texto: `Clasificada con IA (${c.modelo}): ${c.motivo || ""}` }));
  }

  hijos.push(el("p", { clase: "aviso", texto: ficha.aviso || "Resumen orientativo, no es asesoramiento jurídico. Consulta el texto oficial." }));
  $("ficha").replaceChildren(...hijos);
}

function seleccionar(id, porUsuario = false) {
  const n = estado.datos.normas.find((x) => x.id === id);
  if (!n) return;
  estado.seleccion = id;
  pintarFicha(n);
  pintarLista();
  history.replaceState(null, "", `#${id}`);
  if (porUsuario && window.matchMedia("(max-width: 800px)").matches) {
    $("ficha").scrollIntoView({ behavior: "smooth", block: "start" });
    $("ficha").focus({ preventScroll: true });
  }
}

// ---------- Arranque ----------

function actualizar() {
  sincronizarSelects();
  pintarMatriz();
  pintarLista();
}

async function iniciar() {
  try {
    const respuesta = await fetch("datos.json", { cache: "no-cache" });
    if (!respuesta.ok) throw new Error(respuesta.status);
    estado.datos = await respuesta.json();
  } catch (error) {
    $("frase").textContent = "No se han podido cargar los datos. Genera web/datos.json con «python -m boe.exportar» y abre la página con un servidor local.";
    return;
  }
  pintarCabecera();
  pintarTablaDias();
  pintarGrafico();
  prepararFiltros();
  actualizar();

  const inicial = location.hash.slice(1);
  if (inicial) seleccionar(inicial);

  // Repintar con los colores del modo claro/oscuro cuando cambie.
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { pintarGrafico(); pintarMatriz(); });
}

document.addEventListener("DOMContentLoaded", iniciar);
