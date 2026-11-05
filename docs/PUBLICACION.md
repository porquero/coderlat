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
bash ~/publicar-sitio.sh
```

El script (`docs/publicar-sitio.sh`; cópialo a `~/` del servidor) hace `git fetch` + fast-forward de `main`, sincroniza **solo** `pages/02.blog/aportes/` con `rsync --delete` (un aporte retirado del repo desaparece del sitio; el resto de tus páginas no se toca) y ejecuta `php bin/grav clearcache` **únicamente si rsync reportó cambios**. Usa un lock para que dos ejecuciones no se pisen. Ajusta con variables: `SITIO`, `CONTENIDO`, `PHP`.

### Automático con cron

Un solo cron basta (el script ya compara antes de limpiar caché). En cPanel → *Cron Jobs*, cada 10 minutos:

```
*/10 * * * * PHP=/usr/local/bin/php bash $HOME/publicar-sitio.sh >> $HOME/publicar-sitio.log 2>&1
```

Comprueba la ruta de PHP con `which php` (en cPanel suele ser `/usr/local/bin/php` o `/opt/cpanel/ea-phpXX/root/usr/bin/php`) y pon esa en `PHP=`. El log solo recibe líneas cuando hubo cambios.

Si prefieres dos cron separados: el primero hace solo `git fetch/merge`, el segundo ejecuta el rsync + limpieza; aporta poco, porque el rsync ya detecta por sí mismo si hubo cambios, y separar abre una ventana donde el sitio y el repo quedan desfasados.

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
