---
title: 'Enmascarar RUT y datos personales en Polars con MaskOps'
date: '19-10-2026 22:30'
author: fcarvajalbrown
taxonomy:
    tool:
        - polars
    resource:
        - tutorial
    country:
        - chile
metadata:
    description: 'Cómo enmascarar RUT, correos y teléfonos en columnas de Polars con MaskOps, en Python 3.13, y dejar un manifiesto JSON de lo que se detectó.'
faq:
    -
        q: '¿Cómo enmascaro el RUT de una columna de Polars?'
        a: 'Instala maskops y aplica maskops.mask_pii("columna", patterns=["rut"]) dentro de with_columns. Reconoce el RUT con su dígito verificador y reemplaza el número por asteriscos, dejando visible el dígito final.'
    -
        q: '¿MaskOps funciona con Python 3.14?'
        a: 'No con wheel precompilado. La versión 2.1.0 publica wheels para Python 3.9 a 3.13; en 3.14 pip intenta compilar desde el código fuente. Usa 3.13 o menos.'
    -
        q: '¿MaskOps detecta nombres de personas?'
        a: 'No. Trabaja con patrones de datos estructurados (RUT, correos, teléfonos, tarjetas), no con nombres, lugares ni organizaciones en texto libre.'
sources:
    -
        title: 'maskops en PyPI'
        url: 'https://pypi.org/project/maskops/'
    -
        title: 'Repositorio de MaskOps'
        url: 'https://github.com/fcarvajalbrown/MaskOps'
    -
        title: 'Documentación de MaskOps'
        url: 'https://fcarvajalbrown.github.io/MaskOps/'
    -
        title: 'Documentación de Polars'
        url: 'https://docs.pola.rs/'
---

Para enmascarar RUT, correos y teléfonos en una columna de texto de Polars, instala `maskops` y aplica `maskops.mask_pii` dentro de `with_columns`. Reconoce el RUT validando su dígito verificador y no necesita modelos de lenguaje ni archivos intermedios. Lo probé completo en Python 3.13.

===

## Requisitos

MaskOps 2.1.0 publica wheels para Python 3.9 a 3.13. En Python 3.14 no hay wheel y pip intenta compilar desde el código fuente. Si tu máquina trae 3.14, crea un entorno con 3.13.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install maskops polars
```

En Windows, la activación es `.venv\Scripts\activate`.

## Datos de prueba

Los datos son inventados. Hay un RUT con correo, un teléfono, una fila sin datos personales y otro RUT con correo.

```python
import polars as pl
import maskops

