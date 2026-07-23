"""
파일명: phase3.py
설명: [실습 3번] NYC Taxi 데이터 통계 분석 모듈
     - Pandas와 Polars를 모두 활용한 분석 요구사항 반영
     - 1번(phase1)에서 정제된 수치 변수(fare_amount, trip_distance) 분석
     - scipy.stats.ttest_ind를 활용한 t-test 분석 및 p-value 해석 자동화
"""

import os
import pandas as pd
import polars as pl
from scipy import stats


def run_statistical_analysis(df_pandas: pd.DataFrame):
    """
    phase1.py에서 처리 완료된 Pandas DataFrame을 전달받아 통계 분석을 실행합니다.
    """
    print("\n" + "=" * 60)
    print(" [실습 3번] 통계 분석 및 가설 검정 결과 (phase3.py)")
    print("=" * 60)

    # Polars 요구사항 반영을 위해 Pandas DataFrame을 Polars DataFrame으로 빠른 변환
    df_polars = pl.from_pandas(df_pandas)

    # -------------------------------------------------------------------------
    # 1. 기술통계량 산출 (fare_amount, trip_distance)
    # -------------------------------------------------------------------------
    print("\n1. 기술통계량 산출 (요금 및 이동 거리)")
    
    # [Pandas 방식]
    pd_desc = df_pandas[["fare_amount", "trip_distance"]].describe()
    print("\n[Pandas] 요약 기술통계:")
    print(pd_desc)

    # [Polars 방식] (평균, 표준편차, 중앙값 수동 산출 예시)
    pl_desc = df_polars.select([
        pl.col("fare_amount").mean().alias("fare_mean"),
        pl.col("fare_amount").std().alias("fare_std"),
        pl.col("fare_amount").median().alias("fare_median"),
        pl.col("trip_distance").mean().alias("distance_mean"),
        pl.col("trip_distance").std().alias("distance_std"),
        pl.col("trip_distance").median().alias("distance_median"),
    ])
    print("\n[Polars] 주요 통계량:")
    print(pl_desc)

    # -------------------------------------------------------------------------
    # 2. 변수 간 상관계수 계산 (trip_distance vs fare_amount)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 50)
    print("2. 피어슨 상관계수 계산 (이동 거리 vs 요금)")

    # [Pandas 방식]
    corr_pd = df_pandas["trip_distance"].corr(df_pandas["fare_amount"])
    print(f"[Pandas] 상관계수: {corr_pd:.4f}")

    # [Polars 방식]
    corr_pl = df_polars.select(
        pl.corr("trip_distance", "fare_amount", method="pearson")
    ).item()
    print(f"[Polars] 상관계수: {corr_pl:.4f}")

    # -------------------------------------------------------------------------
    # 3. t-test 가설 검정 (이동 거리에 따른 요금 차이 분석)
    # -------------------------------------------------------------------------
    # phase1에서 추출 보존된 컬럼들 중 trip_distance와 fare_amount를 활용해 가설을 수립합니다.
    print("\n" + "-" * 50)
    print("3. 독립표본 t-test 분석 (단거리 vs 장거리 요금 차이)")
    print("   - 귀무가설(H0): 단거리(2마일 미만)와 장거리(2마일 이상) 그룹의 평균 요금은 같다.")
    print("   - 대립가설(H1): 두 그룹의 평균 요금은 통계적으로 유의미한 차이가 있다.")

    # 두 그룹의 데이터 서브셋 슬라이싱
    group_short = df_pandas[df_pandas["trip_distance"] < 2]["fare_amount"]
    group_long = df_pandas[df_pandas["trip_distance"] >= 2]["fare_amount"]

    print(f"\n   - 단거리 그룹 크기: {len(group_short):,}개 (평균 요금: ${group_short.mean():.2f})")
    print(f"   - 장거리 그룹 크기: {len(group_long):,}개 (평균 요금: ${group_long.mean():.2f})")

    # 등분산성 검정 (Levene Test) 수행 후 t-test 옵션(equal_var)에 반영
    _, p_levene = stats.levene(group_short, group_long)
    equal_var = p_levene > 0.05

    # scipy.stats.ttest_ind 수행
    t_stat, p_value = stats.ttest_ind(group_short, group_long, equal_var=equal_var)

    print(f"\n   - t-통계량 (t-statistic): {t_stat:.4f}")
    print(f"   - 유의확률 (p-value): {p_value:.4e}")

    # p-value 해석 알고리즘
    alpha = 0.05
    print("\n   [해석 결과]")
    if p_value < alpha:
        interpretation = (
            f"p-value가 {p_value:.4e}로 유의수준 {alpha}보다 매우 작으므로 귀무가설(H0)을 기각합니다.\n"
            f"   => 즉, 이동 거리(단거리 vs 장거리)에 따른 요금 평균 차이는 통계적으로 매우 유의미합니다."
        )
    else:
        interpretation = (
            f"p-value가 {p_value:.4f}로 유의수준 {alpha}보다 크므로 귀무가설(H0)을 기각할 수 없습니다.\n"
            f"   => 즉, 두 그룹 간 요금 평균의 차이는 통계적으로 유의미하지 않습니다."
        )
    print(f"   {interpretation}")
    print("=" * 60)

    # 4/5번 모듈(보고서 생성기 등)에서 재활용할 수 있도록 데이터 구조 반환
    return {
        "corr_coefficient": corr_pd,
        "t_statistic": t_stat,
        "p_value": p_value,
        "interpretation": interpretation,
        "short_mean": group_short.mean(),
        "long_mean": group_long.mean(),
    }


if __name__ == "__main__":
    # 이 파일을 단독 실행할 경우, 저장된 파일을 경로에서 직접 불러와 동작하도록 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cleaned_file_path = os.path.join(current_dir, "../data/cleaned_taxi.parquet")

    if os.path.exists(cleaned_file_path):
        print(f"[System] 기존 저장된 정제 파일 로드: {cleaned_file_path}")
        df_pd = pd.read_parquet(cleaned_file_path)
        run_statistical_analysis(df_pd)
    else:
        print("[Error] 정제된 데이터 파일이 존재하지 않습니다. phase1.py를 먼저 실행해 주세요.")