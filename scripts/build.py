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
]
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
    "image": SITE + "/img/breitsteine/breitsteine-03.jpg",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": STREET,
        "postalCode": "19243",
        "addressLocality": "Wittenburg OT Lehsen",
        "addressRegion": "Mecklenburg-Vorpommern",
        "addressCountry": "DE",
    },
    "areaServed": "Westmecklenburg",
}


def page(filename, title, description, body, current=None, head_extra=""):
    nav_html = []
    for href, label in NAV:
        cur = ' aria-current="page"' if current == href or (href == "ratgeber.html" and current in RATGEBER_PAGES) else ""
        nav_html.append(f'<a href="{href}"{cur}>{label}</a>')
    cur = ' aria-current="page"' if current == "kontakt.html" else ""
    nav_html.append(f'<a class="nav-cta" href="kontakt.html"{cur}>Kontakt</a>')
    full_title = f"{title} | {NAME}" if title != NAME else f"{NAME} – Grabmale & Grabsteine bei Wittenburg"
    canonical = SITE + "/" + ("" if filename == "index.html" else filename)
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/img/breitsteine/breitsteine-03.jpg">
<meta property="og:locale" content="de_DE">
<meta name="theme-color" content="#26282b">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{v('style.css')}">
{head_extra}</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<div class="notice" id="winter" hidden>
  <div class="wrap"><strong>Winterrabatt</strong><span>In den Wintermonaten bieten wir attraktive Rabatte auf Natursteine und Zubehör.</span><a href="kontakt.html">Unverbindliches Angebot anfragen</a></div>
</div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html"><strong>{NAME}</strong><span>{OWNER} · Steinmetz</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav"><span></span>Menü</button>
    <nav class="nav" id="nav" aria-label="Hauptnavigation">
      {chr(10).join("      " + n if i else n for i, n in enumerate(nav_html))}
    </nav>
  </div>
</header>
<main id="inhalt">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="index.html"><strong>{NAME}</strong><span>{OWNER} · Steinmetz</span></a>
        <p style="margin-top:16px">Grabmale, Grabsteine und Grabanlagen aus Naturstein – mit persönlicher Beratung und eigener Ausstellung in Lehsen.</p>
      </div>
      <div>
        <h4>Kontakt</h4>
        <ul>
          <li>{STREET}<br>{ZIP_CITY}</li>
          <li><a href="tel:{PHONE_HREF}">{PHONE_SHOW}</a></li>
          <li><a href="mailto:{MAIL}">{MAIL}</a></li>
          <li>{HOURS}</li>
          <li><a href="{EBAY_URL}" target="_blank" rel="noopener">Online-Shop bei eBay ↗</a></li>
        </ul>
      </div>
      <div>
        <h4>Grabmale</h4>
        <ul>
          {"".join(f'<li><a href="{c["slug"]}.html">{c["title"]}</a></li>' for c in CATEGORIES)}
          <li><a href="referenzen.html">Referenzen</a></li>
        </ul>
        <h4 style="margin-top:22px">Ratgeber</h4>
        <ul>
          <li><a href="ratgeber.html">Häufige Fragen</a></li>
          <li><a href="friedhofssatzungen.html">Friedhofssatzungen</a></li>
          <li><a href="steinsorten.html">Steinsorten</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> {NAME} – {OWNER}</span>
      <span><a href="impressum.html">Impressum</a> · <a href="datenschutz.html">Datenschutz</a></span>
    </div>
  </div>
