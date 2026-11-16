#!/usr/bin/env python3
"""Erzeugt die statischen HTML-Seiten von grabmale.lionify.de.

Aufruf (im Repo-Ordner):  python3 scripts/build.py
Kopf, Navigation und Fußzeile stehen hier zentral, damit alle Seiten gleich bleiben.
Bilder liegen in img/<kategorie>/<kategorie>-NN.jpg (groß) und -NN-k.jpg (Vorschau).
"""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

SITE = "https://grabmale.lionify.de"
NAME = "Grabmale aus Lehsen"
OWNER = "Bernhard Gerdes"
STREET = "Unter den Linden 14"
ZIP_CITY = "19243 Wittenburg OT Lehsen"
PHONE = "+49 38852 50954"
PHONE_HREF = "+493885250954"
PHONE_SHOW = "038852 / 509 54"
MAIL = "steine@online.de"
HOURS = "Termine nach Vereinbarung – auch abends und samstags"
MAP_URL = "https://www.openstreetmap.org/search?query=Unter%20den%20Linden%2014%2C%2019243%20Wittenburg"

EBAY_URL = "https://www.ebay.de/str/grabsteine"
EBAY_SOLD = "über 6.300"

NAV = [
    ("index.html", "Start"),
    ("grabmale.html", "Grabmale"),
    ("referenzen.html", "Referenzen"),
    ("ratgeber.html", "Ratgeber"),
    ("anfahrt.html", "Anfahrt"),
]
SITEMAP_META = {}
CSS = ""
RATGEBER_PAGES = ("ratgeber.html", "friedhofssatzungen.html", "steinsorten.html")

CATEGORIES = [
    {
        "slug": "breitsteine", "title": "Breitsteine", "card": "breitsteine-07",
        "short": "Das klassische Grabmal für Doppelgrabstellen.",
        "intro": "Breitsteine sind auf unseren Friedhöfen die häufigsten Grabmale für Doppelgrabstellen – ruhig, ausgewogen und mit viel Raum für eine persönliche Gestaltung.",
        "text": [
            "Ihrem Namen entsprechend sind Breitsteine breiter als hoch. Dadurch bieten sie eine relativ große Fläche für Inschriften und Ornamente, und die Gestaltungsmöglichkeiten sind entsprechend vielfältig.",
            "Inschriften und Ornamente arbeiten wir vertieft oder erhaben in den Stein ein oder setzen sie aus langlebigen Materialien wie Bronze, Aluminium oder Edelstahl auf. So erhält jedes Grabmal eine persönliche Note, die an die Interessen und Eigenschaften der Verstorbenen erinnert.",
        ],
    },
    {
        "slug": "reihensteine", "title": "Reihensteine", "card": "reihensteine-10",
        "short": "Das persönliche Zeichen für die Einzelgrabstelle.",
        "intro": "Der Reihenstein – auch Einzelstein genannt – ist in der Regel ein sehr ausdrucksstarkes Erinnerungszeichen für eine Einzelgrabstelle.",
        "text": [
            "Mit einem Spruch und den individuellen Daten der Verstorbenen lässt er sich klassisch oder modern gestalten. Unterschiedliche Granite und Bearbeitungen sind hier möglich.",
            "Bei aller Vielfalt der Gestaltung muss immer die jeweilige Friedhofssatzung der Kommune oder Kirche beachtet werden. Sie gibt oft Größe und Bearbeitung des Grabsteines vor – wir kennen die Vorgaben und beraten Sie entsprechend.",
            "Jeder Grabstein ist ein persönliches Zeichen.",
        ],
    },
    {
        "slug": "stelen", "title": "Stelen", "card": "stelen-12",
        "short": "Eines der ältesten Grabzeichen – heute wieder gefragt.",
        "intro": "Die Grabstele ist eines der ältesten Grabzeichen überhaupt. Im klassischen Sinn hat sie die Form eines Obelisken – schlank, aufrecht und zeitlos.",
        "text": [
            "Früher waren Stelen sehr häufig auf den Friedhöfen zu finden. In jüngster Zeit gewinnen sie wieder an Bedeutung.",
            "Moderne Materialien und Bearbeitungstechniken lassen sich bei der Fertigung sehr schön berücksichtigen. Auch der ursprüngliche Brauch, Stelen neben Inschriften und Grabschmuck mit Abbildungen zu gestalten, gibt uns großen gestalterischen Freiraum.",
        ],
    },
    {
        "slug": "liegesteine", "title": "Liegesteine", "card": "liegesteine-05",
        "short": "Schlicht, pflegeleicht und ideal für Urnengräber.",
        "shop": "Liege- und Rasensteine sowie Grabherzen mit Ihrer Inschrift können Sie auch direkt in unserem eBay-Shop bestellen.",
        "intro": "Liegesteine – auch Kissensteine genannt – liegen flach oder leicht geneigt auf dem Grab. Sie wirken zurückhaltend und fügen sich harmonisch in die Grabgestaltung ein.",
        "text": [
            "Besonders für Urnengrabstellen und kleinere Grabflächen ist der Liegestein eine beliebte Wahl. Er lässt sich gut mit Bepflanzung, Kies oder einer Teilabdeckung kombinieren und ist dabei angenehm pflegeleicht.",
            "Ob naturbelassen mit bruchrauer Kante, fein geschliffen oder in Herz- und Buchform: Durch unterschiedliche Granite, Formen und Oberflächen entsteht auch auf kleiner Fläche ein ganz persönliches Erinnerungszeichen. Inschriften, Ornamente und Symbole arbeiten wir vertieft ein oder setzen sie in Bronze oder Edelstahl auf.",
            "Auch für bestehende Liegesteine übernehmen wir Nachbeschriftungen.",
        ],
    },
    {
        "slug": "grabanlagen", "title": "Grabanlagen", "card": "grabanlagen-06",
        "short": "Einfassung, Abdeckung und Zubehör aus einer Hand.",
        "shop": "Urnengrab-Einfassungen und Zubehör wie Stützen und Sockel finden Sie auch in unserem eBay-Shop.",
        "intro": "Bei der Gestaltung einer Grabstätte haben Angehörige viele Möglichkeiten – von der schlichten Grabtafel bis zur vollständigen, individuellen Grabanlage.",
        "text": [
            "Ob Grabtafel, Kissenstein, Standstein oder eine individuelle Grabanlage mit Grabsteineinfassung und Abdeckung: Mit Grablichtern, Grabvasen und weiterem Zubehör sind der Vielfalt kaum Grenzen gesetzt.",
            "Gerne fertigen wir eine Grabanlage nach Ihren Wünschen und Vorstellungen an – und beraten Sie dabei ausführlich.",
        ],
    },
]


def v(path):
    """Hängt eine Versionsnummer an, damit Browser nach Änderungen neu laden."""
    h = hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]
    return f"{path}?v={h}"


def images(slug):
    files = sorted(p for p in (ROOT / "img" / slug).glob(f"{slug}-[0-9][0-9].jpg"))
    return [f"img/{slug}/{p.stem}" for p in files]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


LOCAL_BUSINESS = {
    "@context": "https://schema.org",
    "@type": "HomeAndConstructionBusiness",
    "name": NAME,
    "alternateName": "Schrift im Stein",
    "founder": {"@type": "Person", "name": OWNER},
    "description": "Grabmale, Grabsteine und Grabanlagen aus Naturstein – persönliche Beratung und Ausstellung in Lehsen bei Wittenburg.",
    "url": SITE + "/",
    "telephone": PHONE,
    "email": MAIL,
    "image": SITE + "/img/hero/ausstellung-960.jpg",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": STREET,
        "postalCode": "19243",
        "addressLocality": "Wittenburg OT Lehsen",
        "addressRegion": "Mecklenburg-Vorpommern",
        "addressCountry": "DE",
    },
    "areaServed": "Westmecklenburg",
    "geo": {"@type": "GeoCoordinates", "latitude": 53.4892, "longitude": 11.0274},
    "priceRange": "Individuelles Angebot",
    "sameAs": ["https://www.ebay.de/str/grabsteine"],
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Leistungen", "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for n in
        ("Grabsteine und Grabmale", "Stelen", "Liegesteine und Grabherzen", "Grabanlagen und Einfassungen", "Nachbeschriftung", "Aufarbeitung und Standsicherheit")]},
    "knowsAbout": ["Grabmale", "Naturstein", "Friedhofssatzungen in Westmecklenburg"],
}


SEARCH_ICON = '<svg class="ico-search" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.5 15.5 21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
WINTER_JS = "(function(){var m=new Date().getMonth();if(m>=10||m<=1){document.getElementById('winter').hidden=false;}})();"
WINTER_HASH = "sha256-" + __import__("base64").b64encode(hashlib.sha256(WINTER_JS.encode()).digest()).decode()


def css_min():
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def to_picture(html):
    """Ersetzt <img src="….jpg"> durch <picture> mit WebP-Quelle, sofern vorhanden."""
    def rep(m):
        tag = m.group(0)
        if "srcset=" in tag:
            return tag
        src = re.search(r'src="([^"]+)\.jpg"', tag)
        if not src:
            return tag
        base = src.group(1)
        local = base.replace("../", "")
        if not (ROOT / f"{local}.webp").exists():
            return tag
        return f'<picture><source type="image/webp" srcset="{base}.webp">{tag}</picture>'
    html = re.sub(r"<img\b[^>]*>", rep, html)
    # Lightbox-Links auf WebP
    html = re.sub(r'(<a href="[^"]+?)\.jpg" data-lb', lambda m: (m.group(1) + '.webp" data-lb') if (ROOT / (m.group(1).split('"')[-1].replace("../", "") + ".webp")).exists() else m.group(0), html)
    return html


def page(filename, title, description, body, current=None, head_extra="", prefix="", noindex=False, crumbs=None, schema=None, full_title=None):
    def nav_link(href, label):
        cur = ' aria-current="page"' if current == href else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    items = []
    for href, label in NAV:
        if href == "ratgeber.html":
            active = current in RATGEBER_PAGES or current == "ratgeber.html"
            sub = "".join(nav_link(h, t) for h, t in (("ratgeber.html", "Häufige Fragen"), ("friedhofssatzungen.html", "Friedhofssatzungen"), ("steinsorten.html", "Steinsorten")))
            items.append(f'<div class="nav-item has-sub"><a href="ratgeber.html" class="nav-parent{" is-active" if active else ""}" aria-haspopup="true">Ratgeber</a><div class="sub">{sub}</div></div>')
        else:
            items.append(nav_link(href, label))
    cur = ' aria-current="page"' if current == "kontakt.html" else ""
    items.append(f'<a class="nav-cta" href="kontakt.html"{cur}>Kontakt</a>')
    if full_title is None:
        full_title = f"{title} | {NAME}" if title != NAME else f"{NAME} – Grabmale & Grabsteine bei Wittenburg"
    canonical = SITE + "/" + ("" if filename == "index.html" else filename)
    ld = list(schema or [])
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + u} for i, (n, u) in enumerate(crumbs)]})
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = '<meta name="robots" content="noindex, follow">\n' if noindex else ""
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
{robots}<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/img/hero/ausstellung-960.jpg">
<meta property="og:locale" content="de_DE">
<meta name="theme-color" content="#26282b">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<style>{CSS}</style>
{head_extra}{ld_html}</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<div class="notice" id="winter" hidden>
  <div class="wrap"><strong>Winterrabatt</strong><span>In den Wintermonaten bieten wir attraktive Rabatte auf Natursteine und Zubehör.</span><a href="kontakt.html">Unverbindliches Angebot anfragen</a></div>
</div>
<script>{WINTER_JS}</script>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html"><strong>{NAME}</strong><span>{OWNER} · Steinmetz</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav"><span></span>Menü</button>
    <nav class="nav" id="nav" aria-label="Hauptnavigation">
      {"".join(items)}
    </nav>
    <button class="search-toggle" type="button" aria-expanded="false" aria-controls="suche" aria-label="Webseite durchsuchen" data-index="__SUCHINDEX__">{SEARCH_ICON}</button>
  </div>
  <div class="hsearch" id="suche" hidden>
    <div class="wrap">
      <form class="hsearch-form" role="search" action="#" autocomplete="off">
        {SEARCH_ICON}
        <label class="sr-only" for="q">Webseite durchsuchen</label>
        <input id="q" type="search" placeholder="Suchen, z. B. Stele, Wittenburg, Genehmigung" role="combobox" aria-expanded="false" aria-controls="q-treffer" aria-autocomplete="list" enterkeyhint="search">
        <button class="hsearch-close" type="button" aria-label="Suche schließen">×</button>
      </form>
      <div class="hsearch-drop" hidden>
        <ul id="q-treffer" class="hsearch-results" role="listbox" aria-label="Suchergebnisse"></ul>
        <p class="hsearch-empty" hidden>Nichts gefunden. <a href="kontakt.html">Fragen Sie uns direkt</a> – wir helfen gern weiter.</p>
      </div>
    </div>
  </div>
</header>
<main id="inhalt">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <a class="brand" href="index.html"><strong>{NAME}</strong><span>{OWNER} · Steinmetz</span></a>
      <p class="footer-contact">{STREET}, {ZIP_CITY}<span>·</span><a href="tel:{PHONE_HREF}">{PHONE_SHOW}</a><span>·</span><a href="mailto:{MAIL}">{MAIL}</a></p>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> {NAME} · <a href="impressum.html">Impressum</a> · <a href="datenschutz.html">Datenschutz</a></span>
      <a class="credit" href="https://lionify.de" target="_blank" rel="noopener" title="Professionelle Websites für Handwerk und Mittelstand">Gestaltet &amp; umgesetzt von lionify.de</a>
    </div>
  </div>
</footer>
<script src="{v('main.js')}" defer></script>
</body>
</html>
"""
    html = to_picture(html)
    if prefix:
        # relative Pfade für Unterordner anpassen (nicht im eingebetteten CSS)
        head, sep, rest = html.partition("</style>")
        rest = re.sub(r'((?:href|src|srcset)=")(?!https?:|mailto:|tel:|#|/|data:)', r"\1" + prefix, rest)
        head = re.sub(r'((?:href|src)=")(?!https?:|mailto:|tel:|#|/|data:)', r"\1" + prefix, head.split("<style>")[0]) + "<style>" + head.split("<style>", 1)[1]
        html = head + sep + rest
    out = ROOT / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    SITEMAP_META[filename] = {"noindex": noindex}
    return filename


def cta(title="Lassen Sie sich persönlich beraten", text="Vereinbaren Sie einen Termin in unserer Ausstellung – auch abends und samstags."):
    return f"""<section class="cta">
  <div class="wrap">
    <div><h2>{title}</h2><p>{text}</p></div>
    <div class="btn-row" style="margin:0"><a class="btn" href="kontakt.html">Termin anfragen</a><a class="btn btn-ghost" href="tel:{PHONE_HREF}">{PHONE_SHOW}</a></div>
  </div>
