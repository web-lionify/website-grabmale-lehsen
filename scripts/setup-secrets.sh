#!/usr/bin/env bash
# Legt die FTP-Zugangsdaten als GitHub-Secrets in der Umgebung "production" an.
# Voraussetzung: GitHub CLI (gh) installiert und per "gh auth login" angemeldet.
set -euo pipefail

REPO="web-lionify/website-grabmale-lehsen"
ENVIRONMENT="production"

command -v gh >/dev/null || { echo "Fehler: GitHub CLI (gh) fehlt. https://cli.github.com"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Fehler: Bitte zuerst 'gh auth login' ausführen."; exit 1; }

echo "Zugangsdaten für $REPO (Umgebung: $ENVIRONMENT)"
echo

read -r -p "FTP-Server (z. B. w0123456.kasserver.com): " FTP_SERVER
read -r -p "FTP-Benutzer (z. B. f0123456): " FTP_USERNAME
read -r -s -p "FTP-Passwort: " FTP_PASSWORD; echo
read -r -p "Zielordner auf dem Server (z. B. /grabmale.lionify.de/ – mit / am Ende): " FTP_SERVER_DIR

[[ -n "$FTP_SERVER" && -n "$FTP_USERNAME" && -n "$FTP_PASSWORD" && -n "$FTP_SERVER_DIR" ]] \
  || { echo "Fehler: Alle Felder müssen ausgefüllt sein."; exit 1; }

[[ "$FTP_SERVER_DIR" == */ ]] || FTP_SERVER_DIR="$FTP_SERVER_DIR/"

# Umgebung anlegen (falls noch nicht vorhanden)
gh api --method PUT "repos/$REPO/environments/$ENVIRONMENT" >/dev/null

set_secret() {
  printf '%s' "$2" | gh secret set "$1" --repo "$REPO" --env "$ENVIRONMENT"
}

set_secret FTP_SERVER     "$FTP_SERVER"
set_secret FTP_USERNAME   "$FTP_USERNAME"
set_secret FTP_PASSWORD   "$FTP_PASSWORD"
set_secret FTP_SERVER_DIR "$FTP_SERVER_DIR"

echo
echo "Fertig. Secrets in '$ENVIRONMENT':"
gh secret list --repo "$REPO" --env "$ENVIRONMENT"
