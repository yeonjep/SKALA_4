"""
울산_4반_박연제_practice 4번

[실습 4] 시각화 4종 / 통계 검정 / sklearn Pipeline

실습 3(practice3.py)에서 만든 IQR 이상치 제거 로직을 그대로 재사용해서
sales_100k.csv를 정제한 뒤,
1) 2x2 서브플롯으로 EDA 시각화 4종(히스토그램+KDE, 박스플롯, 월별 라인, 상관 히트맵)
2) t-test(서울 vs 부산 매출 평균 차이) + 카이제곱(카테고리 x 결제수단 독립성) 통계 검정
3) ColumnTransformer + Pipeline으로 전처리·모델을 묶어 학습/평가/저장/재로딩
4) 지역·카테고리별 총매출 Plotly 인터랙티브 막대 차트를 HTML로 저장
을 수행한다.

변경내역
- 2026-07-16 최초 작성
"""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
from scipy.stats import chi2_contingency, ttest_ind
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 실습 3의 IQR 정제 로직·상수를 그대로 재사용 (실습 3→4 연계)
from practice3 import AMOUNT_COLUMN, CSV_FILE, GROUP_COLUMNS, compute_iqr_bounds, filter_outliers

# matplotlib/seaborn 그래프에서 한글이 깨지지 않도록 macOS 기본 한글 폰트 지정
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
EDA_CHART_FILE = OUTPUT_DIR / "eda_charts.png"
PLOTLY_CHART_FILE = OUTPUT_DIR / "region_category_sales.html"
MODEL_FILE = OUTPUT_DIR / "sales_amount_pipeline.joblib"

NUMERIC_FEATURES = ["quantity", "unit_price", "customer_age"]
CATEGORICAL_FEATURES = ["region", "category", "payment_method", "customer_gender"]
SIGNIFICANCE_LEVEL = 0.05


# 실습 3과 동일한 방식(IQR)으로 이상치를 제거한 데이터를 불러온다.
def load_cleaned_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    lower_bound, upper_bound = compute_iqr_bounds(df, AMOUNT_COLUMN)

    return filter_outliers(df, AMOUNT_COLUMN, lower_bound, upper_bound)


# 2x2 서브플롯 하나에 EDA 시각화 4종을 그려서 파일로 저장한다.
def plot_eda_charts(df: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1) 히스토그램 + KDE: 매출액 분포
    sns.histplot(df[AMOUNT_COLUMN], kde=True, ax=axes[0, 0])
    axes[0, 0].set_title("매출액 분포 (히스토그램 + KDE)")

    # 2) 박스플롯: 카테고리별 매출액 분포
    sns.boxplot(data=df, x="category", y=AMOUNT_COLUMN, ax=axes[0, 1])
    axes[0, 1].set_title("카테고리별 매출액 박스플롯")
    axes[0, 1].tick_params(axis="x", rotation=45)

    # 3) 월별 라인: 주문일을 월 단위로 묶은 총매출 추이
    monthly_sales = (
        df.assign(month=pd.to_datetime(df["order_date"]).dt.to_period("M").astype(str))
        .groupby("month")[AMOUNT_COLUMN]
        .sum()
        .sort_index()
    )
    axes[1, 0].plot(monthly_sales.index, monthly_sales.values, marker="o")
    axes[1, 0].set_title("월별 총매출 추이")
    axes[1, 0].tick_params(axis="x", rotation=45)

    # 4) 상관 히트맵: 수치형 컬럼 간 상관관계
    numeric_columns = [*NUMERIC_FEATURES, AMOUNT_COLUMN]
    correlation = df[numeric_columns].corr()
    sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", ax=axes[1, 1])
    axes[1, 1].set_title("수치형 변수 상관 히트맵")

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


# 서울 vs 부산의 평균 매출 차이를 t-test로 검정하고 통계량·p-value·해석을 반환한다.
def run_ttest_seoul_busan(df: pd.DataFrame) -> tuple[float, float, str]:
    seoul_amount = df.loc[df["region"] == "서울", AMOUNT_COLUMN].dropna()
    busan_amount = df.loc[df["region"] == "부산", AMOUNT_COLUMN].dropna()

    t_stat, p_value = ttest_ind(seoul_amount, busan_amount, equal_var=False)

    interpretation = (
        "서울과 부산의 평균 매출 차이는 통계적으로 유의미합니다."
        if p_value < SIGNIFICANCE_LEVEL
        else "서울과 부산의 평균 매출 차이는 통계적으로 유의미하지 않습니다."
    )

    return t_stat, p_value, interpretation


