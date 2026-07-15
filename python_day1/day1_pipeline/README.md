# Day 1 종합 실습 – 데이터 수집 미니 파이프라인

SKALA 2) AI의 서비스화 데이터분석 및 AIOps – Day 1 종합 실습 과제입니다.
3개의 외부 API를 비동기로 동시에 호출하고, Pydantic v2로 응답을 검증한 뒤
CSV·Parquet 두 형식으로 저장하며 읽기/쓰기 성능을 비교합니다.

## 주요 기능

- `asyncio` + `httpx`로 3개 API를 `asyncio.gather()`를 통해 동시 수집
- Pydantic v2 모델로 타입·범위 검증 (범위를 벗어나면 예외 처리)
- 검증을 통과한 데이터를 CSV / Parquet으로 저장
- CSV·Parquet의 읽기·쓰기 시간을 측정하여 비교
- `pytest`로 스키마 검증 테스트, `ruff`로 코드 스타일 검사

## 사용 API

| API | 설명 | 엔드포인트 |
| --- | --- | --- |
| Open-Meteo | 서울 3일 시간대별 기온·강수확률 | `https://api.open-meteo.com/v1/forecast` |
| countries.dev | 대한민국 국가 정보 (RestCountries v3.1 지원 종료로 대체) | `https://countries.dev/alpha/KR` |
| ip-api | IP 기반 지역 정보 | `http://ip-api.com/json/8.8.8.8` |

## 폴더 구조

    day1_pipeline/
    ├── main.py           # 파이프라인 실행 (수집 → 검증 → 저장 → 성능 비교)
    ├── models.py         # Pydantic 모델 (WeatherRecord, CountryRecord, IPRecord)
    ├── test_main.py      # 스키마 검증 테스트
    ├── requirements.txt  # 의존성 목록
    └── output/           # 결과 저장 폴더 (collected_data.csv / .parquet)

## 설치 방법

1. 가상환경 생성 및 활성화

       python -m venv .venv
       source .venv/bin/activate

2. 의존성 설치

       pip install -r requirements.txt

## 실행 방법

    python main.py

## 테스트 및 코드 검사

    pytest -v
    ruff check .

## 실행 결과 예시

    [1] API 3개 동시 수집 시작
    [2] API 수집 완료
    [3] Pydantic 데이터 검증 시작
    [4] 검증 완료: 74건

    [저장 결과]
    CSV 파일: output/collected_data.csv
    Parquet 파일: output/collected_data.parquet

    [성능 비교]
    CSV 쓰기: 0.008797초
    Parquet 쓰기: 2.233102초
    CSV 읽기: 0.001232초
    Parquet 읽기: 1.665397초

## 성능 비교 분석

작은 규모(74건)의 데이터에서는 Parquet의 컬럼 압축·스키마 인코딩 오버헤드 때문에
CSV보다 쓰기·읽기 모두 오히려 느리게 측정되었습니다. Parquet의 이점은 데이터 규모가
훨씬 커지고(수십만 건 이상) 컬럼 단위 조회가 잦아질 때부터 드러납니다.

## 데이터 수집 파이프라인 개요

1. `collect_api_data()`가 `asyncio.gather()`로 3개 API를 동시에 호출합니다.
2. `validate_weather`, `validate_country`, `validate_ip`가 각 응답을 Pydantic
   모델(`WeatherRecord`, `CountryRecord`, `IPRecord`)로 검증합니다.
3. 검증된 레코드를 하나의 DataFrame으로 합쳐 CSV와 Parquet으로 저장합니다.
4. 저장된 파일을 다시 읽어 들여 원본과 건수가 같은지 확인하고, 읽기·쓰기
   소요 시간을 각각 측정해 출력합니다.
