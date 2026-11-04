# Fuentes: investigación y comprobación real

Última comprobación HTTP/XML de los endpoints nuevos: **2026-11-04** (ver `data/feed-verification.json` para la corrida reproducible completa).

Se relevaron 56 endpoints: 43 verificados y 13 fallidos. `verified` exige una respuesta HTTP 200 y XML RSS/Atom con entradas, no sólo un URL plausible. Los errores describen lo observado desde este entorno y pueden cambiar según la red, el bloqueo por IP o cambios del sitio.

## Criterio editorial híbrido

El Diario Celeste es una edición **híbrida**: combina medios independientes con medios consolidados (grandes grupos generalistas, portales comerciales y medios públicos). El objetivo es una portada representativa, no un boletín de un solo tipo de medio.

- `independent: true` prioriza proyectos periodísticos autónomos, cooperativas y publicaciones especializadas ajenas a grandes grupos generalistas. No equivale a imparcialidad ni a una auditoría societaria.
- `independent: false` marca a los medios consolidados que se incorporan para dar cobertura amplia (política, economía, deportes, tecnología, viajes) y presencia regional.
- La **insignia de independiente** se conserva en la interfaz: los artículos de medios `independent: true` se señalan como tales.
- El ranking **prioriza a los independientes para la apertura y los destacados**, pero mezcla medios consolidados en el cuerpo de cada sección.
- Se aplican **topes por región y por sección** (ver `REGION_CAPS` y `SECTION_REGION_CAP` en `scripts/build_diario.py`) para que España no domine la edición y Argentina mantenga una presencia fuerte. Las regiones más chicas quedan prácticamente sin tope.

La región indica el origen editorial del medio. Los blogs de viajes y los medios con orientación transnacional se agrupan en Mundo. El endpoint de ESPN se verifica, pero declara idioma inglés y se excluye de la edición en español por el mismo criterio de idioma que descarta feeds en portugués/inglés.

**Cambio de clasificación:** *Revista Anfibia* pasa a `independent: true` a pedido editorial, reconociéndola como proyecto periodístico autónomo pese a su vínculo con la UNSAM.

Referencias primarias consultadas para la búsqueda y el criterio:

