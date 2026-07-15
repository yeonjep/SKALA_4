"""
Day 1 데이터 수집 파이프라인의 Pydantic 스키마 테스트
"""

import pytest
from pydantic import ValidationError

from models import WeatherRecord


def test_weather_record_validation() -> None:
    """정상 날씨는 통과하고 잘못된 강수확률은 실패하는지 확인한다."""

    valid_weather = WeatherRecord(
        time="2026-07-15T15:00",
        temperature=28.5,
        precipitation_probability=40,
    )

    assert valid_weather.temperature == 28.5
    assert valid_weather.precipitation_probability == 40

    with pytest.raises(ValidationError):
        WeatherRecord(
            time="2026-07-15T15:00",
            temperature=28.5,
            precipitation_probability=120,
        )