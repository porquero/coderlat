# Guía del mantenedor: buzón → publicación

```
Colaborador ──fork/PR──▶ coderlat (buzón, aportes/)
                              │  merge a main (tú apruebas)
                              ▼
                  Action "Publicar aporte"
                     │                │
        copia a coderlat-contenido   borra aportes/<usuario>/<slug> del buzón
                     │
                     ▼
        Servidor: git pull + rsync → user/pages/02.blog + clearcache
```

Los forks parten del buzón, que casi siempre está vacío: no arrastran los artículos publicados.
(El historial de git conserva las versiones antiguas de texto; es despreciable. Las imágenes se limitan a 1 MB.)

## Configuración única

1. **Crear el repo de contenido**: `porquero/coderlat-contenido` (puede ser privado). Estructura: `pages/02.blog/aportes/<usuario>/<slug>/item.es.md` (URL pública: `/aportes/<usuario>/<slug>`).
   Si ya tienes artículos publicados con el formato antiguo, migra con `python3 docs/migrar_contenido.py /ruta/a/coderlat-contenido` (ver *Migración al formato /aportes/usuario/slug*).
2. **Token (PAT)**: GitHub → Settings → Developer settings → Fine-grained tokens.
   Repositorios: `coderlat` y `coderlat-contenido`. Permiso: *Contents: Read and write*. Caducidad: 90 días o más.
3. **Secreto**: en el repo `coderlat` → Settings → Secrets and variables → Actions → New secret → `PUBLICAR_TOKEN` = el token.
4. **Protección de `main`** (Settings → Branches/Rulesets): exige PR, el check **Validar contenido** y la revisión de CODEOWNERS.
   Permite que los administradores salten la regla (*no marcar* "Do not allow bypassing"), porque la Action empuja con tu token para limpiar el buzón.
5. **Aprobación de workflows** (ver abajo).
6. **Estructura del buzón**: los aportes viven en `aportes/<usuario>/<slug>/`. Un PR externo solo puede tocar `aportes/<su-login-en-minúsculas>/` y el `author` debe coincidir con la carpeta: nadie puede escribir sobre el artículo de otra persona.

## ¿Se puede evitar aprobar el workflow en cada PR?

GitHub exige aprobación manual la **primera vez** que alguien envía un PR desde un fork. Ajuste: Settings → Actions → General → *Fork pull request workflows from outside collaborators*.
- *Require approval for first-time contributors who are new to GitHub*: pide aprobación solo a cuentas nuevas. Es la opción más cómoda.
- *Require approval for first-time contributors*: a quien nunca ha tenido un PR aceptado.
- *Require approval for all outside collaborators*: siempre (la más estricta).

Con cualquiera de las dos primeras, quien ya tiene un PR aprobado no vuelve a necesitar aprobación. Es seguro relajarlo porque el workflow de validación corre con `pull_request`, permisos de solo lectura y **sin secretos**. No uses `pull_request_target` para evitar la aprobación: ejecutaría código del fork con acceso a secretos.

## Publicar en el servidor

```bash
# Primera vez (repo privado: usa una deploy key de solo lectura)
git clone git@github.com:porquero/coderlat-contenido.git ~/coderlat-contenido

# Cada publicación
cd ~/coderlat-contenido && git pull origin main \
  && rsync -av --delete pages/02.blog/aportes/ /RUTA/AL/SITIO/user/pages/02.blog/aportes/ \
  && cd /RUTA/AL/SITIO && php bin/grav clearcache
```

`--delete` solo actúa dentro de `02.blog/aportes/`: si retiras un aporte del repo de contenido, desaparece del sitio, y no toca el resto de tus páginas.

## Qué pasa si algo falla
- **Check "Validar contenido" en rojo**: el detalle indica qué corregir.
- **"Publicar aporte" en rojo**: el aporte queda en `aportes/` (no se borra) y el error aparece en el log. Casos típicos: nombre reservado, carpeta de usuario distinta de `author` o archivo no permitido.
- **Token vencido**: renueva el PAT y actualiza el secreto `PUBLICAR_TOKEN`.

## URLs de los aportes

- `/aportes/<usuario>/<slug>`: el artículo.
- `/aportes/<usuario>`: lista de aportes de esa persona (página `autor.md`, la crea el publicador la primera vez).
- `/aportes`: redirige al inicio.

El usuario sale de la carpeta y es el login de GitHub en minúsculas, así que no hay choques entre colaboradores ni con rutas del sitio (`/admin`, `/login`, `/blog`...). Además se rechazan como nombre de artículo los términos reservados (lista `RESERVADOS` en `.github/scripts/validar.py`).

## Migración al formato /aportes/usuario/slug

1. En tu clon de `coderlat-contenido`, crea una rama y ejecuta `python3 migrar_contenido.py . ` (simulación) y luego con `--aplicar`. Mueve cada carpeta a `aportes/<author>/<slug>/`, agrega `visible: true` y crea las páginas índice.
2. Haz commit y push a `main` de `coderlat-contenido`.
3. En el servidor, borra las carpetas antiguas que imprime el script (el `rsync` no elimina) y ejecuta la publicación.
4. Las redirecciones 301 de las URLs antiguas ya están en `user/config/site.yaml` del sitio; para aportes nuevos que migres, agrega las líneas que imprime el script.
5. **Comentarios (Giscus):** el hilo se identifica por la ruta de la página. En GitHub → Discussions, renombra cada discusión existente al nuevo path (por ejemplo `aportes/ana-dev/mi-articulo`) para conservar sus comentarios.
