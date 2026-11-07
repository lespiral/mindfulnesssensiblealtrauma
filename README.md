# Web de Mindfulness Sensible al Trauma

Web estàtica de Mindfulness Sensible al Trauma (Aleix Boronat i Anna Viñas): sessions individuals online de mindfulness, ioga i psicoteràpia humanista sensibles al trauma. La web és en castellà.

Fet amb el mateix sistema que espiralosona.com (repositori `lespiral/espiralosona`). Es publica amb GitHub Pages des de la carpeta `docs/`.

Estat (7 de novembre de 2026): primera versió, sense imatges i fora dels cercadors (`noindex` i `robots.txt` amb Disallow), a https://lespiral.github.io/mindfulnesssensiblealtrauma/. El domini mindfulnesssensiblealtrauma.com encara no hi apunta.

El seguiment de la feina és al document del projecte de Claude `claude/pla-de-treball.md`.

## On és cada cosa

- `data/site.json`: el nom, l'adreça pública (`publish`), el menú (`nav`), el botó de la capçalera (`cta`), el contacte (`contact`), l'enllaç de reserves (`booking`), les xarxes (`social`), el peu amb l'avís d'urgències (`footer`), les adreces antigues (`redirects`) i la pàgina d'inici (`home`).
- `data/pages/<adreça>.json`: una pàgina per fitxer. `data/pages/reservar.json` es publica a `/reservar/`.
- `src/templates/`: les plantilles. `page.html` pinta qualsevol pàgina; `parts.html` té les peces (capçalera de pàgina, seccions, targetes, imatges).
- `src/site.css` i `src/site.js`: l'aspecte (Inter, com la plantilla aprovada d'Instagram, i els colors del logo: blau petroli #084859 i verds #DCEEE9 i #7AA888) i el menú del mòbil.
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

Preus i horaris: només els que l'Aleix hagi confirmat. Els horaris no surten a la web (són al calendari de reserves). La web no parla de pagament per avançat ni mostra dades bancàries.

## Una pàgina

```json
{
  "seo_title": "El títol de la pestanya i dels cercadors",
  "kicker": "Avantítol petit",
  "title": "El títol gran (h1)",
  "lead": "Una frase sota el títol.",
  "buttons": [{"text": "Escríbenos", "href": "mailto:mindfulnesssensiblealtrauma@gmail.com"}, {"text": "Cómo reservar", "href": "reservar"}],
  "description": "El text dels cercadors.",
  "sections": [ ... ]
}
```

Tipus de secció (`"type"`):

- `text`: `title`, `kicker`, `intro`, `paragraphs`, `list`, `blocks` (`{"h": …, "paragraphs": […], "list": […]}`), `after`. Amb `"image"`, el text va al costat de la foto (`"reverse": true` la posa a l'esquerra; `"ratio": "sq"` la fa quadrada).
- `cards`: targetes (`items`) amb `image`, `icon`, `badge`, `title`, `subtitle`, `meta` (la línia «Online · 60 minutos · 70 €»), `lead`, `text`, `paragraphs`, `list`, `href` i `button`. `"cols": 2` per dues columnes.
- `list`: llista en quadres (`items`; `list_icon` canvia la icona).
- `steps`: passos numerats (`items` amb `title` i `text`).
- `team`: les persones (`items` amb `id`, `photo`, `name`, `role`, `paragraphs` i `blocks` per a la formació).
- `note`: un quadre destacat (`"style": "care"` per a l'avís d'urgències, `"info"` blau fosc).
- `quote`: una cita (`text`, `cite`).
- `cta`: un quadre fosc amb paràgrafs i botons.
- `contact`: quadres per demanar una sessió (`items` amb `icon`, `title`, `paragraphs` i `buttons`).

Cada secció pot portar `"band"` (`white`, `soft`, `stone`, `cream`, `dark`), `"buttons"` i `"id"`. Els enllaços (`href`) amb una paraula sola són pàgines de la web (`"reservar"` porta a `/reservar/`; `""` és l'inici). `**així**` surt en negreta.

## Imatges

A les dades s'escriu el nom del fitxer (p. ex. `"03-mindfulness.jpg"`). Si és a `src/img/fotos/`, surt la foto; si no, un requadre «Imagen pendiente» amb el nom. `IMATGES-PENDENTS.md` (es refà sol amb `build.py`) diu quines falten i on surten.

Les imatges 01–05 es fan amb IA (Flow, Nano Banana Pro), totes amb el mateix estil: fotografia documental serena, llum natural, colors del logo, sense cares de cara a càmera i sense res que pugui activar. L'Aleix les puja al Drive amb el número davant del nom. Per posar-les:

```
python3 tools/posa-imatges.py 01.png 02.png …   # les retalla (01 vertical 4:5; la resta 4:3), redueix i desa a src/img/fotos/
python3 build.py
```

`aleix-boronat.jpg` i `anna-vinas.jpg` són fotos reals (quadrades), no d'IA.

## Adreces antigues

`/inicio/` (del Google Sites) porta a l'inici; `/reservar/` es manté com a pàgina.

## Publicació

- GitHub Pages, branca `main`, carpeta `/docs`.
- L'adreça i si surt als cercadors són a `data/site.json`, a `publish`. Ara: `https://lespiral.github.io/mindfulnesssensiblealtrauma/` i `"index": false`.
- Per passar al domini (quan l'Aleix digui que sí): apuntar abans tota la zona DNS al pla de treball; fitxer `CNAME` amb `mindfulnesssensiblealtrauma.com`; `publish` a `https://mindfulnesssensiblealtrauma.com/` i `"index": true`; DNS: A `@` a 185.199.108.153, 185.199.109.153, 185.199.110.153 i 185.199.111.153, i CNAME `www` → `lespiral.github.io`. El correu (MX) no es toca. Després, «Enforce HTTPS» i Search Console.
