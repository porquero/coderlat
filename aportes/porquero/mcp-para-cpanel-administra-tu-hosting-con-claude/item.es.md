---
title: 'MCP para cPanel: administra tu hosting con Claude'
date: '24-11-2026 15:15'
author: porquero
ia: asistido
taxonomy:
    tool: [cpanel]
    resource: [mcp]
    country: [chile]
metadata:
    description: 'Servidor MCP local que conecta Claude con cPanel para gestionar correos, subdominios, bases MySQL y archivos con simulación previa y auditoría.'
faq:
    -
        q: '¿Cómo conecto Claude Desktop con cPanel?'
        a: 'Instala este servidor MCP local, crea un token de API de cPanel y registra el servidor en claude_desktop_config.json con tu host, usuario y token. Después reinicia Claude Desktop por completo.'
    -
        q: '¿Qué permisos necesita el token de API de cPanel?'
        a: 'Permisos sobre los módulos Email, DomainInfo, SubDomain, Mysql y Fileman de UAPI. Además, la cuenta necesita activos los roles de correo, almacenamiento de archivos, servidor web y base de datos que vayas a usar.'
    -
        q: '¿Es seguro dejar que una IA cambie mi hosting?'
        a: 'El servidor simula cada cambio por defecto (dry-run), confina las rutas a /public_html, mueve lo borrado a la papelera de cPanel y guarda una auditoría sin contraseñas. Además puedes desactivar herramientas en allowed_actions.json. Las contraseñas generadas quedan en el historial de la conversación del cliente.'
    -
        q: '¿Puedo instalar WordPress con este MCP sin WP Toolkit?'
        a: 'La herramienta prepare_wordpress descarga el paquete oficial, lo sube y lo extrae en un directorio vacío de tu cuenta. La instalación la completas tú en el navegador.'
sources:
    -
        title: 'Repositorio huevohost-cpanel-mcp (GitHub)'
        url: 'https://github.com/porquero/huevohost-cpanel-mcp'
---

Este servidor MCP local permite que Claude Desktop, u otro cliente MCP, ejecute acciones acotadas sobre una cuenta de cPanel: leer dominios, crear correos, subdominios y bases MySQL, y gestionar archivos. Está pensado para quien administra su propio hosting con cPanel y quiere delegar tareas repetitivas a un asistente con límites claros.

El proyecto está escrito en Python, usa la comunicación stdio y se autentica con un token de API de UAPI. Por defecto cada cambio se simula antes de ejecutarse.

## Qué puedes hacer

Cada herramienta tiene un nivel de riesgo definido en `allowed_actions.json`. Una acción con `enabled=false` no se registra en MCP y el modelo no puede invocarla.

| Herramienta | Nivel | Qué hace |
|---|---|---|
| `list_domains` | lectura | Lista dominio principal, addon, parked y subdominios |
| `list_email_accounts` | lectura | Lista las cuentas de correo de un dominio |
| `create_email_account` | escritura reversible | Crea una cuenta con contraseña aleatoria de 20 caracteres y la verifica |
| `create_subdomain` | escritura reversible | Crea subdominios sobre dominios de la cuenta, con document root dentro de `/public_html` |
| `list_databases` | lectura | Lista bases MySQL con uso de disco y usuarios asociados |
| `create_database` | escritura reversible | Crea una base MySQL vacía |
| `list_database_users` | lectura | Lista usuarios MySQL y sus bases, sin contraseñas |
| `create_database_user` | escritura reversible | Crea un usuario con permisos sobre una sola base (`all`, `read_write` o `read_only`) |
| `change_database_user_password` | alto impacto | Genera una contraseña nueva para un usuario MySQL que perdió la suya |
| `prepare_wordpress` | alto impacto | Deja los archivos de WordPress listos en un directorio vacío |
| `list_files`, `download_file` | lectura | Lista y descarga archivos de texto dentro de `/public_html` |
| `create_file`, `upload_file` | escritura reversible | Crea o sube archivos de texto y pequeños binarios |
| `list_local_files`, `upload_local_file` | lectura / escritura reversible | Sube fotos, logos, PDF y fuentes desde tu equipo sin que los bytes pasen por el modelo |
| `delete_file` | alto impacto | Mueve a la papelera de cPanel, con confirmación de la ruta exacta |
| `publish_landing_page` | alto impacto | Diseñada para una fase futura y desactivada por defecto |