</footer>
<script src="{v('main.js')}" defer></script>
</body>
</html>
"""
    (ROOT / filename).write_text(html, encoding="utf-8")
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
      <img src="img/breitsteine/breitsteine-03.jpg" alt="Ausstellung mit Grabsteinen aus verschiedenen Graniten in Lehsen" width="960" height="367" fetchpriority="high">
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

{cta()}
<script type="application/ld+json">{json.dumps(LOCAL_BUSINESS, ensure_ascii=False)}</script>"""
    return page("index.html", NAME,
                "Grabmale aus Lehsen – Steinmetz Bernhard Gerdes bei Wittenburg: Grabsteine, Stelen, Liegesteine und Grabanlagen aus Naturstein. Persönliche Beratung und Ausstellung, auch abends und samstags.",
                body, "index.html")


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
                "Breitsteine, Reihensteine, Stelen, Liegesteine und Grabanlagen aus Naturstein – Beispiele und Beratung bei Grabmale aus Lehsen.",
                body, "grabmale.html")


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
{cta()}"""
    return page(f'{c["slug"]}.html', c["title"],
                f'{c["title"]} aus Naturstein von Grabmale aus Lehsen: {c["short"]} Beispiele, Gestaltung und persönliche Beratung bei Wittenburg.',
                body, "grabmale.html")


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
                "Referenzen von Grabmale aus Lehsen: gefertigte und aufgestellte Grabmale auf Friedhöfen in Westmecklenburg.",
                body, "referenzen.html")


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
        <li><small>Anfahrt</small>Lehsen liegt direkt bei Wittenburg, nur wenige Minuten von der A24 (Anschlussstelle Wittenburg) entfernt – aus Schwerin, Hagenow und Hamburg gut erreichbar.</li>
        <li><small>Online-Shop</small><a href="{EBAY_URL}" target="_blank" rel="noopener">Liegesteine &amp; Grabherzen bei eBay ↗</a></li>
      </ul>
      <a class="btn btn-ghost" href="{MAP_URL}" target="_blank" rel="noopener">Route planen (OpenStreetMap)</a>
      <p class="muted" style="font-size:.85rem;margin-top:10px">Der Link öffnet OpenStreetMap in einem neuen Fenster.</p>
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
                body, "kontakt.html")


def build_imprint():
    body = f"""<section class="page-head"><div class="wrap"><h1>Impressum</h1></div></section>
<section class="section"><div class="wrap prose">
<h2>Angaben gemäß § 5 DDG</h2>
<p>{OWNER}<br>{NAME} – Schrift im Stein<br>{STREET}<br>{ZIP_CITY}</p>
<h2>Kontakt</h2>
<p>Telefon: <a href="tel:{PHONE_HREF}">{PHONE}</a><br>Telefax: {PHONE}<br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></p>
<h2>Umsatzsteuer</h2>
<p>Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br>DE246444446</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Inhalte</h2>
<p>Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden entsprechender Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.</p>
<h2>Haftung für Links</h2>
<p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar. Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.</p>
<h2>Urheberrecht</h2>
<p>Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten – insbesondere Texte und Fotos – unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter beachtet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, bitten wir um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Inhalte umgehend entfernen.</p>
</div></section>"""
    return page("impressum.html", "Impressum", f"Impressum von {NAME} – {OWNER}, {ZIP_CITY}.", body)


def build_privacy():
    body = f"""<section class="page-head"><div class="wrap"><h1>Datenschutzerklärung</h1><p class="lead">Stand: November 2026</p></div></section>
<section class="section"><div class="wrap prose">
<h2>1. Verantwortlicher</h2>
<p>Verantwortlich für die Datenverarbeitung auf dieser Website ist:<br>{OWNER}, {NAME} – Schrift im Stein<br>{STREET}, {ZIP_CITY}<br>Telefon: {PHONE}<br>E-Mail: <a href="mailto:{MAIL}">{MAIL}</a></p>

<h2>2. Das Wichtigste in Kürze</h2>
<ul>
  <li>Diese Website verwendet <strong>keine Cookies</strong>, keine Analyse- oder Tracking-Werkzeuge und keine Social-Media-Plugins.</li>
  <li>Es werden keine Schriften oder Skripte von fremden Servern geladen. Die Karte auf der Seite „Friedhofssatzungen“ lädt erst, wenn Sie dem ausdrücklich zustimmen (siehe Abschnitt 7).</li>
  <li>Personenbezogene Daten verarbeiten wir nur, wenn Sie uns über das Kontaktformular, per E-Mail oder telefonisch kontaktieren, sowie in technisch notwendigen Server-Logdateien.</li>
</ul>

<h2>3. Hosting und Server-Logdateien</h2>
<p>Diese Website wird bei der ALL-INKL.COM – Neue Medien Münnich, Inh. René Münnich, Hauptstraße 68, 02742 Friedersdorf, gehostet. Beim Aufruf der Website erhebt der Server automatisch Informationen, die Ihr Browser übermittelt (Server-Logdateien): IP-Adresse, Datum und Uhrzeit des Zugriffs, aufgerufene Seite, übertragene Datenmenge, Referrer-URL, Browsertyp und Betriebssystem.</p>
<p>Diese Daten werden ausschließlich benötigt, um die Website sicher und stabil bereitzustellen, und nicht mit anderen Daten zusammengeführt. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO; unser berechtigtes Interesse liegt im sicheren Betrieb der Website. Mit dem Hoster besteht ein Vertrag zur Auftragsverarbeitung gemäß Art. 28 DSGVO. Die Logdateien werden nach kurzer Zeit automatisch gelöscht.</p>