</section>"""


def gallery(slug, label):
    items = []
    for i, img in enumerate(images(slug), 1):
        items.append(
            f'<a href="{img}.jpg" data-lb><img src="{img}-k.jpg" alt="{label} – Beispiel {i}" loading="lazy" decoding="async" width="480" height="480"></a>'
        )
    return '<div class="gallery">\n' + "\n".join(items) + "\n</div>"


def cards():
    out = []
    for c in CATEGORIES:
        out.append(f"""<a class="card" href="{c["slug"]}.html">
  <img src="img/{c["slug"]}/{c["card"]}-k.jpg" alt="{c["title"]}" loading="lazy" width="480" height="600">
  <div class="card-body"><h3>{c["title"]}</h3><p>{c["short"]}</p><span class="more">Ansehen →</span></div>
</a>""")
    return '<div class="cards">\n' + "\n".join(out) + "\n</div>"


def shop_section():
    return f"""<section class="section shop">
  <div class="wrap shop-grid">
    <div class="shop-media">
      <img src="img/liegesteine/liegesteine-10-k.jpg" alt="Grabherz aus Multicolor-Granit" loading="lazy" width="480" height="480">
      <img src="img/liegesteine/liegesteine-03-k.jpg" alt="Liegestein mit Weidenmotiv" loading="lazy" width="480" height="480">
    </div>
    <div>
      <p class="eyebrow">Online-Shop</p>
      <h2>Liegesteine &amp; Grabherzen – auch online bestellen</h2>
      <p>Viele unserer Liege- und Rasensteine, Grabherzen und Urnengrab-Einfassungen können Sie auch bequem über unseren eBay-Shop bestellen – mit Ihrer persönlichen Inschrift und Ihrem Wunschsymbol, gefertigt in unserer Werkstatt in Lehsen.</p>
      <ul class="shop-facts">
        <li><strong>{EBAY_SOLD}</strong><span>verkaufte Artikel</span></li>
        <li><strong>100 %</strong><span>positive Bewertungen</span></li>
      </ul>
      <div class="btn-row"><a class="btn" href="{EBAY_URL}" target="_blank" rel="noopener">Zum eBay-Shop ↗</a><a class="btn btn-ghost" href="kontakt.html">Lieber persönlich beraten lassen</a></div>
      <p class="muted" style="font-size:.82rem;margin-top:12px">Der Link führt zu eBay. Dort gelten die Datenschutzbestimmungen von eBay.</p>
    </div>
  </div>
</section>"""


def shop_hint(text):
    return f"""<div class="shop-hint">
      <p><strong>Auch online erhältlich:</strong> {text}</p>
      <a href="{EBAY_URL}" target="_blank" rel="noopener">Zum eBay-Shop ↗</a>
    </div>"""


STEPS = """<ol class="steps">
  <li><h3>Beratung</h3><p>In Ruhe und ohne Zeitdruck – in unserer Ausstellung in Lehsen, gern auch abends oder samstags.</p></li>
  <li><h3>Entwurf</h3><p>Wir stimmen Stein, Form, Schrift und Ornamente mit Ihnen ab und beachten die Friedhofssatzung.</p></li>
  <li><h3>Fertigung</h3><p>Ihr Grabmal wird sorgfältig gefertigt und beschriftet – vertieft, erhaben oder mit aufgesetzter Schrift.</p></li>
  <li><h3>Aufstellung</h3><p>Wir kümmern uns um die Genehmigung und stellen das Grabmal fachgerecht auf dem Friedhof auf.</p></li>
</ol>"""


def build_index():
    body = f"""<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">Steinmetz in Lehsen bei Wittenburg</p>
      <h1>Grabmale, die <em>bleiben</em>.</h1>
      <p class="lead">Ein Grabmal ist ein Zeichen der Erinnerung – persönlich, würdevoll und für Generationen gemacht. Wir begleiten Sie mit Erfahrung, Ruhe und einer vielseitigen Ausstellung.</p>
      <div class="btn-row"><a class="btn" href="kontakt.html">Beratungstermin vereinbaren</a><a class="btn btn-ghost" href="grabmale.html">Grabmale ansehen</a></div>
    </div>
    <div class="hero-media">
      <picture><source type="image/webp" srcset="img/hero/ausstellung-640.webp 640w, img/hero/ausstellung-960.webp 960w" sizes="(max-width: 860px) calc(100vw - 50px), 600px"><img src="img/hero/ausstellung-960.jpg" srcset="img/hero/ausstellung-640.jpg 640w, img/hero/ausstellung-960.jpg 960w" sizes="(max-width: 860px) calc(100vw - 50px), 600px" alt="Ausstellung mit Grabsteinen aus verschiedenen Graniten in Lehsen" width="960" height="367" fetchpriority="high" decoding="async"></picture>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap split">
    <div>
      <p class="eyebrow">Willkommen</p>
      <h2>Mein kleines, aber feines Unternehmen</h2>
      <p>In Lehsen finden Sie mein kleines, aber feines Unternehmen. Bei mir stehen Sie und Ihre Wünsche im Mittelpunkt – von der ersten Idee bis zum fertig aufgestellten Grabmal.</p>
      <p>Ich freue mich auf ein Beratungsgespräch mit Ihnen. Damit ich mir ausreichend Zeit nehmen kann, sind Terminabsprachen wünschenswert.</p>
      <p class="signature">Ihr Bernhard Gerdes</p>
    </div>
    <ul class="values">
      <li><strong>Fachliche Kompetenz</strong><span>Erfahrung in Gestaltung, Schrift und Fertigung.</span></li>
      <li><strong>Vielseitige Ausstellung</strong><span>Zahlreiche Grabmale und Materialien vor Ort ansehen.</span></li>
      <li><strong>Seriöse Beratung</strong><span>Freundlich, ehrlich und ohne Zeitdruck.</span></li>
      <li><strong>Faire Preise</strong><span>Transparente Angebote ohne versteckte Kosten.</span></li>
      <li><strong>Flexible Termine</strong><span>Auch abends und samstags.</span></li>
    </ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Unser Angebot</p>
      <h2>Grabmale für jede Grabstätte</h2>
      <p class="lead">Vom klassischen Breitstein bis zur kompletten Grabanlage – entdecken Sie Beispiele aus unserer Arbeit.</p>
    </div>
    {cards()}
  </div>
</section>

{shop_section()}

<section class="section section-alt" id="ablauf">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Ablauf</p>
      <h2>So entsteht Ihr Grabmal</h2>
      <p class="lead">Wir begleiten Sie Schritt für Schritt und nehmen Ihnen dabei so viel wie möglich ab.</p>
    </div>
    {STEPS}
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="callout">
      <h3>Gut zu wissen: die Friedhofssatzung</h3>
      <p>Jeder Friedhof hat eigene Vorgaben der Kommune oder Kirche – etwa zu Größe, Material und Bearbeitung des Grabsteines. Wir kennen die Satzungen der Friedhöfe in der Region und berücksichtigen sie von Anfang an.</p>
    </div>
    <div>
      <h3>Nachbeschriftung &amp; Zubehör</h3>
      <p>Auch für bestehende Grabmale sind wir für Sie da: Nachbeschriftungen, Ornamente, Grablichter, Grabvasen und weiteres Zubehör.</p>
      <p><a href="kontakt.html">Sprechen Sie uns an →</a></p>
    </div>
  </div>
</section>

{cta()}"""
    return page("index.html", NAME,
                "Steinmetz Bernhard Gerdes in Lehsen bei Wittenburg: Grabsteine, Stelen, Liegesteine und Grabanlagen aus Naturstein. Beratung auch abends und samstags.",
                body, "index.html", schema=[LOCAL_BUSINESS])


def build_overview():
    body = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Grabmale</p>
    <h1>Unsere Grabmale</h1>
    <p class="lead">Jeder Stein erzählt von einem Menschen. Ob klassisch oder modern, schlicht oder kunstvoll – hier finden Sie Beispiele aus unserer Arbeit, sortiert nach Art des Grabmals.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">{cards()}</div>
</section>
<section class="section section-alt">
  <div class="wrap split">
    <div>
      <h2>Gestaltung nach Ihren Wünschen</h2>
      <p>Granit in vielen Farben und Strukturen, poliert, geschliffen oder naturbelassen: Wir zeigen Ihnen die Möglichkeiten und entwickeln gemeinsam ein Grabmal, das zur Persönlichkeit der Verstorbenen passt.</p>
      <p>Inschriften und Ornamente werden vertieft oder erhaben eingearbeitet oder aus Bronze, Aluminium oder Edelstahl aufgesetzt.</p>
    </div>
    <div class="callout">
      <h3>Friedhofssatzung</h3>
      <p>Größe und Bearbeitung des Grabsteines sind oft von der Kommune oder Kirche vorgegeben. Wir beraten Sie dazu und kümmern uns um die Genehmigung.</p>
    </div>
  </div>
</section>
{cta()}"""
    return page("grabmale.html", "Grabmale",
                "Breitsteine, Reihensteine, Stelen, Liegesteine und Grabanlagen aus Naturstein – Beispiele aus unserer Werkstatt und persönliche Beratung in Lehsen.",
                body, "grabmale.html", crumbs=[("Start", ""), ("Grabmale", "grabmale.html")])


def subnav(active):
    return '<nav class="subnav" aria-label="Grabmal-Arten">' + "".join(
        f'<a href="{c["slug"]}.html"{" aria-current=page" if c["slug"] == active else ""}>{c["title"]}</a>' for c in CATEGORIES
    ) + "</nav>"


def build_category(c):
    paras = "".join(f"<p>{p}</p>" for p in c["text"])
    n = len(images(c["slug"]))
    body = f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Start</a> / <a href="grabmale.html">Grabmale</a> / {c["title"]}</div>
    <h1>{c["title"]}</h1>
    <p class="lead">{c["intro"]}</p>
    {subnav(c["slug"])}
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div class="prose">{paras}{shop_hint(c["shop"]) if c.get("shop") else ""}</div>
    <div class="callout">
      <h3>Persönliche Beratung</h3>
      <p>In unserer Ausstellung in Lehsen zeigen wir Ihnen Materialien, Formen und Schriften – und erstellen Ihnen gern ein unverbindliches Angebot.</p>
      <p><a class="btn" href="kontakt.html">Termin anfragen</a></p>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <div class="section-head"><h2>Beispiele</h2><p class="muted">{n} Arbeiten – zum Vergrößern auf ein Bild tippen.</p></div>
    {gallery(c["slug"], c["title"])}
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="satz-more">
      <section><h2 class="h3">Gut vorbereitet</h2><div class="more-links">
        <a href="friedhofssatzungen.html"><strong>Friedhofssatzungen der Region</strong><span>Was auf Ihrem Friedhof für Grabmale gilt</span></a>
        <a href="steinsorten.html"><strong>Steinsorten</strong><span>Farben, Herkunft und Wirkung von Naturstein</span></a>
        <a href="ratgeber.html"><strong>Häufige Fragen</strong><span>Genehmigung, Fristen, Preis und Pflege</span></a>
      </div></section>
      <section><h2 class="h3">Weitere Grabmale</h2><div class="more-links">
        {"".join(f'<a href="{o["slug"]}.html"><strong>{o["title"]}</strong><span>{o["short"]}</span></a>' for o in CATEGORIES if o["slug"] != c["slug"])}
      </div></section>
    </div>
  </div>
</section>
{cta()}"""
    return page(f'{c["slug"]}.html', c["title"],
                f'{c["title"]} aus Naturstein vom Steinmetz in Lehsen: {c["short"]} Beispiele aus unserer Werkstatt und Beratung.',
                body, "grabmale.html", crumbs=[("Start", ""), ("Grabmale", "grabmale.html"), (c["title"], f'{c["slug"]}.html')])


def build_references():
    body = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Referenzen</p>
    <h1>Aufgestellte Grabmale</h1>
    <p class="lead">Eine Auswahl von Grabmalen, die wir auf Friedhöfen in der Region gefertigt und aufgestellt haben.</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    {gallery("referenzen", "Referenz")}
    <p class="gallery-note">Weitere Beispiele finden Sie bei den einzelnen <a href="grabmale.html">Grabmal-Arten</a>.</p>
  </div>
</section>
{cta()}"""
    return page("referenzen.html", "Referenzen",
                "Referenzen von Grabmale aus Lehsen: von uns gefertigte und aufgestellte Grabmale auf Friedhöfen in Westmecklenburg – Breitsteine, Stelen und mehr.",
                body, "referenzen.html", crumbs=[("Start", ""), ("Referenzen", "referenzen.html")])


def build_contact():
    options = "".join(f"<option>{c['title']}</option>" for c in CATEGORIES)
    body = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Kontakt</p>
    <h1>Wir sind für Sie da</h1>
    <p class="lead">Rufen Sie an, schreiben Sie uns oder nutzen Sie das Formular. Wir melden uns zeitnah bei Ihnen.</p>
  </div>
</section>
<section class="section">
  <div class="wrap contact-grid">
    <div>
      <ul class="info-list">
        <li><small>Adresse</small>{NAME}<br>{OWNER}<br>{STREET}<br>{ZIP_CITY}</li>
        <li><small>Telefon</small><a href="tel:{PHONE_HREF}">{PHONE_SHOW}</a></li>
        <li><small>E-Mail</small><a href="mailto:{MAIL}">{MAIL}</a></li>
        <li><small>Öffnungszeiten</small>{HOURS}.<br><span class="muted">Terminabsprachen sind wünschenswert.</span></li>
        <li><small>Anfahrt</small>Lehsen liegt direkt bei Wittenburg, nur wenige Minuten von der A24 entfernt. <a href="anfahrt.html">Wegbeschreibung &amp; Karte →</a></li>
        <li><small>Online-Shop</small><a href="{EBAY_URL}" target="_blank" rel="noopener">Liegesteine &amp; Grabherzen bei eBay ↗</a></li>
      </ul>
      <a class="btn btn-ghost" href="anfahrt.html">So finden Sie zu uns</a>
    </div>
    <form class="form" action="kontakt.php" method="post" novalidate>
      <div class="msg msg-ok" id="msg-ok" hidden>Vielen Dank für Ihre Nachricht! Wir melden uns so bald wie möglich bei Ihnen.</div>
      <div class="msg msg-err" id="msg-err" hidden>Ihre Nachricht konnte leider nicht gesendet werden. Bitte prüfen Sie Ihre Angaben oder rufen Sie uns an: <a href="tel:{PHONE_HREF}">{PHONE_SHOW}</a>.</div>
      <h2 style="font-size:1.6rem">Nachricht senden</h2>
      <div class="row">
        <div class="field"><label for="name">Name <span class="req">*</span></label><input id="name" name="name" autocomplete="name" required maxlength="120"></div>
        <div class="field"><label for="phone">Telefon</label><input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="60"></div>
      </div>
      <div class="field"><label for="email">E-Mail <span class="req">*</span></label><input id="email" name="email" type="email" autocomplete="email" required maxlength="160"></div>
      <div class="field"><label for="topic">Worum geht es?</label>
        <select id="topic" name="topic"><option>Beratungstermin</option>{options}<option>Nachbeschriftung</option><option>Sonstiges</option></select></div>
      <div class="field"><label for="message">Ihre Nachricht <span class="req">*</span></label><textarea id="message" name="message" required maxlength="5000"></textarea></div>
      <div class="hp" aria-hidden="true"><label for="website">Bitte leer lassen</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div>
      <input type="hidden" name="ts" id="ts" value="">
      <label class="check"><input type="checkbox" name="consent" value="1" required><span>Ich bin einverstanden, dass meine Angaben zur Bearbeitung meiner Anfrage verwendet werden. Details in der <a href="datenschutz.html">Datenschutzerklärung</a>. <span class="req">*</span></span></label>
      <button class="btn" type="submit">Nachricht senden</button>
      <p class="muted" style="font-size:.82rem;margin:14px 0 0"><span class="req">*</span> Pflichtfeld</p>
    </form>
  </div>
