---
title: 'Visor web para cámaras DVR XMeye con go2rtc y PHP'
date: '05-11-2026 17:45'
author: MarioRiffoCortes
ia: asistido
taxonomy:
    tool: [go2rtc]
    resource: [tutorial]
    country: [chile]
metadata:
    description: 'Ve en el navegador o el celular las cámaras de un DVR XMeye (app XVR Pro): en vivo con go2rtc y grabaciones con línea de tiempo, en PHP.'
faq:
    -
        q: '¿Se pueden ver las cámaras de un DVR XVR Pro en el navegador sin la app del fabricante?'
        a: 'Sí. go2rtc toma el flujo RTSP del DVR (puerto 554) y lo entrega al navegador por WebRTC o MSE, así que basta con una página web servida desde un PC de la casa.'
    -
        q: '¿Cómo veo las grabaciones del disco del DVR desde una página web?'
        a: 'El proyecto habla con el DVR por su protocolo binario en el puerto 34567: busca los archivos de cada día, descarga el tramo pedido y lo reproduce en el navegador mientras llega, con opción de bajarlo en MP4.'
    -
        q: '¿Cómo veo las cámaras desde el celular fuera de casa sin abrir puertos?'
        a: 'Con Tailscale instalado en el PC y en el celular se entra al portal por la red privada de Tailscale. El PC con el portal debe estar encendido.'
    -
        q: '¿Por qué el DVR rechaza una segunda conexión con el mismo usuario?'
        a: 'Estos DVR admiten una sola sesión y una sola reproducción por usuario. Por eso el proyecto usa usuarios distintos para el vivo, las búsquedas y la reproducción de grabaciones.'
sources:
    -
        title: 'Repositorio del proyecto vigilancia'
        url: 'https://github.com/MarioRiffoCortes/vigilancia'
    -
        title: 'go2rtc (AlexxIT)'
        url: 'https://github.com/AlexxIT/go2rtc'
    -
        title: 'OpenXM-DVR: documentación del protocolo binario XMeye'
        url: 'https://github.com/crazy3tr/OpenXM-DVR'
    -
        title: 'JMuxer'
        url: 'https://github.com/samirkumardas/jmuxer'
    -
        title: 'TensorFlow.js COCO-SSD'
        url: 'https://github.com/tensorflow/tfjs-models/tree/master/coco-ssd'
    -
        title: 'Tailscale'
        url: 'https://tailscale.com/'
    -
        title: 'Laragon'
        url: 'https://laragon.org/'
---

Si tienes un DVR o XVR tipo XMeye / Xiongmai (los que se usan con la app **XVR Pro**), este proyecto te permite ver tus cámaras en el navegador del PC o del celular, en vivo y también las **grabaciones del disco del DVR**, sin depender de la app del fabricante. Está pensado para quien tiene un PC con Windows en casa y quiere un portal propio, instalable como app y accesible desde fuera con Tailscale.

## Qué hace

### En vivo

- Grilla con todas las cámaras en 16:9, sin franjas negras.
- Modo **Enfoque**: una cámara grande y las demás al costado, sin reconectar los videos al cambiar de vista.
- Calidad **SD / HD / UHD** (UHD prioriza WebRTC para tener menos retraso).
- Estado real de cada cámara (en vivo, conectando o sin señal) y contador de cámaras en línea.
- En el celular: deslizar para cambiar de cámara y ficha técnica con resolución, bitrate, FPS, códec, retraso y audio.
- Modo **Auto**: un detector de personas (TensorFlow.js + COCO-SSD) corre en el navegador y pone en Enfoque la cámara donde aparece alguien.
- Se instala como aplicación (PWA) en Android.

### Grabaciones

- Calendario con los días que tienen grabación.
- Línea de tiempo del día por cámara: haces clic en un punto y el video parte mientras llega del DVR.
- Una o dos pantallas sincronizadas a la misma hora real.
- Velocidad de ½× a 16×, avance por tramos y pantalla completa.
- Descarga del tramo en **MP4** (con dos pantallas, ambas cámaras lado a lado en un solo video).
- Acceso protegido con inicio de sesión.

## Cómo funciona

```
Navegador (PC / celular / app instalada)
   │ HTTP (Apache + PHP)          │ WebSocket :1984 (video en vivo)
   ▼                              ▼
index.php / grabaciones.php    go2rtc ──RTSP :554──► DVR
   │
api.php ──► dvr.php ──protocolo binario :34567──► DVR (búsqueda y descarga)
   │
ffmpeg (convierte el H.264 del DVR a MP4)
```

