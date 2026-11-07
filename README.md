# Web de Mindfulness Sensible al Trauma

Web estàtica de Mindfulness Sensible al Trauma (Aleix Boronat i Anna Viñas): sessions individuals online de mindfulness, ioga i psicoteràpia humanista sensibles al trauma. La web és en castellà.

Fet amb el mateix sistema que espiralosona.com (repositori `lespiral/espiralosona`). Es publica amb GitHub Pages des de la carpeta `docs/`.

Estat (7 de novembre de 2026): web sencera amb l'estil de la maqueta de l'Aleix (Lora + Inter, verd sàlvia, fons crema, formes orgàniques) i l'estructura d'espiralosona; falten les 4 imatges d'IA. Fora dels cercadors (`noindex` i `robots.txt` amb Disallow), a https://mindfulnesssensiblealtrauma.com/ (DNS canviats el 7/11/2026 a SWPanel).

El seguiment de la feina és al document del projecte de Claude `claude/pla-de-treball.md`.

## On és cada cosa

- `data/site.json`: el nom, l'adreça pública (`publish`), el menú (`nav`), el botó de la capçalera (`cta`), el contacte (`contact`), les maneres de demanar una sessió amb els preus (`booking`: una sola font per a tota la web), el feed d'Instagram (`instagram`), les xarxes (`social`), el peu amb l'avís d'urgències i els enllaços legals (`footer`), les adreces antigues (`redirects`) i la pàgina d'inici (`home`).
- `data/pages/<adreça>.json`: una pàgina per fitxer. `data/pages/reservar.json` es publica a `/reservar/`.
- `src/templates/`: les plantilles. `page.html` pinta qualsevol pàgina; `parts.html` té les peces (capçalera de pàgina, seccions, targetes, imatges).
- `src/site.css` i `src/site.js`: l'aspecte (Lora per als títols, Inter per al text; verd sàlvia #698770, crema #FAF9F6 i el blau petroli del logo #084859 als blocs foscos), el menú del mòbil i l'exercici d'ancoratge.
- `src/img/`: el logo (`logo.png`, `logo-512.png`) i les icones de la pestanya; `src/img/fotos/`: les fotos.
- `docs/`: la web generada. No s'edita a mà: es torna a generar.
- `tools/proves.py`: prova totes les pàgines en mòbil (390 px) i en ordinador (1440 px).
- `tools/posa-imatges.py`: prepara les imatges noves (vegeu «Imatges»).

## Com es fa un canvi

1. Canvia el text al fitxer de `data/`.
2. Genera la web: `python3 build.py`. Si hi ha alguna errada (un tipus de secció que no existeix, un enllaç del menú a una pàgina que no hi és, un JSON mal escrit), ho diu i no genera res.
3. Prova-la: `python3 tools/proves.py` (errors de JavaScript, scroll lateral i enllaços trencats; amb `--captures` desa captures a `captures/`).
4. Desa i puja els canvis. GitHub Pages la publica sola.

No s'han d'inventar dades: si en falta alguna, es deixa marcada amb `[PENDENT]`. En generar la web, `build.py` diu quantes marques queden.

Preus i horaris: només els que l'Aleix hagi confirmat. Els horaris no surten a la web (les sessions es demanen per correu). La web no parla de pagament per avançat ni mostra dades bancàries.

## Una pàgina

```json
{
  "seo_title": "El títol de la pestanya i dels cercadors",
  "kicker": "Avantítol petit",
  "title": "El títol gran (h1)",
  "title_em": "la part en cursiva i verda",
  "lead": "Una frase sota el títol.",
  "buttons": [{"text": "Escríbenos", "href": "mailto:mindfulnesssensiblealtrauma@gmail.com"}, {"text": "Cómo reservar", "href": "reservar"}],
  "description": "El text dels cercadors.",
  "sections": [ ... ]
}
```

Tipus de secció (`"type"`):