</section>"""
    return page("kontakt.html", "Kontakt & Anfahrt",
                f"Kontakt zu Grabmale aus Lehsen: {STREET}, {ZIP_CITY}. Telefon {PHONE_SHOW}. Beratungstermine auch abends und samstags.",
                body, "kontakt.html", crumbs=[("Start", ""), ("Kontakt", "kontakt.html")])


def legal_head(eyebrow, h1, lead, crumb_name, crumb_url):
    return f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Start</a> / {crumb_name}</div>
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>"""


ROUTES = [
    ("Über die A24 – Abfahrt Wittenburg", "aus Richtung Berlin und Schwerin, auch aus Richtung Hamburg möglich",
     ["Nehmen Sie die Abfahrt <strong>Wittenburg</strong> und fahren Sie im Kreisverkehr auf die L 05 in Richtung Wittenburg.",
      "Folgen Sie dem <strong>Südring</strong> um die Stadt herum.",
      "Am nächsten Kreisverkehr biegen Sie auf die <strong>Lehsener Chaussee</strong> (L 05) ab.",
      "Nach rund 3,5 km erreichen Sie Lehsen – die Ausstellung liegt an der Straße <strong>Unter den Linden</strong>."]),
    ("Aus Richtung Hamburg – Abfahrt Zarrentin", "die kürzere Strecke von Westen",
     ["Verlassen Sie die A24 an der Abfahrt <strong>Zarrentin</strong> (B 195) und fahren Sie Richtung Zarrentin.",
      "Durch Zarrentin und dort rechts auf die <strong>L 04</strong> (Wittenburger Chaussee) in Richtung Wittenburg.",
      "Nach etwa 6 km rechts auf die Kreisstraße <strong>K 11</strong> nach Lehsen abbiegen.",
      "Nach rund 4 km am Ende der Straße links in <strong>Unter den Linden</strong>."]),
]
DRIVES = [("Wittenburg", "4 km", "5 Min."), ("Zarrentin", "12 km", "15 Min."), ("Hagenow", "19 km", "20 Min."),
          ("Boizenburg", "28 km", "30 Min."), ("Schwerin", "39 km", "40 Min."), ("Hamburg", "79 km", "1 Std.")]


def build_directions():
    routes = "".join(f"""<article class="route"><h3>{t}</h3><p class="muted">{sub}</p><ol>{"".join(f"<li>{x}</li>" for x in steps)}</ol></article>""" for t, sub, steps in ROUTES)
    drives = "".join(f"<li><strong>{n}</strong><span>{d} · ca. {t}</span></li>" for n, d, t in DRIVES)
    body = f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Start</a> / Anfahrt</div>
    <p class="eyebrow">Anfahrt</p>
    <h1>So finden Sie zu uns</h1>
    <p class="lead">Unsere Ausstellung liegt in Lehsen, rund 4 km südwestlich der Wittenburger Innenstadt und nur wenige Minuten von der A24 entfernt.</p>
  </div>
</section>
<section class="section">
  <div class="wrap anfahrt-grid">
    <div>
      <div class="address-card">
        <h2 class="box-title">Adresse</h2>
        <p class="address-big">{NAME}<br>{STREET}<br>{ZIP_CITY}</p>
        <p class="muted" style="font-size:.9rem">Tipp fürs Navi: „Lehsen, Unter den Linden 14“ eingeben.</p>
        <div class="btn-row" style="margin-top:16px"><a class="btn" href="{MAP_URL}" target="_blank" rel="noopener">Route planen</a><a class="btn btn-ghost" href="tel:{PHONE_HREF}">{PHONE_SHOW}</a></div>
        <p class="muted" style="font-size:.8rem;margin-top:10px">„Route planen“ öffnet OpenStreetMap in einem neuen Fenster.</p>
      </div>
      <div class="address-card" style="margin-top:16px">
        <h2 class="box-title">Besuch der Ausstellung</h2>
        <p>{HOURS}. Damit wir uns ausreichend Zeit für Sie nehmen können, vereinbaren Sie bitte vorab einen Termin.</p>
        <p style="margin-top:12px"><a href="kontakt.html">Termin anfragen →</a></p>
      </div>
    </div>
    <div class="map-wrap">
      <div id="map" class="map" aria-label="Karte: Lage der Ausstellung in Lehsen"></div>
      <div class="map-consent" id="map-consent">
        <div>
          <h3>Karte anzeigen</h3>
          <p>Die Karte wird von OpenStreetMap geladen. Dabei wird Ihre IP-Adresse an die OpenStreetMap Foundation übertragen. Mehr dazu in der <a href="datenschutz.html#karte">Datenschutzerklärung</a>.</p>
          <button class="btn" type="button" id="map-load">Karte laden</button>
          <label class="check" style="justify-content:center;margin:14px 0 0"><input type="checkbox" id="map-remember"><span>Karte künftig immer laden</span></label>
        </div>
      </div>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <div class="section-head"><h2>Wegbeschreibung</h2></div>
    <div class="routes">{routes}</div>
    <h2 class="h3" style="margin-top:48px">Entfernungen</h2>
    <ul class="drives">{drives}</ul>
    <p class="muted" style="font-size:.85rem;margin-top:12px">Ungefähre Fahrstrecken und -zeiten mit dem Auto, berechnet mit OpenStreetMap.</p>
  </div>
</section>
{cta("Wir freuen uns auf Ihren Besuch", "Vereinbaren Sie einen Termin – auch abends und samstags.")}
<script type="application/json" id="anfahrt-data">{json.dumps({"lehsen": ORTE["Lehsen"]})}</script>
<script src="{v("anfahrt.js")}" defer></script>"""
    return page("anfahrt.html", "Anfahrt", f"Anfahrt zu {NAME}: {STREET}, {ZIP_CITY} – wenige Minuten von der A24, Abfahrt Wittenburg. Wegbeschreibung, Karte und Entfernungen.",
                body, "anfahrt.html", crumbs=[("Start", ""), ("Anfahrt", "anfahrt.html")])


def build_imprint():
    body = legal_head("Rechtliches", "Impressum", "Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG).", "Impressum", "impressum.html") + f"""
<section class="section">
  <div class="wrap">
    <div class="legal-cards">
      <div class="legal-card">
        <h2 class="box-title">Anbieter</h2>
        <p><strong>{OWNER}</strong><br>{NAME} – Schrift im Stein<br>{STREET}<br>{ZIP_CITY}</p>
      </div>
      <div class="legal-card">
        <h2 class="box-title">Kontakt</h2>
        <p>Telefon: <a href="tel:{PHONE_HREF}">{PHONE_SHOW}</a><br>Telefax: {PHONE_SHOW}<br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></p>
      </div>
      <div class="legal-card">
        <h2 class="box-title">Steuern</h2>
        <p>Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br><strong>DE246444446</strong></p>
      </div>
    </div>
    <div class="legal-text">
      <h2>Verbraucherstreitbeilegung</h2>
      <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
      <h2>Haftung für Inhalte</h2>
      <p>Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben unberührt; eine Haftung ist erst ab Kenntnis einer konkreten Rechtsverletzung möglich. Entsprechende Inhalte entfernen wir dann umgehend.</p>
      <p>Die Zusammenfassungen von Friedhofssatzungen auf dieser Website wurden mit größter Sorgfalt erstellt; verbindlich ist jedoch allein die jeweils aktuelle Satzung des Friedhofsträgers.</p>
      <h2>Haftung für Links</h2>
      <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Für diese fremden Inhalte ist stets der jeweilige Anbieter verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft; rechtswidrige Inhalte waren nicht erkennbar. Bei Bekanntwerden von Rechtsverletzungen entfernen wir derartige Links umgehend.</p>
      <h2>Urheberrecht und Bildnachweis</h2>
      <p>Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten – insbesondere Texte und Fotos – unterliegen dem deutschen Urheberrecht. Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechts bedürfen der schriftlichen Zustimmung. Alle Fotos zeigen Arbeiten von {NAME} und stammen aus eigenem Bestand.</p>
      <h2>Gestaltung und Umsetzung</h2>
      <p><a href="https://lionify.de" target="_blank" rel="noopener">lionify.de</a></p>
    </div>
  </div>
</section>"""
    return page("impressum.html", "Impressum", f"Impressum von {NAME}: Steinmetz {OWNER}, {STREET}, {ZIP_CITY}. Kontakt und Angaben nach § 5 DDG.", body)


PRIVACY_SECTIONS = [
    ("verantwortlicher", "Verantwortlicher", f"""<p>Verantwortlich für die Datenverarbeitung auf dieser Website ist:</p>
<div class="legal-card legal-inline"><p><strong>{OWNER}</strong><br>{NAME} – Schrift im Stein<br>{STREET}, {ZIP_CITY}<br>Telefon: <a href="tel:{PHONE_HREF}">{PHONE_SHOW}</a> · E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></p></div>"""),
    ("hosting", "Hosting und Server-Logdateien", """<p>Diese Website wird bei der ALL-INKL.COM – Neue Medien Münnich, Inh. René Münnich, Hauptstraße 68, 02742 Friedersdorf, gehostet. Beim Aufruf der Website erhebt der Server automatisch Informationen, die Ihr Browser übermittelt (Server-Logdateien): IP-Adresse, Datum und Uhrzeit des Zugriffs, aufgerufene Seite, übertragene Datenmenge, Referrer-URL, Browsertyp und Betriebssystem.</p>
<p>Diese Daten werden ausschließlich benötigt, um die Website sicher und stabil bereitzustellen, und nicht mit anderen Daten zusammengeführt. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO; unser berechtigtes Interesse liegt im sicheren Betrieb der Website. Mit dem Hoster besteht ein Vertrag zur Auftragsverarbeitung gemäß Art. 28 DSGVO. Die Logdateien werden nur für einen begrenzten Zeitraum gespeichert und anschließend gelöscht bzw. anonymisiert.</p>"""),
    ("ssl", "SSL-/TLS-Verschlüsselung", """<p>Diese Seite nutzt aus Sicherheitsgründen eine SSL-/TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie an „https://“ in der Adresszeile Ihres Browsers. Zusätzlich weisen wir Browser an, die Seite ausschließlich verschlüsselt aufzurufen (HSTS).</p>"""),
    ("kontakt", "Kontaktformular, E-Mail und Telefon", """<p>Wenn Sie uns über das Kontaktformular, per E-Mail oder telefonisch kontaktieren, verarbeiten wir Ihre Angaben (Name, E-Mail-Adresse, ggf. Telefonnummer, Ihr Anliegen und Ihre Nachricht) ausschließlich zur Bearbeitung Ihrer Anfrage und für mögliche Anschlussfragen.</p>
<p>Die Nachricht aus dem Kontaktformular wird per E-Mail an unser Postfach übermittelt, das bei einem externen E-Mail-Anbieter geführt wird; sie wird nicht in einer Datenbank auf dem Webserver gespeichert. Zum Schutz vor automatisiertem Spam nutzt das Formular ein unsichtbares Feld und eine Zeitprüfung; dabei werden keine zusätzlichen personenbezogenen Daten erhoben.</p>
<p>Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, sofern Ihre Anfrage mit der Anbahnung oder Erfüllung eines Vertrages zusammenhängt, und im Übrigen Art. 6 Abs. 1 lit. a DSGVO (Einwilligung) bzw. lit. f DSGVO (berechtigtes Interesse an der Beantwortung von Anfragen). Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft widerrufen.</p>
<p>Ihre Daten werden gelöscht, sobald Ihre Anfrage abschließend bearbeitet ist und keine gesetzlichen Aufbewahrungspflichten (z. B. bei Angeboten und Aufträgen) entgegenstehen. Eine Weitergabe an Dritte findet nicht statt. Die Angabe Ihrer Daten ist freiwillig; ohne sie können wir Ihre Anfrage jedoch nicht beantworten.</p>"""),
    ("karte", "Karte (OpenStreetMap)", """<p>Auf der Seite „Friedhofssatzungen“ bieten wir eine interaktive Karte an. Die Kartendarstellung (Kartenkacheln) wird von der OpenStreetMap Foundation (OSMF), St John’s Innovation Centre, Cowley Road, Cambridge, CB4 0WS, Großbritannien, geladen. Die Programmbibliothek für die Karte (Leaflet) liegt auf unserem eigenen Server.</p>
<p>Die Karte wird <strong>erst geladen, wenn Sie auf „Karte laden“ klicken</strong>. Erst dann stellt Ihr Browser eine Verbindung zu den Servern von OpenStreetMap her; dabei werden insbesondere Ihre IP-Adresse, der angefragte Kartenausschnitt sowie technische Angaben Ihres Browsers übertragen. Rechtsgrundlage ist Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO und § 25 Abs. 1 TDDDG. Für das Vereinigte Königreich besteht ein Angemessenheitsbeschluss der EU-Kommission.</p>
<p>Wenn Sie „Karte künftig immer laden“ auswählen, wird diese Entscheidung ausschließlich lokal in Ihrem Browser gespeichert (Local Storage) und nicht an uns übertragen. Sie können die Einwilligung jederzeit widerrufen, indem Sie die gespeicherten Websitedaten in Ihrem Browser löschen. Weitere Informationen: <a href="https://osmfoundation.org/wiki/Privacy_Policy" target="_blank" rel="noopener">Datenschutzerklärung der OpenStreetMap Foundation</a>.</p>"""),
    ("links", "Externe Links", """<p>Unsere Website enthält Links zu externen Angeboten, unter anderem zu unserem Shop bei eBay sowie zu Satzungen und Informationen von Städten, Ämtern, Kirchengemeinden und Verbänden. Diese Inhalte werden nicht in unsere Website eingebunden; beim bloßen Aufruf unserer Seiten werden keine Daten an diese Anbieter übertragen. Erst wenn Sie einen Link anklicken, wird die jeweilige Seite geöffnet und es gelten die Datenschutzbestimmungen des jeweiligen Anbieters.</p>"""),
    ("rechte", "Ihre Rechte", """<p>Sie haben im Rahmen der gesetzlichen Bestimmungen jederzeit das Recht auf:</p>
<ul><li>Auskunft über Ihre gespeicherten personenbezogenen Daten (Art. 15 DSGVO),</li><li>Berichtigung unrichtiger Daten (Art. 16 DSGVO),</li><li>Löschung (Art. 17 DSGVO) und Einschränkung der Verarbeitung (Art. 18 DSGVO),</li><li>Datenübertragbarkeit (Art. 20 DSGVO),</li><li>Widerspruch gegen die Verarbeitung auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO (Art. 21 DSGVO),</li><li>Widerruf einer erteilten Einwilligung mit Wirkung für die Zukunft (Art. 7 Abs. 3 DSGVO).</li></ul>
<p>Wenden Sie sich dazu einfach an die oben genannten Kontaktdaten. Eine automatisierte Entscheidungsfindung einschließlich Profiling findet nicht statt.</p>"""),
    ("beschwerde", "Beschwerderecht bei der Aufsichtsbehörde", """<p>Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren. Zuständig für uns ist:</p>
<div class="legal-card legal-inline"><p><strong>Der Landesbeauftragte für Datenschutz und Informationsfreiheit Mecklenburg-Vorpommern</strong><br>Werderstraße 74a, 19055 Schwerin</p></div>"""),
    ("aenderungen", "Änderungen dieser Erklärung", """<p>Wir passen diese Datenschutzerklärung an, wenn sich die Website oder die rechtlichen Anforderungen ändern. Es gilt die jeweils hier veröffentlichte Fassung.</p>"""),
]


