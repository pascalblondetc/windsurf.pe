# windsurf.pe — Circuito Peruano de Windsurf

Web oficial del CPW.

- `site/` es lo que se publica (Cloudflare Pages, carpeta de salida `site`, sin comando de build).
- `site/data/pronostico.json` lo actualiza la acción **Pronóstico WindGuru** 3 veces al día.
- `site/data/riders.json` y `site/data/eventos.json`: perfiles de riders y textos/fotos de cada campeonato.
- `tools/build_site.py` arma `site/` desde el `index.html` de trabajo.
