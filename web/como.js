/* El BOE en llano — «Cómo se ha hecho» (como.html): fuentes, método, límites,
   glosario y correcciones. No depende de la edición semanal. */

"use strict";

function pintarGlosario() {
  $("glosario").replaceChildren(...Object.values(GLOSARIO)
    .sort((a, b) => a[0].localeCompare(b[0], "es"))
    .flatMap(([t, d]) => [el("dt", { texto: t }), el("dd", { texto: d })]));
}

function pintarEstadoFichas() {
  const n = estado.indice.num_normas;
  const ok = estado.indice.resumen.fichas_verificadas;
  $("estado-fichas").textContent = ok === 0
    ? `Ahora mismo las ${miles(n)} fichas están pendientes.`
    : `Ahora mismo ${miles(ok)} de ${miles(n)} fichas tienen resumen automático experimental; el resto están pendientes porque el resumen no superó las comprobaciones.`;
}

// Los enlaces «Cómo se calcula», «Limitaciones» o «Correcciones» llevan a un apartado (como.html#correcciones):
// se abre y se baja hasta él.
function abrirApartado() {
  const destino = location.hash.length > 1 && document.getElementById(location.hash.slice(1));
  if (!destino || destino.tagName !== "DETAILS") return;
  destino.open = true;
  destino.scrollIntoView();
}

window.PAGINA = {
  sinEdicion: true,
  preparar() { window.addEventListener("hashchange", abrirApartado); },
  pintar() {
    pintarGlosario();
    pintarEstadoFichas();
    abrirApartado();
  },
};
