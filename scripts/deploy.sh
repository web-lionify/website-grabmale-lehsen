#!/usr/bin/env bash
# Lädt die Webseite per rsync über SSH hoch – nur geänderte Dateien.
#
#   scripts/deploy.sh staging            -> staging.grabmale-aus-lehsen.de  (/webseite/staging/)
#   scripts/deploy.sh produktiv          -> grabmale-aus-lehsen.de          (/webseite/produktiv/)
#   scripts/deploy.sh staging --dry-run  -> zeigt nur, was sich ändern würde
#
# Läuft normalerweise in GitHub Actions (.github/workflows/deploy.yml).
# Lokal nur mit rsync + ssh (z. B. WSL, macOS, Linux) und eingerichtetem SSH-Schlüssel.
#
# Zielpfade: KAS-Pfad /webseite/... liegt per SSH unter /www/htdocs/w012fee6/webseite/... (all-inkl, chroot).
#
# Umgebungsvariablen:
#   SSH_HOST (Pflicht), SSH_USER (Pflicht), SSH_PORT (Standard 22)
#   SSH_KEY_FILE      privater Schlüssel (optional, sonst ssh-agent / ~/.ssh/config)
#   DEPLOY_PATH       Zielordner überschreiben (Standard je Ziel siehe unten)
set -euo pipefail

ZIEL="${1:-}"
shift || true
DRY_RUN=()
for arg in "$@"; do
  case "$arg" in
    --dry-run|-n) DRY_RUN=(--dry-run) ;;
    *) echo "Unbekannte Option: $arg"; exit 1 ;;
  esac
done

case "$ZIEL" in
  staging)   PFAD_STANDARD="/www/htdocs/w012fee6/webseite/staging/";    URL="https://staging.grabmale-aus-lehsen.de" ;;
  produktiv) PFAD_STANDARD="/www/htdocs/w012fee6/webseite/produktiv/"; URL="https://grabmale-aus-lehsen.de" ;;
  *) echo "Aufruf: $0 staging|produktiv [--dry-run]"; exit 1 ;;
esac

: "${SSH_HOST:?SSH_HOST fehlt}"
: "${SSH_USER:?SSH_USER fehlt}"
SSH_PORT="${SSH_PORT:-22}"
DEPLOY_PATH="${DEPLOY_PATH:-$PFAD_STANDARD}"
[[ "$DEPLOY_PATH" == */ ]] || DEPLOY_PATH="$DEPLOY_PATH/"

command -v rsync >/dev/null || { echo "Fehler: rsync ist nicht installiert."; exit 1; }

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Sicherheitsnetz für lokale Aufrufe: produktiv nur von main mit sauberem Arbeitsstand.
if [[ "$ZIEL" == "produktiv" && -z "${GITHUB_ACTIONS:-}" ]]; then
  BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)"
  [[ "$BRANCH" == "main" ]] || { echo "Fehler: Produktiv nur vom Branch main (aktuell: $BRANCH)."; exit 1; }
  [[ -z "$(git -C "$ROOT" status --porcelain)" ]] || { echo "Fehler: Es gibt nicht committete Änderungen."; exit 1; }
fi

# Upload-Stand in einem Temp-Ordner zusammenstellen (Repo bleibt unverändert).
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT
rsync -a --exclude-from="$ROOT/scripts/deploy-exclude.txt" "$ROOT/" "$BUILD/"

if [[ "$ZIEL" == "staging" ]]; then
  # Staging darf nicht in Suchmaschinen landen.
  printf 'User-agent: *\nDisallow: /\n' > "$BUILD/robots.txt"
  cat >> "$BUILD/.htaccess" <<'EOF'

# --- nur Staging (von scripts/deploy.sh ergänzt) ---
<IfModule mod_headers.c>
  Header always set X-Robots-Tag "noindex, nofollow"
</IfModule>
EOF
fi

SSH_CMD=(ssh -p "$SSH_PORT" -o BatchMode=yes)
[[ -n "${SSH_KEY_FILE:-}" ]] && SSH_CMD+=(-i "$SSH_KEY_FILE" -o IdentitiesOnly=yes)
[[ -n "${SSH_KNOWN_HOSTS_FILE:-}" ]] && SSH_CMD+=(-o UserKnownHostsFile="$SSH_KNOWN_HOSTS_FILE" -o StrictHostKeyChecking=yes)

echo "Ziel:   $ZIEL  ($URL)"
echo "Server: $SSH_USER@$SSH_HOST:$DEPLOY_PATH (Port $SSH_PORT)"
[[ ${#DRY_RUN[@]} -gt 0 ]] && echo "Modus:  DRY-RUN – es wird nichts geändert"
echo

# Vorabprüfung: Übergeordneter Zielordner muss existieren (rsync legt nur die letzte Ebene an).
# Sonst Login-Verzeichnis und Inhalt anzeigen, damit der richtige Pfad sichtbar wird.
PARENT="$(dirname "${DEPLOY_PATH%/}")"
if ! "${SSH_CMD[@]}" "$SSH_USER@$SSH_HOST" "test -d '$PARENT'"; then
  echo "Fehler: Ordner '$PARENT' existiert auf dem Server nicht (Zielpfad: $DEPLOY_PATH)."
  echo "Login-Verzeichnis und Inhalt:"
  "${SSH_CMD[@]}" "$SSH_USER@$SSH_HOST" 'echo "pwd: $(pwd)"; echo "HOME: $HOME"; ls -la; for d in */; do echo "--- $d"; ls -la "$d" 2>&1 | head -15; done' || true
  exit 1
fi

# --checksum:   vergleicht Inhalte statt Zeitstempel -> nur wirklich geänderte Dateien werden übertragen
#               (wichtig in GitHub Actions, dort haben alle Dateien frische Zeitstempel).
# ohne -t:      Zeitstempel unveränderter Dateien auf dem Server bleiben erhalten (Browser-Cache).
# --delete:     auf dem Server gelöschte/umbenannte Dateien entfernen;
#               geschützt (P) bleiben Dinge, die nur auf dem Server liegen.
rsync -rlpz --checksum --omit-dir-times \
  --chmod=D755,F644 \
  --delete --delete-delay \
  --filter='P .well-known/' \
  --filter='P .htpasswd' \
  --filter='P .user.ini' \
  --filter='P /logs/' \
  --itemize-changes --stats \
  ${DRY_RUN[@]+"${DRY_RUN[@]}"} \
  -e "${SSH_CMD[*]}" \
  "$BUILD/" "$SSH_USER@$SSH_HOST:$DEPLOY_PATH"

echo
echo "Fertig: $URL"
