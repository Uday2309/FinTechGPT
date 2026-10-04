from datetime import date
from app.services.xirr import xirr


def test_xirr_positive_example():
    result = xirr([
        (date(2025, 1, 1), -1000.0),
        (date(2026, 1, 1), 1100.0),
    ])
    assert result is not None
    assert 0.09 < result < 0.11