- [la diaria: RSS oficial](https://ayuda.ladiaria.com.uy/seguir-a-la-diaria-a-traves-de-rss/) y [propiedad cooperativa](https://ayuda.ladiaria.com.uy/preguntas-frecuentes/).
- [Delfino.cr: periodismo independiente](https://delfino.cr/acerca/periodismo-independiente).
- [El Observador CR: origen digital y compromiso editorial](https://observador.cr/5-anos-comprometidos-con-el-periodismo-serio-e-independiente/).
- [Cenital: identificación editorial y societaria](https://cenital.com/politica-de-privacidad/).
- [Hipertextual: equipo e historia](https://hipertextual.com/acerca-de-hipertextual/).
- [Gigantes del Basket: titularidad](https://www.gigantes.com/nota-legal/) y [Punto de Break: titularidad](https://www.puntodebreak.com/aviso-legal.html). Estos medios especializados se incluyen en la prioridad editorial; no se afirma que carezcan de inversores privados.

## Catálogo por región

Leyenda: Independiente (insignia) · Verificado (RSS HTTP 200 + XML con entradas).

### Argentina

| Medio | Independiente | Verificado | Temas | RSS comprobado |
|---|---|---|---|---|
| elDiarioAR | Sí | Sí | Política, Economía | [RSS](https://www.eldiarioar.com/rss/) |
| Cenital | Sí | Sí | Política, Economía | [RSS](https://cenital.com/feed/) |
| Revista Anfibia | Sí | Sí | Política | [RSS](https://www.revistaanfibia.com/feed/) |
| Chequeado | Sí | Sí | Política, Economía | [RSS](https://chequeado.com/feed/) |
| El Destape | Sí | No | Política, Economía | [RSS](https://www.eldestapeweb.com/rss) |
| Infobae | No | Sí | Política, Economía | [RSS](https://www.infobae.com/arc/outboundfeeds/rss/?outputType=xml) |
| La Nación | No | Sí | Política, Economía | [RSS](https://www.lanacion.com.ar/arc/outboundfeeds/rss/?outputType=xml) |
| Clarín | No | Sí | Política, Economía | [RSS](https://www.clarin.com/rss/lo-ultimo/) |
| Perfil | No | Sí | Política, Economía | [RSS](https://www.perfil.com/feed) |
| Olé | No | Sí | Fútbol, Básquetbol, Tenis | [RSS](https://www.ole.com.ar/rss/ultimas-noticias/) |
| Infobae Deportes | No | Sí | Fútbol, Básquetbol, Tenis | [RSS](https://www.infobae.com/arc/outboundfeeds/rss/category/deportes/?outputType=xml) |
| Página/12 | No | No | Política, Economía | [RSS](https://www.pagina12.com.ar/rss/portada) |
| TyC Sports | No | No | Fútbol, Básquetbol, Tenis | [RSS](https://www.tycsports.com/rss.xml) |

### Uruguay

| Medio | Independiente | Verificado | Temas | RSS comprobado |
|---|---|---|---|---|
| la diaria | Sí | Sí | Política, Economía, Fútbol | [RSS](https://ladiaria.com.uy/feeds/articulos/) |
| Montevideo Portal | No | Sí | Política, Economía, Fútbol | [RSS](https://www.montevideo.com.uy/anxml.aspx?58) |
| Montevideo Deportes | No | Sí | Fútbol, Básquetbol, Tenis | [RSS](https://www.montevideo.com.uy/anxml.aspx?59) |
| Sudestada | Sí | No | Política, Economía | [RSS](https://www.sudestada.com.uy/feed/) |
| El País UY | No | No | Política, Economía | [RSS](https://www.elpais.com.uy/rss/) |
| El Observador UY | No | No | Política, Economía | [RSS](https://www.elobservador.com.uy/rss/home.xml) |
| Ovación | No | No | Fútbol, Básquetbol, Tenis | [RSS](https://www.elpais.com.uy/rss/ovacion) |

### Costa Rica

| Medio | Independiente | Verificado | Temas | RSS comprobado |
|---|---|---|---|---|
| Delfino.cr | Sí | Sí | Política, Economía | [RSS](https://delfino.cr/feed) |
| El Observador CR | Sí | Sí | Política, Economía | [RSS](https://observador.cr/feed/) |
| Semanario Universidad | No | Sí | Política, Economía | [RSS](https://semanariouniversidad.com/feed/) |
| La Nación CR | No | Sí | Política, Economía | [RSS](https://www.nacion.com/arc/outboundfeeds/rss/?outputType=xml) |
| CRHoy | No | No | Política, Economía | [RSS](https://www.crhoy.com/feed/) |
| Teletica | No | No | Política, Economía | [RSS](https://www.teletica.com/rss/) |

### España

| Medio | Independiente | Verificado | Temas | RSS comprobado |
|---|---|---|---|---|
| elDiario.es | Sí | Sí | Política, Economía | [RSS](https://www.eldiario.es/rss/) |
| El Confidencial | Sí | Sí | Política, Economía | [RSS](https://rss.elconfidencial.com/espana/) |
| infoLibre | Sí | Sí | Política, Economía | [RSS](https://www.infolibre.es/rss/) |
| Microsiervos | Sí | Sí | Tech, IA | [RSS](https://www.microsiervos.com/index.xml) |
| Gigantes del Basket | Sí | Sí | Básquetbol | [RSS](https://www.gigantes.com/feed/) |
| Solo Basket | Sí | Sí | Básquetbol | [RSS](https://www.solobasket.com/rss.xml) |
| Punto de Break | Sí | Sí | Tenis | [RSS](https://www.puntodebreak.com/rss.xml) |
| elDiario.es Viajes | Sí | Sí | Viajes | [RSS](https://www.eldiario.es/rss/viajes/) |
| El País | No | Sí | Política, Economía | [RSS](https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada) |
| RTVE | No | Sí | Política, Economía | [RSS](https://api2.rtve.es/rss/temas_noticias.xml) |
| Xataka | No | Sí | Tech, IA | [RSS](https://www.xataka.com/index.xml) |
| Genbeta | No | Sí | Tech, IA | [RSS](https://www.genbeta.com/index.xml) |
| Marca | No | Sí | Fútbol, Básquetbol, Tenis | [RSS](https://e00-marca.uecdn.es/rss/portada.xml) |
| Público | No | No | Política, Economía | [RSS](https://www.publico.es/rss/) |

### Mundo

| Medio | Independiente | Verificado | Temas | RSS comprobado |
|---|---|---|---|---|
| Agencia Pública | Sí | Sí | Política, Economía | [RSS](https://apublica.org/feed/) |
| Hipertextual | Sí | Sí | Tech, IA | [RSS](https://hipertextual.com/feed) |
| Viajeros Callejeros | Sí | Sí | Viajes | [RSS](https://www.viajeroscallejeros.com/feed/) |
| Viajablog | Sí | Sí | Viajes | [RSS](https://www.viajablog.com/feed/) |
| El Pachinko | Sí | Sí | Viajes | [RSS](https://www.elpachinko.com/feed/) |
| BBC Mundo | No | Sí | Política, Economía | [RSS](https://feeds.bbci.co.uk/mundo/rss.xml) |
| DW español | No | Sí | Política, Economía | [RSS](https://rss.dw.com/rdf/rss-sp-all) |
| France24 español | No | Sí | Política, Economía | [RSS](https://www.france24.com/es/rss) |
| Euronews en español | No | Sí | Política, Economía | [RSS](https://es.euronews.com/rss) |
| MIT Technology Review en español | No | Sí | Tech, IA | [RSS](https://www.technologyreview.es/rss) |
| Lonely Planet ES | No | Sí | Viajes | [RSS](https://www.lonelyplanet.es/rss.xml) |
| Diario del Viajero | No | Sí | Viajes | [RSS](https://www.diariodelviajero.com/index.xml) |
| ESPN | No | Sí | Fútbol, Básquetbol, Tenis | [RSS](https://www.espn.com/espn/rss/news?section=deportes) |
| El Faro | Sí | No | Política, Economía | [RSS](https://elfaro.net/es/rss.xml) |
| FutbolRed | No | No | Fútbol | [RSS](https://www.futbolred.com/rss) |
| CNN en Español | No | No | Política, Economía | [RSS](https://cnnespanol.cnn.com/feed/) |

## Endpoints fallidos

| Medio | Endpoint | Resultado observado |
|---|---|---|
| El Destape | `https://www.eldestapeweb.com/rss` | HTTP Error 404: Not Found |
| Sudestada | `https://www.sudestada.com.uy/feed/` | unbound prefix (XML con prefijo no declarado) |
| Público | `https://www.publico.es/rss/` | HTTP Error 404: Not Found |
| El Faro | `https://elfaro.net/es/rss.xml` | not well-formed (devuelve HTML, no RSS) |
| Ovación | `https://www.elpais.com.uy/rss/ovacion` | HTTP Error 403: Forbidden |
| FutbolRed | `https://www.futbolred.com/rss` | not well-formed (devuelve HTML, no RSS) |
| Página/12 | `https://www.pagina12.com.ar/rss/portada` | HTTP Error 404 en todas las rutas probadas (`/rss/portada`, `/rss/portada.xml`, `/rss/secciones/...`) |
| TyC Sports | `https://www.tycsports.com/rss.xml` | HTTP Error 404 (`/rss.xml`, `/rss/`, `/rss/ultimas-noticias.xml`) |
| El País UY | `https://www.elpais.com.uy/rss/` | HTTP Error 403: Forbidden (bloqueo del grupo El País UY) |
| El Observador UY | `https://www.elobservador.com.uy/rss/home.xml` | HTTP Error 404 (`/rss/home.xml`, `/rss/`, `/arc/outboundfeeds/...`) |
| CRHoy | `https://www.crhoy.com/feed/` | HTTP Error 404 (`/feed/`, `/rss/`, `/rss.xml`) |
| Teletica | `https://www.teletica.com/rss/` | not well-formed (invalid token): la respuesta no es XML válido |
| CNN en Español | `https://cnnespanol.cnn.com/feed/` | HTTP Error 404 en `/feed/` y feeds de sección |

## Notas sobre endpoints nuevos comprobados

- **Infobae, La Nación (AR), La Nación CR, El País (ES):** los feeds productivos están en `/arc/outboundfeeds/rss/` (plataforma Arc) o en `feeds.elpais.com`; las rutas antiguas `/feeds/rss/` dieron 404.
- **AP / Reuters:** no se encontró un RSS público operativo (Reuters discontinuó sus feeds abiertos y AP no publica uno general accesible), por eso no se añadieron. En su lugar, para Mundo se incorporaron **Euronews en español** y **MIT Technology Review en español**, ambos verificados.
- **WIRED en español** tiene RSS válido pero declara `language: en-US`, por lo que el filtro de idioma lo excluiría; no se añadió.
- Los medios uruguayos consolidados (El País UY, El Observador UY) y varios costarricenses/CNN fallan desde este entorno por bloqueo (403) o rutas inexistentes (404); se conservan en el catálogo con `verified: false` para revisarlos.

## Reproducir

```bash
python3 scripts/verify_sources.py   # revalida todos los endpoints y reescribe sources.json + feed-verification.json
python3 scripts/build_diario.py     # arma la edición
bash scripts/daily_update.sh        # rearma y publica sólo si cambió data/
```

No se usa Google News ni un proxy de feeds. Las URL de los artículos seleccionados se verifican por separado al preparar cada edición.
