# Cómo publicar en Coderlat

Hay dos formas de preparar tu artículo: **a mano** (Opción A, abajo) o **con ayuda de IA** (Opción B). En ambos casos se publica con un Pull Request.

## Opción A: manualmente

1. Haz **fork** de este repositorio.
2. Copia `templates/articulo/` a `aportes/<tu-usuario-de-github>/<slug-de-tu-articulo>/`. Tu usuario va **en minúsculas** y el slug en minúsculas, sin tildes, con guiones. Ejemplo: `aportes/ana-dev/cobranza-whatsapp-n8n/`. Tu artículo se publicará en `coderlat.com/aportes/ana-dev/cobranza-whatsapp-n8n`, y en `coderlat.com/aportes/ana-dev` verás todos tus aportes.
3. Renombra el archivo a `item.es.md` y completa el encabezado (frontmatter) y el texto en Markdown. Imágenes: en la misma carpeta, referenciadas por nombre.
4. Abre un **Pull Request** hacia `main`. La validación automática te dirá si falta algo.
5. Revisamos, pedimos ajustes si hace falta y, al aprobar, **se publica en el sitio automáticamente** y tu carpeta sale de `aportes/` (este repositorio es solo un buzón, por eso es liviano).

> Tip: no necesitas clonar nada. En GitHub, entra a `aportes/` → **Add file → Create new file** y escribe `tu-usuario/mi-articulo/item.es.md`; GitHub crea el fork y el PR por ti. Tu PR solo puede tocar archivos dentro de `aportes/tu-usuario/`, y el campo `author` debe ser tu mismo usuario.

Archivos permitidos junto al artículo: `.md`, `.png`, `.jpg`, `.gif`, `.webp`, `.webm`, `.mp4` (máx. 1 MB por imagen, sin subcarpetas).

## Opción B: genera tu artículo con IA

Si ya tienes un repositorio o un artículo publicado en tu blog, un asistente de IA (Claude, ChatGPT, Gemini u otro) puede darte el borrador con el formato correcto en minutos.

1. Copia el prompt de abajo en tu asistente y reemplaza los campos entre corchetes. En `FUENTE` pega la URL de tu repo o artículo, o el texto.
2. Revisa el resultado. **La IA se equivoca**: prueba tú mismo los pasos y comandos, y corrige lo que no coincida con lo que viviste.
3. Resuelve cada marca `[VERIFICAR ...]`, en especial la sección **Mi experiencia**, que solo puedes escribir tú. Mientras queden marcas, la validación del PR fallará a propósito.
4. Guarda el resultado como `aportes/<tu-usuario>/<carpeta>/item.es.md` y abre el PR (como en los pasos de arriba), o pégalo en el Issue **Proponer solución** si no usas git.

````text
Actúa como editor técnico de Coderlat, una comunidad latinoamericana de soluciones open source e IA.
Convierte la FUENTE en UN solo archivo `item.es.md` listo para publicar. Escribe en español neutro, claro y directo.

FUENTE (URL de un repo de GitHub, URL de un artículo o texto pegado):
[PEGA AQUÍ LA URL O EL TEXTO]

DATOS DEL AUTOR:
- Usuario de GitHub: [TU-USUARIO]
- País: [PAÍS]
- Herramienta principal: [HERRAMIENTA]
- Tipo (skill, plantilla, tutorial, glosario, automatizacion): [TIPO]
- Fecha de hoy (dd-mm-aaaa hh:mm): [FECHA]

REGLAS DE CONTENIDO
1. Usa SOLO información presente en la fuente. No inventes comandos, versiones, resultados, métricas ni funciones. Si algo no está claro o no puedes confirmarlo, escribe [VERIFICAR: motivo] en ese punto.
2. Si la fuente es de otra persona, no copies párrafos: resume con tus palabras, enlázala en `sources` y agrega al final la línea [VERIFICAR: confirmar permiso o licencia de la fuente].
3. El primer párrafo responde en 2 o 3 frases qué problema resuelve y para quién.
4. Estructura: encabezados desde `##` (nunca `#`), párrafos cortos, listas y tablas cuando compares cosas.
5. Incluye una sección `## Mi experiencia` que contenga solo esto: [VERIFICAR: el autor completa aquí qué probó, en qué versión y qué resultado obtuvo]. No la rellenes tú.
6. Sin HTML, sin `<script>`, sin iframes y sin código Twig. Imágenes solo con texto alternativo descriptivo: ![qué muestra](archivo.png).
7. Etiquetas en minúsculas, sin tildes ni espacios (ejemplos: chile, automatizacion, n8n).

