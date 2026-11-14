# Anleitung: Zugangsdaten für grabmale.lionify.de einrichten

## 1. Subdomain bei all-inkl anlegen
1. Im **KAS** anmelden: https://kas.all-inkl.com
2. **Domain → Subdomains → Neue Subdomain anlegen**
3. Subdomain: `grabmale`, Domain: `lionify.de`
4. Zielverzeichnis: `/grabmale.lionify.de/` (Vorschlag übernehmen und merken)
5. Unter **SSL-Schutz** für die Subdomain ein Let's-Encrypt-Zertifikat aktivieren.

## 2. Eigenen FTP-Benutzer anlegen
Nicht den Haupt-FTP-Zugang verwenden – ein eigener Benutzer, der nur den Webseiten-Ordner sieht, ist sicherer.

1. Im KAS: **FTP → Neuen FTP-Benutzer anlegen**
2. Kommentar: `GitHub Deploy grabmale`
3. Verzeichnis: `/grabmale.lionify.de/` (dasselbe wie bei der Subdomain)
4. Ein starkes Passwort vergeben (z. B. im Passwort-Manager erzeugen) und notieren.
5. Speichern. Notiere dir:
   - **FTP-Benutzer**, z. B. `f0123456`
   - **Server**, z. B. `w0123456.kasserver.com` (steht in der FTP-Übersicht / in der Willkommens-Mail)

> Wichtig: Weil der FTP-Benutzer auf `/grabmale.lionify.de/` beschränkt ist, ist das Zielverzeichnis
> aus seiner Sicht das Hauptverzeichnis. Beim Script also als Zielordner **`/`** eingeben.
> (Nur falls du doch den Haupt-FTP-Zugang nimmst: `/grabmale.lionify.de/` eingeben.)

## 3. GitHub CLI installieren und anmelden (einmalig)
```bash
brew install gh
```
```bash
gh auth login
```
(GitHub.com → HTTPS → im Browser anmelden.)

## 4. Secrets ins Repo eintragen
Im Repo-Ordner ausführen:
```bash
./scripts/setup-secrets.sh
```
Das Script fragt Server, Benutzer, Passwort und Zielordner ab und legt sie als Repository-Secrets an.

## 5. Ersten Deploy auslösen
- Entweder einen Commit auf `main` pushen, oder
- auf GitHub: **Actions → Deploy grabmale.lionify.de → Run workflow**

Danach https://grabmale.lionify.de aufrufen. Schlägt der Upload fehl, im Actions-Log nachsehen –
meist ist es ein falscher Server, ein falsches Passwort oder ein falscher Zielordner.
