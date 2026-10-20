<p align="center">
  <a href="https://www.coderlat.com/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="docs/img/logo-dark.png">
      <img src="docs/img/logo-light.png" alt="Coderlat, codeando desde Latinoamérica" width="360">
    </picture>
  </a>
</p>

# Coderlat: comunidad open source de Latinoamérica

Coderlat reúne tutoriales, plantillas, herramientas, servidores MCP, skills y automatizaciones hechos en Latinoamérica, escritos por quienes los usan. Este repositorio es el **buzón** de aportes: abres un Pull Request con tu artículo y, cuando se aprueba, se publica en [coderlat.com](https://www.coderlat.com/) con tu nombre como autor.

## Qué se publica

El sitio tiene tutoriales, plantillas, un glosario, herramientas y un servidor MCP, con temas como EspoCRM, Kanboard y WHM. Cada artículo resuelve un problema concreto con pasos que otra persona pueda repetir.

## Cómo publicar

Con git: haz un fork, copia `templates/articulo/` a `aportes/<slug>/item.es.md` y abre un Pull Request. La guía paso a paso está en [CONTRIBUTING.md](CONTRIBUTING.md), con un prompt para armar el borrador a partir de tu repo o de un artículo que ya tengas.

Sin git: abre un Issue con la plantilla [Proponer solución](../../issues/new/choose) y lo convertimos en artículo.

## Comentarios

Cada artículo del sitio tiene su hilo en [Discussions](../../discussions), con login de GitHub (vía Giscus).

## Estructura

```
aportes/<slug>/item.es.md         # aportes pendientes de revisión (vacío cuando no hay)
templates/articulo/               # plantilla para copiar
.github/                          # plantillas, validación y publicación automática
docs/PUBLICACION.md               # guía para el mantenedor
```
