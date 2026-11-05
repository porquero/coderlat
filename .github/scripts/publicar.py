"""Mueve los aportes aprobados (aportes/<usuario>/<slug>/) al repo de contenido
(contenido/pages/02.blog/aportes/<usuario>/<slug>/) -> URL pública /aportes/<usuario>/<slug>.

- Revalida cada aporte antes de copiarlo.
- Inyecta `visible: true` (el muro lista solo páginas visibles; los colaboradores no pueden fijarlo).
- Crea, si faltan, las páginas índice: /aportes (redirige al inicio) y /aportes/<usuario> (lista de la persona).
Escribe en $RUNNER_TEMP: publicados.txt (usuario/slug, para limpiar el buzón) y errores.txt.
Se ejecuta SOLO tras el merge en main (evento push), nunca sobre código de un PR."""
import os, re, shutil, subprocess, sys, pathlib
import yaml

BEFORE = os.environ.get("BEFORE", "")
TMP = pathlib.Path(os.environ.get("RUNNER_TEMP", "/tmp"))
DEST_BASE = pathlib.Path(os.environ.get("DEST_BASE", "contenido/pages/02.blog/aportes"))
SLUG = re.compile(r"^[a-z0-9][a-z0-9\-]*$")

INDICE_APORTES = """---
title: Aportes
redirect: '/'
routable: false
---
"""
INDICE_AUTOR = """---
title: '{usuario}'
date: '01-01-2000 00:00'
---
"""


def sh(*a): return subprocess.run(a, capture_output=True, text=True)


def pares_cambiados():
    """(usuario, slug) de los aportes agregados o modificados en este push."""
    base = pathlib.Path("aportes")
    if re.fullmatch(r"0*", BEFORE or "0"):
        return sorted((u.name, s.name) for u in base.iterdir() if u.is_dir() for s in u.iterdir() if s.is_dir())
    r = sh("git", "diff", "--name-only", "--diff-filter=AM", BEFORE, "HEAD", "--", "aportes/")
    out = set()
    for f in r.stdout.splitlines():
        parts = f.split("/")
        if len(parts) >= 4: out.add((parts[1], parts[2]))
    return sorted(out)


def inyectar_visible(item):
    txt = item.read_text(encoding="utf-8")
    if re.search(r"^visible:", txt.split("\n---\n", 1)[0], re.M):
        return
    item.write_text(txt.replace("---\n", "---\nvisible: true\n", 1), encoding="utf-8")


def asegurar_indices(usuario):
    DEST_BASE.mkdir(parents=True, exist_ok=True)
    idx = DEST_BASE / "default.md"
    if not idx.exists(): idx.write_text(INDICE_APORTES, encoding="utf-8")
    ud = DEST_BASE / usuario
    ud.mkdir(parents=True, exist_ok=True)
    au = ud / "autor.md"
    if not au.exists(): au.write_text(INDICE_AUTOR.format(usuario=usuario), encoding="utf-8")


publicados, errores = [], []
for usuario, slug in pares_cambiados():
    etiqueta = f"{usuario}/{slug}"
    src = pathlib.Path("aportes") / usuario / slug
    if not SLUG.match(usuario) or not SLUG.match(slug) or not src.is_dir():
        errores.append(f"{etiqueta}: ruta inválida"); continue
    items = sorted(src.glob("item*.md"))
    if not items:
        errores.append(f"{etiqueta}: no tiene item*.md"); continue
    v = sh(sys.executable, ".github/scripts/validar.py", *map(str, items))
    if v.returncode != 0:
        errores.append(f"{etiqueta}: no pasa la validación\n{v.stdout}"); continue
    asegurar_indices(usuario)
    dest = DEST_BASE / usuario / slug
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(src, dest)
    for it in sorted(dest.glob("item*.md")): inyectar_visible(it)
    publicados.append(etiqueta)
    print(f"publicado: {etiqueta}")

(TMP / "publicados.txt").write_text("\n".join(publicados) + ("\n" if publicados else ""))
(TMP / "errores.txt").write_text("\n".join(errores) + ("\n" if errores else ""))
print(f"{len(publicados)} publicados, {len(errores)} con error")
