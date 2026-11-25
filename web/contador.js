/* El BOE en llano — contador de visitas sin cookies (GoatCounter).

   No se carga el script de GoatCounter: estas líneas piden una imagen de 1×1 a su servidor con un
   único dato, la página visitada (p. ej. «/boe-en-llano/legislatura.html»). No se envía el título, ni
   de dónde viene la visita, ni el tamaño de pantalla, ni la cabecera Referer; no se guarda nada en el
   navegador. GoatCounter ve, como cualquier servidor, la dirección IP y el navegador: los usa en
   memoria para no contar dos veces la misma visita y no los guarda (https://www.goatcounter.com/privacy).

   No cuenta: fuera de la web publicada (vista previa, copias) ni si el navegador pide no ser
   rastreado (Global Privacy Control o Do Not Track). Explicado en «Cómo se ha hecho». */

"use strict";

(() => {
  const WEB = "hadadepie.github.io";
  const CONTADOR = "https://boe-en-llano.goatcounter.com/count";
  const noRastrear = navigator.globalPrivacyControl === true || navigator.doNotTrack === "1";
  if (location.hostname !== WEB || noRastrear) return;
  const pagina = location.pathname.endsWith("/") ? `${location.pathname}index.html` : location.pathname;
  const pixel = new Image();
  pixel.referrerPolicy = "no-referrer";
  pixel.src = `${CONTADOR}?p=${encodeURIComponent(pagina)}&rnd=${Math.random().toString(36).slice(2)}`;
})();