- `text`: `title`, `kicker`, `intro`, `paragraphs`, `list`, `blocks` (`{"h": …, "paragraphs": […], "list": […]}`), `after`. Amb `"image"`, el text va al costat de la foto (`"reverse": true` la posa a l'esquerra; `"ratio": "sq"` la fa quadrada).
- `cards`: targetes blanques (`items`) amb `image`, `icon`, `title`, `subtitle`, `meta` (la línia «Online · 60 minutos · 70 €»), `lead`, `text`, `paragraphs`, `list`, `href` i `button`. `"cols": 2` per dues columnes.
- `pillars`: els pilars amb icona rodona (`items` amb `icon`, `title`, `text`). Amb `"panel": true` van dins el panell blanc arrodonit.
- `anchor`: l'exercici d'ancoratge (`title`, `paragraphs`, `list`, `note`; el cercle: `phases`, `seconds`, `idle`, `start`, `stop`). No dona instruccions de respiració: només acompanya la mirada, i s'atura amb «Parar».
- `booking`: el bloc fosc per demanar una sessió (opcions de `site.booking`; `title` i `paragraphs` s'hi poden canviar).
- `instagram`: els carrussels d'Instagram (vegeu «Instagram»).
- `list`: llista en quadres (`items`; `list_icon` canvia la icona).
- `steps`: passos numerats (`items` amb `title` i `text`).
- `team`: les persones (`items` amb `id`, `photo`, `name`, `role`, `paragraphs` i `blocks` per a la formació).
- `note`: un quadre destacat (`"style": "care"` per a l'avís d'urgències, `"info"` blau fosc).
- `quote`: una cita (`text`, `cite`).
- `cta`: un quadre fosc amb paràgrafs i botons.
- `contact`: quadres per demanar una sessió (per defecte, les opcions de `site.booking`).

Cada secció pot portar `"band"` (`cream`, per defecte, `white`, `soft`, `dark`), `"buttons"` i `"id"`. Els enllaços (`href`) amb una paraula sola són pàgines de la web (`"reservar"` porta a `/reservar/`; `""` és l'inici). `**així**` surt en negreta.

## Imatges

A les dades s'escriu el nom del fitxer (p. ex. `"02-mindfulness.jpg"`). Si és a `src/img/fotos/`, surt la foto; si no, un requadre «Imagen pendiente» amb el nom. `IMATGES-PENDENTS.md` (es refà sol amb `build.py`) diu quines falten i on surten.

Les imatges 01–04 es fan amb IA (Flow, Nano Banana Pro), totes amb el mateix estil: fotografia documental serena, llum natural, colors del logo, sense cares de cara a càmera i sense res que pugui activar. L'Aleix les puja al Drive amb el número davant del nom. Per posar-les:

```
python3 tools/posa-imatges.py 01.png 02.png …   # les retalla a 4:3, redueix i desa a src/img/fotos/
python3 build.py
```

`aleix-boronat.jpg` i `anna-vinas.jpg` són fotos reals (quadrades, de la carpeta de fotos de col·laboradors del Drive), no d'IA.

## Instagram

La secció `instagram` de la portada mostra els carrussels de @mindfulnesssensiblealtrauma automàticament amb Behold (behold.so) quan a `data/site.json` hi ha `instagram.feed_id`. Per activar-ho: l'Aleix crea un feed a behold.so connectant-hi el compte d'Instagram, copia l'ID del feed i es posa a `feed_id`. Mentre és buit, la secció només porta el botó «Seguir en Instagram».

## Avís legal

Els enllaços legals del peu porten a les pàgines de lespiral.cat (com a espiralosona.com).

## Adreces antigues

`/inicio/` (del Google Sites) porta a l'inici; `/reservar/` es manté com a pàgina.

## Publicació

- GitHub Pages, branca `main`, carpeta `/docs`.
- L'adreça i si surt als cercadors són a `data/site.json`, a `publish`. Ara: `https://mindfulnesssensiblealtrauma.com/` i `"index": false` (fins que hi hagi HTTPS).
- Domini (7/11/2026): registrat a SW Hosting (SWPanel → servei «Hosting Redirect Free» del domini → Gestió de DNS). Fitxer `CNAME` amb `mindfulnesssensiblealtrauma.com`; DNS: A `@` a 185.199.108.153, 185.199.109.153, 185.199.110.153 i 185.199.111.153, i CNAME `www` → `lespiral.github.io`. No hi ha correu al domini. Quan hi hagi certificat: «Enforce HTTPS», `"index": true` (treu el noindex, robots Allow i sitemap) i Search Console amb un TXT de verificació (no esborrar-lo mai).