def build_privacy():
    glance = [("Keine Cookies", "Wir setzen keine Cookies und keine Analyse- oder Tracking-Werkzeuge ein."),
              ("Keine fremden Dienste", "Schriften und Skripte liegen auf unserem eigenen Server."),
              ("Karte nur nach Klick", "OpenStreetMap wird erst geladen, wenn Sie zustimmen."),
              ("Nur für Ihre Anfrage", "Kontaktdaten nutzen wir ausschließlich zur Beantwortung.")]
    cards = "".join(f'<div class="legal-card glance"><h2 class="box-title">{t}</h2><p>{d}</p></div>' for t, d in glance)
    toc = "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t, _ in PRIVACY_SECTIONS)
    secs = "".join(f'<section class="legal-sec" id="{a}"><h2><span>{i:02d}</span>{t}</h2>{c}</section>' for i, (a, t, c) in enumerate(PRIVACY_SECTIONS, 1))
    body = legal_head("Rechtliches", "Datenschutzerklärung", "Stand: November 2026", "Datenschutz", "datenschutz.html") + f"""
<section class="section">
  <div class="wrap">
    <h2 class="glance-title">Auf einen Blick</h2>
    <div class="legal-cards glance-cards">{cards}</div>
    <div class="legal-layout">
      <nav class="legal-toc" aria-label="Inhalt"><h2 class="box-title">Inhalt</h2><ol>{toc}</ol></nav>
      <div class="legal-text">{secs}</div>
    </div>
  </div>
</section>"""
    return page("datenschutz.html", "Datenschutzerklärung", f"Datenschutzerklärung von {NAME}: keine Cookies, kein Tracking. Informationen zu Kontaktformular, Hosting, Karte und Ihren Rechten.", body, noindex=True)


STONES = [
    {"name": "Orion", "art": "Granit", "herkunft": "Indien", "img": "liegesteine/liegesteine-17",
     "farbe": "Blaugrau mit dunklen Einsprengseln",
     "text": "Ein ruhiger, gleichmäßig gemusterter Granit mit kühlem Blauton. Poliert wirkt er elegant und tief, gestockt oder geflammt hell und natürlich – ideal für klare, gut lesbare Inschriften."},
    {"name": "Himalaya", "art": "Granit", "herkunft": "Indien", "img": "reihensteine/reihensteine-08",
     "farbe": "Grau- und Brauntöne mit fließender Maserung",
     "text": "Die bewegte, wellenartige Struktur macht jeden Stein zum Unikat. Himalaya passt besonders gut zu modernen Formen und naturnahen Motiven wie Bäumen oder Blättern."},
    {"name": "Multicolor Red", "art": "Granit", "herkunft": "Indien", "img": "liegesteine/liegesteine-05",
     "farbe": "Rot, Grau und Schwarz, kräftig geflammt",
     "text": "Ein lebendiger, warmer Stein mit ausdrucksstarker Zeichnung. Sehr beliebt für Liegesteine und Grabherzen, weil er auch auf kleiner Fläche viel Wirkung entfaltet."},
    {"name": "Halmstad", "art": "Granit", "herkunft": "Schweden", "img": "liegesteine/liegesteine-09",
     "farbe": "Rotbraun mit dunkler Struktur",
     "text": "Ein nordischer Granit von großer Härte und Beständigkeit. Poliert zeigt er eine warme, tiefe Farbe, die über Jahrzehnte schön bleibt."},
    {"name": "Viscont White", "art": "Granit", "herkunft": "Indien", "img": "grabanlagen/grabanlagen-21",
     "farbe": "Hellgrau bis Weiß mit grauen Adern",
     "text": "Ein heller, freundlicher Granit mit feiner Aderung. Er eignet sich besonders für Einfassungen und Abdeckungen und lässt Grabanlagen offen und licht wirken."},
    {"name": "Rainbow", "art": "Sandstein", "herkunft": "Indien", "img": "liegesteine/liegesteine-28",
     "farbe": "Gelb, Ocker und Rotbraun in Wellenlinien",
     "text": "Kein Granit, sondern ein Sandstein mit auffälliger, regenbogenartiger Zeichnung. Weicher als Granit und deshalb mit naturbelassener Oberfläche besonders schön."},
]


def build_stones():
    items = []
    for st in STONES:
        items.append(f"""<article class="stone" id="stein-{slug(st["name"])}">
  <a href="img/{st["img"]}.jpg" data-lb><img src="img/{st["img"]}-k.jpg" alt="{st["name"]} – {st["art"]} aus {st["herkunft"]}" loading="lazy" width="480" height="480"></a>
  <div class="stone-body">
    <h3>{st["name"]}</h3>
    <dl><dt>Art</dt><dd>{st["art"]}</dd><dt>Herkunft</dt><dd>{st["herkunft"]}</dd><dt>Farbe</dt><dd>{st["farbe"]}</dd></dl>
    <p>{st["text"]}</p>
  </div>
</article>""")
    body = f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Start</a> / <a href="ratgeber.html">Ratgeber</a> / Steinsorten</div>
    <h1>Steinsorten</h1>
    <p class="lead">Jeder Naturstein hat seine eigene Farbe, Zeichnung und Wirkung. Hier stellen wir eine Auswahl der Sorten vor, die wir häufig verarbeiten – alle Fotos zeigen Arbeiten aus unserer Werkstatt.</p>
    {ratgeber_nav("steinsorten.html")}
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="stones">
{chr(10).join(items)}
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap split">
    <div>
      <h2>Weitere Sorten in der Ausstellung</h2>
      <p>Neben diesen Beispielen verarbeiten wir viele weitere Granite, Sandsteine und Marmore – von schwarzem Granit bis zu hellen nordischen Sorten. Am besten wirken Natursteine im Original: In unserer Ausstellung können Sie Farben und Oberflächen direkt vergleichen.</p>
    </div>
    <div class="callout">
      <h3>Oberfläche macht den Unterschied</h3>
      <p>Derselbe Stein wirkt poliert dunkel und glänzend, geschliffen matt und gestockt oder bruchrau hell und natürlich. Gern zeigen wir Ihnen Muster.</p>
    </div>
  </div>
</section>
{cta()}"""
    return page("steinsorten.html", "Steinsorten",
                "Steinsorten für Grabmale: Orion, Himalaya, Multicolor Red, Halmstad, Viscont White und Rainbow-Sandstein – Farben, Herkunft und Wirkung erklärt.",
                body, "steinsorten.html", crumbs=[("Start", ""), ("Ratgeber", "ratgeber.html"), ("Steinsorten", "steinsorten.html")],
                schema=[{"@context": "https://schema.org", "@type": "ItemList", "name": "Steinsorten für Grabmale", "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": st["name"], "description": f'{st["art"]} aus {st["herkunft"]}: {st["farbe"]}'} for i, st in enumerate(STONES)]}])


SRC_BESTATTG = ("Bestattungsgesetz M-V (Landesrecht M-V)", "https://www.landesrecht-mv.de/bsmv/document/jlr-NNLMV00007941")
SRC_AET_GRABMAL = ("Aeternitas: Die Auswahl eines Grabmals", "https://www.aeternitas.de/fileadmin/user_upload/Downloads/Spalte2/leitfaden_09_grabmalkauf.pdf")
SRC_AET_STAND = ("Aeternitas: Die Standsicherheit des Grabmals", "https://www.aeternitas.de/fileadmin/user_upload/Downloads/Spalte3/rechtsgutachten_grabmalstandsicherheit.pdf")
SRC_AET_KOSTEN = ("Aeternitas: Kostenüberblick Grabmal", "https://www.aeternitas.de/fuer-betroffene/kosten-und-vorsorge/kostenueberblick/steinmetze/grabmal")
SRC_FAIRSTONE = ("Fair Stone e.V.", "https://www.fairstone.org/")

FAQ = [
    ("Wann kann der Grabstein gesetzt werden?", """
<p>Eine landesweit einheitliche Frist gibt es nicht – maßgeblich ist die <a href="friedhofssatzungen.html">Friedhofssatzung</a> des jeweiligen Friedhofs.</p>
<p>Nach einer Erdbestattung muss sich der Boden zunächst setzen, damit das Grabmal später sicher steht. Üblich sind deshalb einige Monate bis etwa ein Jahr Wartezeit. Bei Urnengräbern ist eine Aufstellung meist früher möglich. Manche Satzungen schreiben umgekehrt vor, dass ein Grabmal innerhalb einer bestimmten Frist gesetzt werden muss, und erlauben ein Holzkreuz nur übergangsweise.</p>
<p>Unser Tipp: Die Beratung und der Entwurf können schon vorher stattfinden – dann ist alles vorbereitet, sobald der Stein gesetzt werden darf.</p>""", [SRC_AET_GRABMAL]),
    ("Braucht ein Grabmal eine Genehmigung?", """
<p>Ja. Jedes Grabmal muss vor der Aufstellung vom Friedhofsträger genehmigt werden – ebenso spätere Veränderungen wie eine Nachbeschriftung oder das Entfernen des Steins.</p>
<p>Für den Antrag werden in der Regel benötigt:</p>
<ul><li>eine maßstäbliche Zeichnung mit Vorder- und Seitenansicht</li><li>Angaben zu Material, Farbe und Oberflächenbearbeitung</li><li>Wortlaut der Inschrift sowie Ornamente und Symbole</li><li>Angaben zu Fundament und Befestigung</li><li>der Nachweis, dass der Naturstein ohne Kinderarbeit hergestellt wurde</li></ul>
<p>Den Antrag stellt der bzw. die Nutzungsberechtigte des Grabes – <strong>wir übernehmen das gern für Sie</strong> und stimmen alles mit der Friedhofsverwaltung ab.</p>""", [SRC_AET_GRABMAL]),
    ("Natursteine ohne Kinderarbeit – was gilt in Mecklenburg-Vorpommern?", """
<p>In Mecklenburg-Vorpommern ist das gesetzlich geregelt: Nach <strong>§ 14a des Bestattungsgesetzes M-V</strong> dürfen Grabmale und Einfassungen aus Naturstein nur aufgestellt werden, wenn sie</p>
<ul><li>in Ländern gewonnen und verarbeitet wurden, in denen die Natursteinproduktion nicht gegen das ILO-Übereinkommen 182 gegen die schlimmsten Formen der Kinderarbeit verstößt, <strong>oder</strong></li><li>von einer anerkannten Zertifizierungsstelle als frei von Kinderarbeit bestätigt und dauerhaft gekennzeichnet sind, zum Beispiel mit einem Siegel.</li></ul>
<p>Ausgenommen sind Steine, die schon vor dem 1. Juli 2021 nach Deutschland eingeführt wurden.</p>
<p>Wir achten bei jedem Stein auf die erforderlichen Nachweise und legen sie dem Genehmigungsantrag bei. Fragen Sie uns gern, woher ein Stein stammt und wie er zertifiziert ist.</p>""", [SRC_BESTATTG, SRC_FAIRSTONE]),
    ("Wovon hängt der Preis eines Grabmals ab?", """
<p>Jedes Grabmal ist eine Einzelanfertigung, deshalb erstellen wir Ihnen immer ein individuelles, schriftliches Angebot. Den Preis bestimmen vor allem:</p>
<ul>
<li><strong>Steinsorte und Herkunft</strong> – heimische, nordische oder überseeische Natursteine unterscheiden sich deutlich (<a href="steinsorten.html">Steinsorten</a>)</li>
<li><strong>Größe und Stärke</strong> – die Friedhofssatzung schreibt oft Mindeststärken vor</li>
<li><strong>Oberfläche</strong> – poliert, geschliffen, gestockt oder bruchrau</li>
<li><strong>Schrift</strong> – Anzahl der Buchstaben und Technik: vertieft, erhaben oder aufgesetzt aus Bronze, Aluminium oder Edelstahl</li>
<li><strong>Ornamente und Symbole</strong></li>
<li><strong>Einfassung und Abdeckung</strong>, falls gewünscht</li>
<li><strong>Fundament, Transport und Aufstellung</strong></li>
<li><strong>Genehmigungsgebühr</strong> der Friedhofsverwaltung</li>
</ul>""", [SRC_AET_KOSTEN, SRC_AET_GRABMAL]),
    ("Standsicherheit: Wer ist verantwortlich?", """
<p>Ein Grabmal muss dauerhaft sicher stehen. Nach der Aufstellung wird es deshalb mit einer festgelegten Prüflast auf Standsicherheit geprüft und das Ergebnis dokumentiert – je nach Friedhof nach der <em>TA Grabmal</em> oder der Richtlinie des Bundesinnungsverbands des Steinmetzhandwerks. Diese Abnahmeprüfung übernehmen wir als Fachbetrieb.</p>
<p>Danach prüft der Friedhofsträger die Grabmale regelmäßig, in der Regel einmal jährlich nach der Frostperiode. Verantwortlich für den sicheren Zustand des Grabmals ist laut den Friedhofssatzungen der bzw. die Nutzungsberechtigte. Wird ein Grabmal locker, sprechen Sie uns an – wir richten es fachgerecht wieder auf.</p>""", [SRC_AET_STAND]),
    ("Nachbeschriftung, Pflege und Ruhezeit", """