FORMATO DE SALIDA
Entrega el archivo completo, empezando por este encabezado:

---
title: 'Máx. 60 caracteres, con la palabra clave al inicio'
date: 'dd-mm-aaaa hh:mm'
author: usuario-github
ia: asistido
taxonomy:
    tool: [herramienta]
    resource: [tipo]
    country: [pais]
metadata:
    description: 'Entre 70 y 160 caracteres: qué resuelve y para quién'
faq:
    -
        q: '¿Pregunta real que alguien escribiría en Google o en un chat de IA?'
        a: 'Respuesta directa de 1 a 3 frases, que se entienda sin leer el resto.'
sources:
    -
        title: 'Nombre de la fuente'
        url: 'https://...'
---

Incluye de 2 a 4 preguntas en `faq`. Después del archivo, agrega:
- CARPETA: el nombre sugerido para la carpeta del artículo (minúsculas, sin tildes, con guiones; no puede ser un nombre reservado como admin, login, blog o api).
- PENDIENTES DEL AUTOR: lista de todo lo marcado con [VERIFICAR] y de los datos que faltaron.
````

**Reglas para publicar con IA**
- Debes tener permiso sobre la fuente. Si el artículo original es de otra persona, pídele autorización y cítala.
- Declara el uso de IA con `ia: asistido` en el encabezado (el prompt ya lo agrega). El sitio mostrará la nota "Redactado con asistencia de IA y revisado por el autor".
- Eres el responsable de lo que publicas: que sea correcto, probado y sin datos sensibles.

## Si la revisión automática marca algo

No necesitas abrir otro PR ni volver a llenar la plantilla. Entra a tu Pull Request, abre **Files changed**: los problemas aparecen marcados en la línea exacta. Corrige el archivo (⋯ → **Edit file** o un nuevo commit en tu rama) y la revisión se repite sola. Las **recomendaciones** (descripción corta, título largo, falta un `##`) no bloquean la publicación; los **errores** sí.

## Encabezado obligatorio

```yaml
---
title: 'Título claro y específico'
date: '31-12-2026 10:00'      # dd-mm-aaaa hh:mm
author: tu-usuario-github
taxonomy:
    tool: [n8n]               # herramienta principal, en minúsculas
    resource: [tutorial]      # skill, plantilla, tutorial, glosario, automatizacion, ...
    country: [chile]         # país de origen, sin tildes, en minúsculas
metadata:
    description: 'Resumen de 70 a 160 caracteres'
ia: asistido                  # opcional: solo si usaste IA para redactar
---
```

Solo se aceptan estos campos en el encabezado: `title`, `date`, `updated`, `author`, `ia`, `taxonomy`, `metadata`, `faq`, `sources`, `media_order` y `hero_image`.

Las etiquetas van en minúsculas y sin tildes para que los filtros del sitio no se dupliquen (`n8n` y `N8N` serían filtros distintos).

## Escribe para buscadores y para IA (SEO · AEO · GEO)

- **Título** claro, de hasta ~60 caracteres, con la palabra clave al inicio.
- **`metadata.description`**: 70–160 caracteres. Es lo que se ve en Google, en redes y en la discusión de comentarios.
- **Primer párrafo = respuesta.** Resuelve el problema en 2–3 frases antes de explicar el contexto.
- **Estructura:** empieza en `##` (el título ya es el H1), usa `###` para subtemas, listas y tablas cuando comparas cosas.
- **`faq`**: 2–4 preguntas reales con respuestas de 1–3 frases, que se entiendan sin leer el resto.
- **`sources`**: enlaza documentación oficial y datos que respalden lo que afirmas; las IA citan fuentes verificables.
- **Imágenes** con texto alternativo descriptivo (`![Qué muestra](archivo.png)`).
- **Experiencia propia:** cuenta qué probaste, en qué versión y qué resultado obtuviste. Eso diferencia tu artículo.
- Actualiza `updated: 'dd-mm-aaaa hh:mm'` cuando revises el contenido.

## Criterios editoriales

- Resuelve un problema real, con pasos que otra persona pueda reproducir.
- Es contenido propio o con permiso; cita fuentes y licencias.
- No incluyas credenciales, datos personales ni información de clientes.
- Sin publicidad ni autopromoción encubierta.

## Sin git

Abre un Issue con la plantilla **Proponer solución**; lo convertimos en artículo y te damos el crédito como autor.
