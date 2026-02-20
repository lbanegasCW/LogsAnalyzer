"""Pruebas para utilidades del parser."""

from logproc.parser import parse_line


def test_parse_log_line_ok():
    line = '192.168.0.1 - - [10/Sep/2024:15:03:27] "GET /index.html" 200 125'
    assert parse_line(line) == ("/index.html", 200, 125)


def test_parse_log_line_bad():
    assert parse_line("línea malformada") is None
