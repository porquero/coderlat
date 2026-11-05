#!/usr/bin/env bash
# Publica en el sitio Grav lo que hay en main de coderlat-contenido.
# Solo sincroniza pages/02.blog/aportes/ y solo limpia la caché si hubo cambios.
# Uso manual: bash ~/publicar-sitio.sh      Cron: ver docs/PUBLICACION.md
set -euo pipefail

CONTENIDO="${CONTENIDO:-$HOME/coderlat-contenido}"
SITIO="${SITIO:-/home/playaspa/public_html/coderlat.com}"
PHP="${PHP:-php}"
ORIGEN="$CONTENIDO/pages/02.blog/aportes/"
DESTINO="$SITIO/user/pages/02.blog/aportes/"

# Evita ejecuciones solapadas (cron + manual)
exec 9>"${TMPDIR:-/tmp}/coderlat-publicar.lock"
flock -n 9 || { echo "Ya hay una publicación en curso"; exit 0; }

cd "$CONTENIDO"
git fetch --quiet origin main
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  git merge --ff-only --quiet origin/main
fi

mkdir -p "$DESTINO"
# -i lista solo lo que cambia; --delete retira aportes eliminados (solo dentro de aportes/)
CAMBIOS="$(rsync -rltDi --delete --exclude '.gitkeep' "$ORIGEN" "$DESTINO" | grep -v '^\.' || true)"

if [ -n "$CAMBIOS" ]; then
  echo "$(date '+%F %T') cambios:"; echo "$CAMBIOS"
  cd "$SITIO" && "$PHP" bin/grav clearcache >/dev/null
  echo "$(date '+%F %T') caché limpiada"
fi
