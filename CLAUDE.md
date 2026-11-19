# Webseite grabmale-aus-lehsen.de

Statische Webseite (Webhosting mit SSH-Zugang). Repo: web-lionify/website-grabmale-lehsen

## Deployment (Staging + Produktiv)
| Ziel | Domain | Ordner auf dem Server | Branch |
|---|---|---|---|
| Staging | https://staging.grabmale-aus-lehsen.de | `/webseite/staging/` | `staging` |
| Produktiv | https://grabmale-aus-lehsen.de | `/webseite/produktiv/` | `main` |

- Upload per **rsync über SSH** aus GitHub Actions (`.github/workflows/deploy.yml` → `scripts/deploy.sh`).
  Es werden nur geänderte Dateien übertragen (`--checksum`), auf dem Server entfernte Dateien werden gelöscht (`--delete`).
  Was nicht hochgeladen wird: `scripts/deploy-exclude.txt`.
- Staging bekommt beim Upload automatisch `robots.txt` „Disallow: /“ und den Header `X-Robots-Tag: noindex`.
- Produktiv läuft über die GitHub-Umgebung `production` (Freigabe nötig, nur Branch `main`).
- Zugangsdaten als Repository-Secrets: `SSH_HOST`, `SSH_PORT`, `SSH_USER`, `SSH_PRIVATE_KEY`, `SSH_KNOWN_HOSTS`.
  Einrichten mit `scripts/setup-secrets.ps1` (Windows) bzw. `scripts/setup-secrets.sh` (Anleitung: `ANLEITUNG-ZUGANGSDATEN.md`).
- Manuell: GitHub → Actions → „Deploy grabmale-aus-lehsen.de“ → Run workflow (Ziel wählen, optional dry-run).

## Aufbau
- Seiten werden mit `python3 scripts/build.py` erzeugt (Kopf, Navigation, Fußzeile und Texte zentral dort). HTML-Dateien nicht von Hand bearbeiten, sondern im Script ändern und neu bauen.
- `style.css` und `main.js` (Navigation, Lightbox, Winterrabatt Nov–Feb, Formular-Status) werden direkt bearbeitet.
- Bilder: `img/<kategorie>/<kategorie>-NN.jpg` (max. 1200 px) und `-NN-k.jpg` (Vorschau, max. 480 px). Neue Bilder einfach mit der nächsten Nummer ablegen und neu bauen.
- Kontaktformular: `kontakt.php` (PHP `mail()` an steine@online.de, Honeypot + Zeitprüfung). Lokal gibt es kein PHP, Test auf Staging.
- Friedhofssatzungen: Zusammenfassungen als JSON in `scripts/satzungen/<id>.json` (je Satzung eine Unterseite `friedhofssatzungen/<id>.html`), Koordinaten in `scripts/orte.json`, Zuordnung Ort → Satzung in `ORT_SATZUNG` (build.py). Jede Angabe mit §-Verweis; Stand der Prüfung: November 2026.
- Suche (Lupe im Header): Index `suche.json` wird von build.py aus den fertigen Seiten erzeugt (plus FAQ, Steinsorten, Orte), Logik in `main.js`. Textbausteine, die auf ≥ 4 Seiten gleich sind, werden nicht indexiert.
- Lokale Vorschau: `python3 -m http.server 8080` im Repo-Ordner.

## Arbeitsweise
1. Änderungswünsche werden **nicht sofort umgesetzt**, sondern erst besprochen und in einer Liste gesammelt.
2. Erst wenn ausdrücklich gesagt wird „Liste abarbeiten“, werden die Punkte umgesetzt.
3. **Freigabe in drei Stufen** – nie direkt auf `main` pushen:
   1. **Lokal**: bauen (`python3 scripts/build.py`), Vorschau mit `python3 -m http.server 8080`, intern freigeben.
   2. **Staging**: Commit auf Branch `staging` pushen → automatisch auf staging.grabmale-aus-lehsen.de. Kunde prüft dort.
   3. **Live**: nach Kundenfreigabe `staging` in `main` mergen und pushen → Deploy-Job wartet auf Freigabe (GitHub-Umgebung `production`) → grabmale-aus-lehsen.de.
   Vor jedem Push kurz zusammenfassen, was auf Staging bzw. live geht.
4. Fragen an Herrn Gerdes werden nicht sofort gestellt, sondern in `OFFENE-FRAGEN.md` gesammelt. Bei „offene Fragen beantworten“ alle Fragen daraus ausgeben.
