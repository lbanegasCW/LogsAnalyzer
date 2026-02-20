# logproc

Procesador eficiente de logs grandes con arquitectura limpia y dos interfaces: CLI + Dashboard Django.

## Arquitectura

El repositorio separa **núcleo reutilizable** de interfaces:

- `logproc/` (core):
  - `reader.py`: lectura streaming en batches (sin cargar archivo completo).
  - `parser.py`: `parse_line` pura y testeable.
  - `worker.py`: `process_batch` para lotes.
  - `reducer.py`: merge de parciales.
  - `metrics.py`: dataclasses/resultados + helpers top URLs.
  - `api.py`: **API pública estable** `process_log(...)` para CLI/Web.
- `logproc/__main__.py` (CLI): solo parsea args y delega en `logproc.api`.
- `logproc_web/` (Django): interfaz web que también llama a `logproc.api`.

Principios aplicados:

- E/S eficiente vía streaming + batching.
- Complejidad temporal O(n).
- Memoria acotada a batch + agregados (`dict/Counter`).
- Concurrencia controlada (`ProcessPoolExecutor` configurable).
- Profiling con cProfile opcional.
- Sin optimización prematura: claridad primero, medir luego.

## Uso CLI

```bash
python -m logproc --input /ruta/access.log --batch-size 10000 --slow-threshold 200 --status 500 --workers 4 --json-out out.json --profile
```

Parámetros:

- `--input` obligatorio.
- `--batch-size` por defecto `10000`.
- `--slow-threshold` por defecto `200`.
- `--status` por defecto `500`.
- `--workers` por defecto `os.cpu_count()`.
- `--json-out` opcional.
- `--profile` opcional.
- `--profile-stats-path` default `profile.stats`.

## Web Dashboard

### Características

- Listado de ejecuciones con filtros por estado y fecha.
- Alta de nueva ejecución con:
  - `input_path` (recomendado para logs grandes).
  - upload opcional (solo pruebas pequeñas).
  - parámetros de procesamiento.
  - checkbox de profiling.
- Detalle de ejecución con cards de métricas, tablas top 10 y gráfico simple (Chart.js CDN).
- Ejecución en background con hilo daemon para no bloquear request.

> Nota: para producción se recomienda reemplazar runner thread por Celery/RQ con workers externos y retries.

### Ejecutar Django

1. Instalar dependencias:

```bash
pip install -e .[dev]
```

2. Migrar DB:

```bash
python manage.py migrate
```

3. Levantar servidor:

```bash
python manage.py runserver
```

4. Abrir `http://127.0.0.1:8000/` para crear ejecuciones y ver métricas.

## Profiling

CLI o dashboard pueden ejecutar con profiling:

- se guarda archivo `.stats`
- se puede inspeccionar con:

```bash
python -c "import pstats; p=pstats.Stats('profile.stats'); p.sort_stats('cumtime').print_stats(30)"
```

## Documentación

Se incluye Sphinx con autodoc en `docs/`.

### Generar HTML

```bash
pip install -e .[dev]
make -C docs html
```

Salida en `docs/_build/html/index.html`.

## Tests

```bash
pytest -q
```

## Estructura final del repositorio

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
