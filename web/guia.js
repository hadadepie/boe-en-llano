/* Guía: la fecha de la última actualización de los datos (la guía no carga app.js). */
(async () => {
  try {
    const r = await fetch("datos/indice.json", { cache: "no-cache" });
    const generado = new Date((await r.json()).generado);
    if (Number.isNaN(generado.getTime())) return;
    const fecha = generado.toLocaleDateString("es-ES", { dateStyle: "long" });
    document.getElementById("datos-al").textContent = `Datos actualizados el ${fecha}`;
    document.getElementById("datos-al-guia").textContent = `La última actualización es del ${fecha}.`;
  } catch {
    /* Sin datos, la guía se lee igual. */
  }
})();
