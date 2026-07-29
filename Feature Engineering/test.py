import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations

TARGET = "Machine failure"  # 타겟(고장 여부) 컬럼 이름

# 살펴볼 수치형 변수들 (범주형인 Type, 타겟인 Machine failure는 제외)
NUMERIC_VARS = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

OUT_DIR = "outputs"  # 그래프 이미지를 저장할 폴더


def load_data(path="data/ai4i2020.csv"):
    """csv 파일을 읽어서 DataFrame으로 반환"""
    return pd.read_csv(path)


def plot_single_variable(df, col):
    """
    [1. 변수 하나씩] 단계용 함수
    - 변수 하나(col)를 고장(1)/정상(0) 그룹으로 나눠서 박스플롯 그림
    - 두 그룹의 박스가 많이 겹치면 그 변수 혼자로는 구분력이 약하다는 뜻
    - 결과는 화면에 띄우지 않고 outputs 폴더에 png로 저장
    """
    os.makedirs(OUT_DIR, exist_ok=True)  # outputs 폴더 없으면 생성

    plt.figure(figsize=(5, 4))
    sns.boxplot(x=TARGET, y=col, data=df)  # x축: 고장여부, y축: 해당 변수
    plt.title(col)

    fname = f"{OUT_DIR}/single_{col.split(' ')[0]}.png"
    plt.savefig(fname, bbox_inches="tight")  # 이미지 파일로 저장
    plt.close()  # 메모리에서 그래프 닫기 (창 안 띄움)
    print(f"saved: {fname}")  # 터미널에 저장 경로 출력



def plot_variable_pair(df, col1, col2):
    """
    [2. 변수 두개씩] 단계용 함수
    - 두 변수(col1, col2)를 x축, y축에 놓고 산점도를 그림
    - 점 색깔(hue)을 고장 여부로 다르게 표시해서, 두 변수를 같이 봤을 때
      고장/정상 그룹이 시각적으로 갈라지는지 확인
    """
    os.makedirs(OUT_DIR, exist_ok=True)

    plt.figure(figsize=(5, 4))
    sns.scatterplot(x=col1, y=col2, hue=TARGET, data=df, alpha=0.4)  # alpha: 점 겹침 확인용 투명도
    plt.title(f"{col1} vs {col2}")

    fname = f"{OUT_DIR}/pair_{col1.split(' ')[0]}_{col2.split(' ')[0]}.png"
    plt.savefig(fname, bbox_inches="tight")
    plt.close()
    print(f"saved: {fname}")

def plot_all_pairs(df, variables):
    """[2. 변수 두개씩] 단계: 가능한 모든 변수 쌍을 자동으로 순회하며 산점도 저장"""
    for col1, col2 in combinations(variables, 2):
        plot_variable_pair(df, col1, col2)
        


if __name__ == "__main__":
    df = load_data()

    # 1단계: 수치형 변수 5개를 각각 박스플롯으로 저장 (혼자서 얼마나 구분되는지 확인용)
    for col in NUMERIC_VARS:
        plot_single_variable(df, col)

    # 2단계: 변수 두 개를 골라 산점도 저장 (조합했을 때 더 잘 구분되는지 확인용)
    # 이 줄의 두 변수명만 바꿔가며 여러 조합을 눈으로 비교해보면 됨
    plot_all_pairs(df, NUMERIC_VARS)