"""
울산_4반_박연제_day2_종합실습

[Day 2] End2End 데이터 분석 프로젝트 - NYC Yellow Taxi (2026-05)

1) yellow_tripdata_2026-05.parquet를 Pandas와 Polars 양쪽으로 로딩해 결과를 비교하고,
   결측치·중복·이상치를 처리한 뒤 기본 EDA를 수행한다.
2) Seaborn 정적 차트와 Plotly 인터랙티브 차트를 각각 1개 이상 작성한다.
3) 기술통계·상관계수를 산출하고, 신용카드 vs 현금 결제의 팁 금액 차이를 t-test로 검정한다.
4) sklearn.pipeline.Pipeline으로 결제수단(신용카드/현금) 분류 모델을 구성해 평가 지표를 출력하고
   joblib으로 저장한다.
5) 분석 결과를 report.md로 자동 생성한다.

데이터가 커서(약 409만 행) 시각화·모델 학습 단계는 무작위 샘플(기본 10만 행)을 사용한다.
결측치 처리, 기술통계, 상관계수, t-test는 전체 정제 데이터를 대상으로 수행한다.


"""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import polars as pl
import seaborn as sns
from scipy.stats import ttest_ind
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# matplotlib/seaborn 그래프에서 한글이 깨지지 않도록 macOS 기본 한글 폰트 지정
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).parent
PARQUET_FILE = BASE_DIR / "yellow_tripdata_2026-05.parquet"
OUTPUT_DIR = BASE_DIR / "output"
SEABORN_CHART_FILE = OUTPUT_DIR / "seaborn_chart.png"
PLOTLY_CHART_FILE = OUTPUT_DIR / "plotly_chart.html"
MODEL_FILE = OUTPUT_DIR / "payment_type_pipeline.joblib"
REPORT_FILE = BASE_DIR / "report.md"

# 20개 컬럼 중 분석에 필요한 것만 선택해서 로딩(메모리 절약)
USE_COLUMNS = [
    "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime",
    "passenger_count", "trip_distance", "PULocationID", "DOLocationID",
    "payment_type", "fare_amount", "tip_amount", "total_amount",
]
NUMERIC_FEATURES = ["trip_distance", "fare_amount", "passenger_count", "pickup_hour"]
CATEGORICAL_FEATURES = ["VendorID", "PULocationID", "DOLocationID"]
TARGET_COLUMN = "payment_type"
STATS_COLUMNS = ["trip_distance", "fare_amount", "tip_amount", "total_amount"]
SIGNIFICANCE_LEVEL = 0.05
SAMPLE_SIZE = 100_000
RANDOM_STATE = 42


# Pandas로 parquet 파일을 로딩한다.
def load_with_pandas(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path, columns=USE_COLUMNS)


# Polars로 동일한 parquet 파일을 로딩한다.
def load_with_polars(path: Path) -> pl.DataFrame:
    return pl.read_parquet(path, columns=USE_COLUMNS)


# Pandas와 Polars 로딩 결과를 비교해서 출력한다.
def compare_pandas_polars(pandas_df: pd.DataFrame, polars_df: pl.DataFrame) -> None:
    print(f"[1] Pandas shape: {pandas_df.shape}")
    print(f"[1] Polars shape: {polars_df.shape}")
    print(f"\n[1] Pandas dtypes:\n{pandas_df.dtypes}")
    print(f"\n[1] Polars dtypes:\n{polars_df.schema}")


# IQR 방법으로 이상치 정상 범위(하한, 상한)를 계산한다.
def compute_iqr_bounds(df: pd.DataFrame, column: str) -> tuple[float, float]:
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


# 중복·결측치·명백한 오기록(0 이하 거리/요금)·요금 이상치를 정리하고 EDA 요약을 출력한다.
def clean_and_explore(df: pd.DataFrame) -> pd.DataFrame:
    before_count = len(df)
    df = df.drop_duplicates()
    print(f"\n[1] 중복 제거: {before_count}행 -> {len(df)}행")

    print(f"\n[1] 컬럼별 결측치 개수:\n{df.isnull().sum()}")
    df = df.dropna()
    print(f"[1] 결측치 제거 후: {len(df)}행")

    df = df[(df["trip_distance"] > 0) & (df["fare_amount"] > 0) & (df["passenger_count"] > 0)]
    print(f"[1] 0 이하 거리/요금/승객수 제거 후: {len(df)}행")

    lower_bound, upper_bound = compute_iqr_bounds(df, "fare_amount")
    df = df[df["fare_amount"].between(lower_bound, upper_bound)]
    print(
        f"[1] 요금 IQR 이상치 제거 후: {len(df)}행 "
        f"(정상범위: [{lower_bound:.2f}, {upper_bound:.2f}])"
    )

    df = df.copy()
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour

    print("\n[1] 데이터 구조")
    df.info()

    return df


