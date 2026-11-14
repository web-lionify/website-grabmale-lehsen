#!/usr/bin/env python3
"""Erzeugt die statischen HTML-Seiten von grabmale.lionify.de.

Aufruf (im Repo-Ordner):  python3 scripts/build.py
Kopf, Navigation und Fußzeile stehen hier zentral, damit alle Seiten gleich bleiben.
Bilder liegen in img/<kategorie>/<kategorie>-NN.jpg (groß) und -NN-k.jpg (Vorschau).
"""
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

NAV = [
    ("index.html", "Start"),
    ("grabmale.html", "Grabmale"),
    ("referenzen.html", "Referenzen"),
    ("index.html#ablauf", "Ablauf"),
]

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
        "intro": "Bei der Gestaltung einer Grabstätte haben Angehörige viele Möglichkeiten – von der schlichten Grabtafel bis zur vollständigen, individuellen Grabanlage.",
        "text": [
            "Ob Grabtafel, Kissenstein, Standstein oder eine individuelle Grabanlage mit Grabsteineinfassung und Abdeckung: Mit Grablichtern, Grabvasen und weiterem Zubehör sind der Vielfalt kaum Grenzen gesetzt.",
            "Gerne fertigen wir eine Grabanlage nach Ihren Wünschen und Vorstellungen an – und beraten Sie dabei ausführlich.",
        ],
    },
]


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
        cur = ' aria-current="page"' if current == href else ""
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
<link rel="stylesheet" href="style.css">
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
        </ul>
      </div>
      <div>
        <h4>Grabmale</h4>
        <ul>
          {"".join(f'<li><a href="{c["slug"]}.html">{c["title"]}</a></li>' for c in CATEGORIES)}
          <li><a href="referenzen.html">Referenzen</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> {NAME} – {OWNER}</span>
      <span><a href="impressum.html">Impressum</a> · <a href="datenschutz.html">Datenschutz</a></span>
    </div>
  </div>
</footer>
<script src="main.js" defer></script>
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
    <div class="prose">{paras}</div>
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
  <li>Es werden keine Schriften, Karten oder Skripte von fremden Servern geladen.</li>
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
<p>Auf der Kontaktseite verlinken wir zur Routenplanung auf OpenStreetMap. Die Karte wird nicht in unsere Website eingebunden; erst wenn Sie den Link anklicken, wird die Seite von OpenStreetMap geöffnet und es gelten deren Datenschutzbestimmungen.</p>

<h2>7. Ihre Rechte</h2>
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

<h2>8. Beschwerderecht bei der Aufsichtsbehörde</h2>
<p>Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren. Zuständig für uns ist der Landesbeauftragte für Datenschutz und Informationsfreiheit Mecklenburg-Vorpommern, Werderstraße 74a, 19055 Schwerin.</p>
</div></section>"""
    return page("datenschutz.html", "Datenschutzerklärung", f"Datenschutzerklärung von {NAME}.", body)


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
    files += [build_references(), build_contact(), build_imprint(), build_privacy()]
    build_sitemap(files)
    print("Erstellt:", ", ".join(files), "+ sitemap.xml")