| Pieza | Función |
|---|---|
| go2rtc | Lee el RTSP del DVR y lo entrega al navegador por WebRTC, MSE, HLS o MJPEG |
| `index.php` | Vista en vivo, enfoque, calidad, ficha técnica y modo Auto |
| `grabaciones.php` | Calendario, línea de tiempo, reproductor y descargas |
| `api.php` | API de grabaciones: días, tramos, reproducción inmediata y clips |
| `dvr.php` | Cliente del protocolo binario del DVR (login, búsqueda, descarga) |
| ffmpeg | Convierte el video del DVR a MP4 para descargarlo |

## Requisitos

- Windows con **Laragon** (Apache + PHP 8.1 o superior).
- **go2rtc** (`go2rtc.exe` en la carpeta `go2rtc/`).
- **ffmpeg** (`ffmpeg.exe` en la carpeta `ffmpeg/`), solo para grabaciones.
- Un DVR/XVR compatible con XMeye / Xiongmai, con RTSP en el puerto 554 y su protocolo propio en el 34567.
- Opcional: **Tailscale** en el PC y en el celular.

## Instalación paso a paso

1. Descarga el repositorio en la carpeta web de Laragon: `C:\laragon\www\vigilancia`.
2. Descarga `go2rtc.exe` en `vigilancia\go2rtc\` y `ffmpeg.exe` en `vigilancia\ffmpeg\`.
3. Crea tu configuración a partir de los ejemplos:

```
copy config.example.php config.php
copy go2rtc\go2rtc.example.yaml go2rtc\go2rtc.yaml
```

4. En `go2rtc/go2rtc.yaml` pon la IP del DVR, el usuario y la clave, y deja solo los canales que tengas. Si la clave tiene símbolos, escríbelos codificados (`@` = `%40`, `:` = `%3A`, `#` = `%23`).
5. En `config.php` pon los nombres de las cámaras, la IP, los usuarios del DVR, la clave y la carpeta de caché.
6. Con Laragon iniciado, ejecuta `Camaras ON-OFF.bat` (o `iniciar.bat`). La primera vez, acepta el permiso de firewall para **redes privadas**.
7. Abre `http://localhost/vigilancia/`. Desde otro equipo de la casa: `http://IP-DEL-PC/vigilancia/`.

### Usuarios del DVR

El DVR acepta una sola sesión por usuario y entrega una grabación a la vez por usuario. Por eso se crean tres usuarios en el DVR, con la misma clave:

| Usuario | Uso |
|---|---|
| Usuario del vivo | Video en vivo, calendario, línea de tiempo e inicio de sesión del portal |
| Usuario de grabaciones 1 | Reproducir grabaciones de las cámaras 1 y 2 |
| Usuario de grabaciones 2 | Reproducir grabaciones de las cámaras 3 y 4 |

Con dos pantallas, si ambas cámaras corresponden al mismo usuario, la segunda se pide automáticamente con el otro.

### Ver desde el celular fuera de casa

1. Instala Tailscale en el PC y en el celular con la misma cuenta.
2. Entra a `http://NOMBRE-TAILSCALE-DEL-PC/vigilancia/`.
3. En Chrome o Brave usa **Instalar aplicación** (o el botón *Instalar* del portal).

El PC con Laragon y go2rtc tiene que estar encendido.

## Problemas comunes

- **Una cámara no carga:** abre `http://localhost:1984`, el panel de go2rtc muestra el error de cada flujo.
- **La cámara HD se ve en negro:** probablemente transmite en H.265. Usa el subflujo también para la versión HD o configura el DVR en H.264.
- **Tu DVR es Dahua o Hikvision:** `go2rtc.example.yaml` trae los formatos RTSP alternativos para esas marcas.
- **Cambiaste `go2rtc.yaml` y no pasa nada:** ejecuta `detener.bat` y luego `iniciar.bat`.

## Seguridad

- No subas `config.php` ni `go2rtc.yaml` a ningún repositorio: contienen la clave del DVR. El `.gitignore` del proyecto ya los excluye.
- La vista en vivo no pide contraseña; las grabaciones sí. Úsalo solo en tu red de casa o por Tailscale y **no abras puertos del router a Internet**.
- La API de go2rtc (puerto 1984) muestra las URL RTSP con la clave a quien llegue a ese puerto: mantén el firewall de Windows en redes privadas.
- El protocolo del DVR es delicado: un paquete mal formado puede reiniciarlo. Por eso cada acceso pasa por un candado que evita conexiones simultáneas.