# 택시 이동 거리 분포를 Seaborn 히스토그램+KDE로 시각화해 저장한다.
def plot_seaborn_chart(df: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(data=df, x="trip_distance", kde=True, bins=50, ax=ax)
    ax.set_title("택시 이동 거리 분포")
    ax.set_xlabel("이동 거리 (마일)")
    ax.set_ylabel("빈도")

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


# 시간대별 평균 요금을 Plotly 인터랙티브 막대 차트로 저장한다.
def plot_plotly_chart(df: pd.DataFrame, output_path: Path) -> None:
    summary = (
        df.groupby("pickup_hour")["fare_amount"]
        .mean()
        .reset_index()
        .sort_values("pickup_hour")
    )

    fig = px.bar(
        summary,
        x="pickup_hour",
        y="fare_amount",
        title="시간대별 평균 요금",
        labels={"pickup_hour": "승차 시각(시)", "fare_amount": "평균 요금($)"},
    )
    fig.write_html(output_path)


# 수치형 변수의 기술통계와 상관계수를 계산해서 출력하고 반환한다.
def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[2] 기술통계 (평균·표준편차·분위수)")
    print(df[STATS_COLUMNS].describe())

    correlation = df[STATS_COLUMNS].corr()
    print("\n[2] 수치형 변수 간 상관계수")
    print(correlation)

    return correlation


# 신용카드(1) vs 현금(2) 결제의 팁 금액 차이를 t-test로 검정하고 통계량·p-value·해석을 반환한다.
def run_ttest_by_payment_type(df: pd.DataFrame) -> tuple[float, float, str]:
    credit_tip = df.loc[df[TARGET_COLUMN] == 1, "tip_amount"]
    cash_tip = df.loc[df[TARGET_COLUMN] == 2, "tip_amount"]

    t_stat, p_value = ttest_ind(credit_tip, cash_tip, equal_var=False)

    interpretation = (
        "신용카드와 현금 결제의 팁 금액 차이는 통계적으로 유의미합니다."
        if p_value < SIGNIFICANCE_LEVEL
        else "신용카드와 현금 결제의 팁 금액 차이는 통계적으로 유의미하지 않습니다."
    )

    print("\n[2] t-test (신용카드 vs 현금 결제의 팁 금액 차이)")
    print(f"t-통계량: {t_stat:.4f}, p-value: {p_value:.4f}")
    print(f"해석: {interpretation}")

    return t_stat, p_value, interpretation


# 수치형/범주형 전처리를 묶은 ColumnTransformer 기반 분류 Pipeline을 만든다.
def build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


# 신용카드/현금 결제만 대상으로 Pipeline을 학습·평가하고 joblib으로 저장한다.
def train_evaluate_save(df: pd.DataFrame, model_path: Path) -> tuple[float, float]:
    subset = df[df[TARGET_COLUMN].isin([1, 2])]
    features = subset[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    target = (subset[TARGET_COLUMN] == 1).astype(int)  # 1=신용카드

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=RANDOM_STATE, stratify=target
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)

    print(f"\n[3] 정확도: {accuracy:.4f}")
    print(f"[3] F1 스코어: {f1:.4f}")

    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"[3] 모델 저장 완료: {model_path}")

    return accuracy, f1


# DataFrame을 마크다운 표 문자열로 변환한다 (report.md 조립용, 외부 패키지 불필요).
def dataframe_to_markdown_table(df: pd.DataFrame) -> str:
    header = "| " + " | ".join([""] + list(df.columns)) + " |"
    separator = "| " + " | ".join(["---"] * (len(df.columns) + 1)) + " |"
    rows = [
        "| " + " | ".join([str(idx)] + [f"{value:.4f}" for value in row]) + " |"
        for idx, row in zip(df.index, df.to_numpy())
    ]

    return "\n".join([header, separator, *rows])