<h2>4. SSL-/TLS-Verschlüsselung</h2>
<p>Diese Seite nutzt aus Sicherheitsgründen eine SSL-/TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie an „https://“ in der Adresszeile Ihres Browsers.</p>

<h2>5. Kontaktformular, E-Mail und Telefon</h2>
<p>Wenn Sie uns über das Kontaktformular, per E-Mail oder telefonisch kontaktieren, verarbeiten wir Ihre Angaben (Name, E-Mail-Adresse, ggf. Telefonnummer, Ihr Anliegen und Ihre Nachricht) ausschließlich zur Bearbeitung Ihrer Anfrage und für mögliche Anschlussfragen. Die Nachricht aus dem Kontaktformular wird per E-Mail an uns übermittelt; sie wird nicht in einer Datenbank auf dem Webserver gespeichert.</p>
<p>Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO, sofern Ihre Anfrage mit der Anbahnung oder Erfüllung eines Vertrages zusammenhängt, und im Übrigen Art. 6 Abs. 1 lit. a DSGVO (Einwilligung) bzw. lit. f DSGVO (berechtigtes Interesse an der Beantwortung von Anfragen). Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft widerrufen.</p>
<p>Ihre Daten werden gelöscht, sobald Ihre Anfrage abschließend bearbeitet ist und keine gesetzlichen Aufbewahrungspflichten (z. B. bei Angeboten und Aufträgen) entgegenstehen. Eine Weitergabe an Dritte findet nicht statt.</p>

<h2>6. Externe Links</h2>
<p>Unsere Website enthält Links zu externen Angeboten, unter anderem zu unserem Shop bei eBay, zur Routenplanung bei OpenStreetMap sowie zu Satzungen und Informationen von Städten, Ämtern, Kirchengemeinden und Verbänden. Diese Inhalte werden nicht in unsere Website eingebunden; beim bloßen Aufruf unserer Seiten werden keine Daten an diese Anbieter übertragen. Erst wenn Sie einen Link anklicken, wird die jeweilige Seite geöffnet und es gelten die Datenschutzbestimmungen des jeweiligen Anbieters.</p>

<h2 id="karte">7. Karte (OpenStreetMap)</h2>
<p>Auf der Seite „Friedhofssatzungen“ bieten wir eine interaktive Karte an. Die Kartendarstellung (Kartenkacheln) wird von der OpenStreetMap Foundation (OSMF), St John’s Innovation Centre, Cowley Road, Cambridge, CB4 0WS, Großbritannien, geladen. Die Programmbibliothek für die Karte (Leaflet) liegt auf unserem eigenen Server.</p>
<p>Die Karte wird <strong>erst geladen, wenn Sie auf „Karte laden“ klicken</strong>. Erst dann stellt Ihr Browser eine Verbindung zu den Servern von OpenStreetMap her; dabei werden insbesondere Ihre IP-Adresse, der angefragte Kartenausschnitt sowie technische Angaben Ihres Browsers übertragen. Rechtsgrundlage ist Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO und § 25 Abs. 1 TDDDG. Für das Vereinigte Königreich besteht ein Angemessenheitsbeschluss der EU-Kommission.</p>
<p>Wenn Sie „Karte künftig immer laden“ auswählen, wird diese Entscheidung ausschließlich lokal in Ihrem Browser gespeichert (Local Storage) und nicht an uns übertragen. Sie können die Einwilligung jederzeit widerrufen, indem Sie die gespeicherten Websitedaten in Ihrem Browser löschen. Weitere Informationen: <a href="https://osmfoundation.org/wiki/Privacy_Policy" target="_blank" rel="noopener">Datenschutzerklärung der OpenStreetMap Foundation</a>.</p>

<h2>8. Ihre Rechte</h2>
<p>Sie haben im Rahmen der gesetzlichen Bestimmungen jederzeit das Recht auf:</p>
<ul>
  <li>Auskunft über Ihre gespeicherten personenbezogenen Daten (Art. 15 DSGVO),</li>
  <li>Berichtigung unrichtiger Daten (Art. 16 DSGVO),</li>
  <li>Löschung (Art. 17 DSGVO) und Einschränkung der Verarbeitung (Art. 18 DSGVO),</li>
  <li>Datenübertragbarkeit (Art. 20 DSGVO),</li>
  <li>Widerspruch gegen die Verarbeitung auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO (Art. 21 DSGVO),</li>
  <li>Widerruf einer erteilten Einwilligung mit Wirkung für die Zukunft (Art. 7 Abs. 3 DSGVO).</li>
