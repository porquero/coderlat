"""Migra el repo de contenido (coderlat-contenido) al formato /aportes/<usuario>/<slug>.

Uso (dentro de tu clon de coderlat-contenido, rama nueva):
    python3 migrar_contenido.py /ruta/a/coderlat-contenido            # simulación (no cambia nada)
    python3 migrar_contenido.py /ruta/a/coderlat-contenido --aplicar  # mueve las carpetas

Qué hace, para cada carpeta pages/02.blog/<slug>/ que tenga item*.md y un campo `author`:
  1. la mueve a pages/02.blog/aportes/<author en minúsculas>/<slug>/  (git mv si es un repo git)
  2. agrega `visible: true` al encabezado (el muro lista solo páginas visibles)
  3. crea las páginas índice /aportes y /aportes/<usuario> si faltan
Al final imprime: las redirecciones 301 para user/config/site.yaml y las carpetas antiguas a borrar en el servidor.
"""
import pathlib, re, shutil, subprocess, sys
import yaml

INDICE_APORTES = "---\ntitle: Aportes\nredirect: '/'\nroutable: false\n---\n"
INDICE_AUTOR = "---\ntitle: '{u}'\ndate: '01-01-2000 00:00'\n---\n"
SLUG = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    aplicar = "--aplicar" in sys.argv
    if not args:
        print(__doc__); sys.exit(2)
    raiz = pathlib.Path(args[0])
    blog = raiz / "pages" / "02.blog"
    if not blog.is_dir():
        print(f"No existe {blog}"); sys.exit(1)
    es_git = (raiz / ".git").exists()
    destino = blog / "aportes"
    movidos, saltados = [], []

    for d in sorted(p for p in blog.iterdir() if p.is_dir() and p.name != "aportes"):
        items = sorted(d.glob("item*.md"))
        if not items:
            saltados.append((d.name, "sin item*.md")); continue
        txt = items[0].read_text(encoding="utf-8")
        try:
            fm = yaml.safe_load(txt.split("---")[1]) or {}
        except Exception:
            saltados.append((d.name, "encabezado ilegible")); continue
        autor = str(fm.get("author") or "").strip().lower()
        if not autor or not SLUG.match(autor) or not SLUG.match(d.name):
            saltados.append((d.name, f"author inválido o ausente ({fm.get('author')!r})")); continue
        movidos.append((d, autor))

    print(f"{'APLICANDO' if aplicar else 'SIMULACIÓN'}: {len(movidos)} a migrar, {len(saltados)} omitidos\n")
    for nombre, motivo in saltados: print(f"  omitido  {nombre}: {motivo}")

    redirects, borrar = [], []
    for d, autor in movidos:
        nuevo = destino / autor / d.name
        print(f"  {d.name}  ->  aportes/{autor}/{d.name}")
        redirects.append(f"  '/{d.name}$': '/aportes/{autor}/{d.name}[301]'")
        borrar.append(d.name)
        if not aplicar: continue
        (destino / autor).mkdir(parents=True, exist_ok=True)
        if es_git:
            subprocess.run(["git", "-C", str(raiz), "mv", str(d.relative_to(raiz)), str(nuevo.relative_to(raiz))], check=True)
        else:
            shutil.move(str(d), str(nuevo))
        for it in nuevo.glob("item*.md"):
            t = it.read_text(encoding="utf-8")
            if not re.search(r"^visible:", t.split("\n---\n", 1)[0], re.M):
                it.write_text(t.replace("---\n", "---\nvisible: true\n", 1), encoding="utf-8")
        idx = destino / "default.md"
        if not idx.exists(): idx.write_text(INDICE_APORTES, encoding="utf-8")
        au = destino / autor / "autor.md"
        if not au.exists(): au.write_text(INDICE_AUTOR.format(u=autor), encoding="utf-8")

    print("\n=== 1) Agrega esto en user/config/site.yaml (clave `redirects:`) ===")
    print("redirects:")
    for r in redirects: print(r)
    print("\n=== 2) Borra estas carpetas antiguas en el servidor (rsync no elimina) ===")
    for n in borrar: print(f"rm -rf /RUTA/AL/SITIO/user/pages/02.blog/{n}")
    if not aplicar: print("\n(Simulación: vuelve a ejecutar con --aplicar para mover las carpetas.)")


main()
