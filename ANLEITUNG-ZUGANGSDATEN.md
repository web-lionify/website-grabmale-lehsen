# Anleitung: SSH-Deploy für grabmale-aus-lehsen.de einrichten

| Ziel | Domain | Ordner auf dem Server | Branch |
|---|---|---|---|
| Staging | staging.grabmale-aus-lehsen.de | `/webseite/staging/` | `staging` |
| Produktiv | grabmale-aus-lehsen.de | `/webseite/produktiv/` | `main` |

## 1. Hosting vorbereiten (Kundenmenü des Hosters)
1. Domain `grabmale-aus-lehsen.de` auf den Ordner `/webseite/produktiv/` zeigen lassen.
2. Subdomain `staging.grabmale-aus-lehsen.de` anlegen, Ziel `/webseite/staging/`.
3. Für beide ein SSL-Zertifikat (Let's Encrypt) aktivieren.
4. SSH-Zugang aktivieren und notieren: **Server**, **Benutzer**, **Port**.
   Die SSH-Fingerabdrücke des Servers (meist in der Doku/Willkommens-Mail) bereithalten.
5. Die Ordner `/webseite/staging/` und `/webseite/produktiv/` sind die Pfade aus KAS-Sicht. Per SSH liegen sie
   relativ zum Login-Verzeichnis (`webseite/staging/`). So sind sie in `scripts/deploy.sh` (`PFAD_STANDARD`) eingetragen.
   Der Ordner `webseite` muss existieren, sonst bricht der Upload ab.

## 2. Secrets und GitHub-Umgebungen anlegen (einmalig)
**Windows (PowerShell)** im Repo-Ordner:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup-secrets.ps1
```
Optional direkt mit Angaben: `-SshHost ssh.example.de -SshUser web123 -SshPort 22`.
Mit `-DryRun` werden nur der Schlüssel erzeugt und die Fingerabdrücke angezeigt, in GitHub ändert sich nichts.

**macOS/Linux/Git Bash:** `./scripts/setup-secrets.sh`

Das Script
- erzeugt einen eigenen SSH-Schlüssel nur für GitHub Actions,
- liest den Server-Fingerabdruck (bitte vergleichen),
- legt die Secrets `SSH_HOST`, `SSH_PORT`, `SSH_USER`, `SSH_PRIVATE_KEY`, `SSH_KNOWN_HOSTS` an,
- legt die Umgebungen `staging` und `production` an (`production` nur von `main`, mit Freigabe).

## 3. Öffentlichen Schlüssel auf dem Server eintragen
Das Script gibt am Ende den öffentlichen Schlüssel aus (PowerShell: auch in der Zwischenablage)
und bietet an, ihn per SSH mit Passwort direkt einzutragen.
Er muss in `~/.ssh/authorized_keys` des SSH-Benutzers (oder im Kundenmenü unter „SSH-Schlüssel“).

## 4. Branch `staging` anlegen und testen
```bash
git switch -c staging main
```
```bash
git push -u origin staging
```
Erst einmal trocken: GitHub → **Actions → Deploy grabmale-aus-lehsen.de → Run workflow**,
Branch `staging`, Ziel `staging`, **dry-run** anhaken. Im Log steht, welche Dateien übertragen würden.
Danach ohne dry-run ausführen und https://staging.grabmale-aus-lehsen.de prüfen.

## 5. Live gehen
Nach Freigabe durch den Kunden `staging` in `main` mergen und pushen. Der Job wartet in GitHub
auf die Freigabe („Review deployments“) und lädt dann nach `/webseite/produktiv/` hoch.

## Fehlersuche
- `Permission denied (publickey)`: Schlüssel nicht in `authorized_keys` oder falscher Benutzer.
- `Host key verification failed`: `SSH_KNOWN_HOSTS` passt nicht → Script erneut ausführen.
- `rsync: command not found` (auf dem Server): Hoster bietet kein rsync – beim Hoster nachfragen.
- `No such file or directory` beim Zielordner: Pfad aus SSH-Sicht prüfen (Schritt 1.5).
