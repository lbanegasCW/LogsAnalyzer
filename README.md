# logproc

Procesador de logs grande (varios GB) con **streaming + batching + paralelismo por bloques**.

## Objetivo
Procesar líneas con formato:

```text
IP_Address - - [Date] "Request_Type URL" Status_Code Response_Time
```

y calcular métricas sobre:

- errores de servidor (`status == 500`, configurable)
- solicitudes lentas (`response_time > 200 ms`, configurable)
- líneas malformadas (`bad_lines`)

## Diseño y eficiencia

- **Complejidad temporal:** `O(n)` sobre cantidad de líneas.
- **Memoria acotada:** no se guardan todas las líneas, solo agregados (`Counter`/dict).
- **E/S eficiente:** lectura lineal + lotes fijos (10.000 por default).
- **Paralelismo:** cada lote se procesa en worker (`ProcessPoolExecutor`) y luego se mergean parciales.
- **Robustez:** líneas corruptas no abortan el proceso; se contabilizan en `bad_lines`.

> Nota de ingeniería: se prioriza claridad + correcta arquitectura. La optimización fina debe basarse en mediciones reales, no en optimización prematura.

## Uso

```bash
python -m logproc --input /ruta/access.log --batch-size 10000 --slow-threshold 200 --status 500 --workers 4 --json-out out.json --profile
```

Parámetros principales:

- `--input` (obligatorio)
- `--batch-size` (default: `10000`)
- `--slow-threshold` (default: `200`)
- `--status` (default: `500`)
- `--workers` (default: `os.cpu_count()`)
- `--json-out` (opcional)
- `--profile` (opcional, activa cProfile)
- `--profile-stats-path` (default: `profile.stats`)

## Profiling

Con `--profile`:

1. se corre el procesamiento bajo `cProfile`
2. se guarda archivo de stats (`profile.stats` por default)
3. se imprime top de funciones por `cumtime`

Ejemplo para inspección posterior:

```bash
python -c "import pstats; p=pstats.Stats('profile.stats'); p.sort_stats('cumtime').print_stats(30)"
```

Interpretación rápida:

- Si domina parsing, optimizar parser.
- Si domina IO, revisar disco/buffering/infra.
- Si domina serialización IPC (multiprocessing), ajustar `batch-size` o `workers`.

## Tests

```bash
pytest -q
```

Incluye tests para:

- filtrado de status 500 y URL top
- filtrado de lentas y URL top
- procesamiento end-to-end con archivo temporal, lotes pequeños y `bad_lines`
