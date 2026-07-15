"""
[Day 1 종합 실습] 데이터 수집 미니 파이프라인

주요 기능
1. asyncio와 httpx를 이용해 3개 API를 동시에 호출
2. Pydantic v2 모델로 API 응답의 타입과 범위 검증
3. 검증을 통과한 데이터를 CSV와 Parquet으로 저장
4. CSV와 Parquet의 읽기·쓰기 시간을 측정하여 비교
"""

import asyncio
import time
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from pydantic import ValidationError

from models import CountryRecord, IPRecord, WeatherRecord


# --------------------------------------------------
# API 및 파일 경로 설정
# --------------------------------------------------

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.5665"
    "&longitude=126.9780"
    "&hourly=temperature_2m,precipitation_probability"
    "&forecast_days=3"
    "&timezone=Asia/Seoul"
)

COUNTRY_URL = "https://countries.dev/alpha/KR"
IP_URL = "http://ip-api.com/json/8.8.8.8"

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
CSV_FILE = OUTPUT_DIR / "collected_data.csv"
PARQUET_FILE = OUTPUT_DIR / "collected_data.parquet"


# --------------------------------------------------
# API 호출
# --------------------------------------------------

# 지정한 API를 호출하고 JSON 응답을 반환한다.
async def fetch_json(
    client: httpx.AsyncClient,
    url: str,
) -> Any:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


# 3개 API를 asyncio.gather()로 동시에 호출한다.
async def collect_api_data() -> tuple[Any, Any, Any]:
    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
    ) as client:
        weather_data, country_data, ip_data = await asyncio.gather(
            fetch_json(client, WEATHER_URL),
            fetch_json(client, COUNTRY_URL),
            fetch_json(client, IP_URL),
        )

    return weather_data, country_data, ip_data


# --------------------------------------------------
# Pydantic 검증
# --------------------------------------------------

# Open-Meteo 응답을 시간대별 WeatherRecord로 변환한다.
def validate_weather(data: dict[str, Any]) -> list[WeatherRecord]:
    hourly = data["hourly"]

    times = hourly["time"]
    temperatures = hourly["temperature_2m"]
    probabilities = hourly["precipitation_probability"]

    return [
        WeatherRecord(
            time=time_value,
            temperature=temperature,
            precipitation_probability=probability,
        )
        for time_value, temperature, probability in zip(
            times,
            temperatures,
            probabilities,
            strict=True,
        )
    ]


# countries.dev 응답에서 필요한 필드를 추출하고 검증한다.
def validate_country(data: dict[str, Any]) -> CountryRecord:
    return CountryRecord(
        name=data["name"],
        capital=data["capital"],
        population=data["population"],
        region=data["region"],
    )


# ip-api 응답에서 필요한 필드를 추출하고 검증한다.
def validate_ip(data: dict[str, Any]) -> IPRecord:
    return IPRecord(
        status=data["status"],
        query=data["query"],
        country=data["country"],
        city=data["city"],
        latitude=data["lat"],
        longitude=data["lon"],
        isp=data["isp"],
    )


# 세 API의 응답을 검증하고 하나의 딕셔너리 리스트로 만든다.
def validate_all_data(
    weather_data: dict[str, Any],
    country_data: dict[str, Any],
    ip_data: dict[str, Any],
) -> list[dict[str, Any]]:
    weather_records = validate_weather(weather_data)
    country_record = validate_country(country_data)
    ip_record = validate_ip(ip_data)

    all_records = [*weather_records, country_record, ip_record]

    return [record.model_dump(mode="json") for record in all_records]


# --------------------------------------------------
# CSV·Parquet 저장 및 성능 측정
# --------------------------------------------------

# CSV와 Parquet의 저장 시간을 측정한다.
def measure_write_time(
    dataframe: pd.DataFrame,
) -> tuple[float, float]:
    csv_start = time.perf_counter()
    dataframe.to_csv(
        CSV_FILE,
        index=False,
        encoding="utf-8-sig",
    )
    csv_write_time = time.perf_counter() - csv_start

    parquet_start = time.perf_counter()
    dataframe.to_parquet(
        PARQUET_FILE,
        index=False,
    )
    parquet_write_time = time.perf_counter() - parquet_start

    return csv_write_time, parquet_write_time


# CSV와 Parquet의 재로딩 시간을 측정한다.
def measure_read_time() -> tuple[pd.DataFrame, pd.DataFrame, float, float]:
    csv_start = time.perf_counter()
    csv_reloaded = pd.read_csv(CSV_FILE)
    csv_read_time = time.perf_counter() - csv_start

    parquet_start = time.perf_counter()
    parquet_reloaded = pd.read_parquet(PARQUET_FILE)
    parquet_read_time = time.perf_counter() - parquet_start

    return (
        csv_reloaded,
        parquet_reloaded,
        csv_read_time,
        parquet_read_time,
    )


# --------------------------------------------------
# 프로그램 실행
# --------------------------------------------------

# 데이터 수집부터 검증, 저장, 성능 비교까지 실행한다.
async def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    try:
        print("[1] API 3개 동시 수집 시작")

        weather_data, country_data, ip_data = await collect_api_data()

        print("[2] API 수집 완료")
        print("[3] Pydantic 데이터 검증 시작")

        validated_records = validate_all_data(
            weather_data,
            country_data,
            ip_data,
        )

        dataframe = pd.DataFrame(validated_records)

        print(f"[4] 검증 완료: {len(dataframe)}건")

        csv_write, parquet_write = measure_write_time(dataframe)

        (
            csv_reloaded,
            parquet_reloaded,
            csv_read,
            parquet_read,
        ) = measure_read_time()

        # 저장 전후 데이터 건수가 동일한지 확인한다.
        assert len(csv_reloaded) == len(dataframe)
        assert len(parquet_reloaded) == len(dataframe)

        print("\n[저장 결과]")
        print(f"CSV 파일: {CSV_FILE}")
        print(f"Parquet 파일: {PARQUET_FILE}")

        print("\n[성능 비교]")
        print(f"CSV 쓰기: {csv_write:.6f}초")
        print(f"Parquet 쓰기: {parquet_write:.6f}초")
        print(f"CSV 읽기: {csv_read:.6f}초")
        print(f"Parquet 읽기: {parquet_read:.6f}초")

        print("\n데이터 수집 파이프라인 실행 완료")

    except httpx.HTTPStatusError as error:
        print(
            "HTTP 응답 오류:",
            error.response.status_code,
            error.request.url,
        )

    except httpx.RequestError as error:
        print(f"API 연결 오류: {error}")

    except ValidationError as error:
        print(f"Pydantic 검증 오류:\n{error}")

    except (KeyError, IndexError, ValueError) as error:
        print(f"API 응답 데이터 오류: {error}")


if __name__ == "__main__":
    asyncio.run(main())