"""End-to-end and unit tests for processing pipeline."""

from logproc.api import process_log
from logproc.worker import process_batch


def test_filtrado_500():
    batch = [
        '10.0.0.1 - - [10/Sep/2024:15:03:27] "GET /a" 500 100',
        '10.0.0.2 - - [10/Sep/2024:15:03:28] "GET /a" 500 90',
        '10.0.0.3 - - [10/Sep/2024:15:03:29] "GET /b" 500 80',
        '10.0.0.4 - - [10/Sep/2024:15:03:30] "GET /c" 200 50',
    ]

    partial = process_batch(batch, status_code=500, slow_threshold=200)
    assert partial.total_status == 3
    assert partial.status_by_url["/a"] == 2
    assert max(partial.status_by_url.items(), key=lambda x: x[1]) == ("/a", 2)


def test_filtrado_lento():
    batch = [
        '10.0.0.1 - - [10/Sep/2024:15:03:27] "GET /slow" 200 250',
        '10.0.0.2 - - [10/Sep/2024:15:03:28] "GET /slow" 200 300',
        '10.0.0.3 - - [10/Sep/2024:15:03:29] "GET /other" 200 210',
        '10.0.0.4 - - [10/Sep/2024:15:03:30] "GET /fast" 200 90',
    ]

    partial = process_batch(batch, status_code=500, slow_threshold=200)
    assert partial.total_slow == 3
    assert partial.slow_by_url["/slow"] == 2
    assert max(partial.slow_by_url.items(), key=lambda x: x[1]) == ("/slow", 2)


def test_procesamiento_archivo(tmp_path):
    lines = [
        '10.0.0.1 - - [10/Sep/2024:15:03:27] "GET /a" 500 250',
        '10.0.0.2 - - [10/Sep/2024:15:03:28] "GET /b" 200 201',
        '10.0.0.3 - - [10/Sep/2024:15:03:29] "GET /a" 500 190',
        "bad line that should be ignored",
        '10.0.0.4 - - [10/Sep/2024:15:03:30] "GET /c" 200 50',
    ]

    log_file = tmp_path / "access.log"
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = process_log(
        str(log_file),
        batch_size=2,
        slow_threshold=200,
        status_code=500,
        workers=1,
    )

    assert result.total_lines == 5
    assert result.bad_lines == 1
    assert result.total_status == 2
    assert result.total_slow == 2
    assert result.top_url_status == ("/a", 2)
    assert result.top_url_slow == ("/a", 1)
