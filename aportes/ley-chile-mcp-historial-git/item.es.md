---
title: 'MCP de leyes chilenas: historial de la ley en git'
date: '29-10-2026 00:00'
author: pisanvs
ia: asistido
taxonomy:
    tool: [mcp]
    resource: [automatizacion]
    country: [chile]
metadata:
    description: 'Servidor MCP de solo lectura para consultar leyes chilenas desde 1810 y comparar versiones. Para agentes de IA y quienes investigan la ley chilena.'
faq:
    -
        q: '¿Cómo consulto leyes chilenas desde un agente de IA con MCP?'
        a: 'Conecta el servidor MCP remoto https://leyes.pisanvs.cl/api/mcp, que es de solo lectura y no pide autenticación. Ofrece siete herramientas, entre ellas search_laws, get_article y diff_versions.'
    -
        q: '¿Puedo ver qué decía una ley chilena en una fecha anterior?'
        a: 'Sí. El proyecto reconstruye cada norma como historial en git y la herramienta get_article entrega el texto de un artículo en cualquier fecha. Con diff_versions comparas dos versiones de una misma norma.'
    -
        q: '¿De dónde salen los datos de ley-chile?'
        a: 'Provienen de la Biblioteca del Congreso Nacional (BCN). El catálogo se obtiene por SPARQL y los textos desde el sistema LeyChile; con ellos el pipeline arma un commit por cada publicación.'
    -
        q: '¿Cada cuánto se actualiza el repositorio de la ley chilena?'
        a: 'Según el README, una GitHub Action ejecuta las cuatro fases del pipeline cada 3 horas.'
sources:
    -
        title: 'Repositorio pisanvs/ley-chile en GitHub'
        url: 'https://github.com/pisanvs/ley-chile'
---

El sistema LeyChile de la BCN publica el texto vigente de cada norma, pero no permite saber qué decía un artículo en una fecha anterior ni qué norma lo modificó. ley-chile reconstruye ese historial como un repositorio git y lo expone mediante un servidor MCP de solo lectura. Sirve a agentes de IA y a personas que investigan, desarrollan o consultan normativa chilena.

## Qué problema resuelve

LeyChile entrega textos refundidos: versiones consolidadas que ya incorporan todas las modificaciones. Ese texto es una fotografía del presente, sin autor ni fecha de origen por artículo, y no responde preguntas como «¿qué decía esto en 2013?».

ley-chile reescribe la ley chilena como un repositorio git. Cada publicación legislativa es un commit y cada artículo tiene su ventana de vigencia, de modo que una investigación histórica se convierte en una consulta. El objetivo declarado es cubrir cada ley, decreto y resolución desde 1810.

## Servidor MCP para agentes

El servidor remoto cubre todo el corpus, es de solo lectura y no requiere autenticación:

```
https://leyes.pisanvs.cl/api/mcp
```

| Herramienta | Qué hace |
| --- | --- |
| `search_laws` | Busca normas con texto libre; usa organismo e idNorma para distinguir normas parecidas. |
| `get_law` | Entrega metadatos, índice de artículos e historial de versiones de una norma. |
| `get_article` | Devuelve el texto de un artículo en cualquier fecha. |
| `search_articles` | Encuentra el artículo pertinente dentro de una norma extensa. |
| `diff_versions` | Compara dos versiones de una norma. |
| `get_modifications` | Muestra qué normas modificaron a la consultada y cuáles modifica ella. |
| `list_versions` | Lista todas las versiones con fecha de una norma. |

### Cómo conectarlo

La portada del sitio permite añadirlo con un clic en Claude, Claude Code, Cursor, VS Code y Codex. Para agentes que leen instrucciones en texto, el proyecto publica un archivo en `https://leyes.pisanvs.cl/`.

En el link anterior selecciona el modelo o herramienta que integrarás el mcp.

### Consultas que habilita

- Qué decía un artículo en una fecha concreta, con `get_article`.
- Qué cambió entre dos versiones de una norma, con `diff_versions`.
- Qué normas modificaron a otra y a cuáles afecta, con `get_modifications`.
- Qué versiones fechadas existen de una norma, con `list_versions`.

El sitio también ofrece una vista de comparación que muestra lo eliminado en rojo y lo añadido en verde, palabra por palabra.

## Cómo se construye el historial

El pipeline tiene cuatro fases idempotentes y resumibles:

| Script | Resultado | Función |
| --- | --- | --- |
| `build_catalog.py` | `catalog.json` | Obtiene todos los idNorma desde BCN SPARQL. |
| `fetch_normas.py` | `graph.json` | Descarga metadatos de LeyChile y expande el grafo con búsqueda en anchura (BFS). |
| `fetch_versions.py` | `cache/diffs`, versiones | Descarga versiones y diffs por norma. |
| `build_history.py` | Branch `historial` | Importa los commits con `git fast-import`. |

Cada commit de `historial` representa un evento de publicación: el texto de la norma nueva, el texto actualizado de cada norma que ésta modificó, las derogaciones y los symlinks de sucesión. La Action `pipeline.yml` corre las cuatro fases cada 3 horas.

Git, en la branch `historial`, es la única fuente de verdad. Postgres y Meilisearch funcionan como modelos de lectura derivados y descartables.

### Diseño de tres branches

| Branch | Contiene | Montada en |
| --- | --- | --- |
| `main` | Scripts, configuración y CI; nunca datos de leyes. | — |
| `pipeline-cache` (huérfana) | Versiones y diffs descargados. | `./cache/` |
| `historial` (huérfana) | Los commits de leyes reconstruidos. | `./historial/` |

## Estado de avance

Según el README (con última ejecución indicada el 25-08-2026):

- Historial reconstruido: 95 %, con 339.065 de 353.511 normas construibles y marca de avance al 06-06-2026.
- Grafo de metadatos: 99 %, con 357.266 de 358.228 normas descargadas.
- Excluidas: 4.717 normas sin fecha o con fecha centinela.

Una norma es construible cuando tiene fecha de publicación y al menos una vigencia real. LeyChile usa la fecha `2222-02-02` para marcar versiones abiertas («vigente»), y el filtro `int(fecha[:4]) <= 2100` la descarta.

## Correr el pipeline en tu máquina

```
pip install -r requirements.txt
LEYCHILE_DATA_ROOT=./historial python scripts/run_pipeline.py
LEYCHILE_DATA_ROOT=./historial python scripts/build_history.py --dry-run
python -m pytest
```

El primer comando instala las dependencias y el segundo ejecuta el pipeline completo. El tercero muestra una vista previa de los commits sin importar nada, y el cuarto corre los tests, que son funciones puras sin red ni git. El archivo `CLAUDE.md` del repositorio detalla la arquitectura.

Confirma si tu versión de Python es compatible.

## Fuentes de datos

| Fuente | Endpoint | Límite |
| --- | --- | --- |
| BCN SPARQL | `https://datos.bcn.cl/sparql` | Sin límite indicado |
| LeyChile, norma en JSON | Endpoint `get_norma_json` | Adaptativo |
| LeyChile, XML versionado | Endpoint `obtxml` con la fecha de versión | 1 solicitud por segundo |

## Licencia

El README indica que los textos legales son documentos públicos del Estado de Chile y que el código se distribuye bajo licencia MIT. El proyecto cuenta con el auspicio de kerokero.

## Mi experiencia

Soy pisanvs, puedes pronunciarlo como quieras. Soy estudiante de secundaria, programador, emprendedor, atleta de matemáticas y fanático del código abierto. Puedes encontrar más información sobre mí en mi sitio web. Mis lenguajes favoritos son Go, TypeScript y C.