</ul>
<p>Wenden Sie sich dazu einfach an die oben genannten Kontaktdaten.</p>

<h2>9. Beschwerderecht bei der Aufsichtsbehörde</h2>
<p>Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren. Zuständig für uns ist der Landesbeauftragte für Datenschutz und Informationsfreiheit Mecklenburg-Vorpommern, Werderstraße 74a, 19055 Schwerin.</p>
</div></section>"""
    return page("datenschutz.html", "Datenschutzerklärung", f"Datenschutzerklärung von {NAME}.", body)


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
        items.append(f"""<article class="stone">
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
                body, "steinsorten.html")


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
        items.append(f"""<details{" open" if i == 1 else ""}>
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
{cta("Noch Fragen?", "Wir beraten Sie persönlich – auch zur Friedhofssatzung und zur Genehmigung.")}
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>"""
    return page("ratgeber.html", "Ratgeber Grabmal",
                "Ratgeber Grabmal: Wann darf der Grabstein gesetzt werden, welche Genehmigung braucht es, was gilt zu Kinderarbeit in MV, wovon hängt der Preis ab?",
                body, "ratgeber.html")


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
        ("Wittendörp", "ca. 5 km", "Gemeindliche Satzung; Döbbersen, Lassahn und Neuenkirchen sind kirchlich.", [
            ("Ortsrecht der Gemeinde", "https://www.amt-wittenburg.de/Verwaltung-Aktuelles/Ortsrecht-Wittend%C3%B6rp/"),
            ("Kirchengemeinde Döbbersen", f"{KM}/doebbersen/friedhof")]),
        ("Zarrentin am Schaalsee und Amt Zarrentin", "ca. 8 km", "Stadtfriedhof: Ev.-Luth. Kirchengemeinde. Gemeindliche Satzungen u. a. für Gallin und Vellahn.", [
            ("Friedhofsordnung Zarrentin", f"{KM}/fileadmin/Mecklenburg/Friedhofsverwaltung/Propstei_Parchim/Zarrentin/251118_Friedhofsordnung_Zarrentin.pdf"),
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
    ]),
    ("Kreis Herzogtum Lauenburg (Schleswig-Holstein)", [
        ("Mölln", "ca. 26 km", "Friedhof der Ev.-Luth. Kirchengemeinde Mölln.", [
            ("Friedhofssatzung Mölln", "https://www.friedhof-moelln.de/assets/friedhofssatzung-ab-2022.pdf")]),
        ("Güster (Amt Büchen)", "ca. 27 km", "", [
            ("Friedhofssatzung Güster", "https://www.amt-buechen.de/fileadmin/user_upload/public/downloads/orts_verbandsrecht/guester/nutzung_oeffentlicher_einrichtungen/Satzung_Friedhofs-_u._Bestattungswesen.pdf")]),
        ("Grambek (Amt Breitenfelde)", "ca. 28 km", "", [
            ("Friedhofssatzung Grambek", "https://www.grambek.de/fileadmin/download/gemeinden/grambek/ortsrecht/finanzen/satzung_%C3%BCber_das_friedhofs-_und_bestattungswesen_in_der_gemeinde_grambek.pdf")]),
        ("Amt Lauenburgische Seen", "18–30 km", "Keine Satzungen online – die Friedhöfe sind überwiegend kirchlich. Bitte bei der Kirchengemeinde erfragen.", []),
    ]),
]


MARKERS = []
ORTE = json.loads((ROOT / "scripts" / "orte.json").read_text(encoding="utf-8"))