<p><strong>Nachbeschriftung:</strong> Wir ergänzen Inschriften passend zur vorhandenen Schrift – je nach Stein vor Ort oder in unserer Werkstatt. Auch dafür ist die Zustimmung der Friedhofsverwaltung nötig; die holen wir für Sie ein.</p>
<p><strong>Pflege:</strong> Am besten reinigen Sie den Stein mit klarem Wasser und einer weichen Bürste. Von scharfen Reinigungsmitteln und Hochdruckreinigern raten wir ab, weil sie Oberfläche und Schrift angreifen können. Bei hartnäckigen Verschmutzungen beraten wir Sie gern.</p>
<p><strong>Ruhezeit:</strong> Die Mindestruhezeit beträgt in Mecklenburg-Vorpommern nach § 15 Bestattungsgesetz mindestens 20 Jahre; viele Friedhöfe legen 20 bis 25 Jahre fest. Nach Ablauf des Nutzungsrechts muss das Grabmal innerhalb der in der Satzung genannten Frist entfernt werden.</p>""", [SRC_BESTATTG, SRC_AET_GRABMAL]),
]


def build_faq():
    items = []
    for i, (q, a, srcs) in enumerate(FAQ, 1):
        src = " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in srcs)
        items.append(f"""<details id="frage-{slug(q)}">
  <summary><span class="num">{i:02d}</span>{q}</summary>
  <div class="answer">{a.strip()}
    <p class="src">Quellen: {src}</p>
  </div>
</details>""")
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", " ", a).strip()}} for q, a, _ in FAQ]}
    body = f"""<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Ratgeber</p>
    <h1>Gut informiert zum Grabmal</h1>
    <p class="lead">In einer schweren Zeit kommen viele Fragen auf einmal. Hier finden Sie Antworten auf die häufigsten – und für alles Weitere nehmen wir uns gern persönlich Zeit.</p>
    {ratgeber_nav("ratgeber.html")}
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="faq">
{chr(10).join(items)}
    </div>
    <p class="muted" style="font-size:.85rem;margin-top:28px;max-width:760px">Diese Informationen ersetzen keine Rechtsberatung. Verbindlich sind das Bestattungsgesetz M-V und die Satzung des jeweiligen Friedhofs (Stand: November 2026).</p>
  </div>
