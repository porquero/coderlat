"""Valida artículos de Coderlat. Uso: validar.py archivo.md ...

Dos niveles:
  · ERROR (bloquea el PR): seguridad, estructura y datos que rompen el sitio.
  · ADVERTENCIA (no bloquea): recomendaciones de estilo y SEO.
En GitHub Actions emite anotaciones en la línea exacta (pestaña "Files changed") y un resumen.
Nada de esto exige abrir otro PR: se corrige el archivo en la misma rama y el check se repite solo.
"""
import os, re, sys, datetime, pathlib
import yaml

REQUIRED = ["title", "date", "author"]
TAXONOMIAS = ["tool", "resource", "country"]
CLAVES_PERMITIDAS = {"title", "media_order", "date", "updated", "author", "ia", "hero_image",
                     "taxonomy", "metadata", "faq", "sources"}
METADATA_PERMITIDA = {"description", "keywords"}
TAXONOMIA_PERMITIDA = set(TAXONOMIAS) | {"tag"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9\-]*$")
# Nombres que no pueden usarse como slug de artículo: rutas del sitio, de plugins, de la API y términos técnicos
RESERVADOS = {
    "admin", "login", "logout", "register", "registro", "profile", "user", "users", "usuario", "usuarios",
    "forgot-password", "reset-password", "activate", "unauthorized", "api", "feed", "rss", "atom", "json",
    "sitemap", "robots", "favicon", "index", "home", "inicio", "blog", "aportes", "aporte", "tag", "tags",
    "tool", "resource", "country", "category", "author", "autor", "search", "buscar", "page", "pages",
    "assets", "images", "img", "css", "js", "fonts", "user-data", "system", "vendor", "cache", "logs", "tmp",
    "backup", "bin", "cgi-bin", "db", "static", "public", "tests", "webserver-configs", "well-known",
    "quienes-somos", "herramientas", "herramientas-open-source", "comunidad", "recursos", "contenido",
    "publicar", "unirse", "contacto", "privacidad", "terminos", "error", "404", "500", "maintenance",
    "random", "subscribe", "newsletter", "grav", "null", "undefined", "con", "prn", "aux", "nul",
}
MAX_IMG = 1024 * 1024
PERMITIDAS = {".md", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".webm", ".mp4"}
MARCAS = re.compile(r"\[\s*(VERIFICAR|PEGA\s+AQU)", re.I)
IA_VALORES = {"asistido", "no"}
PELIGROSO = re.compile(r"<\s*(script|iframe|object|embed|form|style|link|meta|base)\b|javascript\s*:|\son[a-z]+\s*=|\{\{|\{%", re.I)
CI = os.environ.get("GITHUB_ACTIONS") == "true"

errores, avisos = [], []

def _reg(lista, f, linea, msg):
    lista.append((f, linea, msg))

def err(f, msg, linea=1): _reg(errores, f, linea, msg)
def adv(f, msg, linea=1): _reg(avisos, f, linea, msg)


def sin_codigo(texto):
    """Reemplaza por espacios los bloques ``` / ~~~ y los `código en línea`, conservando los saltos de línea.
    El código se muestra escapado (no se ejecuta), así que no debe disparar reglas de HTML ni de encabezados."""
    out, fence = [], None
    for linea in texto.split("\n"):
        m = re.match(r"^\s{0,3}(`{3,}|~{3,})", linea)
        if fence is None and m:
            fence = (m.group(1)[0], len(m.group(1))); out.append(""); continue
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and linea.strip() == m.group(1):
                fence = None
            out.append(""); continue
        out.append(re.sub(r"`[^`\n]*`", lambda x: " " * len(x.group(0)), linea))
    return "\n".join(out)


