"""
울산_4반_박연제_practice 3번

[실습 3] Pandas EDA / Polars Lazy / DuckDB SQL 비교

sales_100k.csv를 대상으로
1) Pandas 기초 EDA + IQR 이상치 처리
2) Pandas groupby named aggregation (region/category별 총매출/평균/건수)
3) Polars Lazy API로 동일 집계
4) DuckDB SQL로 동일 집계 + 세 도구 성능(timeit) 비교를 수행한다.
"""


import timeit
from pathlib import Path
import duckdb
import pandas as pd
import polars as pl

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "sales_100k.csv"

AMOUNT_COLUMN = "amount"
GROUP_COLUMNS = ["region", "category"]
REQUIRED_COLUMNS = {AMOUNT_COLUMN, *GROUP_COLUMNS}
TIMEIT_REPEAT = 3


# CSV를 로딩하고 기본 구조·결측치를 출력한다.
def explore_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")

    print("[1] 데이터 구조")
    df.info()

    print("\n[1] 컬럼별 결측치 개수")
    print(df.isnull().sum())

    return df


# 집계에 필요한 컬럼이 모두 있는지 검증한다.
def validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise KeyError(f"필수 컬럼 누락: {missing}")


# IQR 방법으로 이상치 정상 범위(하한, 상한)를 계산한다.
def compute_iqr_bounds(df: pd.DataFrame, column: str) -> tuple[float, float]:
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


# IQR 정상 범위를 벗어난 행을 제거한다.
def filter_outliers(
    df: pd.DataFrame,
    column: str,
    lower_bound: float,
    upper_bound: float,
) -> pd.DataFrame:
    return df[df[column].between(lower_bound, upper_bound)]


# Pandas로 CSV를 읽어 이상치를 제거하고 region·category별 named aggregation을 수행한다.
def pandas_pipeline(
    path: Path,
    lower_bound: float,
    upper_bound: float,
) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    filtered = filter_outliers(df, AMOUNT_COLUMN, lower_bound, upper_bound)

    return (
        filtered.groupby(GROUP_COLUMNS)
        .agg(
            total=(AMOUNT_COLUMN, "sum"),
            mean=(AMOUNT_COLUMN, "mean"),
            count=(AMOUNT_COLUMN, "count"),
        )
        .reset_index()
        .sort_values("total", ascending=False)
    )


# Polars Lazy API로 Pandas와 동일한 집계를 수행한다.
def polars_pipeline(
    path: Path,
    lower_bound: float,
    upper_bound: float,
) -> pl.DataFrame:
    return (
        pl.scan_csv(path)
        .filter(pl.col(AMOUNT_COLUMN).is_between(lower_bound, upper_bound))
        .group_by(GROUP_COLUMNS)
        .agg(
            pl.col(AMOUNT_COLUMN).sum().alias("total"),
            pl.col(AMOUNT_COLUMN).mean().alias("mean"),
            pl.col(AMOUNT_COLUMN).count().alias("count"),
        )
        .sort("total", descending=True)
        .collect()
    )


# DuckDB SQL로 Pandas와 동일한 집계를 수행한다.
def duckdb_pipeline(
    path: Path,
    lower_bound: float,
    upper_bound: float,
) -> pd.DataFrame:
    query = f"""
        SELECT
            region,
            category,
            SUM({AMOUNT_COLUMN}) AS total,
            AVG({AMOUNT_COLUMN}) AS mean,
            COUNT({AMOUNT_COLUMN}) AS count
        FROM read_csv_auto('{path.as_posix()}')
        WHERE {AMOUNT_COLUMN} BETWEEN {lower_bound} AND {upper_bound}
        GROUP BY region, category
        ORDER BY total DESC
    """

    return duckdb.sql(query).df()


# 세 도구의 실행 시간을 동일 조건(timeit, 3회 반복)으로 측정하고 평균을 비교한다.
def compare_performance(
    path: Path,
    lower_bound: float,
    upper_bound: float,
) -> dict[str, float]:
    pipelines = {
        "pandas": lambda: pandas_pipeline(path, lower_bound, upper_bound),
        "polars": lambda: polars_pipeline(path, lower_bound, upper_bound),
        "duckdb": lambda: duckdb_pipeline(path, lower_bound, upper_bound),
    }

    return {
        name: sum(timeit.repeat(func, number=1, repeat=TIMEIT_REPEAT)) / TIMEIT_REPEAT
        for name, func in pipelines.items()
    }


# 데이터 탐색부터 세 도구 집계, 성능 비교까지 실행한다.
def main() -> None:
    try:
        df = explore_data(CSV_FILE)
        validate_columns(df)

        lower_bound, upper_bound = compute_iqr_bounds(df, AMOUNT_COLUMN)
        cleaned_df = filter_outliers(df, AMOUNT_COLUMN, lower_bound, upper_bound)

        print(f"\n[1] IQR 이상치 범위: [{lower_bound:.2f}, {upper_bound:.2f}]")
        print(f"[1] 이상치 제거 전 행 수: {len(df)}")
        print(f"[1] 이상치 제거 후 행 수: {len(cleaned_df)}")
        print(f"[1] 제거된 이상치 수: {len(df) - len(cleaned_df)}")

        print("\n[2] Pandas named aggregation 결과 (총매출 내림차순, 상위 10건)")
        pandas_result = pandas_pipeline(CSV_FILE, lower_bound, upper_bound)
        print(pandas_result.head(10))

        print("\n[3] Polars Lazy API 집계 결과 (상위 10건)")
        polars_result = polars_pipeline(CSV_FILE, lower_bound, upper_bound)
        print(polars_result.head(10))

        print("\n[4] DuckDB SQL 집계 결과 (상위 10건)")
        duckdb_result = duckdb_pipeline(CSV_FILE, lower_bound, upper_bound)
        print(duckdb_result.head(10))

        print(f"\n[4] 성능 비교 (timeit {TIMEIT_REPEAT}회 반복 평균)")
        averages = compare_performance(CSV_FILE, lower_bound, upper_bound)
        for tool, avg_time in sorted(averages.items(), key=lambda item: item[1]):
            print(f"{tool}: 평균 {avg_time:.4f}초")

    except FileNotFoundError as error:
        print(f"파일을 찾을 수 없습니다: {error}")

    except KeyError as error:
        print(f"필요한 컬럼이 없습니다: {error}")

    except Exception as error:
        print(f"예상치 못한 오류가 발생했습니다: {error}")


if __name__ == "__main__":
    main()