Con `create_subdomain`, `create_file` y `upload_local_file` ya puedes publicar una landing estática en un subdominio. El repositorio detalla ese flujo y sus límites: sin vista previa, sin reversión del sitio completo y sin carga atómica.

## Requisitos

- Python 3.11 o superior.
- Token de API de cPanel con permisos sobre `Email`, `DomainInfo`, `SubDomain`, `Mysql` y `Fileman`.
- Roles activos en la cuenta según lo que uses: Receive Mail (correo), File Storage (archivos), Web Server (subdominios) y Database Server (MySQL).

## Instalación

Los comandos del README están escritos para PowerShell en Windows:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Variables de entorno

| Variable | Obligatoria | Para qué sirve |
|---|---|---|
| `CPANEL_HOST` | Sí | Hostname o IP de cPanel, con puerto opcional |
| `CPANEL_USER` | Sí | Usuario de la cuenta cPanel |
| `CPANEL_TOKEN` | Sí | Token de API; nunca se imprime ni se registra |
| `CPANEL_PORT` | No | Puerto, por defecto `2083` |
| `CPANEL_VERIFY_SSL` | No | `true` por defecto; `false` solo para pruebas con certificado autofirmado |
| `MCP_FILE_MAX_BYTES` | No | Tamaño máximo por archivo; 1 MiB por defecto, hasta 10 MiB |
| `MCP_LOCAL_UPLOAD_DIRS` | No | Carpetas locales desde las que se pueden subir archivos; por defecto, `archivos/` |
| `AUDIT_LOG_PATH` | No | Ruta del registro de auditoría |
| `ALLOWED_ACTIONS_PATH` | No | Ruta de `allowed_actions.json` |
| `CPANEL_MCP_LOG_LEVEL` | No | Nivel de log; por defecto `WARNING`, con salida a stderr |

Define las credenciales como variables de usuario del sistema. El archivo `.env` está excluido de Git y el servidor no lo carga automáticamente.

## Conectar con Claude Desktop

Agrega el servidor en `claude_desktop_config.json` con las rutas absolutas de tu instalación:

```json
{
  "mcpServers": {
    "huevohost-cpanel": {
      "command": "C:\\ruta\\a\\cpanel-api-open\\.venv\\Scripts\\python.exe",
      "args": ["-m", "cpanel_mcp"],
      "env": {
        "CPANEL_HOST": "cpanel.example.com:2083",
        "CPANEL_USER": "usuario",
        "CPANEL_TOKEN": "TU_TOKEN"
      }
    }
  }
}
```

Si pones el token dentro de este archivo, ese archivo pasa a contener una copia de la credencial: protégelo y mantenlo fuera de cualquier repositorio. Reinicia Claude Desktop por completo después del cambio.

## Controles de seguridad

- Dry-run por defecto: con `execute=false` no se contacta cPanel ni se genera ninguna contraseña.
- Rutas de archivos confinadas a `/public_html`, sin seguir enlaces simbólicos.
- Los reemplazos mueven antes el original a la papelera de cPanel.
- Timeout de 30 segundos y TLS verificado por defecto.
- Auditoría en formato JSONL que no registra contraseñas, tokens ni contenido de archivos.
- Los archivos PHP exigen `allow_php=true`, que Claude solo debe activar tras preguntarte. Extensiones como `.phtml`, `.htaccess` o `wp-config.php` quedan bloqueadas.
- `upload_local_file` solo admite jpg, png, webp, gif, ico, pdf y fuentes, validados por su contenido real.

## Puntos de atención

- Las contraseñas generadas se muestran una sola vez y quedan en el historial de la conversación del cliente MCP. Si se filtran, cámbialas desde cPanel.
- `change_database_user_password` invalida la contraseña anterior: un sitio que la use, por ejemplo en `wp-config.php`, deja de conectar hasta que la actualices.
- Si la creación de un correo agota el timeout, cPanel pudo haber creado la cuenta sin confirmar. Revisa el listado y restablece la contraseña manualmente.
- El servidor no borra bases de datos ni subdominios, y tampoco administra DNS ni SSL. Esas tareas se hacen desde cPanel.
- Mantén `archivos/` como única carpeta de subida. Agregar carpetas con documentos privados a `MCP_LOCAL_UPLOAD_DIRS` los dejaría publicables en la web.

## Mi experiencia

Desarrollador web con alma open source https://www.coderlat.com/aportes/porquero