df = pl.DataFrame(
    {
        "id": [1, 2, 3, 4],
        "notas": [
            "Cliente 12.345.678-5, escribir a ana.perez@ejemplo.cl",
            "Llamar al +56912345678 por el reclamo",
            "Sin datos personales en esta fila",
            "RUT 76.354.771-K, correo contacto@empresa.cl",
        ],
    }
)
```

## Encontrar las filas con datos personales

`contains_pii` devuelve una columna de verdadero o falso. Sirve para filtrar antes de enmascarar.

```python
con_datos = df.filter(maskops.contains_pii("notas"))
```

Quedan las filas 1, 2 y 4. La fila 3 no tiene nada que enmascarar.

## Enmascarar todo lo que detecta

```python
enmascarado = df.with_columns(maskops.mask_pii("notas"))
```

La columna `notas` queda así:

```text
Cliente **********-5, escribir a *********@ejemplo.cl
Llamar al +56********* por el reclamo
Sin datos personales en esta fila
RUT **********-K, correo ********@empresa.cl
```

Del RUT queda solo el dígito verificador. El correo mantiene el dominio y pierde todo lo que va antes de la arroba, y del teléfono sobrevive el código de país.

## Enmascarar solo el RUT

Con `patterns` eliges qué familias tocar. Las demás quedan intactas.

```python
solo_rut = df.with_columns(maskops.mask_pii("notas", patterns=["rut"]))
```

```text
Cliente **********-5, escribir a ana.perez@ejemplo.cl
Llamar al +56912345678 por el reclamo
Sin datos personales en esta fila
RUT **********-K, correo contacto@empresa.cl
```

Los nombres de las familias están en el docstring de `mask_pii`, y un nombre que no existe lanza un error en vez de ignorarse en silencio.

## Mantener la relación entre tablas

Los asteriscos son irreversibles y borran la relación entre filas. ¿Y si necesitas que el mismo RUT dé el mismo resultado en varias columnas o tablas? Usa el modo `consistent` con una sal secreta.

```python
seudonimo = df.with_columns(
    maskops.mask_pii("notas", mode="consistent", salt="cambia-esta-sal")
)
```

```text
Cliente 34.478.496-5, escribir a *********@ejemplo.cl
Llamar al +56629231746 por el reclamo
Sin datos personales en esta fila
RUT 25.666.729-K, correo ********@empresa.cl
```

Con la misma sal, el mismo valor da siempre la misma salida. Los correos siguen con asteriscos. La sal va fuera de los datos, por ejemplo en una variable de entorno, y nunca escrita en el código como en este ejemplo.

## Dejar constancia de lo que se detectó

`masking_manifest` cuenta cuántas veces apareció cada familia en cada columna, y `write_manifest` lo guarda como JSON.

```python
manifiesto = maskops.masking_manifest(df, columns=["notas"])
maskops.write_manifest(manifiesto, "rat.json", source="clientes.csv")
```

El resultado en pantalla:

```text
column  pii_family  match_count  mask_mode
notas   email       2            asterisk
notas   phone       1            asterisk
notas   rut         2            asterisk
```

El archivo `rat.json` trae `maskops_version`, `generated_at`, `source`, `record_count` y la lista `records` con esas mismas filas. Cada registro incluye también un campo `regulation`. La herramienta etiqueta el RUT con "Ley 21.719", y el correo y el teléfono como datos personales generales.

## Mi experiencia

Busqué un nicho para Rust, un lenguaje que me resulta cómodo de leer, y vi que no había herramientas de PII pensadas para LATAM. Vivo en Chile y me pareció ridículo. De ahí salió MaskOps.

Las primeras tablas de velocidad del README salieron malas, entre 0,4 y 0,7 veces la velocidad de Python. ¿El problema? La comparación era injusta: MaskOps corría todos sus patrones en cada fila y el código de Python solo uno. Lo arreglé pasando `patterns=` con la familia que se medía, el mismo parámetro que usaste arriba para enmascarar solo el RUT, y agregué un atajo en Rust que salta las filas sin dígitos ni arroba. Con un millón de filas y datos mezclados, la ventaja quedó entre 1,2 y 3,2 veces. En un caso, documentos europeos con datos en todas las filas, sigue en 0,9, y el README lo dice tal cual.

Para este tutorial corrí el código completo en Python 3.13.13, en Windows, con maskops 2.1.0 y polars 2.0.0. Las salidas de arriba son las que obtuve. Primero lo intenté en Python 3.14.2: pip se puso a compilar en vez de instalar un wheel, lo detuve y pasé a 3.13. En el modo `consistent`, dos ejecuciones con la misma sal dieron el mismo resultado.

## Qué no hace

MaskOps busca patrones, no entiende texto. No detecta nombres de personas, lugares ni organizaciones escritos en texto libre. Para eso hace falta otra herramienta, y el README del proyecto sugiere combinarlo con una de reconocimiento de entidades cuando el texto trae nombres. Antes de enmascarar una tabla real, prueba con una muestra y mira el resultado.

## Recursos

- [maskops en PyPI](https://pypi.org/project/maskops/)
- [Repositorio](https://github.com/fcarvajalbrown/MaskOps) y [documentación](https://fcarvajalbrown.github.io/MaskOps/)
- Licencia MPL-2.0. El README del proyecto indica que el uso comercial requiere una licencia aparte, descrita en su `CLA.md`.
