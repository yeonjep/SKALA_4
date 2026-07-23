"""
울산_4반_박연제_day2_종합실습 (담당: 2. 시각화)
담당 : Seaborn 정적 차트 + Plotly 인터랙티브 차트 (분포·상관관계·그룹비교)

1) [Seaborn] 이동 거리 분포 (히스토그램 + KDE) > 결과 : .png
2) [Plotly] 시간대별 평균 요금 (그룹 비교, 인터랙티브 막대) > 결과 : .html

    1), 2) 의 결과 (정적이미지, html) 은 output 폴더에 저장

"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns

# matplotlib/seaborn 그래프에서 한글이 깨지지 않도록 macOS 기본 한글 폰트 지정
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CLEANED_DATA_FILE = DATA_DIR / "cleaned_taxi.parquet"
OUTPUT_DIR = PROJECT_ROOT / "output"
DISTRIBUTION_CHART_FILE = OUTPUT_DIR / "seaborn_distribution.png"
GROUP_CHART_FILE = OUTPUT_DIR / "plotly_group_comparison.html"


# 팀원 1이 정제한 결과 파일을 읽고 시각화에 필요한 시간대(pickup_hour)를 파생
def load_cleaned_data(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)

    if "pickup_hour" not in df.columns:
        df = df.copy()
        df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour

    return df


# [Seaborn] 이동 거리 분포를 히스토그램+KDE로 시각화해 저장
def plot_distribution(df: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    # 극단적 이상치(수백~수천 마일) 때문에 bin 계산 자체가 왜곡되는 문제 방지
    # 원본 df는 그대로 두고, 그래프 계산용 사본만 상위 1% 극단값 제외
    upper_limit = df["trip_distance"].quantile(0.99)
    plot_df = df[df["trip_distance"] <= upper_limit]

    # stat="percent": 원시 빈도(count) 대신 전체 대비 비율(%)로 표시
    sns.histplot(data=plot_df, x="trip_distance", kde=True, bins=50, stat="percent", ax=ax)
    ax.set_title("택시 이동 거리 분포")
    ax.set_xlabel("이동 거리 (마일)")
    ax.set_ylabel("비율 (%)")

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


# [Plotly] 시간대별 평균 요금을 인터랙티브 막대 차트(그룹 비교)로 저장
def plot_group_comparison(df: pd.DataFrame, output_path: Path) -> None:
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


# 정제된 데이터를 로딩하고 Seaborn, 3Plotly 차트를 각 1개씩 생성
def main() -> None:
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)

        print("[2] 정제된 데이터 로딩 ")
        df = load_cleaned_data(CLEANED_DATA_FILE)
        print(f"로딩된 데이터: {len(df):,}행")

        print("\n[2] 시각화 생성")
        plot_distribution(df, DISTRIBUTION_CHART_FILE)
        print(f"Seaborn 분포 차트 저장 완료: {DISTRIBUTION_CHART_FILE}")

        plot_group_comparison(df, GROUP_CHART_FILE)
        print(f"Plotly 그룹비교 차트 저장 완료: {GROUP_CHART_FILE}")

    except FileNotFoundError as error:
        print(f"파일을 찾을 수 없습니다: {error}")

    except KeyError as error:
        print(f"필요한 컬럼이 없습니다: {error}")

    except Exception as error:
        print(f"예상치 못한 오류가 발생했습니다: {error}")


if __name__ == "__main__":
    main()
