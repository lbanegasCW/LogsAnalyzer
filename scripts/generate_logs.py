# Para generar logs con el script se debe correr:
# python .\generate_logs.py -o .\access.log --size-gb 1
import os
import random
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

METHODS = ["GET", "POST", "PUT", "DELETE"]
STATUS_CODES = [200, 201, 204, 301, 302, 400, 401, 403, 404, 429, 500, 502, 503]

BASE_URLS = [
    "/",
    "/index.html",
    "/login",
    "/logout",
    "/products",
    "/products/123",
    "/cart",
    "/checkout",
    "/api/v1/items",
    "/api/v1/items/123",
    "/search",
    "/assets/app.js",
    "/assets/styles.css",
    "/images/banner.jpg",
]


@dataclass
class Config:
    output: Path
    target_bytes: int
    batch_lines: int = 5000
    add_query_prob: float = 0.35      # % de URLs con querystring (para hacer líneas más largas)
    query_len_min: int = 10
    query_len_max: int = 80
    days_back: int = 60               # fechas aleatorias en los últimos N días
    seed: int | None = None
    progress_every_mb: int = 100      # imprime progreso cada X MB


def random_ip() -> str:
    # Evita 0 y 255 para que se vea más realista
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def random_date_str(days_back: int) -> str:
    now = datetime.now()
    dt = now - timedelta(
        days=random.randint(0, days_back),
        seconds=random.randint(0, 24 * 60 * 60 - 1),
    )
    # Formato: 10/Sep/2024:15:03:27
    return f"{dt.day:02d}/{MONTHS[dt.month - 1]}/{dt.year}:{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"


def random_query_string(min_len: int, max_len: int) -> str:
    n = random.randint(min_len, max_len)
    # Query simple: ?q=...&p=...
    alphabet = string.ascii_letters + string.digits
    token = "".join(random.choice(alphabet) for _ in range(n))
    return f"?q={token}&p={random.randint(1, 9999)}"


def random_url(cfg: Config) -> str:
    url = random.choice(BASE_URLS)
    if random.random() < cfg.add_query_prob:
        url += random_query_string(cfg.query_len_min, cfg.query_len_max)
    return url


def random_response_time_ms() -> int:
    # Distribución simple: la mayoría rápida, algunas lentas
    r = random.random()
    if r < 0.85:
        return random.randint(20, 350)
    if r < 0.97:
        return random.randint(351, 1200)
    return random.randint(1201, 8000)


def generate_line(cfg: Config) -> str:
    ip = random_ip()
    date_str = random_date_str(cfg.days_back)
    method = random.choice(METHODS)
    url = random_url(cfg)
    status = random.choice(STATUS_CODES)
    rt = random_response_time_ms()
    # Formato EXACTO pedido:
    # IP_Address - - [Date] "Request_Type URL" Status_Code Response_Time
    return f'{ip} - - [{date_str}] "{method} {url}" {status} {rt}\n'


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Genera un archivo de logs sintéticos (>= 1GB por defecto).")
    parser.add_argument("-o", "--output", default="access.log", help="Ruta del archivo de salida (default: access.log)")
    parser.add_argument("--size-gb", type=float, default=1.0, help="Tamaño mínimo en GB (default: 1.0)")
    parser.add_argument("--seed", type=int, default=None, help="Seed para reproducibilidad")
    args = parser.parse_args()

    cfg = Config(
        output=Path(args.output),
        target_bytes=int(args.size_gb * 1024**3),
        seed=args.seed,
    )

    if cfg.seed is not None:
        random.seed(cfg.seed)

    cfg.output.parent.mkdir(parents=True, exist_ok=True)

    bytes_written = 0
    next_progress = cfg.progress_every_mb * 1024**2

    # Escribimos en binario para contar bytes exactos (UTF-8 sin sorpresas)
    with open(cfg.output, "wb") as f:
        while bytes_written < cfg.target_bytes:
            lines: List[str] = [generate_line(cfg) for _ in range(cfg.batch_lines)]
            chunk = "".join(lines).encode("utf-8")
            f.write(chunk)
            bytes_written += len(chunk)

            if bytes_written >= next_progress:
                mb = bytes_written / (1024**2)
                print(f"Progreso: {mb:,.0f} MB escritos en {cfg.output}")
                next_progress += cfg.progress_every_mb * 1024**2

    final_size = os.path.getsize(cfg.output)
    print(f"\nOK: generado {cfg.output} con {final_size / (1024**3):.3f} GB ({final_size:,} bytes).")


if __name__ == "__main__":
    main()