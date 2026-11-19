#!/usr/bin/env bash
# Richtet den SSH/rsync-Deploy für grabmale-aus-lehsen.de ein (einmalig):
#  1. erzeugt einen eigenen SSH-Schlüssel nur für GitHub Actions
#  2. liest den Fingerabdruck des Servers (known_hosts)
#  3. legt die Repository-Secrets an: SSH_HOST, SSH_PORT, SSH_USER, SSH_PRIVATE_KEY, SSH_KNOWN_HOSTS
#  4. legt die GitHub-Umgebungen "staging" und "production" an (production mit Freigabe)
# Voraussetzung: GitHub CLI (gh) angemeldet ("gh auth login"), ssh-keygen und ssh-keyscan vorhanden
# (unter Windows: Git Bash).
set -euo pipefail

REPO="web-lionify/website-grabmale-lehsen"

command -v gh >/dev/null || { echo "Fehler: GitHub CLI (gh) fehlt. https://cli.github.com"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Fehler: Bitte zuerst 'gh auth login' ausführen."; exit 1; }
command -v ssh-keygen >/dev/null && command -v ssh-keyscan >/dev/null || { echo "Fehler: ssh-keygen/ssh-keyscan fehlen."; exit 1; }

echo "SSH-Deploy für $REPO"
echo "Staging:   staging.grabmale-aus-lehsen.de -> /webseite/staging/"
echo "Produktiv: grabmale-aus-lehsen.de         -> /webseite/produktiv/"
echo

read -r -p "SSH-Server (Hostname): " SSH_HOST
read -r -p "SSH-Benutzer: " SSH_USER
read -r -p "SSH-Port [22]: " SSH_PORT
SSH_PORT="${SSH_PORT:-22}"
[[ -n "$SSH_HOST" && -n "$SSH_USER" ]] || { echo "Fehler: Server und Benutzer sind Pflicht."; exit 1; }

# 1. Schlüssel (ohne Passphrase, nur für den Deploy)
KEYDIR="$(mktemp -d)"
trap 'rm -rf "$KEYDIR"' EXIT
ssh-keygen -q -t ed25519 -N "" -C "github-actions deploy grabmale-aus-lehsen" -f "$KEYDIR/deploy_key"

# 2. Server-Fingerabdruck
echo
echo "Lese Server-Fingerabdruck von $SSH_HOST:$SSH_PORT ..."
KNOWN_HOSTS="$(ssh-keyscan -p "$SSH_PORT" -T 10 "$SSH_HOST" 2>/dev/null)"
[[ -n "$KNOWN_HOSTS" ]] || { echo "Fehler: Server nicht erreichbar (ssh-keyscan)."; exit 1; }
printf '%s\n' "$KNOWN_HOSTS" > "$KEYDIR/known_hosts"
echo "Fingerabdrücke (bitte mit den Angaben des Hosters vergleichen):"
ssh-keygen -lf "$KEYDIR/known_hosts"
read -r -p "Stimmen die Fingerabdrücke? [j/N] " OK
[[ "$OK" =~ ^[jJyY]$ ]] || { echo "Abgebrochen."; exit 1; }

# 3. Secrets
set_secret() { printf '%s' "$2" | gh secret set "$1" --repo "$REPO"; }
set_secret SSH_HOST        "$SSH_HOST"
set_secret SSH_PORT        "$SSH_PORT"
set_secret SSH_USER        "$SSH_USER"
set_secret SSH_PRIVATE_KEY "$(cat "$KEYDIR/deploy_key")"
set_secret SSH_KNOWN_HOSTS "$KNOWN_HOSTS"

# 4. Umgebungen: staging ohne Freigabe, production mit Freigabe durch dich
ME_ID="$(gh api user --jq .id)"
gh api -X PUT "repos/$REPO/environments/staging" --silent
gh api -X PUT "repos/$REPO/environments/production" --silent --input - <<EOF
{"reviewers":[{"type":"User","id":$ME_ID}],
 "deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}
EOF
gh api -X POST "repos/$REPO/environments/production/deployment-branch-policies" \
  -f name=main -f type=branch --silent 2>/dev/null || true

echo
echo "Secrets angelegt:"
gh secret list --repo "$REPO"
echo
echo "================================================================"
echo "LETZTER SCHRITT: Diesen öffentlichen Schlüssel auf dem Server in"
echo "~/.ssh/authorized_keys eintragen (bzw. im Kundenmenü des Hosters):"
echo
cat "$KEYDIR/deploy_key.pub"
echo
echo "Mit Passwort-Login geht das auch direkt:"
echo "  echo '$(cat "$KEYDIR/deploy_key.pub")' | ssh -p $SSH_PORT $SSH_USER@$SSH_HOST 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'"
echo "================================================================"
echo "Der private Schlüssel liegt nur noch als GitHub-Secret vor (lokal gelöscht)."
echo "Alte FTP-Secrets entfernen (wenn nicht mehr gebraucht):"
echo "  for s in FTP_SERVER FTP_USERNAME FTP_PASSWORD FTP_SERVER_DIR; do gh secret delete \$s --repo $REPO; done"