# Welche Orte (Kartenpunkte) gehören zu welchem Eintrag. Zweiter Wert: Linktext,
# der für diesen Ort gilt (None = alle Links des Eintrags).
ENTRY_ORTE = {
    "Wittenburg": [("Wittenburg", None), ("Zühr", "Städtische Satzung (Zühr)"), ("Körchow", "Friedhofsordnung Körchow, Camin, Marsow"),
                   ("Camin", "Friedhofsordnung Körchow, Camin, Marsow"), ("Marsow", "Friedhofsordnung Körchow, Camin, Marsow")],
    "Wittendörp": [("Wittendörp", None), ("Döbbersen", "Kirchengemeinde Döbbersen"), ("Lassahn", "Kirchengemeinde Döbbersen")],
    "Zarrentin am Schaalsee und Amt Zarrentin": [("Zarrentin am Schaalsee", "Friedhofsordnung Zarrentin"), ("Gallin", "Satzungen des Amtes"), ("Vellahn", "Satzungen des Amtes")],
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
    "Amt Lauenburgische Seen": [("Gudow", None)],
}


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
            search = " ".join([name, note] + [o for o, _ in orte] + [t for t, _ in links]).lower()
            for o, lbl in orte:
                if ORTE.get(o):
                    ll = [(t, u) for t, u in links if lbl is None or t == lbl]
                    MARKERS.append({"n": o, "e": name, "id": eid, "p": ORTE[o], "l": ll})
            if links:
                lk = "<br>".join(f'<a class="dl" href="{u}" target="_blank" rel="noopener">{t} ↗</a>' for t, u in links)
            else:
                lk = '<span class="none">nicht online</span>'
            many = len(links) > 4
            if many:
                lk = " ".join(f'<a class="dl" href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in links)
            lis.append(f"""<li id="{eid}" data-search="{esc(search)}"{' class="many"' if many else ""}><div class="ort"><strong>{name} <span class="km">· {km}</span></strong>{f"<small>{note}</small>" if note else ""}</div><div class="links">{lk}</div></li>""")
        regions.append(f"""<div class="region" data-region><h2>{region}</h2><ul class="satzungen">{"".join(lis)}</ul></div>""")
    body = f"""<section class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Start</a> / <a href="ratgeber.html">Ratgeber</a> / Friedhofssatzungen</div>
    <h1>Friedhofssatzungen</h1>
    <p class="lead">Jeder Friedhof legt eigene Regeln für Grabmale fest. Hier finden Sie die Satzungen und Friedhofsordnungen im Umkreis von etwa 30 km um Lehsen – sortiert nach Landkreis und Entfernung.</p>
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
          <input id="ortsuche" type="search" placeholder="Ort eingeben, z. B. Hoort oder Zarrentin" autocomplete="off">
        </div>
        <p class="search-info" id="search-info" aria-live="polite"></p>
        <div class="quick" aria-label="Schnellauswahl">
          {"".join(f'<button type="button" data-quick="{q}">{q}</button>' for q in ("Wittenburg", "Hagenow", "Zarrentin", "Boizenburg", "Lübtheen", "Gadebusch", "Schwerin", "Mölln"))}
        </div>
        <p class="finder-hint">Tippen Sie den Namen Ihres Ortes ein oder klicken Sie auf einen Punkt in der Karte. Ein Klick auf einen Eintrag in der Liste zeigt ihn auf der Karte.</p>
        <p class="search-empty" id="search-empty" hidden>Kein passender Ort gefunden. <a href="kontakt.html">Fragen Sie uns</a> – wir helfen gern weiter.</p>
      </div>
      <div class="map-wrap">
        <div id="map" class="map" aria-label="Karte der Friedhöfe im Umkreis von 30 km um Lehsen"></div>
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
    <script>window.SATZUNG_MARKERS = {json.dumps(MARKERS, ensure_ascii=False)}; window.LEHSEN = {json.dumps(ORTE["Lehsen"])};</script>
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
                "Friedhofssatzungen und Friedhofsordnungen im Umkreis von 30 km um Wittenburg: Hagenow, Zarrentin, Boizenburg, Lübtheen, Gadebusch, Schwerin, Mölln und mehr.",
                body, "friedhofssatzungen.html")


def ratgeber_nav(active):
    pages = [("ratgeber.html", "Häufige Fragen"), ("friedhofssatzungen.html", "Friedhofssatzungen"), ("steinsorten.html", "Steinsorten")]
    return '<nav class="subnav" aria-label="Ratgeber">' + "".join(
        f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in pages
    ) + "</nav>"


def build_sitemap(files):
    urls = []
    for f in files:
        loc = SITE + "/" + ("" if f == "index.html" else f)
        prio = "1.0" if f == "index.html" else ("0.3" if f in ("impressum.html", "datenschutz.html") else "0.8")
        urls.append(f"  <url><loc>{loc}</loc><priority>{prio}</priority></url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    files = [build_index(), build_overview()]
    files += [build_category(c) for c in CATEGORIES]
    files += [build_references(), build_faq(), build_satzungen(), build_stones(), build_contact(), build_imprint(), build_privacy()]
    build_sitemap(files)
    print("Erstellt:", ", ".join(files), "+ sitemap.xml")
