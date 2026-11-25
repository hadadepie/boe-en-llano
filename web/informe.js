/* El BOE en llano — lo común de los informes de toda la legislatura (legislatura.html,
   dinero.html y tribunales.html): carga de datos/informe.json, ayudas para los gráficos de
   Chart.js y la etiqueta de la cabecera. Va después de app.js y antes del script de cada página. */

"use strict";

function pintarEtiquetaLegislatura() {
  const L = estado.indice.legislatura;
  $("legislatura-etiqueta").textContent = L
    ? `${L.legislatura} legislatura · desde el ${fechaMedia(L.desde)} hasta la disolución, el ${fechaMedia(L.hasta_pleno)}`
    : "Todavía no hay datos de la legislatura.";
}

// Repintar con los colores del modo claro/oscuro, o al cruzar el corte de pantalla estrecha
// (los nombres largos pasan a partirse en líneas o dejan de hacerlo).
function repintarAlCambiar(repintar) {
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", repintar);
  window.matchMedia("(max-width: 560px)").addEventListener("change", repintar);
}

// Las secciones están ocultas hasta que llegan los datos: el navegador no puede bajar solo al ancla
// de la URL (p. ej. tribunales.html#sentencias-tc), así que se baja al terminar de pintar.
function irAlAncla() {
  const destino = location.hash.length > 1 && document.getElementById(location.hash.slice(1));
  if (destino) destino.scrollIntoView();
}

const graficosInforme = {};
const pct = (parte, total) => (total ? Math.round((100 * parte) / total) : 0);
const nombreMes = (m) => aFecha(`${m}-01`).toLocaleDateString("es-ES", { month: "long", year: "numeric" });
const unos = (x) => (Number.isInteger(x) ? miles(x) : `unos ${miles(Math.round(x))}`);

function nuevoGrafico(clave, lienzo, config) {
  if (graficosInforme[clave]) graficosInforme[clave].destroy();
  graficosInforme[clave] = new Chart(lienzo, config);
}

const leyendaArriba = () => ({ position: "top", align: "start", labels: { color: variable("--tinta"), boxWidth: 12, boxHeight: 12 } });
const ejeValores = (extra = {}) => ({ beginAtZero: true, ticks: { precision: 0, color: variable("--tinta-2"), ...extra }, grid: { color: variable("--linea") } });
const ejeNombres = () => ({ ticks: { color: variable("--tinta"), autoSkip: false }, grid: { display: false } });
const estrecho = () => window.matchMedia("(max-width: 560px)").matches; // el mismo corte que estilos.css
const enLineas = (texto, ancho = 18) => texto.split(" ").reduce((lineas, palabra) => {
  const ultima = lineas[lineas.length - 1];
  if (ultima && (ultima + " " + palabra).length <= ancho) lineas[lineas.length - 1] = `${ultima} ${palabra}`;
  else lineas.push(palabra);
  return lineas;
}, []);

const lista = (xs) => (xs.length > 1 ? `${xs.slice(0, -1).join(", ")} y ${xs[xs.length - 1]}` : xs.join(""));
const recortar = (texto, n = 140) => (texto.length > n ? `${texto.slice(0, n).replace(/\s+\S*$/, "")}…` : texto);
const mayuscula = (t) => t.charAt(0).toUpperCase() + t.slice(1);

let informeCargado;
async function cargarInforme() {
  if (informeCargado === undefined) {
    try { informeCargado = await cargarJson("informe.json"); } catch (e) { informeCargado = null; }
  }
  return informeCargado;
}
