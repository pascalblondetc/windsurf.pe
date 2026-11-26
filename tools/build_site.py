#!/usr/bin/env python3
"""Arma la web oficial (windsurf.pe) a partir de index.html.

Uso:  python3 tools/build_site.py <carpeta-del-repo>
Escribe <repo>/site/ (lo que publica Cloudflare Pages). No toca site/data/pronostico.json
si ya existe, porque ese archivo lo actualiza la acción de GitHub.
"""
import json, re, shutil, sys, datetime as dt
from pathlib import Path

DOMAIN = 'https://windsurf.pe'
SRC = Path(__file__).resolve().parent.parent          # carpeta con index.html e img/
OUT = Path(sys.argv[1]).resolve() / 'site'

TITLE = 'Circuito Peruano de Windsurf (CPW) · Campeonatos, ranking y spots del Perú'
DESC = ('Circuito Peruano de Windsurf: calendario de campeonatos 2026, resultados y ranking nacional, '
        'spots del Perú con pronóstico de viento y olas, y las modalidades Olas, Slalom, IQFoil y Techno 293.')

body = (SRC / 'index.html').read_text(encoding='utf-8')
# quitar el <title>/<meta description> del artefacto: van en el <head> de abajo
body = re.sub(r'<title>.*?</title>\s*', '', body, count=1, flags=re.S)
body = re.sub(r'<meta name="description"[^>]*>\s*', '', body, count=1)
body = re.sub(r'<meta name="claude:[^>]*>\s*', '', body)

# eventos para datos estructurados (Google)
events = []
for m in re.finditer(r"\{id:'(\w+)',name:'([^']+)'(?:,sub:'[^']*')?,start:'([\d-]+)',end:'([\d-]+)'[^}]*?place:'([^']+)'[^}]*?\}", body):
    eid, name, start, end, place = m.groups()
    cancelled = 'cancelled:true' in m.group(0)
    ev = {'@type': 'SportsEvent', 'name': name + ' · Circuito Peruano de Windsurf', 'sport': 'Windsurf',
          'startDate': start, 'endDate': end, 'url': f'{DOMAIN}/#evento-{eid}',
          'eventStatus': 'https://schema.org/EventCancelled' if cancelled else 'https://schema.org/EventScheduled',
          'location': {'@type': 'Place', 'name': place, 'address': {'@type': 'PostalAddress', 'addressCountry': 'PE', 'streetAddress': place}},
          'organizer': {'@type': 'SportsOrganization', 'name': 'Circuito Peruano de Windsurf', 'url': DOMAIN}}
    events.append(ev)
ld = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'SportsOrganization', 'name': 'Circuito Peruano de Windsurf', 'alternateName': 'CPW', 'sport': 'Windsurf',
     'url': DOMAIN, 'logo': f'{DOMAIN}/img/logo.png', 'areaServed': 'PE',
     'sameAs': ['https://www.instagram.com/windsurfing.peru/']},
    {'@type': 'WebSite', 'name': 'Circuito Peruano de Windsurf', 'url': DOMAIN, 'inLanguage': 'es-PE'}] + events}

head = f'''<!doctype html>
<html lang="es-PE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{DOMAIN}/">
<meta name="theme-color" content="#C8102E">
<link rel="icon" type="image/png" href="/img/favicon.png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Circuito Peruano de Windsurf">
<meta property="og:locale" content="es_PE">
<meta property="og:title" content="Circuito Peruano de Windsurf">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{DOMAIN}/">
<meta property="og:image" content="{DOMAIN}/img/og-cpw.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>[hidden]{{display:none!important}}body{{margin:0}}</style>
</head>
<body>
'''
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'index.html').write_text(head + body + '\n</body>\n</html>\n', encoding='utf-8')

# imágenes
shutil.copytree(SRC / 'img', OUT / 'img', dirs_exist_ok=True)

# SEO
today = dt.date.today().isoformat()
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n')
(OUT / 'sitemap.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>
</urlset>
''')
# Cloudflare Pages: los datos cambian seguido, las imágenes no
(OUT / '_headers').write_text('''/data/*
  Cache-Control: no-cache
/img/*
  Cache-Control: public, max-age=604800
/fotos/*
  Cache-Control: public, max-age=604800
''')
(OUT / 'data').mkdir(exist_ok=True)
print('site listo:', OUT, '·', len(events), 'eventos en datos estructurados')