</section>
{cta("Noch Fragen?", "Wir beraten Sie persönlich – auch zur Friedhofssatzung und zur Genehmigung.")}"""
    return page("ratgeber.html", "Ratgeber Grabmal",
                "Ratgeber Grabmal: Wann darf der Grabstein gesetzt werden, welche Genehmigung braucht es, was gilt zu Kinderarbeit in MV, wovon hängt der Preis ab?",
                body, "ratgeber.html", crumbs=[("Start", ""), ("Ratgeber", "ratgeber.html")], schema=[faq_ld])


KM = "https://www.kirche-mv.de"
HL = "https://www.amt-hagenow-land.de/amt-gemeinden/{}/ortsrecht/"
BL = "https://www.amtboizenburgland.de/amt-gemeinden/{}/ortsrecht/"

# (Name, Entfernung, Hinweis, [(Linktext, URL), ...]) – alle Links geprüft am 14.11.2026
SATZUNGEN = [
    ("Landkreis Ludwigslust-Parchim", [
        ("Wittenburg", "0–3 km", "Hauptfriedhof: Ev.-Luth. Kirchengemeinde St. Bartholomäus. Die städtische Satzung gilt nur für den Friedhof Zühr.", [
            ("Friedhof der Kirchengemeinde", f"{KM}/wittenburg-bartholomaeus/gemeinde/friedhof"),
            ("Städtische Satzung (Zühr)", "https://www.amt-wittenburg.de/output/download.php?fid=3627.2435.1.PDF"),
            ("Friedhofsordnung Körchow, Camin, Marsow", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Koerchow-Camin/20240813_Friedhofsordnung_fuer_die__Friedhoefe_Koerchow__Camin_und_Marsow.pdf"),
            ("Übersicht Kirchen & Friedhöfe im Amt", "https://www.amt-wittenburg.de/Familie-Soziales/Kirchen-und-Friedh%C3%B6fe/")]),
        ("Wittendörp", "ca. 5 km", "Gemeindliche Satzung für Dodow, Tessin und Pogreß; der Friedhof Döbbersen ist kirchlich.", [
            ("Ortsrecht der Gemeinde", "https://www.amt-wittenburg.de/Verwaltung-Aktuelles/Ortsrecht-Wittend%C3%B6rp/"),
            ("Kirchengemeinde Döbbersen", f"{KM}/doebbersen/friedhof")]),
        ("Zarrentin am Schaalsee und Amt Zarrentin", "ca. 8 km", "Stadtfriedhof: Ev.-Luth. Kirchengemeinde; Lassahn und Neuenkirchen mit eigenen kirchlichen Satzungen. Gemeindliche Satzungen für Gallin und Vellahn.", [
            ("Friedhofsordnung Zarrentin", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Zarrentin/251118_Friedhofsordnung_Zarrentin.pdf"),
            ("Friedhofssatzung Lassahn", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Lassahn/2026-05-07_Lassahn_-_FS.pdf"),
            ("Friedhofssatzung Neuenkirchen", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Neuenkirchen/2026-05-06_Neuenkirchen_-_FS.pdf"),
            ("Satzungen des Amtes", "https://www.amt-zarrentin.de/portal/seiten/satzungen-900000012-29120.html")]),
        ("Hagenow", "ca. 10 km", "Der Friedhof wird von der Kirchengemeinde betrieben; eine Friedhofsordnung ist nicht online veröffentlicht.", [
            ("Kirchengemeinde Hagenow", f"{KM}/hagenow/friedhof")]),
        ("Amt Hagenow-Land", "5–25 km", "Eigene Satzungen je Gemeinde:", [
            ("Alt Zachun", HL.format("alt-zachun")), ("Bresegard b. Picher", HL.format("bresegard-bei-picher")),
            ("Groß Krams", HL.format("gross-krams")), ("Hoort", HL.format("hoort")), ("Hülseburg", HL.format("huelseburg")),
            ("Kirch Jesar", HL.format("kirch-jesar")), ("Kuhstorf", HL.format("kuhstorf")), ("Moraas", HL.format("moraas")),
            ("Pritzier", HL.format("pritzier")), ("Strohkirchen", HL.format("strohkirchen")), ("Warlitz", HL.format("warlitz"))]),
        ("Amt Stralendorf", "12–22 km", "Online nur die Satzung von Holthusen; die übrigen Friedhöfe sind überwiegend kirchlich.", [
            ("Friedhofssatzung Holthusen", "https://www.amt-stralendorf.de/loadDocument.phtml?FID=3499.54.1&Ext=PDF")]),
        ("Amt Boizenburg-Land", "12–28 km", "Eigene Satzungen je Gemeinde:", [
            ("Brahlstorf", BL.format("brahlstorf")), ("Dersenow", BL.format("dersenow")), ("Schwanheide", BL.format("schwanheide"))]),
        ("Lübtheen", "18–25 km", "Stadtfriedhof: Kirchengemeinde. Gemeindliche Satzung für Gößlow.", [
            ("Friedhofsordnung Lübtheen", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Luebtheen/210302_Friedhofsordnung_Luebtheen.pdf"),
            ("Ortsrecht der Stadt (Gößlow)", "https://www.luebtheen.de/aktuelles-ortsrecht/ortsrecht/6-oeffentliche-einrichtungen/")]),
        ("Amt Ludwigslust-Land", "18–30 km", "Gemeindliche Satzungen u. a. für Alt Krenzlin, Göhlen, Lüblow, Rastow, Sülstorf und Warlow.", [
            ("Satzungen des Amtes", "https://www.amt-ludwigslust-land.de/rechtsgrundlagen/index.php?typ=1")]),
        ("Boizenburg/Elbe", "ca. 25 km", "Friedhof der Kirchengemeinde St. Marien (Boizenburg und Rensdorf).", [
            ("Friedhofsordnung Boizenburg", f"{KM}/fileadmin/elkm/propstei_parchim/boizenburg/Friedhof/190618_Friedhofsordnung__Boizenburg.pdf")]),
        # --- Erweiterung 30–80 km (November 2026) ---
        ("Ludwigslust", "ca. 36 km", "Friedhof der Ev.-Luth. Stadtkirchengemeinde Ludwigslust.", [
            ("Friedhofsordnung Ludwigslust", f"{KM}/fileadmin/projektseiten/friedhof-ludwigslust/Aktuelles/3.Aenderung_FO_Lesefassung.pdf")]),
        ("Neustadt-Glewe", "ca. 39 km", "Kirchlicher Friedhof; eine Friedhofsordnung für die Stadt ist nicht online veröffentlicht (online nur Brenz, Blievenstorf und Stolpe).", [
            ("Friedhof der Kirchengemeinde", f"{KM}/neustadt-glewe/kirche-im-leben/beerdigung-und-friedhof")]),
        ("Dömitz", "ca. 41 km", "Kirchlicher Friedhof; online nur Gebührenregelungen, keine Friedhofsordnung.", [
            ("Friedhof der Kirchengemeinde", f"{KM}/doemitz/friedhof")]),
        ("Crivitz und Amt Crivitz", "ca. 42 km", "Städtischer Friedhof Crivitz; Satzungen weiterer Amtsgemeinden (u. a. Raben Steinfeld, Banzkow, Leezen) auf der Ortsrechtsseite des Amtes.", [
            ("Friedhofssatzung Stadt Crivitz", "https://www.amt-crivitz.de/export/sites/crivitz/pdf/crivitz/satzungen/Friedhofssatzung-der-Stadt-Crivitz-26.01.2024.pdf"),
            ("Ortsrecht Amt Crivitz", "https://www.amt-crivitz.de/das-amt/ihre-amtsverwaltung/ortsrecht-satzungen/")]),
        ("Grabow", "ca. 43 km", "Friedhof der Ev.-Luth. Kirchengemeinde Grabow.", [
            ("Friedhofsordnung Grabow", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Grabow/20200101_Friedhofsordnung_Grabow_.pdf")]),
        ("Parchim", "ca. 55 km", "Städtischer Neuer Friedhof an der Lübzer Chaussee.", [
            ("Friedhofssatzung Parchim", "https://www.parchim.de/de/buergerservice-1/ortsrecht-bekanntmachungen/ortsrecht/friedhof/2022-03-14-1.-aenderung-der-friedhofssatzung-der-stadt-parchim-lesefassung.pdf?cid=kqd")]),
        ("Brüel (Penzin, Tempzin)", "ca. 57 km", "Kirchliche Friedhöfe Penzin und Tempzin der Kirchengemeinde Brüel.", [
            ("Friedhofsordnung Brüel", f"{KM}/fileadmin/elkm/propstei_wismar/KR_Sternberg/Brueel/180130_Friedhofsordnung_Brueel.pdf")]),
        ("Sternberg", "ca. 58 km", "Städtischer Friedhof.", [
            ("Friedhofssatzung Sternberg", "https://www.stadt-sternberg.de/satzungen/1Sternberg_Friedhofssatzung_vom_03_11_2006.pdf")]),
        ("Lübz", "ca. 66 km", "Friedhöfe der Ev.-Luth. Kirchengemeinde Lübz (Lübz, Lutheran, Benzin).", [
            ("Friedhofsordnung Lübz", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Luebz/230921_Friedhofsordnung_Luebz_Lutheran_und_Benzin.pdf")]),
    ]),
    ("Landeshauptstadt Schwerin", [
        ("Schwerin", "22–26 km", "Die Friedhöfe werden von der Stadt betrieben.", [
            ("Friedhofssatzung Schwerin", "https://www.schwerin.de/export/sites/default/.galleries/Dokumente/Ortsrecht/Friedhofssatzung.pdf")]),
    ]),
    ("Landkreis Nordwestmecklenburg", [
        ("Amt Lützow-Lübstorf", "10–30 km", "Gemeindliche Satzung u. a. für Lützow.", [
            ("Satzungen des Amtes", "https://www.luetzow-luebstorf.de/rechtsgrundlagen/index.php?typ=1")]),
        ("Gadebusch und Amt Gadebusch", "17–24 km", "Der Stadtfriedhof wird seit 2024 von der Kirchengemeinde betrieben (auch Roggendorf, Groß Eichsen, Vietlübbe, Groß Salitz).", [
            ("Friedhofsordnung Gadebusch", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Wismar/Gadebusch-Roggendorf/20240125_KG_Gadebusch-Roggendorf_Friedhofsordnung_fuer_den_FH_Gadebusch.pdf"),
            ("Satzungen von Stadt und Amt", "https://www.gadebusch.de/verwaltung/satzungen/")]),
        ("Holdorf (Amt Rehna)", "26–30 km", "Gemeindliche Friedhofssatzung Holdorf auf der Satzungsseite des Amtes.", [
            ("Satzungen des Amtes Rehna", "https://www.rehna.de/satzungen/")]),
        ("Rehna", "ca. 32 km", "Kirchliche Friedhöfe Rehna, Meetzen und Kirch Grambow.", [
            ("Friedhofssatzung Rehna", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Wismar/Rehna/2026-01-27_Rehna__Meetzen_und_Kirch_Grambow_-_FS.pdf")]),
        ("Schönberg", "ca. 41 km", "Friedhöfe der Ev.-Luth. Kirchengemeinde Schönberg.", [
            ("Friedhofssatzung Schönberg", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Wismar/Schoenberg/251203_Friedhofssatzung_Schoenberg.pdf")]),
        ("Grevesmühlen", "ca. 43 km", "Friedhof der Ev.-Luth. Kirchengemeinde Grevesmühlen.", [
            ("Friedhofssatzung Grevesmühlen", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Wismar/Grevesmuehlen/2026-03-05_Grevesmuehlen_-_FS.pdf")]),
        ("Dassow", "ca. 47 km", "Friedhöfe der Ev.-Luth. Kirchengemeinde Dassow.", [
            ("Friedhofssatzung Dassow", f"{KM}/fileadmin/Gemeindeseiten/mecklenburg/dassow/Dassow_Friedhofssatzung_2025.pdf")]),
        ("Hansestadt Wismar", "ca. 53 km", "Städtischer Friedhof mit Altem Friedhof und Westfriedhof.", [
            ("Friedhofssatzung Wismar", "https://www.wismar.de/loadDocument.phtml?FID=2634.12595.1&Ext=PDF")]),
        ("Klütz", "ca. 54 km", "Alter Friedhof der Ev.-Luth. Kirchengemeinde Klütz.", [
            ("Friedhofsordnung Klütz", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Wismar/Kluetz/210525_Friedhofsordnung_Alter_Friedhof_Kluetz.pdf")]),
        ("Neukloster", "ca. 60 km", "Friedhof der Ev.-Luth. Sonnenkamp-Kirchengemeinde.", [
            ("Friedhofssatzung Neukloster", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Wismar/Neukloster/251028_Friedhofssatzung_Friedhof_Neukloster.pdf")]),
    ]),
    ("Landkreis Rostock", [
        ("Bützow", "ca. 75 km", "Friedhöfe der Ev.-Luth. Kirchengemeinde (Bützow, Langen Trechow, Passin, Zepelin).", [
            ("Friedhofsordnung Bützow", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Rostock/Buetzow/Buetzow/170815_Friedhofsordnung_Buetzow.pdf")]),
    ]),
    ("Kreis Herzogtum Lauenburg (Schleswig-Holstein)", [
        ("Mölln", "ca. 26 km", "Friedhof der Ev.-Luth. Kirchengemeinde Mölln.", [
            ("Friedhofssatzung Mölln", "https://www.friedhof-moelln.de/assets/friedhofssatzung-ab-2022.pdf")]),
        ("Güster (Amt Büchen)", "ca. 27 km", "", [
            ("Friedhofssatzung Güster", "https://www.amt-buechen.de/fileadmin/user_upload/public/downloads/orts_verbandsrecht/guester/nutzung_oeffentlicher_einrichtungen/Satzung_Friedhofs-_u._Bestattungswesen.pdf")]),
        ("Grambek (Amt Breitenfelde)", "ca. 28 km", "", [
            ("Friedhofssatzung Grambek", "https://www.grambek.de/fileadmin/download/gemeinden/grambek/ortsrecht/finanzen/satzung_%C3%BCber_das_friedhofs-_und_bestattungswesen_in_der_gemeinde_grambek.pdf")]),
        ("Amt Lauenburgische Seen", "18–30 km", "Keine Satzungen online – die Friedhöfe sind überwiegend kirchlich. Bitte bei der Kirchengemeinde erfragen.", []),
        ("Ratzeburg", "ca. 29 km", "Friedhof St. Georg auf dem Berge der Kirchengemeinde St. Georgsberg; für den Domfriedhof ist keine Satzung online.", [
            ("Friedhofssatzung St. Georgsberg", "http://www.st-georgsberg.de/uploads/kp3AtX6B/Friedhofssatzung.pdf")]),
        ("Lauenburg/Elbe", "ca. 34 km", "Friedhof der Ev.-Luth. Kirchengemeinde Lauenburg (mit Schnakenbek).", [
            ("Friedhofssatzung Lauenburg", "https://www.friedhof-lauenburg.de/fileadmin/user_upload/Downloads/FriedhofsSATZUNG.pdf")]),
        ("Geesthacht", "ca. 44 km", "Städtische Friedhöfe Alter Friedhof und Waldfriedhof.", [
            ("Friedhofssatzung Geesthacht", "https://www.geesthacht.de/output/download.php?fid=3777.883.1.PDF")]),
    ]),
    ("Hansestadt Lübeck (Schleswig-Holstein)", [
        ("Lübeck", "ca. 48 km", "Städtische Friedhöfe Vorwerk, Burgtor, Waldhusen, St. Jürgen und Ehrenfriedhof.", [
            ("Friedhofssatzung Lübeck", "https://www.luebeck.de/file/6_12_friedhofssatzung_der_hansestadt_luebeck.pdf")]),
    ]),
    ("Kreise Stormarn und Segeberg (Schleswig-Holstein)", [
        ("Trittau", "ca. 44 km", "Südfriedhof der Gemeinde.", [
            ("Friedhofssatzung Trittau", "https://www.trittau.de/downloads/datei/MTU2NzEyYTA3NmRiZDhmZGFKZFV0SW9EUUhBVmI4bGdmc2xzUTNEU1lxeUcwSlZlQTZwS25XWHhMb0NOdG9VQ0QzYXdhTVQ5ZE9vNWcvaU8ya0U5K04ra29hdEs0ZDN2dGt5bEMvNHV0bzJvaHJDQ0lNSDFoNTdOdjdoQ2FhSmRKQXhOMUpNMFZYUXEwMmxyN0RrTzRlRGR3WUdLOVZhUmh4bGI4RGpIMUFkek9YSjc2aDR0S1FsQ1lBST0")]),
        ("Ahrensburg", "ca. 56 km", "Friedhof der Kirchengemeinde (Alter Teil) und der Stadt (Neuer Teil), verwaltet von der Kirchengemeinde.", [
            ("Friedhofssatzung Ahrensburg", "https://friedhof-ahrensburg.com/wp-content/uploads/2024/02/Friedhofssatzung-Ahrensburg-2023.pdf")]),
        ("Norderstedt", "ca. 72 km", "Kommunale Friedhöfe Friedrichsgabe, Glashütte und Harksheide.", [
            ("Friedhofssatzung Norderstedt", "https://www.norderstedt.de/media/custom/1087_6234_1.PDF?1767606584")]),
    ]),
    ("Hamburg", [
        ("Hamburg", "ca. 66 km", "Die großen Friedhöfe (u. a. Ohlsdorf und Öjendorf) betreibt die Hamburger Friedhöfe AöR; eine Friedhofsordnung ist dort nicht als Dokument veröffentlicht. Bitte bei der Friedhofsverwaltung erfragen.", [
            ("Hamburger Friedhöfe AöR", "https://www.friedhof-hamburg.de/")]),
    ]),
    ("Niedersachsen: Landkreise Lüneburg, Lüchow-Dannenberg und Harburg", [
        ("Amt Neuhaus", "ca. 24 km", "Kommunale Friedhöfe der Gemeinde.", [
            ("Friedhofssatzung Amt Neuhaus", "https://www.amt-neuhaus.de/ResourceImage.aspx?raid=28947")]),
        ("Bleckede (Breetze)", "ca. 29 km", "Online nur die städtische Satzung für den Friedhof Breetze.", [
            ("Friedhofssatzung Breetze", "https://www.bleckede.de/ResourceImage.aspx?raid=32691")]),
        ("Samtgemeinde Elbtalaue (Hitzacker, Dannenberg)", "38–44 km", "Kommunale Friedhöfe der Samtgemeinde; kirchliche Friedhöfe haben eigene Ordnungen.", [
            ("Friedhofsordnung Elbtalaue", "https://www.elbtalaue.de/downloads/datei/NDU1ZGEyY2FhMWE2MWVmMnNMTExYYUkwaGNWRy9LRWdkSDZxMU9HQmZnTWw5RTE4WjNMcE1ETkduT3EvYU5TR0sxWUx5eFVOakdpZnpNbkNrYUpyUjYrd051MHg4dVloaCtyc21xTGQwaVRNNndYUjBjTXIwQmhUWXhDZDBac0dTWTNlbVZRTzZ1aWwxckdUcDJhRlVLQnJmUUNXbE1QM0prckovQT09")]),
        ("Samtgemeinde Scharnebeck", "ca. 41 km", "Kommunale Friedhöfe der Samtgemeinde, u. a. Echem und Hohnstorf/Elbe.", [
            ("Friedhofssatzung Scharnebeck", "https://www.scharnebeck.de/ResourceImage.aspx?raid=31740")]),
        ("Adendorf", "ca. 45 km", "Kommunaler Friedhof der Gemeinde.", [
            ("Friedhofssatzung Adendorf", "http://www.adendorf.de/1/wp-content/uploads/2026/01/2025-12-12-Friedhofsatzung.pdf")]),
        ("Hansestadt Lüneburg", "ca. 49 km", "Städtische Friedhöfe, u. a. Wald-, Zentral- und Michaelisfriedhof.", [
            ("Friedhofssatzung Lüneburg", "https://www.hansestadt-lueneburg.de/_Resources/Persistent/2/7/0/6/2706b041a02f93f20445d8ac2af0073bb974c0da/67_01_friedhofssatzung.pdf")]),
        ("Winsen (Luhe)", "ca. 56 km", "Städtische Friedhofssatzung (in Kraft seit 01.01.2026); eine Zusammenfassung folgt.", [
            ("Friedhofssatzung Winsen", "https://www.winsen.de/portal/seiten/19-satzung-ueber-das-friedhofs-und-bestattungswesen-in-der-stadt-winsen-luhe-friedhofssatzung-902000500-20260.html?rubrik=902000117")]),
        ("Seevetal", "ca. 65 km", "Kommunale Friedhöfe Maschen, Ramelsloh, Ohlendorf und Holtorfsloh; Hittfeld und Meckelfeld/Over sind kirchlich.", [
            ("Friedhofssatzung Seevetal", "https://www.seevetal.de/downloads/datei/MGQxYTNlYTljZDcyMzM3NEJDVmE0UGVmUytZSnNtQU5XSFM4aUM5UHFsdHpXaS9jQ2NNcjRMSWllOWNCSkJLV3RCOTdSR05WR2VWSjdFMFpnditocnhtY1VzQlFFbXh1MDR0cG9kMkdDZTZyRTVUeVROZ1pqbHIwLzU1U29RNGpHb05BeDdWd0FONmR6STRPSXFiTkRqRHRpZkdxSWtVS0ZZMDg5UT09")]),
        ("Buchholz in der Nordheide", "ca. 78 km", "Städtische Friedhöfe Seppensen, Sprötze und Trelde; Waldfriedhof Buchholz ist kirchlich.", [
            ("Friedhofssatzung Buchholz", "https://www.buchholz.de/downloads/datei/OGMwZDBhYTM5Y2YyMDY3OVY4dUZodG5veWp2K1NrQVFHYUY5SFYyR012ekwyL3ZZOFh5TC92cEpoR25MQytPQ0ExM0U3UGdaT09yQzkyTFFTY3RhZzhUN3RvRGh5dEdUMW9RN216R3BoTjFvdFhYUktxbXBmbEoxeWJ2SGZ0TU5wdk1aSks5QkFhRFhuMG9TZ2dxY05ITG5iS2lKbzRRcmttNDVPUT09")]),
    ]),
]


MARKERS = []
SEARCH = []
ORTE = json.loads((ROOT / "scripts" / "orte.json").read_text(encoding="utf-8"))

# Welche Orte (Kartenpunkte) gehören zu welchem Eintrag. Zweiter Wert: Linktext,
# der für diesen Ort gilt (None = alle Links des Eintrags).
ENTRY_ORTE = {
    "Wittenburg": [("Wittenburg", None), ("Zühr", "Städtische Satzung (Zühr)"), ("Körchow", "Friedhofsordnung Körchow, Camin, Marsow"),
                   ("Camin", "Friedhofsordnung Körchow, Camin, Marsow"), ("Marsow", "Friedhofsordnung Körchow, Camin, Marsow")],
    "Wittendörp": [("Wittendörp", "Ortsrecht der Gemeinde"), ("Döbbersen", "Kirchengemeinde Döbbersen")],
    "Zarrentin am Schaalsee und Amt Zarrentin": [("Zarrentin am Schaalsee", "Friedhofsordnung Zarrentin"), ("Lassahn", "Friedhofssatzung Lassahn"), ("Neuenkirchen", "Friedhofssatzung Neuenkirchen"), ("Gallin", "Satzungen des Amtes"), ("Vellahn", "Satzungen des Amtes")],
    "Hagenow": [("Hagenow", None)],
    "Amt Hagenow-Land": [("Alt Zachun", "Alt Zachun"), ("Bresegard bei Picher", "Bresegard b. Picher"), ("Groß Krams", "Groß Krams"), ("Hoort", "Hoort"),
                         ("Hülseburg", "Hülseburg"), ("Kirch Jesar", "Kirch Jesar"), ("Kuhstorf", "Kuhstorf"), ("Moraas", "Moraas"),
                         ("Pritzier", "Pritzier"), ("Strohkirchen", "Strohkirchen"), ("Warlitz", "Warlitz")],
    "Amt Stralendorf": [("Holthusen", None)],
    "Amt Boizenburg-Land": [("Brahlstorf", "Brahlstorf"), ("Dersenow", "Dersenow"), ("Schwanheide", "Schwanheide")],
    "Lübtheen": [("Lübtheen", "Friedhofsordnung Lübtheen"), ("Gößlow", "Ortsrecht der Stadt (Gößlow)")],
    "Amt Ludwigslust-Land": [(o, None) for o in ("Alt Krenzlin", "Göhlen", "Lüblow", "Rastow", "Sülstorf", "Warlow")],
    "Boizenburg/Elbe": [("Boizenburg/Elbe", None)],
    "Schwerin": [("Schwerin", None)],
    "Amt Lützow-Lübstorf": [("Lützow", None)],
    "Gadebusch und Amt Gadebusch": [("Gadebusch", None)],
    "Holdorf (Amt Rehna)": [("Holdorf", None)],
    "Mölln": [("Mölln", None)],
    "Güster (Amt Büchen)": [("Güster", None)],
    "Grambek (Amt Breitenfelde)": [("Grambek", None)],
    "Amt Lauenburgische Seen": [("Seedorf (Lauenburg)", None), ("Sterley", None), ("Salem", None)],
    # --- Erweiterung 30–80 km ---
    "Ludwigslust": [("Ludwigslust", None)],
    "Neustadt-Glewe": [("Neustadt-Glewe", None)],
    "Dömitz": [("Dömitz", None)],
    "Crivitz und Amt Crivitz": [("Crivitz", None)],
    "Grabow": [("Grabow", None)],
    "Parchim": [("Parchim", None)],
    "Brüel (Penzin, Tempzin)": [("Penzin", None), ("Tempzin", None)],
    "Sternberg": [("Sternberg", None)],
    "Lübz": [("Lübz", None)],
    "Rehna": [("Rehna", None)],
    "Schönberg": [("Schönberg", None)],
    "Grevesmühlen": [("Grevesmühlen", None)],
    "Dassow": [("Dassow", None)],
    "Hansestadt Wismar": [("Wismar", None)],
    "Klütz": [("Klütz", None)],
    "Neukloster": [("Neukloster", None)],
    "Bützow": [("Bützow", None)],
    "Ratzeburg": [("Ratzeburg", None)],
    "Lauenburg/Elbe": [("Lauenburg/Elbe", None)],
    "Geesthacht": [("Geesthacht", None)],
    "Lübeck": [("Lübeck", None)],
    "Trittau": [("Trittau", None)],
    "Ahrensburg": [("Ahrensburg", None)],
    "Norderstedt": [("Norderstedt", None)],
    "Hamburg": [("Hamburg-Ohlsdorf", None)],
    "Amt Neuhaus": [("Amt Neuhaus", None)],
    "Bleckede (Breetze)": [("Breetze", None)],
    "Samtgemeinde Elbtalaue (Hitzacker, Dannenberg)": [("Hitzacker (Elbe)", None), ("Dannenberg (Elbe)", None)],
    "Samtgemeinde Scharnebeck": [("Scharnebeck", None)],
    "Adendorf": [("Adendorf", None)],
    "Hansestadt Lüneburg": [("Lüneburg", None)],
    "Winsen (Luhe)": [("Winsen (Luhe)", None)],
    "Seevetal": [("Seevetal", None)],
    "Buchholz in der Nordheide": [("Buchholz i. d. N.", None)],
}


def satz_data_json():
    return json.dumps({"markers": MARKERS, "lehsen": ORTE["Lehsen"], "search": SEARCH}, ensure_ascii=False).replace("</", "<\\/")


def dist_km(a, b):
    import math
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    return 2 * 6371 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


def slug(t):
    t = t.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def build_satzungen():
    regions = []
    MARKERS.clear()
    SEARCH.clear()
    for region, entries in SATZUNGEN:
        lis = []
        for name, _km, note, links in entries:
            orte = ENTRY_ORTE.get(name, [])
            ds = [dist_km(ORTE["Lehsen"], ORTE[o]) for o, _ in orte if ORTE.get(o)]
            if ds:
                lo, hi = round(min(ds)), round(max(ds))
                km = f"ca. {lo} km" if lo == hi else f"{lo}–{hi} km"
            else:
                km = _km
            eid = "ort-" + slug(name)
            extra = []
            for o, _ in orte:
                sid = ORT_SATZUNG.get(o)
                if sid in SATZ:
                    extra += SATZ[sid].get("orte", []) + SATZ[sid].get("friedhoefe", [])
            search = " ".join([name, note] + [o for o, _ in orte] + [t for t, _ in links] + extra).lower()
            for o, lbl in orte:
                if ORTE.get(o):
                    ll = [(t, u) for t, u in links if lbl is None or t == lbl]
                    sid = ORT_SATZUNG.get(o)
                    keys = [o, name] + (SATZ[sid].get("orte", []) + SATZ[sid].get("friedhoefe", []) if sid in SATZ else [])
                    arttxt = {"kommunal": "kommunal", "kirchlich": "kirchlich", "keine_online": "keine Satzung online"}.get(SATZ.get(sid, {}).get("art"), "")
                    sub = " · ".join(x for x in (name if name != o else "", arttxt, f"{round(dist_km(ORTE['Lehsen'], ORTE[o]))} km") if x)
                    SEARCH.append({"n": o, "sub": sub, "u": satz_url(sid) if sid in SATZ else f"#{eid}", "k": " ".join(keys), "d": round(dist_km(ORTE['Lehsen'], ORTE[o]), 1)})
                    MARKERS.append({"n": o, "e": name, "id": eid, "p": ORTE[o], "l": ll,
                                    "s": f"friedhofssatzungen/{sid}.html" if sid in SATZ else ""})
            sids = []
            for o, _ in orte:
                sid = ORT_SATZUNG.get(o)
                if sid and sid in SATZ and sid not in sids:
                    sids.append(sid)
            summ = ""
            if sids:
                if len(sids) == 1:
                    summ = f'<a class="summ" href="friedhofssatzungen/{sids[0]}.html">Zusammenfassung lesen →</a>'
                else:
                    def short(x):
                        names = [o for o, _ in orte if ORT_SATZUNG.get(o) == x]
                        return "/".join(n.replace(" am Schaalsee", "") for n in names) or x
                    summ = '<span class="summ-label">Zusammenfassungen:</span> ' + " ".join(
                        f'<a class="summ" href="friedhofssatzungen/{x}.html">{esc(short(x))}</a>' for x in sids)
            if links:
                lk = "<br>".join(f'<a class="dl" href="{u}" target="_blank" rel="noopener">{t} ↗</a>' for t, u in links)
            else:
                lk = '<span class="none">nicht online</span>'
            many = len(links) > 4
            if many:
                lk = " ".join(f'<a class="dl" href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in links)
            lis.append(f"""<li id="{eid}" data-search="{esc(search)}"{' class="many"' if many else ""}><div class="ort"><strong>{name} <span class="km">· {km}</span></strong>{f"<small>{note}</small>" if note else ""}{f'<div class="summ-row">{summ}</div>' if summ else ""}</div><div class="links">{lk}</div></li>""")
        regions.append(f"""<div class="region" data-region><h2>{region}</h2><ul class="satzungen">{"".join(lis)}</ul></div>""")
    body = f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Start</a> / <a href="ratgeber.html">Ratgeber</a> / Friedhofssatzungen</div>
    <h1>Friedhofssatzungen</h1>
    <p class="lead">Jeder Friedhof legt eigene Regeln für Grabmale fest. Hier finden Sie die Satzungen und Friedhofsordnungen im Umkreis von etwa 80 km um Lehsen – sortiert nach Landkreis und Entfernung.</p>
    {ratgeber_nav("friedhofssatzungen.html")}
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <div>
      <h2 style="font-size:1.6rem">Was regelt eine Friedhofssatzung?</h2>
      <ul class="prose" style="padding-left:1.2em">
        <li>zulässige <strong>Größe und Stärke</strong> des Grabmals</li>
        <li><strong>Material, Farbe und Bearbeitung</strong> der Oberfläche</li>
        <li><strong>Fundament und Befestigung</strong> für die Standsicherheit</li>
        <li>das <strong>Genehmigungsverfahren</strong> und die nötigen Unterlagen</li>
        <li><strong>Ruhezeit</strong>, Nutzungsrecht und Fristen</li>
      </ul>
    </div>
    <div class="callout">
      <h3>Kirchlich oder kommunal?</h3>
      <p>In vielen Städten unserer Region – etwa Wittenburg, Hagenow, Zarrentin, Boizenburg und Gadebusch – wird der Friedhof von der evangelischen Kirchengemeinde betrieben. Dort gilt deren <em>Friedhofsordnung</em>. Kommunale Satzungen gibt es vor allem für Dorffriedhöfe.</p>
      <p>Sie wissen nicht, welche Regeln für Ihren Friedhof gelten? <a href="kontakt.html">Fragen Sie uns</a> – wir kennen die Vorgaben und klären alles mit der Friedhofsverwaltung.</p>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
    <div class="finder">
      <div class="finder-search">
        <label for="ortsuche">Ihren Friedhof finden</label>
        <div class="search-box">
          <input id="ortsuche" type="search" placeholder="Ort eingeben, z. B. Hoort oder Zarrentin" autocomplete="off"
                 role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="search-results">
          <ul class="search-results" id="search-results" role="listbox" aria-label="Treffer" hidden></ul>
        </div>
        <p class="search-empty" id="search-empty" hidden>Kein passender Ort gefunden. <a href="kontakt.html">Fragen Sie uns</a> – wir helfen gern weiter.</p>
        <div class="quick" aria-label="Schnellauswahl">
          {"".join(f'<button type="button" data-quick="{q}">{q}</button>' for q in ("Wittenburg", "Hagenow", "Zarrentin", "Boizenburg", "Schwerin", "Wismar", "Lübeck", "Lüneburg", "Ludwigslust", "Parchim"))}
        </div>
        <p class="finder-hint">Geben Sie den Namen Ihres Ortes ein und wählen Sie ihn aus der Trefferliste – Sie gelangen direkt zur Zusammenfassung der Friedhofssatzung. Die Karte daneben können Sie zusätzlich zur Orientierung laden.</p>
      </div>
      <div class="map-wrap">
        <div id="map" class="map" aria-label="Karte der Friedhöfe im Umkreis von 80 km um Lehsen"></div>
        <div class="map-consent" id="map-consent">
          <div>
            <h3>Karte anzeigen</h3>
            <p>Die Karte wird von OpenStreetMap geladen. Dabei wird Ihre IP-Adresse an die OpenStreetMap Foundation übertragen. Mehr dazu in der <a href="datenschutz.html#karte">Datenschutzerklärung</a>.</p>
            <button class="btn" type="button" id="map-load">Karte laden</button>
            <label class="check" style="justify-content:center;margin:14px 0 0"><input type="checkbox" id="map-remember"><span>Karte künftig immer laden</span></label>
          </div>
        </div>
      </div>
    </div>
    <script type="application/json" id="satz-data">{satz_data_json()}</script>
    {"".join(regions)}
    <div class="region">
      <h2>Kirchliche Friedhöfe in Mecklenburg</h2>
      <ul class="satzungen">
        <li><div class="ort"><strong>Zentrale Friedhofsverwaltung</strong><small>Kirchenkreis Mecklenburg der Nordkirche – Ansprechpartner für kirchliche Friedhöfe</small></div><div class="links"><a class="dl" href="{KM}/mecklenburg/kirchenkreisverwaltung/liegenschaften-und-friedhof/zentrale-friedhofsverwaltung" target="_blank" rel="noopener">Zur Friedhofsverwaltung ↗</a></div></li>
        <li><div class="ort"><strong>Friedhofsrichtlinie</strong><small>Grundlage für die Friedhofsordnungen der Kirchengemeinden</small></div><div class="links"><a class="dl" href="{KM}/fileadmin/Mecklenburg/Downloads/Friedhof/1801_Friedhofsrichtlinie_KK_Mecklenburg.pdf" target="_blank" rel="noopener">Richtlinie (PDF) ↗</a></div></li>
      </ul>
    </div>
    <p class="muted" style="font-size:.85rem;max-width:760px">Alle Links führen zu den offiziellen Seiten der Städte, Ämter und Kirchengemeinden (geprüft im November 2026). Satzungen ändern sich gelegentlich – maßgeblich ist immer die aktuelle Fassung beim Friedhofsträger. Ihr Friedhof fehlt? Sprechen Sie uns an.</p>
  </div>
</section>
{cta()}"""
    body += f'<script src="{v("satzungen.js")}" defer></script>'
    return page("friedhofssatzungen.html", "Friedhofssatzungen in der Region",
                "Friedhofssatzungen im Umkreis von 80 km um Wittenburg – Hagenow, Schwerin, Wismar, Lübeck, Lüneburg, Parchim u. v. m., verständlich zusammengefasst.",
                body, "friedhofssatzungen.html", crumbs=[("Start", ""), ("Ratgeber", "ratgeber.html"), ("Friedhofssatzungen", "friedhofssatzungen.html")])


