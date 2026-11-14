# Webseite grabmale.lionify.de

Statische Webseite, gehostet bei all-inkl. Repo: web-lionify/website-grabmale-lehsen

## Deployment
- **Kein Staging.** Es gibt nur den Branch `main`. Jeder Push auf `main` geht sofort live auf grabmale.lionify.de.
- Upload per **FTPS** über GitHub Actions (`.github/workflows/deploy.yml`, SamKirkland/FTP-Deploy-Action).
  Es werden nur geänderte Dateien hochgeladen (Sync-Stand in `.ftp-deploy-sync-state.json` auf dem Server).
- Zugangsdaten liegen als Repository-Secrets: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`, `FTP_SERVER_DIR`.
  Einrichten mit `scripts/setup-secrets.sh`.

## Arbeitsweise
1. Änderungswünsche werden **nicht sofort umgesetzt**, sondern erst besprochen und in einer Liste gesammelt.
2. Erst wenn ausdrücklich gesagt wird „Liste abarbeiten“, werden die Punkte umgesetzt.
3. Danach Commit und Push auf `main` (= live, da kein Staging). Vor dem Push kurz zusammenfassen, was live geht.
