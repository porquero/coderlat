---
title: 'RadarCL: correos públicos .cl con Certificate Transparency'
date: '19-10-2026 23:00'
author: fcarvajalbrown
taxonomy:
    tool:
        - radarcl
    resource:
        - herramienta
    country:
        - chile
metadata:
    description: 'Cómo RadarCL descubre sitios .cl con Certificate Transparency y extrae correos públicos desde la línea de comandos, probado en Python 3.13.'
faq:
    -
        q: '¿Cómo saco los correos públicos de un sitio .cl con RadarCL?'
        a: 'Instala las dependencias de requirements-core.txt y ejecuta python -m app.cli scan dominio.cl --output correos.json. RadarCL descubre las páginas de partida, rastrea solo dentro de .cl y exporta lo que encontró.'
    -
        q: '¿RadarCL funciona con dominios .com?'
        a: 'No. Su alcance es solo .cl: el rastreo y el filtro de correos se quedan en ese dominio por defecto.'
    -
        q: '¿Un correo con estado "unknown" es inválido?'
        a: 'No. Significa que no se pudo comprobar. En una prueba con --no-smtp, los 22 correos encontrados quedaron como unknown.'
sources:
    -
        title: 'Repositorio de RadarCL'
        url: 'https://github.com/fcarvajalbrown/RadarCL'
    -
        title: 'crt.sh, buscador de registros de Certificate Transparency'
        url: 'https://crt.sh/'
---

RadarCL es un rastreador en Python que descubre y verifica correos públicos de sitios chilenos `.cl`. Para encontrar las páginas de partida usa los registros de Certificate Transparency, y se puede ejecutar completo desde la línea de comandos, sin interfaz gráfica. Este artículo lo prueba con Python 3.13 y deja claro qué no probé.

===

## Cómo encuentra el sitio por dónde partir

La mayoría de los rastreadores de correos parten de una lista de URLs que alguien armó a mano. RadarCL la arma solo:

1. Busca el dominio en registros de Certificate Transparency (crt.sh, con CertSpotter de respaldo cuando crt.sh no contesta) para listar subdominios con certificado.
2. Comprueba por DNS que cada uno esté activo.
3. Puntúa los enlaces por su significado, y el descubrimiento de semillas depende del tipo de entidad.

Después rastrea por fases, acotado a `.cl` por defecto, extrae los correos (incluso los ofuscados) y los verifica por etapas: sintaxis, registro MX y SMTP.

## Instalación

RadarCL pide Python 3.12 o superior. El núcleo y la línea de comandos no dependen de Qt, así que basta con el archivo de requisitos del núcleo.

```bash
git clone https://github.com/fcarvajalbrown/RadarCL.git
cd RadarCL
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
```

En Windows, la activación es `.venv\Scripts\activate`.

## Descubrir las páginas de partida

```bash
python -m app.cli discover nunoa.cl
```

```text
Buscando semillas para nunoa.cl...
20 semillas encontradas.
https://serviciosenlinea.nunoa.cl
https://nunoa.cl
https://www.nunoa.cl
```

La lista sigue hasta las 20 semillas. Este comando solo descubre: no rastrea ni extrae nada.

## Escanear un dominio

```bash
python -m app.cli scan nunoa.cl --no-smtp --no-session --max-pages 40 --delay 1 --output correos.json
```

- `--no-smtp` omite la etapa SMTP.
- `--no-session` evita guardar la ejecución en `~/.radarcl/sessions.db`.
- `--max-pages` y `--delay` acotan el rastreo: 40 páginas, un segundo entre peticiones.

El formato de salida sale de la extensión de `--output`. El resumen del JSON quedó así:

```json
{"total": 22, "valid": 0, "catch_all": 0, "unknown": 22, "invalid": 0}
```

Encontró 22 direcciones. Ninguna queda como válida porque salté la etapa SMTP, y sin ella nada se puede confirmar. `unknown` no es `invalid`: es un correo que no se pudo comprobar. Cada resultado trae `email`, `source` (la página donde apareció), `status`, `error`, `evidence`, `generated` y `hidden`.

## Qué contiene cada formato

| Formato | Qué contiene |
|---|---|
| CSV | Solo las direcciones válidas. |
| JSON | Todos los resultados, con su estado, el motivo de la falla y un resumen de conteos. |
| HTML | Lo mismo que el JSON, como reporte de un solo archivo. |

La diferencia es deliberada: un CSV que filtra por válidas esconde las que solo quedaron sin comprobar. Además, el CSV deja fuera las direcciones que solo aparecían en partes del HTML que un lector no ve, porque suelen ser trampas para recolectores. En JSON y HTML siguen apareciendo, marcadas como ocultas.

## Cuando el sitio no te deja entrar

Un escaneo que no logra leer ninguna página termina con código de salida 1 y lo dice. Antes informaba cero correos como si fuera un resultado, y no lo era.

## Mi experiencia

Quise usar RadarCL para juntar los correos públicos de las 52 comunas de Santiago y contarles de MuniANCI, otra herramienta mía de código abierto.

El caso que más me enseñó fue el de aprimin.cl. Buscar aprimin@aprimin.cl en Google toma dos segundos, y RadarCL no lo encontraba y se daba por vencido. ¿Por qué? El servidor contestaba 202 con una página de 169 bytes, y 202 es un código de éxito, así que el muro pasaba por una página buena y vacía. Escaneaba, informaba "0 correos encontrados" y terminaba en tres páginas sin decir nunca que no lo dejaron entrar. La versión 0.6.0 reconoce ese muro por la forma de la respuesta y avisa. Cero no era un hallazgo.

El 22 de agosto vi cero resultados con nunoa.cl y bhp.com. Hoy, con la versión 0.6.0, el mismo escaneo de nunoa.cl por línea de comandos encontró 22 direcciones, y lo repetí en una instalación limpia en Python 3.13.13 con el mismo resultado. No sé qué cambió entre una prueba y otra.

## Qué no probé y qué no hace

- No probé la etapa SMTP ni el comando `verify`.
- No probé la interfaz gráfica de Windows. En agosto anoté que no funcionaba.
- Solo cubre `.cl`. Los dominios `.com` de empresas chilenas, como bhp.com, quedan fuera.
- No sé con qué frecuencia los sitios chilenos ponen trampas para recolectores, ni cuántos tienen muros: el proyecto no lo ha medido.

Las direcciones que salen son las que cada institución publicó. Este artículo no incluye ninguna, y no conviene subir listas a un repositorio.

## Recursos

- [Repositorio de RadarCL](https://github.com/fcarvajalbrown/RadarCL), con licencia Apache 2.0
- [crt.sh](https://crt.sh/)
