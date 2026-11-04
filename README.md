# Diario Celeste · Diario online

Diario estático en español rioplatense, listo para servir desde la raíz de un repositorio de GitHub Pages o desde un subdirectorio. Sin frameworks, fuentes web, CDN, analítica ni dependencias de ejecución en el navegador. Modo noche por defecto; la elección día/noche se guarda en `localStorage`.

## Preparar una edición

Requiere Python 3.10+ en Linux/macOS, acceso HTTPS y datos de zonas horarias del sistema. El generador usa **sólo la biblioteca estándar**.

```bash
python3 scripts/verify_sources.py   # HTTP 200 + XML RSS/Atom con entradas
python3 -m unittest discover -s tests -v
python3 scripts/build_diario.py
python3 -m http.server 8790
```

Abrí `http://localhost:8790`. Los JSON y las imágenes son estáticos: **no se actualizan automáticamente al abrir la web**. Ejecutá el generador de nuevo cuando quieras preparar otra edición. La interfaz avisa si el cierre tiene más de 36 horas.

En este entorno el puerto IPv4 8790 pertenece al túnel de red del sistema. La vista previa se sirve en el mismo puerto sobre IPv6, sin interrumpir ese proceso:

```bash
python3 -m http.server 8790 --bind ::1
# http://[::1]:8790/
```

Para GitHub Pages alcanza con publicar los archivos de la raíz en la rama elegida. `.nojekyll` evita el procesamiento de Jekyll; todos los enlaces y recursos son relativos. No se configuró ningún remoto, publicación ni DNS.

## Cómo se prepara el diario

- `sources.json`: catálogo de fuentes con región editorial, temas, endpoint RSS, clasificación de independencia y estado de la última verificación. La región describe el medio, no necesariamente el país de cada noticia.
- `scripts/verify_sources.py`: descarga de verdad cada fuente, exige HTTP 200 y analiza XML con entradas. Guarda fecha, redirección, cantidad y errores en `data/feed-verification.json`. Una fuente puede estar verificada y no tener noticias recientes. Las fallidas quedan documentadas y se omiten al construir hasta una nueva verificación.
- `scripts/build_diario.py`: descarga RSS/Atom en hasta 12 hilos, con timeout de 10 segundos por intento y un reintento para fallas transitorias. Limita bytes y tiempo de lectura, rechaza notas sin fecha, anteriores a 36 horas o con fecha futura de más de 15 minutos. Excluye feeds que declaran portugués o inglés.
- Clasifica con el tema de feeds especializados y palabras del título, categorías y extracto. No asigna todos los temas del feed general a cada noticia. Sigue siendo una heurística y puede equivocarse.
- Normaliza acentos, puntuación y espacios; agrupa títulos por similitud textual o coincidencia de palabras. Conserva la versión independiente de duplicados y registra sus medios de cobertura. El solapamiento más amplio de un evento suma puntos sin borrar enfoques distintos.
- Puntaje: hasta 10 puntos por cobertura en otros medios, 4 por independencia y hasta 6 por actualidad. Apertura de política/economía; cinco destacadas que buscan diversidad regional; hasta seis notas distintas por sección. Agota las candidatas independientes antes de usar respaldos. Con cuatro o cinco independientes válidas no completa con medios generalistas. Si no hay cuatro en una sección, muestra la cantidad disponible y lo explica; nunca rellena con noticias viejas.
- Hace GET de cada enlace candidato con lectura mínima y exige HTTP 200/HTML; descarta redirecciones a la portada y reemplaza candidatos fallidos. La verificación corresponde al cierre, no garantiza disponibilidad futura ni ausencia de paywall. Todos los ítems publicados incluyen estado y fecha de comprobación.
- Sólo para apertura y destacadas consulta `og:image` (260 KB de HTML, timeout de 5 segundos). Descarga como máximo 2 MB por imagen y comprueba firmas JPEG/PNG/WebP. Guarda archivos locales bajo `assets/noticias/`; el navegador no hace solicitudes a medios ni CDN. Las imágenes y los titulares pertenecen a sus autores y siempre se atribuyen.
- Limita títulos a 110 caracteres. El resumen habitual usa cuatro titulares con su medio. No inventa contenido ni redacta una síntesis de artículos no leídos.
- Si la edición no alcanza 20 ítems, cuatro destacadas y seis secciones con contenido, conserva el JSON previo y termina con código 1. Los fallos de una fuente o imagen individual se toleran si hay cobertura suficiente. `data/build-report.json` registra el resultado, enlaces fallidos y secciones escasas.
- Un bloqueo de archivo evita dos escritores simultáneos. Las escrituras JSON usan reemplazo atómico. Antes de reemplazar el diario copia **los bytes exactos de la edición anterior** a `data/archivo/AAAA-MM-DD.json`, usando su fecha en Costa Rica. Mantiene `data/archivo/index.json`. Si hay varias actualizaciones el mismo día, se conserva la última versión reemplazada de esa fecha. No se inventan ediciones históricas.

## Resumen opcional con Claude

```bash
DIARIO_RESUMEN=1 python3 scripts/build_diario.py
```

Si `claude` está instalado y autenticado, ejecuta `claude -p` con los titulares, sin shell. Acepta entre tres y cinco líneas y un máximo de 2.000 caracteres. Ante ausencia, timeout, error o formato inválido usa el resumen extractivo. La interfaz identifica el resumen generado con IA. La generación opcional con Claude no se ejecutó para la edición de muestra.

## Fuentes y verificación

Consultá [FUENTES.md](FUENTES.md) para la investigación, criterios, resultados y endpoints probados; `fuentes.html` muestra el catálogo al lector. `independent` es una categoría editorial conservadora, no una garantía de neutralidad ni una auditoría de propiedad. Los medios de grandes grupos y los públicos/universitarios se marcan como respaldo. Los proyectos periodísticos, cooperativos y especializados autónomos tienen prioridad. Agencia Pública (portugués) y el endpoint de ESPN que declara inglés se verifican pero se omiten de la edición en español. No se usa Google News.

## Comprobaciones y capturas

```bash
python3 -m unittest discover -s tests -v
node --check diario.js
# Sólo para las capturas: Playwright y Chrome instalados en el entorno.
DIARIO_PREVIEW_URL='http://[::1]:8790' python3 scripts/preview.py
```

El script de vista previa comprueba los cuatro estados, persistencia del tema, ausencia de desbordamiento horizontal e imágenes rotas, cero peticiones externas, archivo, filtro regional, ruta de proyecto Pages y error de edición inexistente. Guarda capturas de página completa en `/workspace/diario-preview/` y `browser-checks.json`. Playwright **no es una dependencia del generador ni del sitio**.

Las noticias aparecen una sola vez entre apertura, destacadas y secciones. El explorador regional vuelve a mostrar hasta cuatro enlaces de esa selección para facilitar la navegación, sin aumentar el conteo de noticias únicas.
