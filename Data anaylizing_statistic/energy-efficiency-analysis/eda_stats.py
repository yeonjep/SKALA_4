"""
1. 기술 통계 (eda_stats.py)

목적:
    에너지 효율성 데이터셋(X1~X8, Y1, Y2)에 대한 기초통계량(중심화·퍼짐·분포/대칭)을
    계산하고, 하나의 요약 테이블로 정리한다.

계산 범위 : 
    - 평균/중앙값/최빈값(중심화)
    - 표준편차/변이계수/사분위수/IQR(퍼짐)
    - 왜도/첨도(분포/대칭)

기타 : 
    X6(Orientation), X8(Glazing Area Distribution)은 정수형이지만 실제로는 범주형에
    가까운 변수


"""
import os
import pandas as pd
import numpy as np


# 데이터 셋 컬럼 
FEATURE_COLS = ["X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8"]
TARGET_COLS = ["Y1", "Y2"]

ALL_COLS = FEATURE_COLS + TARGET_COLS

# 아래의 두 컬럼은 정수 컬럼이나 범주형으로 해석
CATEGORICAL_LIKE_COLS = ["X6", "X8"]

# 데이터 로드 
def load_data(path: str) -> pd.DataFrame:

    # 데이터를 로드
    df = pd.read_excel(path)
 
    missing_cols = [c for c in ALL_COLS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"필수 컬럼 누락: {missing_cols}")
    df = df[ALL_COLS]  # 컬럼 순서 고정

    n_missing = df.isnull().sum().sum()
    if n_missing > 0:
        print(f"결측치: {n_missing}개")

    print(f"데이터 로드 완료: {df.shape[0]}행 x {df.shape[1]}열")
    return df

    raise NotImplementedError


# 중심화 통계량: 평균, 중앙값, 최빈값
def central_tendency(df: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame({
        "mean": df.mean(),
        "median": df.median(),
        "mode": df.mode().iloc[0],  # 최빈값이 여러 개면 그중 첫 번째
    })
    result.index.name = "variable"
    return result
 
# 퍼짐 통계량: 표준편차, 변이계수(CV), 1사분위수(Q1), 3사분위수(Q3), IQR
def dispersion(df: pd.DataFrame) -> pd.DataFrame:
 
    std = df.std()
    mean = df.mean()
    q1 = df.quantile(0.25)
    q3 = df.quantile(0.75)
    iqr = q3 - q1
    cv = std / mean
 
    result = pd.DataFrame({
        "std": std,
        "cv": cv,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
    })
    result.index.name = "variable"
    return result
 
# 분포/대칭 통계량: 왜도, 첨도
def shape_stats(df: pd.DataFrame) -> pd.DataFrame:

    result = pd.DataFrame({
        "skew": df.skew(), # 왜도 
        "kurtosis": df.kurt(), # 첨도 
    })
    result.index.name = "variable"
    result["is_categorical_like"] = result.index.isin(CATEGORICAL_LIKE_COLS)
    return result
 
# central_tendency, dispersion, shape_stats 결과를 하나의 표로 합쳐 eda_summary.csv로 저장
def build_summary_table(df: pd.DataFrame, save_path: str = "report/eda_summary.csv") -> pd.DataFrame:
    
    ct = central_tendency(df)
    disp = dispersion(df)
    shape = shape_stats(df)
 
    summary = pd.concat([ct, disp, shape], axis=1)
    summary = summary.round(4)
 
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    summary.to_csv(save_path)
 
    return summary
 
 
if __name__ == "__main__":
    # 모듈 단독 실행 시 동작 확인용
    df = load_data("data/ENB2012_data.xlsx")
    summary = build_summary_table(df)
    print(summary)
 