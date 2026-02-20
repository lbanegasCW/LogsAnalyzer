# logproc

Procesador eficiente de logs grandes con arquitectura limpia y dos interfaces: **CLI** y **Dashboard Django**.

## Qué hace

`logproc` procesa archivos de access logs en modo streaming, calcula métricas agregadas y devuelve:

- Total de líneas procesadas.
- Total de líneas malformadas.
- Total de respuestas para uno o más códigos HTTP.
- Total de requests lentas por umbral configurable.
- Top URLs por código de estado y por lentitud.

Está pensado para archivos grandes sin cargar todo en memoria.

## Arquitectura

El repositorio separa el núcleo reutilizable de las interfaces:

- `logproc/` (**core**)
  - `reader.py`: lectura streaming en batches.
  - `parser.py`: parsing puro y testeable.
  - `worker.py`: procesamiento por lote.
  - `reducer.py`: merge de parciales.
  - `metrics.py`: dataclasses + helpers de top URLs.
  - `api.py`: API pública estable `process_log(...)`.
- `logproc/__main__.py` (**CLI**): parsea argumentos y delega en `logproc.api`.
- `logproc_web/` (**Django**): interfaz web que usa la misma API de core.

Principios aplicados:

- Streaming + batching para E/S eficiente.
- Complejidad temporal O(n).
- Memoria acotada a batch + agregados.
- Concurrencia configurable con `ProcessPoolExecutor`.
- Profiling opcional con `cProfile`.

## Instalación

```bash
pip install -e .[dev]
```

## Uso por CLI

```bash
python -m logproc \
  --input /ruta/access.log \
  --batch-size 10000 \
  --slow-threshold 200 \
  --status 500 \
  --workers 4 \
  --json-out out.json \
  --profile
```

Parámetros principales:

- `--input` (obligatorio): ruta al archivo de log.
- `--batch-size` (default: `10000`).
- `--slow-threshold` (default: `200`).
- `--status` (default: `500`).
- `--workers` (default: `os.cpu_count()`).
- `--json-out` (opcional): exporta el resumen en JSON.
- `--profile` (opcional): ejecuta con cProfile.
- `--profile-stats-path` (default: `profile.stats`).

## API pública de procesamiento

La función principal es:

- `logproc.api.process_log(...)`

Permite integración desde scripts, servicios o la app web, sin depender de la CLI.

## Dashboard web (Django)

### Funcionalidades

- Listado de ejecuciones con filtros por estado y fecha.
- Creación de ejecución con dos modos de entrada:
  - Ruta de archivo (`input_path`), recomendado para archivos grandes.
  - Upload de archivo (más útil para pruebas pequeñas).
- Configuración de parámetros por corrida:
  - `batch_size`, `slow_threshold`, `status_codes`, `workers`, `profile`.
- Ejecución en background para no bloquear la request.
- Vista de detalle con:
  - Métricas generales.
  - Top 10 URLs por códigos de estado y por lentitud.
  - Gráfico de barras simple (Chart.js).

> Nota: para producción se recomienda reemplazar el runner en hilo por Celery o RQ.

### Levantar el dashboard

```bash
python manage.py migrate
python manage.py runserver
```

Luego abrir `http://127.0.0.1:8000/`.

## Profiling

Tanto en CLI como en dashboard se puede ejecutar con profiling.

Para inspeccionar un archivo de stats:

```bash
python -c "import pstats; p=pstats.Stats('profile.stats'); p.sort_stats('cumtime').print_stats(30)"
```

## Tests

```bash
pytest -q
```

## Documentación (Sphinx)

```bash
make -C docs html
```

Salida: `docs/_build/html/index.html`.

## Estructura del repositorio

```text
.
├── docs/
├── logproc/
├── logproc_web/
│   └── dashboard/
├── tests/
├── manage.py
├── pyproject.toml
└── README.md
```