def validar(f):
    p = pathlib.Path(f)
    txt = p.read_text(encoding="utf-8")
    for n, linea in enumerate(sin_codigo(txt).split("\n"), 1):   # las marcas dentro de bloques de código son ejemplos legítimos
        if MARCAS.search(linea):
            err(f, "queda una marca sin resolver ([VERIFICAR...] o [PEGA AQUÍ...]); complétala o elimínala antes de publicar", n)
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        err(f, "falta el encabezado (frontmatter) entre '---'"); return
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        err(f, f"YAML inválido en el encabezado: {e}"); return
    if not isinstance(fm, dict):
        err(f, "el encabezado debe ser una lista de campos clave: valor"); return

    # --- seguridad del encabezado: solo campos conocidos (evita process/twig, redirect, template, routes, etc.)
    for k in fm:
        if k not in CLAVES_PERMITIDAS:
            err(f, f"campo '{k}' no permitido en el encabezado. Permitidos: {', '.join(sorted(CLAVES_PERMITIDAS))}")
    md = fm.get("metadata")
    if isinstance(md, dict):
        for k in md:
            if k not in METADATA_PERMITIDA: err(f, f"metadata.{k} no permitido (solo {', '.join(sorted(METADATA_PERMITIDA))})")
    elif md is not None:
        err(f, "metadata debe contener 'description'")

    for k in REQUIRED:
        if not fm.get(k): err(f, f"falta '{k}'")
    if "ia" in fm and str(fm["ia"]).strip().lower() not in IA_VALORES:
        err(f, "'ia' solo admite 'asistido' (o se omite si no usaste IA)")
    d = fm.get("date")
    if d and not isinstance(d, datetime.datetime):
        try: datetime.datetime.strptime(str(d), "%d-%m-%Y %H:%M")
        except ValueError: err(f, "'date' debe tener formato dd-mm-aaaa hh:mm")
    tax = fm.get("taxonomy") or {}
    if not isinstance(tax, dict): err(f, "taxonomy debe tener tool, resource y country"); tax = {}
    for k in tax:
        if k not in TAXONOMIA_PERMITIDA: err(f, f"taxonomy.{k} no permitido (solo {', '.join(sorted(TAXONOMIA_PERMITIDA))})")
    for t in TAXONOMIAS:
        vals = tax.get(t)
        if not vals: err(f, f"falta taxonomy.{t}"); continue
        for v in (vals if isinstance(vals, list) else [vals]):
            if not SLUG.match(str(v)):
                err(f, f"taxonomy.{t}: '{v}' debe ir en minúsculas, sin tildes ni espacios")
    desc = ((md or {}).get("description") or "").strip() if isinstance(md, dict) else ""
    if not desc: err(f, "falta metadata.description (idealmente 70-160 caracteres)")
    elif not 70 <= len(desc) <= 165: adv(f, f"metadata.description mide {len(desc)} caracteres; para buscadores conviene entre 70 y 160")
    tl = len(str(fm.get("title", "")))
    if tl == 0: pass
    elif tl > 70: adv(f, f"el título mide {tl} caracteres; conviene que no pase de ~60")
    faq = fm.get("faq")
    if faq:
        if not isinstance(faq, list) or any(not isinstance(i, dict) or not i.get("q") or not i.get("a") for i in faq):
            err(f, "faq debe ser una lista de pares q/a completos")
    src = fm.get("sources")
    if src and (not isinstance(src, list) or any(not isinstance(i, dict) or not str(i.get("url", "")).startswith(("http://", "https://")) for i in src)):
        err(f, "sources debe ser una lista con 'title' y 'url' que empiece por http(s)://")

    # --- cuerpo
    cuerpo_ini = txt.index("\n---\n", 4) + 5
    offset = txt[:cuerpo_ini].count("\n")
    cuerpo = txt[cuerpo_ini:]
    prosa = sin_codigo(cuerpo)
    for n, linea in enumerate(prosa.split("\n"), 1 + offset):
        if PELIGROSO.search(linea):
            err(f, f"contenido no permitido fuera de bloques de código (script, iframe, form, style, eventos on*=, javascript: o Twig): {linea.strip()[:60]}", n)
        elif re.match(r"^# [^#]", linea):
            adv(f, "evita '# ' (H1) en el texto: el título ya es el H1; empieza en '## '", n)
        elif re.search(r"!\[\s*\]\(", linea):
            adv(f, "imagen sin texto alternativo: usa ![descripción](archivo.png)", n)
    if not re.search(r"^## ", prosa, re.M): adv(f, "usa al menos un encabezado '## ' para estructurar el artículo")
    if len(cuerpo.strip()) < 200: adv(f, "el artículo es muy corto (menos de ~200 caracteres)")

    # --- carpeta y archivos: aportes/<usuario>/<slug>/item.es.md
    slug, usuario = p.parent.name, p.parent.parent.name
    if not slug or not SLUG.match(slug):
        err(f, f"la carpeta '{slug}' debe ser un slug en minúsculas con guiones")
    elif slug in RESERVADOS:
        err(f, f"'{slug}' es un nombre reservado del sitio; elige otro para la carpeta del artículo (por ejemplo, más específico)")
    elif len(slug) > 80:
        err(f, "el nombre de la carpeta es demasiado largo (máximo 80 caracteres)")
    if not usuario or not SLUG.match(usuario):
        err(f, f"la carpeta del usuario '{usuario}' debe estar en minúsculas (tu usuario de GitHub en minúsculas)")
    else:
        autor = str(fm.get("author") or "").strip().lower()
        if autor and autor != usuario:
            err(f, f"la carpeta del usuario ('{usuario}') debe coincidir con author ('{fm.get('author')}') en minúsculas: la ruta es aportes/{autor}/{slug}/item.es.md")
    for extra in p.parent.rglob("*"):
        if extra.is_symlink(): err(str(extra), "no se permiten enlaces simbólicos")
        elif extra.is_dir(): err(str(extra), "no se permiten subcarpetas dentro del artículo")
        elif extra.suffix.lower() not in PERMITIDAS:
            err(str(extra), f"tipo de archivo no permitido ({extra.suffix or 'sin extensión'}); permitidos: " + ", ".join(sorted(PERMITIDAS)))
        elif extra.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"} and extra.stat().st_size > MAX_IMG:
            err(str(extra), "imagen mayor a 1 MB")


for f in sys.argv[1:]:
    validar(f)

def esc(s): return s.replace("%", "%25").replace("\r", "").replace("\n", " ")

if CI:
    for f, n, m in errores: print(f"::error file={f},line={n},title=Corrige esto para publicar::{esc(m)}")
    for f, n, m in avisos: print(f"::warning file={f},line={n},title=Recomendación::{esc(m)}")
    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen:
        with open(resumen, "a", encoding="utf-8") as fh:
            if errores:
                fh.write("## Hay algo por corregir antes de publicar\n\n")
                for f, n, m in errores: fh.write(f"- `{f}` (línea {n}): {m}\n")
                fh.write("\n**No necesitas abrir otro PR.** Edita el archivo en tu rama (en el PR: *Files changed* → ⋯ → *Edit file*), guarda el cambio y esta revisión se repite sola. El texto del PR no se pierde.\n")
            else:
                fh.write("## Todo en orden\n\nEl artículo cumple las reglas para publicarse.\n")
            if avisos:
                fh.write("\n### Recomendaciones (no bloquean)\n\n")
                for f, n, m in avisos: fh.write(f"- `{f}` (línea {n}): {m}\n")
else:
    for f, n, m in errores: print(f"ERROR {f}:{n}: {m}")
    for f, n, m in avisos: print(f"AVISO {f}:{n}: {m}")

if errores: sys.exit(1)
print("OK: contenido válido" + (f" ({len(avisos)} recomendaciones)" if avisos else ""))
