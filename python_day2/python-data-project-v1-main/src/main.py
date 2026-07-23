"""
# ============================================================================
작성자 : 이설현, 박연제, 이정인, 손수경, 김근홍
작성일 : 2026-07-16
# ============================================================================
#  종합실습 과제 ― NYC 옐로우 택시 데이터 분석 파이프라인
# ----------------------------------------------------------------------------
#  [프로젝트 개요]
#    뉴욕시 TLC(택시·리무진 위원회)가 공개하는 옐로우 택시 트립 기록
#    (2026년 5월, 약 409만 건)을 대상으로, 데이터 로딩부터 시각화·통계분석·
#    머신러닝·리포트 자동생성까지 이어지는 end-to-end 분석 파이프라인을 구축한다.
#
#  [분석 주제]
#    "승객의 결제수단(신용카드 vs 현금)은 트립 특성으로 예측·설명할 수 있는가?"
#      - 이동거리, 요금, 이동시간, 승차 시간대, 승차 지역 등의 특성이
#        카드/현금 결제와 어떤 관계를 갖는지 시각화·통계·ML로 일관되게 분석한다.
#      - 시각화(2번)에서 본 거리·요금 분포가, 통계검정(3번)에서 두 그룹 간
#        유의미한 차이로 확인되고, 최종적으로 ML(4번)에서 결제수단 예측의
#        핵심 변수로 이어지도록 전체 흐름을 하나의 이야기로 구성했다.
#
#  [사용 데이터셋]
#    yellow_tripdata_2026-05.parquet
#      - 규모 : 약 4,090,836 행 × 20 열
#      - 주요 컬럼 : trip_distance(이동거리), fare_amount(요금),
#                    tpep_pickup/dropoff_datetime(승·하차 시각),
#                    payment_type(결제수단: 1=카드, 2=현금 …) 등
#
#  [분석 단계 구성]
#    1. 데이터 준비 : Pandas·Polars 로딩 비교, 결측치·중복 처리, 기본 EDA
#    2. 시각화      : Seaborn 이동거리 분포(히스토그램+KDE, .png),
#                     Plotly 시간대별 평균 요금(그룹 비교 막대, .html)
#    3. 통계 분석   : 기술통계·상관계수, scipy t-test 로 카드/현금 그룹 비교
#    4. ML Pipeline : sklearn Pipeline(전처리+RandomForest)으로 결제수단 예측,
#                     평가지표(정확도·F1 등) 출력, joblib 모델 저장,
#                     특성 중요도(2번 변수와의 연결) 그래프 저장
#    5. 자동화      : 위 분석 결과를 report.md 로 자동 생성
#
#  [산출물]
#    - model.joblib            : 학습된 결제수단 예측 모델(전처리 포함)
#    - feature_importance.png  : 예측에 기여한 특성 중요도 그래프
#    - report.md               : 분석 결과 요약 리포트
#
#  [실행 방법]
#    $ python main.py
# ============================================================================

"""

import os
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))

from phase1 import prepare_taxi_data
from phase2 import main as run_visualization
from phase3 import run_statistical_analysis
from phase4 import run_ml_pipeline
from report.generate_report import generate_report


RAW_DATA_PATH = PROJECT_ROOT / "data" / "yellow_tripdata_2026-05.parquet"


def main() -> int:
    cleaned_df = prepare_taxi_data()

    run_visualization()
    stats_results = run_statistical_analysis(cleaned_df)

    ml_results = {}
    try:
        raw_df = pd.read_parquet(RAW_DATA_PATH)
        ml_results = run_ml_pipeline(raw_df, model_path="model.joblib")
    except Exception as error:
        ml_results = {"error": str(error)}

    generate_report(
        data_frame=cleaned_df,
        stats_results=stats_results,
        ml_results=ml_results,
        command="python3 src/main.py",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
