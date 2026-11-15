# Webseite grabmale.lionify.de

Statische Webseite, gehostet bei all-inkl. Repo: web-lionify/website-grabmale-lehsen

## Deployment
- **Kein Staging.** Es gibt nur den Branch `main`. Jeder Push auf `main` geht sofort live auf grabmale.lionify.de.
- Upload per **FTPS** über GitHub Actions (`.github/workflows/deploy.yml`, SamKirkland/FTP-Deploy-Action).
  Es werden nur geänderte Dateien hochgeladen (Sync-Stand in `.ftp-deploy-sync-state.json` auf dem Server).
- Zugangsdaten liegen als Repository-Secrets: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`, `FTP_SERVER_DIR`.
  Einrichten mit `scripts/setup-secrets.sh`.

## Aufbau
- Seiten werden mit `python3 scripts/build.py` erzeugt (Kopf, Navigation, Fußzeile und Texte zentral dort). HTML-Dateien nicht von Hand bearbeiten, sondern im Script ändern und neu bauen.
- `style.css` und `main.js` (Navigation, Lightbox, Winterrabatt Nov–Feb, Formular-Status) werden direkt bearbeitet.
- Bilder: `img/<kategorie>/<kategorie>-NN.jpg` (max. 1200 px) und `-NN-k.jpg` (Vorschau, max. 480 px). Neue Bilder einfach mit der nächsten Nummer ablegen und neu bauen.
- Kontaktformular: `kontakt.php` (PHP `mail()` an steine@online.de, Honeypot + Zeitprüfung). Lokal gibt es kein PHP, Test nur live.
- Friedhofssatzungen: Zusammenfassungen als JSON in `scripts/satzungen/<id>.json` (je Satzung eine Unterseite `friedhofssatzungen/<id>.html`), Koordinaten in `scripts/orte.json`, Zuordnung Ort → Satzung in `ORT_SATZUNG` (build.py). Jede Angabe mit §-Verweis; Stand der Prüfung: November 2026.
- Suche (Lupe im Header): Index `suche.json` wird von build.py aus den fertigen Seiten erzeugt (plus FAQ, Steinsorten, Orte), Logik in `main.js`. Textbausteine, die auf ≥ 4 Seiten gleich sind, werden nicht indexiert.
- Lokale Vorschau: `python3 -m http.server 8080` im Repo-Ordner.

## Arbeitsweise
1. Änderungswünsche werden **nicht sofort umgesetzt**, sondern erst besprochen und in einer Liste gesammelt.
2. Erst wenn ausdrücklich gesagt wird „Liste abarbeiten“, werden die Punkte umgesetzt.
3. Danach Commit und Push auf `main` (= live, da kein Staging). Vor dem Push kurz zusammenfassen, was live geht.
4. Fragen an Herrn Gerdes werden nicht sofort gestellt, sondern in `OFFENE-FRAGEN.md` gesammelt. Bei „offene Fragen beantworten“ alle Fragen daraus ausgeben.