def ratgeber_nav(active):
    pages = [("ratgeber.html", "Häufige Fragen"), ("friedhofssatzungen.html", "Friedhofssatzungen"), ("steinsorten.html", "Steinsorten")]
    return '<nav class="subnav" aria-label="Ratgeber">' + "".join(
        f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in pages
    ) + "</nav>"


SATZ_DIR = ROOT / "scripts" / "satzungen"


def load_satzungen():
    data = {}
    if SATZ_DIR.exists():
        for f in sorted(SATZ_DIR.glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            data[d["id"]] = d
    return data


SATZ = {}

# Welche Satzung gehört zu welchem Kartenpunkt / Listeneintrag
ORT_SATZUNG = {
    "Wittenburg": "wittenburg-st-bartholomaeus", "Zühr": "wittenburg-zuehr", "Körchow": "koerchow-camin-marsow",
    "Camin": "koerchow-camin-marsow", "Marsow": "koerchow-camin-marsow", "Wittendörp": "wittendoerp",
    "Döbbersen": "doebbersen", "Lassahn": "lassahn", "Neuenkirchen": "neuenkirchen", "Zarrentin am Schaalsee": "zarrentin", "Gallin": "gallin",
    "Vellahn": "vellahn", "Hagenow": "hagenow", "Alt Zachun": "alt-zachun", "Bresegard bei Picher": "bresegard-bei-picher",
    "Groß Krams": "gross-krams", "Hoort": "hoort", "Hülseburg": "huelseburg", "Kirch Jesar": "kirch-jesar",
    "Kuhstorf": "kuhstorf", "Moraas": "moraas", "Pritzier": "pritzier", "Strohkirchen": "strohkirchen", "Warlitz": "warlitz",
    "Holthusen": "holthusen", "Brahlstorf": "brahlstorf", "Dersenow": "dersenow", "Schwanheide": "schwanheide",
    "Lübtheen": "luebtheen", "Gößlow": "goesslow", "Alt Krenzlin": "alt-krenzlin", "Göhlen": "goehlen", "Lüblow": "lueblow",
    "Rastow": "rastow", "Sülstorf": "suelstorf", "Warlow": "warlow", "Boizenburg/Elbe": "boizenburg", "Schwerin": "schwerin",
    "Lützow": "luetzow", "Gadebusch": "gadebusch", "Holdorf": "holdorf", "Mölln": "moelln", "Güster": "guester",
    "Grambek": "grambek", "Seedorf (Lauenburg)": "lauenburgische-seen", "Sterley": "lauenburgische-seen", "Salem": "lauenburgische-seen",
    # --- Erweiterung 30–80 km ---
    "Ludwigslust": "ludwigslust", "Crivitz": "crivitz", "Grabow": "grabow", "Parchim": "parchim", "Penzin": "brueel", "Tempzin": "brueel",
    "Sternberg": "sternberg", "Lübz": "luebz", "Rehna": "rehna", "Schönberg": "schoenberg", "Grevesmühlen": "grevesmuehlen",
    "Dassow": "dassow", "Wismar": "wismar", "Klütz": "kluetz", "Neukloster": "neukloster", "Bützow": "buetzow",
    "Ratzeburg": "ratzeburg", "Lauenburg/Elbe": "lauenburg", "Geesthacht": "geesthacht", "Lübeck": "luebeck",
    "Trittau": "trittau", "Ahrensburg": "ahrensburg", "Norderstedt": "norderstedt", "Amt Neuhaus": "amt-neuhaus",
    "Breetze": "bleckede", "Hitzacker (Elbe)": "elbtalaue", "Dannenberg (Elbe)": "elbtalaue", "Scharnebeck": "scharnebeck",
    "Adendorf": "adendorf", "Lüneburg": "lueneburg", "Seevetal": "seevetal", "Buchholz i. d. N.": "buchholz",
}

# Satzungen der Erweiterung auf 80 km. Bestehende Seiten verlinken unter „Friedhöfe in der Nähe“
# weiterhin nur die bisherigen Satzungen, damit sie unverändert bleiben.
NEW_SATZ = {"ludwigslust", "crivitz", "grabow", "parchim", "brueel", "sternberg", "luebz", "rehna", "schoenberg",
            "grevesmuehlen", "dassow", "wismar", "kluetz", "neukloster", "buetzow", "ratzeburg", "lauenburg",
            "geesthacht", "luebeck", "trittau", "ahrensburg", "norderstedt", "amt-neuhaus", "bleckede", "elbtalaue",
            "scharnebeck", "adendorf", "lueneburg", "seevetal", "buchholz"}

SATZ_SECTIONS = [
    ("masse", "Maße & Stärke"),
    ("material", "Material & Bearbeitung"),
    ("verbote", "Nicht erlaubt"),
    ("genehmigung", "Genehmigung"),
    ("standsicherheit", "Standsicherheit"),
    ("fristen", "Fristen"),
    ("besonderheiten", "Weitere Regeln zur Grabgestaltung"),
]


def lst(items):
    items = [i for i in (items or []) if i and str(i).strip()]
    if not items:
        return '<p class="muted">In dieser Satzung nicht ausdrücklich geregelt.</p>'
    return "<ul>" + "".join(f"<li>{esc(str(i))}</li>" for i in items) + "</ul>"


def satz_primary(sid):
    names = [o for o, x in ORT_SATZUNG.items() if x == sid]
    return names


def satz_label(d):
    sid = d["id"]
    names = [n.replace(" am Schaalsee", "").replace("Seedorf (Lauenburg)", "Seedorf") for n in satz_primary(sid)]
    if sid == "lauenburgische-seen":
        ort = "Amt Lauenburgische Seen"
    elif len(names) > 2:
        ort = ", ".join(names[:-1]) + " & " + names[-1]
    elif len(names) == 2:
        ort = " & ".join(names)
    else:
        ort = names[0] if names else (d.get("orte") or [sid])[0]
    art = d.get("art")
    typ = "Friedhof" if art == "keine_online" else ("Friedhofsordnung" if art == "kirchlich" else "Friedhofssatzung")
    return typ, ort


def satz_url(sid):
    return f"friedhofssatzungen/{sid}.html"


def nearby(sid, n=3):
    here = [ORTE[o] for o in satz_primary(sid) if ORTE.get(o)]
    if not here:
        return []
    c = here[0]
    out = []
    for other in SATZ:
        if other == sid or (sid not in NEW_SATZ and other in NEW_SATZ):
            continue
        pts = [ORTE[o] for o in satz_primary(other) if ORTE.get(o)]
        if pts:
            out.append((min(dist_km(c, p) for p in pts), other))
    return [o for _, o in sorted(out)[:n]]


def related_cats(d):
    txt = json.dumps(d, ensure_ascii=False).lower()
    rel = []
    if "rasen" in txt or "urne" in txt or "liegend" in txt:
        rel.append(("liegesteine", "Liegesteine", "für Urnen- und Rasengräber"))
    rel.append(("reihensteine", "Reihensteine", "für Einzelgrabstätten"))
    rel.append(("breitsteine", "Breitsteine", "für Doppelgrabstätten"))
    if "stele" in txt:
        rel.append(("stelen", "Stelen", "schlank und zeitlos"))
    if "einfassung" in txt or "abdeckung" in txt:
        rel.append(("grabanlagen", "Grabanlagen", "Einfassung und Abdeckung"))
    return rel[:4]


def build_satzung_page(d):
    sid = d["id"]
    keine = d.get("art") == "keine_online"
    typ, ort = satz_label(d)
    h1 = f"{typ} {ort}"
    art = {"kommunal": "Kommunaler Friedhof", "kirchlich": "Kirchlicher Friedhof", "keine_online": "Keine Satzung online"}.get(d.get("art"), "")
    orte = d.get("orte") or []
    chips = "".join(f"<span>{esc(o)}</span>" for o in orte)
    meta = [("Friedhofsträger", d.get("traeger")), ("Fassung", d.get("fassung"))]
    if d.get("friedhoefe"):
        meta.append(("Friedhöfe", ", ".join(d["friedhoefe"])))
    meta_html = "".join(f"<div><dt>{k}</dt><dd>{esc(str(v))}</dd></div>" for k, v in meta if v and not (keine and k == "Fassung"))
    src = d.get("quelle_url")
    src_btn = f'<a class="btn btn-ghost" href="{esc(src)}" target="_blank" rel="noopener">{"Zur Seite des Trägers" if keine else "Original-Satzung öffnen"}</a>' if src else ""

    if keine:
        main = f"""<div class="callout"><h2 class="h3">Satzung liegt uns nicht vor</h2><p>{esc(d.get("kurzfazit") or "")}</p>
    <p>Wir kennen die Gegebenheiten vor Ort und fragen die geltenden Vorgaben gern für Sie bei der Friedhofsverwaltung nach.</p></div>"""
    else:
        cards = [f"""<section class="satz-card satz-wide"><h2>Ruhezeit</h2><p>{esc(d.get("ruhezeit") or "nicht geregelt")}</p></section>"""]
        ga = d.get("grabarten") or []
        if ga:
            rows = "".join(f"<li><strong>{esc(g.get('name',''))}</strong><span>{esc(g.get('regel',''))}</span></li>" for g in ga)
            cards.append(f"""<section class="satz-card satz-wide"><h2>Grabarten mit eigenen Regeln</h2><ul class="grabarten">{rows}</ul></section>""")
        for key, label in SATZ_SECTIONS:
            cards.append(f"""<section class="satz-card"><h2>{label}</h2>{lst(d.get(key))}</section>""")
        cards.append(f"""<section class="satz-card"><h2>Natursteine ohne Kinderarbeit</h2><p>{esc(d.get("kinderarbeit") or "nicht geregelt")}</p></section>""")
        main = f"""<div class="callout satz-fazit"><h2 class="h3">Das Wichtigste in Kürze</h2><p>{esc(d.get("kurzfazit") or "")}</p></div>
    <div class="satz-cards">{"".join(cards)}</div>"""

    rel = "".join(f'<a href="{s_}.html"><strong>{t}</strong><span>{sub}</span></a>' for s_, t, sub in related_cats(d))
    near = "".join(f'<a href="{satz_url(x)}"><strong>{esc(" ".join(satz_label(SATZ[x])))}</strong><span>{esc(SATZ[x].get("traeger") or "")}</span></a>' for x in nearby(sid))
    extra = f"""<div class="satz-more">
      <section><h2 class="h3">Passende Grabmale</h2><div class="more-links">{rel}</div></section>
      <section><h2 class="h3">Friedhöfe in der Nähe</h2><div class="more-links">{near}</div></section>
    </div>"""

    body = f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Start</a> / <a href="ratgeber.html">Ratgeber</a> / <a href="friedhofssatzungen.html">Friedhofssatzungen</a> / {esc(ort)}</div>
    <p class="eyebrow">{art}</p>
    <h1>{esc(h1)}</h1>
    <p class="satz-official">{esc(d.get("titel") or "")}</p>
    <div class="ort-chips">{chips}</div>
    <dl class="satz-meta">{meta_html}</dl>
    <div class="btn-row">{src_btn}<a class="btn" href="kontakt.html">Beratung zu diesem Friedhof</a></div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="satz-grid">
      <div class="satz-main">{main}</div>
      {satz_aside(d)}
    </div>
    {extra}
    <p class="satz-disclaimer">Stand der Zusammenfassung: November 2026. Maßgeblich ist die jeweils aktuelle Fassung der Satzung; die Paragrafen-Angaben beziehen sich auf das verlinkte Original.</p>
    <p><a href="friedhofssatzungen.html">← Alle Friedhofssatzungen in der Region</a></p>
  </div>
</section>
{cta("Wir übernehmen den Antrag", "Wir kennen die Vorgaben dieses Friedhofs und stimmen Ihr Grabmal mit der Friedhofsverwaltung ab.")}"""
    if keine:
        desc = f"Friedhof {ort}: Träger, Ansprechpartner und Hinweise für Grabmale – der Steinmetz aus Lehsen fragt die Vorgaben gern für Sie nach."
    else:
        desc = f"Was gilt für Grabsteine auf dem Friedhof {ort}? Maße, Material, Genehmigung und Fristen – verständlich zusammengefasst vom Steinmetz aus Lehsen."
        if len(desc) > 158:
            desc = desc.replace("verständlich zusammengefasst", "zusammengefasst")
    full_title = f"{h1} – Grabmal-Regeln"
    if len(full_title) > 60:
        full_title = h1
    schema = [{"@context": "https://schema.org", "@type": "Article", "headline": h1, "alternativeHeadline": d.get("titel"),
               "description": desc, "dateModified": "2026-11-15", "datePublished": "2026-11-14", "inLanguage": "de",
               "author": {"@type": "Organization", "name": NAME, "url": SITE + "/"},
               "publisher": {"@type": "Organization", "name": NAME},
               "isBasedOn": src, "about": {"@type": "Place", "name": f"Friedhof {ort}"},
               "mainEntityOfPage": SITE + "/" + satz_url(sid)}]
    crumbs = [("Start", ""), ("Ratgeber", "ratgeber.html"), ("Friedhofssatzungen", "friedhofssatzungen.html"), (ort, satz_url(sid))]
    return page(satz_url(sid), h1, desc, body, "friedhofssatzungen.html", prefix="../", crumbs=crumbs, schema=schema, full_title=full_title)


def satz_aside(d):
    kontakt = d.get("kontakt") or ""
    return f"""<aside class="satz-aside">
    <div class="satz-box">
      <h2 class="box-title">Friedhofsverwaltung</h2>
      <p>{esc(kontakt) if kontakt else "Siehe Original-Satzung."}</p>
    </div>
    <div class="satz-box satz-box-dark">
      <h2 class="box-title">Grabmal für diesen Friedhof?</h2>
      <p>Wir beraten Sie zu den Vorgaben, erstellen den Entwurf und stellen den Genehmigungsantrag für Sie.</p>
      <a class="btn" href="kontakt.html">Termin anfragen</a>
      <p style="margin-top:14px"><a href="tel:{PHONE_HREF}">{PHONE_SHOW}</a></p>
    </div>
    <div class="satz-box">
      <h2 class="box-title">Gut zu wissen</h2>
      <p>Diese Zusammenfassung haben wir mit größter Sorgfalt für Sie erstellt. Verbindlich ist allein die offizielle Satzung des Friedhofsträgers. Bei Fragen beraten wir Sie gern persönlich.</p>
    </div>
  </aside>"""


GENERIC_ALT = re.compile(r"– Beispiel \d+$")


def strip_tags(h):
    import html as _h
    h = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def build_search_index(files):
    """Suchindex für die Lupe im Header (wird erst beim ersten Öffnen geladen)."""
    import html as _h
    from collections import Counter
    pages = []
    for f in files:
        if SITEMAP_META.get(f, {}).get("noindex"):
            continue
        html = (ROOT / f).read_text(encoding="utf-8")
        main = html.split('<main id="inhalt">', 1)[1].split("</main>", 1)[0]
        main = re.sub(r'<div class="crumbs">.*?</div>|<nav class="subnav".*?</nav>|<section class="cta">.*?</section>', " ", main, flags=re.S)
        chunks = list(dict.fromkeys(c for c in (strip_tags(m[2]) for m in re.finditer(r"<(p|li|h2|h3|dt|dd|summary|figcaption)\b[^>]*>(.*?)</\1>", main, re.S)) if c))
        pages.append((f, html, main, chunks))
    # Textbausteine, die auf vielen Seiten gleich sind (Karten, Hinweise), nicht indexieren
    freq = Counter(c for *_, chunks in pages for c in chunks)
    entries = []
    for f, html, main, chunks in pages:
        own = [c for c in chunks if freq[c] < 4]
        h1 = strip_tags((re.search(r"<h1[^>]*>(.*?)</h1>", main, re.S) or [None, f])[1])
        h1 = re.sub(r"\s+([.,;:!?])", r"\1", h1)
        desc = _h.unescape(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))
        heads = [x for x in (strip_tags(x) for x in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", main, re.S)) if freq[x] < 4]
        alts = sorted({_h.unescape(a) for a in re.findall(r'alt="([^"]+)"', main)})
        alts = [a for a in alts if not GENERIC_ALT.search(a)] + sorted({GENERIC_ALT.sub("", a).strip() for a in alts if GENERIC_ALT.search(a)})
        kind = "Friedhofssatzung" if f.startswith("friedhofssatzungen/") else ("Rechtliches" if f in ("impressum.html", "datenschutz.html") else "Seite")
        lead = strip_tags((re.search(r'<p class="lead">(.*?)</p>', main, re.S) or [None, ""])[1])
        entries.append({"t": h1, "u": f, "s": kind, "d": lead or desc, "h": " · ".join(heads), "a": " · ".join(alts), "x": " ".join([desc] + own)})
    for q, a, _ in FAQ:
        entries.append({"t": q, "u": f"ratgeber.html#frage-{slug(q)}", "s": "Häufige Frage", "d": strip_tags(a)[:160], "x": strip_tags(a)})
    for st in STONES:
        entries.append({"t": st["name"], "u": f"steinsorten.html#stein-{slug(st['name'])}", "s": "Steinsorte",
                        "d": f'{st["art"]} aus {st["herkunft"]} – {st["farbe"]}', "x": st["text"]})
    seen = set()
    for e in SEARCH:
        u = e["u"] if not e["u"].startswith("#") else "friedhofssatzungen.html" + e["u"]
        if (e["n"], u) in seen:
            continue
        seen.add((e["n"], u))
        entries.append({"t": e["n"], "u": u, "s": "Ort", "d": e["sub"], "h": e["k"]})
    data = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "suche.json").write_text(data, encoding="utf-8")
    ver = v("suche.json")
    for f in files + ["404.html"]:
        fp = ROOT / f
        if fp.exists():
            t = fp.read_text(encoding="utf-8")
            if "__SUCHINDEX__" in t:
                fp.write_text(t.replace("__SUCHINDEX__", ver), encoding="utf-8")
    return len(entries), len(data)


def build_sitemap(files):
    import datetime
    today = datetime.date.today().isoformat()
    urls = []
    for f in files:
        if SITEMAP_META.get(f, {}).get("noindex"):
            continue
        loc = SITE + "/" + ("" if f == "index.html" else f)
        prio = "1.0" if f == "index.html" else ("0.3" if f in ("impressum.html",) else ("0.6" if f.startswith("friedhofssatzungen/") else "0.8"))
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{prio}</priority></url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n",
        encoding="utf-8",
    )


def build_htaccess():
    csp = ("default-src 'self'; "
           f"script-src 'self' '{WINTER_HASH}' 'unsafe-inline'; "
           "style-src 'self' 'unsafe-inline'; "
           "img-src 'self' data: https://tile.openstreetmap.org; "
           "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; "
           "form-action 'self'; frame-ancestors 'self'; upgrade-insecure-requests")
    (ROOT / ".htaccess").write_text(f"""# grabmale.lionify.de – wird von scripts/build.py erzeugt, nicht von Hand bearbeiten

RewriteEngine On
# www auf Hauptadresse umleiten
RewriteCond %{{HTTP_HOST}} ^www\\.(.+)$ [NC]
RewriteRule ^ https://%1%{{REQUEST_URI}} [L,R=301]
# HTTPS erzwingen
RewriteCond %{{HTTPS}} !=on
RewriteRule ^ https://%{{HTTP_HOST}}%{{REQUEST_URI}} [L,R=301]

# Interne Dateien sperren
<FilesMatch "^\\.ftp-deploy-sync-state\\.json$|\\.(md|py|sh|sql)$">
  Require all denied
</FilesMatch>

Options -Indexes
ErrorDocument 404 /404.html
AddDefaultCharset UTF-8
AddType image/webp .webp
AddType application/manifest+json .webmanifest

<IfModule mod_headers.c>
  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
  Header always set Content-Security-Policy "{csp}"
  Header always set Cross-Origin-Opener-Policy "same-origin"
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
  # versionierte Dateien (?v=…) dürfen lange gecacht werden
  <FilesMatch "\\.(css|js)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\\.(jpe?g|webp|png|svg)$">
    Header set Cache-Control "public, max-age=31536000"
  </FilesMatch>
  <FilesMatch "\\.html$">
    Header set Cache-Control "no-cache"
  </FilesMatch>
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/xml application/json application/manifest+json
</IfModule>
""", encoding="utf-8")


def build_manifest():
    (ROOT / "site.webmanifest").write_text(json.dumps({
        "name": NAME, "short_name": "Grabmale Lehsen", "lang": "de", "start_url": "/",
        "display": "browser", "background_color": "#f6f4f0", "theme_color": "#26282b",
        "icons": [{"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
                  {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    CSS = css_min()
    SATZ.update(load_satzungen())
    files = [build_index(), build_overview()]
    files += [build_category(c) for c in CATEGORIES]
    files += [build_references(), build_faq(), build_satzungen(), build_stones(), build_directions(), build_contact(), build_imprint(), build_privacy()]
    files += [build_satzung_page(d) for d in SATZ.values()]
    n, size = build_search_index(files)
    print(f"Suchindex: {n} Einträge, {size // 1024} KB")
    build_sitemap(files)
    build_htaccess()
    build_manifest()
    print("Erstellt:", ", ".join(files), "+ sitemap.xml")