# 카테고리와 결제수단의 독립성을 카이제곱 검정으로 확인하고 통계량·p-value·해석을 반환한다.
def run_chi2_category_payment(df: pd.DataFrame) -> tuple[float, float, str]:
    contingency_table = pd.crosstab(df["category"], df["payment_method"])
    chi2_stat, p_value, _, _ = chi2_contingency(contingency_table)

    interpretation = (
        "카테고리와 결제수단은 서로 독립적이지 않습니다 (연관 있음)."
        if p_value < SIGNIFICANCE_LEVEL
        else "카테고리와 결제수단은 서로 독립적입니다 (연관 없음)."
    )

    return chi2_stat, p_value, interpretation


# 수치형/범주형 전처리를 묶은 ColumnTransformer 기반 Pipeline을 만든다.
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
            ("regressor", LinearRegression()),
        ]
    )


# Pipeline을 학습·평가하고, joblib으로 저장한 뒤 다시 불러와 재현되는지 확인한다.
def train_evaluate_save_reload(df: pd.DataFrame, model_path: Path) -> None:
    features = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    target = df[AMOUNT_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    train_score = pipeline.score(x_train, y_train)
    test_score = pipeline.score(x_test, y_test)
    print(f"학습 데이터 R² 점수: {train_score:.4f}")
    print(f"평가 데이터 R² 점수: {test_score:.4f}")

    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"모델 저장 완료: {model_path}")

    reloaded_pipeline = joblib.load(model_path)
    reloaded_score = reloaded_pipeline.score(x_test, y_test)
    print(f"재로딩한 모델의 평가 데이터 R² 점수: {reloaded_score:.4f} (원본과 동일해야 정상)")


# 지역·카테고리별 총매출을 Plotly 인터랙티브 막대 차트로 만들어 HTML로 저장한다.
def create_plotly_chart(df: pd.DataFrame, output_path: Path) -> None:
    summary = (
        df.groupby(GROUP_COLUMNS)[AMOUNT_COLUMN]
        .sum()
        .reset_index()
        .rename(columns={AMOUNT_COLUMN: "total"})
    )

    fig = px.bar(
        summary,
        x="region",
        y="total",
        color="category",
        barmode="group",
        title="지역·카테고리별 총매출",
    )

    fig.write_html(output_path)
    print(f"Plotly 차트 저장 완료: {output_path}")


# EDA 시각화, 통계 검정, Pipeline 학습, Plotly 차트까지 순서대로 실행한다.
def main() -> None:
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)

        # 실습 3과 동일한 IQR 기준으로 정제된 데이터 로딩
        df = load_cleaned_data(CSV_FILE)

        # 1) EDA 시각화 4종 (2x2 서브플롯)
        print("[1] EDA 시각화 4종 생성 중...")
        plot_eda_charts(df, EDA_CHART_FILE)
        print(f"EDA 차트 저장 완료: {EDA_CHART_FILE}")

        # 2) 통계 검정: t-test + 카이제곱
        print("\n[2] t-test (서울 vs 부산 매출 평균)")
        t_stat, t_p_value, t_interpretation = run_ttest_seoul_busan(df)
        print(f"t-통계량: {t_stat:.4f}, p-value: {t_p_value:.4f}")
        print(f"해석: {t_interpretation}")

        print("\n[2] 카이제곱 검정 (카테고리 x 결제수단 독립성)")
        chi2_stat, chi2_p_value, chi2_interpretation = run_chi2_category_payment(df)
        print(f"카이제곱 통계량: {chi2_stat:.4f}, p-value: {chi2_p_value:.4f}")
        print(f"해석: {chi2_interpretation}")

        # 3) sklearn Pipeline 구성 + 학습/평가/저장/재로딩
        print("\n[3] sklearn Pipeline 학습/평가/저장/재로딩")
        train_evaluate_save_reload(df, MODEL_FILE)

        # 4) Plotly 인터랙티브 차트 저장
        print("\n[4] Plotly 인터랙티브 차트 생성")
        create_plotly_chart(df, PLOTLY_CHART_FILE)

    except FileNotFoundError as error:
        print(f"파일을 찾을 수 없습니다: {error}")

    except KeyError as error:
        print(f"필요한 컬럼이 없습니다: {error}")

    except Exception as error:
        print(f"예상치 못한 오류가 발생했습니다: {error}")


if __name__ == "__main__":
    main()