# 분석 결과를 종합해 report.md 파일을 자동으로 생성한다.
def generate_report(
    pandas_shape: tuple[int, int],
    polars_shape: tuple[int, int],
    cleaned_count: int,
    correlation: pd.DataFrame,
    t_stat: float,
    p_value: float,
    interpretation: str,
    accuracy: float,
    f1: float,
    report_path: Path,
) -> None:
    lines = [
        "# Day 2 종합 실습 - NYC Yellow Taxi (2026-05) 분석 리포트",
        "",
        "## 1. 데이터 준비",
        f"- Pandas 로딩 shape: {pandas_shape}",
        f"- Polars 로딩 shape: {polars_shape}",
        f"- 결측치·중복·이상치 정제 후 행 수: {cleaned_count:,}",
        "",
        "## 2. 통계 분석",
        "### 수치형 변수 간 상관계수",
        dataframe_to_markdown_table(correlation),
        "",
        "### t-test (신용카드 vs 현금 결제의 팁 금액 차이)",
        f"- t-통계량: {t_stat:.4f}",
        f"- p-value: {p_value:.4f}",
        f"- 해석: {interpretation}",
        "",
        "## 3. ML Pipeline 평가",
        f"- 정확도: {accuracy:.4f}",
        f"- F1 스코어: {f1:.4f}",
        "",
        "## 4. 산출물",
        f"- Seaborn 차트: {SEABORN_CHART_FILE.relative_to(BASE_DIR)}",
        f"- Plotly 차트: {PLOTLY_CHART_FILE.relative_to(BASE_DIR)}",
        f"- 저장된 모델: {MODEL_FILE.relative_to(BASE_DIR)}",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[4] report.md 자동 생성 완료: {report_path}")


# 데이터 준비, 시각화, 통계 분석, ML Pipeline, 리포트 생성까지 순서대로 실행한다.
def main() -> None:
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)

        print("[1] Pandas / Polars 로딩 및 비교")
        pandas_df = load_with_pandas(PARQUET_FILE)
        polars_df = load_with_polars(PARQUET_FILE)
        compare_pandas_polars(pandas_df, polars_df)

        cleaned_df = clean_and_explore(pandas_df)

        print("\n[3] 통계 분석 (전체 정제 데이터 기준)")
        correlation = compute_descriptive_stats(cleaned_df)
        t_stat, p_value, interpretation = run_ttest_by_payment_type(cleaned_df)

        # 시각화·모델 학습은 실행 시간을 줄이기 위해 무작위 샘플을 사용한다.
        sample_size = min(SAMPLE_SIZE, len(cleaned_df))
        sampled_df = cleaned_df.sample(n=sample_size, random_state=RANDOM_STATE)
        print(f"\n[1] 시각화·모델 학습은 {sample_size:,}행 무작위 샘플로 진행")

        print("\n[2] 시각화")
        plot_seaborn_chart(sampled_df, SEABORN_CHART_FILE)
        print(f"Seaborn 차트 저장 완료: {SEABORN_CHART_FILE}")
        plot_plotly_chart(cleaned_df, PLOTLY_CHART_FILE)
        print(f"Plotly 차트 저장 완료: {PLOTLY_CHART_FILE}")

        print("\n[4] ML Pipeline 학습/평가/저장")
        accuracy, f1 = train_evaluate_save(sampled_df, MODEL_FILE)

        print("\n[5] 리포트 자동 생성")
        generate_report(
            pandas_shape=pandas_df.shape,
            polars_shape=polars_df.shape,
            cleaned_count=len(cleaned_df),
            correlation=correlation,
            t_stat=t_stat,
            p_value=p_value,
            interpretation=interpretation,
            accuracy=accuracy,
            f1=f1,
            report_path=REPORT_FILE,
        )

    except FileNotFoundError as error:
        print(f"파일을 찾을 수 없습니다: {error}")

    except KeyError as error:
        print(f"필요한 컬럼이 없습니다: {error}")

    except Exception as error:
        print(f"예상치 못한 오류가 발생했습니다: {error}")


if __name__ == "__main__":
    main()