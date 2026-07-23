# ============================================================================
# 울산 4반 손수경 (담당 : 4. ML Pipeline.pipeline.Pipeline으로 전처리 + 모델 학습 구성,
#                       평가 지표 출력, joblib으로 모델 저장)
# phase4.py  ―   ML Pipeline 모듈
# ----------------------------------------------------------------------------
# 목표
#   - sklearn.pipeline.Pipeline 으로 "전처리 + 모델 학습" 을 하나로 구성
#   - 평가 지표(정확도 / F1 / precision / recall 등) 출력
#   - joblib 으로 학습된 모델(Pipeline 전체)을 파일로 저장
#
# 예측 문제(분류)
#   payment_type(결제수단)을 트립 특성으로 예측한다.
#     - 1 = 신용카드(credit card)
#     - 2 = 현금(cash)
#   ※ 팁(tip_amount) 여부를 타깃으로 쓰면 "현금 결제는 팁이 0으로 기록"되는
#      데이터 특성 때문에 정보 누수(leakage)가 생기므로 결제수단 예측으로 설계.
#
# 사용법(메인에서):
#   from ml_pipeline import run_ml_pipeline
#   results = run_ml_pipeline(df)     # df: 1번에서 정제한 DataFrame
# ============================================================================

# ---- 표준/서드파티 라이브러리 임포트 -------------------------------------
import numpy as np
import pandas as pd

# scikit-learn 구성요소
from sklearn.pipeline import Pipeline                     # 전처리+모델 파이프라인
from sklearn.compose import ColumnTransformer             # 컬럼별 다른 전처리 적용
from sklearn.impute import SimpleImputer                  # 결측치 대치
from sklearn.preprocessing import StandardScaler, OneHotEncoder  # 스케일링/원핫
from sklearn.model_selection import train_test_split      # 학습/검증 분리
from sklearn.ensemble import RandomForestClassifier       # 분류 모델
from sklearn.metrics import (                             # 평가 지표들
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix,
)

import joblib   # 모델 직렬화(저장/로드)

# 시각화(특성 중요도 png 저장용)
import matplotlib
matplotlib.use("Agg")            # GUI 없는 환경에서도 이미지 파일 저장 가능하도록 설정
import matplotlib.pyplot as plt


# ---- 설정값(상수) ---------------------------------------------------------
# 모델 입력으로 사용할 "수치형" 특성 목록
NUMERIC_FEATURES = [
    "trip_distance",       # 이동 거리(마일)
    "fare_amount",         # 기본 요금
    "passenger_count",     # 탑승 인원
    "trip_duration_min",   # 파생: 이동 시간(분)
    "pickup_hour",         # 파생: 승차 시각(시)
]
# 모델 입력으로 사용할 "범주형" 특성 목록
# ※ 정제 데이터(cleaned_taxi.parquet)에는 범주형 컬럼(PULocationID/RatecodeID)이
#   포함되지 않으므로 비워둔다. 만약 1번에서 해당 컬럼을 유지하도록 바꾸면
#   여기에 다시 추가하면 파이프라인이 자동으로 반영한다.
CATEGORICAL_FEATURES = []
TARGET = "payment_type"    # 예측 대상(타깃)

MODEL_PATH = "model.joblib"          # 저장될 모델 파일 경로
IMPORTANCE_PATH = "feature_importance.png"  # 특성 중요도 그래프 저장 경로


# ---- 1) 특성 엔지니어링 + 데이터 정제 ------------------------------------
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    원본 DataFrame에서 모델 학습에 필요한 특성/타깃을 만들고,
    분류에 부적합한 이상치/비대상 행을 걸러낸다.

    Parameters
    ----------
    df : pd.DataFrame
        택시 트립 원본(또는 1번에서 결측/중복 처리된) 데이터.

    Returns
    -------
    pd.DataFrame
        모델 입력 특성 + 타깃만 포함하고 정제까지 끝난 데이터.
    """
    # 원본 훼손을 막기 위해 복사본으로 작업
    data = df.copy()

    # (a) 파생 변수 1: 이동 시간(분) = 하차시각 - 승차시각
    #     datetime 컬럼이 문자열일 수도 있으므로 to_datetime 으로 안전 변환
    data["tpep_pickup_datetime"] = pd.to_datetime(
        data["tpep_pickup_datetime"], errors="coerce"
    )
    data["tpep_dropoff_datetime"] = pd.to_datetime(
        data["tpep_dropoff_datetime"], errors="coerce"
    )
    data["trip_duration_min"] = (
        data["tpep_dropoff_datetime"] - data["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60.0

    # (b) 파생 변수 2: 승차 시각(0~23시) — 시간대별 결제 패턴 반영
    data["pickup_hour"] = data["tpep_pickup_datetime"].dt.hour

    # (c) 타깃 정제: 카드(1)/현금(2) 두 클래스만 남긴다.
    #     (무료/분쟁/미상 등 3,4,5,6 값은 분류 대상에서 제외)
    data = data[data[TARGET].isin([1, 2])]

    # (d) 4번 전용 최소 방어 필터
    #     ※ 거리/요금 양수화, 중복 제거, 결측 제거 같은 '이상치 처리'는
    #        1번(데이터 준비)에서 이미 수행하므로 여기서 중복하지 않는다.
    #     여기서 거르는 것은 오직 '4번이 직접 계산한 파생변수'인
    #     trip_duration_min 의 계산 오류(하차<승차 → 음수, 비정상적 장시간)뿐이다.
    data = data[
        (data["trip_duration_min"] > 0)       # 0분 이하(하차<승차 등) 제거
        & (data["trip_duration_min"] <= 180)  # 3시간 초과 비정상 트립 제거
    ]

    # (e) 필요한 컬럼(특성 + 타깃)만 선택해 반환
    keep_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]
    return data[keep_cols]


# ---- 2) 전처리 + 모델 파이프라인 구성 ------------------------------------
def build_pipeline() -> Pipeline:
    """
    ColumnTransformer(수치형/범주형 각각 전처리) + 분류 모델을
    하나의 sklearn Pipeline 객체로 묶어 반환한다.

    Returns
    -------
    Pipeline
        fit/predict 가능한 완성된 파이프라인.
    """
    # 수치형 전처리: 결측치는 중앙값으로 대치 → 표준화(스케일링)
    numeric_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    # 범주형 전처리: 결측치는 최빈값으로 대치 → 원핫 인코딩
    #   handle_unknown="ignore" : 검증셋에만 등장하는 미지의 범주도 오류 없이 처리
    categorical_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    # 컬럼 그룹별로 서로 다른 전처리를 적용
    #   수치형 전처리는 항상 포함하고, 범주형 특성이 있을 때만 범주형 전처리를 추가.
    transformers = [("num", numeric_pipe, NUMERIC_FEATURES)]
    if CATEGORICAL_FEATURES:  # 범주형 특성이 지정된 경우에만
        transformers.append(("cat", categorical_pipe, CATEGORICAL_FEATURES))
    preprocessor = ColumnTransformer(transformers=transformers)

    # 전처리 + 분류 모델을 하나의 파이프라인으로 결합
    #   n_jobs=-1 : 가용한 모든 CPU 코어 사용 / random_state : 재현성 보장
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",  # 카드/현금 클래스 불균형 보정
        )),
    ])
    return pipeline


# ---- 3) 학습 + 평가 -------------------------------------------------------
def train_and_evaluate(df: pd.DataFrame, test_size: float = 0.2):
    """
    특성 생성 → 학습/검증 분리 → 파이프라인 학습 → 평가지표 계산.

    Parameters
    ----------
    df : pd.DataFrame
        원본(또는 정제된) 데이터.
    test_size : float
        검증셋 비율(기본 0.2 = 20%).

    Returns
    -------
    (pipeline, metrics) : tuple
        학습된 Pipeline 객체와 평가지표(dict).
    """
    # (1) 특성/타깃 생성 및 정제
    data = build_features(df)

    # 학습에 쓸 데이터가 없으면 조기 종료(예외 상황 방어)
    if data.empty:
        raise ValueError("전처리 후 학습 가능한 데이터가 없습니다. 입력 데이터를 확인하세요.")

    X = data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]  # 입력 특성
    y = data[TARGET]                                   # 정답(타깃)

    # (2) 학습/검증 분리 — stratify=y 로 클래스 비율 유지
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    # (3) 파이프라인 구성 후 학습
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    # (4) 예측 및 평가지표 계산
    y_pred = pipeline.predict(X_test)

    # 이진 분류의 양성 클래스를 1(카드)로 지정하여 F1/precision/recall 계산
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred, pos_label=1),
        "precision": precision_score(y_test, y_pred, pos_label=1),
        "recall": recall_score(y_test, y_pred, pos_label=1),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "report": classification_report(
            y_test, y_pred, target_names=["card(1)", "cash(2)"]
        ),
    }

    # (5) 결과 콘솔 출력(발표/확인용)
    print("=" * 60)
    print("[4] ML Pipeline 평가 결과 (payment_type 분류)")
    print("=" * 60)
    print(f"학습 샘플 수 : {metrics['n_train']:,}")
    print(f"검증 샘플 수 : {metrics['n_test']:,}")
    print(f"정확도(Accuracy) : {metrics['accuracy']:.4f}")
    print(f"F1-score        : {metrics['f1']:.4f}")
    print(f"정밀도(Precision): {metrics['precision']:.4f}")
    print(f"재현율(Recall)   : {metrics['recall']:.4f}")
    print("-" * 60)
    print("혼동행렬(confusion matrix):")
    print(np.array(metrics["confusion_matrix"]))
    print("-" * 60)
    print("분류 리포트:")
    print(metrics["report"])

    return pipeline, metrics


# ---- 4) 모델 저장 ---------------------------------------------------------
def save_model(pipeline: Pipeline, path: str = MODEL_PATH) -> str:
    """
    학습된 파이프라인(전처리+모델 포함)을 joblib 으로 파일 저장.

    Parameters
    ----------
    pipeline : Pipeline
        학습이 끝난 파이프라인 객체.
    path : str
        저장할 파일 경로.

    Returns
    -------
    str
        저장된 파일 경로.
    """
    try:
        joblib.dump(pipeline, path)      # 파이프라인 전체를 직렬화하여 저장
        print(f"[저장 완료] 모델이 '{path}' 에 저장되었습니다.")
    except Exception as e:
        # 디스크/권한 등 저장 실패 상황 방어
        print(f"[저장 실패] 모델 저장 중 오류: {e}")
        raise
    return path


# ---- 4-2) 특성 중요도 추출 + 그래프 저장 ---------------------------------
def plot_feature_importance(pipeline: Pipeline,
                            path: str = IMPORTANCE_PATH,
                            top_n: int = 10) -> pd.DataFrame:
    """
    학습된 파이프라인에서 각 특성이 '결제수단 예측'에 얼마나 기여했는지
    (feature importance) 추출하여 상위 top_n 개를 가로 막대그래프(png)로 저장.

    ※ 2번 시각화의 주인공 변수인 trip_distance / fare_amount 가
       예측에 얼마나 기여하는지 확인하는 연결 지점 역할.

    Parameters
    ----------
    pipeline : Pipeline
        학습이 끝난 파이프라인.
    path : str
        그래프 저장 경로(png).
    top_n : int
        표시할 상위 특성 개수.

    Returns
    -------
    pd.DataFrame
        (feature, importance) 정렬 표. 리포트(5번)에서 재활용 가능.
    """
    try:
        # (1) 파이프라인 내부에서 전처리기와 분류기 꺼내기
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]

        # (2) 원핫 인코딩 후 실제 특성 이름 목록 복원
        #     (수치형은 그대로, 범주형은 'PULocationID_138' 형태로 확장됨)
        feature_names = preprocessor.get_feature_names_out()

        # (3) 트리 모델의 중요도 값과 이름을 묶어 표로 정리
        importances = classifier.feature_importances_
        imp_df = (
            pd.DataFrame({"feature": feature_names, "importance": importances})
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )

        # (4) 상위 top_n 개만 가로 막대그래프로 그리기
        top = imp_df.head(top_n).iloc[::-1]  # 위->아래 큰 순서가 되도록 뒤집기
        plt.figure(figsize=(8, 5))
        plt.barh(top["feature"], top["importance"])
        plt.title("Feature Importance for Payment Type Prediction")  # 제목
        plt.xlabel("Importance")   # x축 레이블
        plt.ylabel("Feature")      # y축 레이블
        plt.tight_layout()
        plt.savefig(path, dpi=120)
        plt.close()
        print(f"[저장 완료] 특성 중요도 그래프가 '{path}' 에 저장되었습니다.")

        # (5) 콘솔에도 상위 항목 출력(발표/확인용)
        print("-" * 60)
        print("상위 특성 중요도(Top {}):".format(top_n))
        print(imp_df.head(top_n).to_string(index=False))

        return imp_df

    except Exception as e:
        # 그래프 저장 실패해도 전체 파이프라인은 계속 진행되도록 방어
        print(f"[경고] 특성 중요도 생성 실패(무시하고 진행): {e}")
        return pd.DataFrame(columns=["feature", "importance"])


# ---- 5) 오케스트레이터: 메인에서 한 번에 호출 -----------------------------
def run_ml_pipeline(df: pd.DataFrame, model_path: str = MODEL_PATH) -> dict:
    """
    4번 실습 전체 흐름을 한 번에 실행하는 진입점 함수.
    (특성생성 → 학습/평가 → 모델저장)

    Parameters
    ----------
    df : pd.DataFrame
        분석에 사용할 데이터(1번 단계 산출물 권장).
    model_path : str
        모델 저장 경로.

    Returns
    -------
    dict
        평가지표 + 모델 경로 + 특성 중요도를 담은 결과 딕셔너리
        (리포트 생성에 활용 가능).
    """
    try:
        # 입력 타입 방어: DataFrame 이 아니면 즉시 오류
        if not isinstance(df, pd.DataFrame):
            raise TypeError("run_ml_pipeline 에는 pandas DataFrame 이 필요합니다.")

        pipeline, metrics = train_and_evaluate(df)  # 학습 + 평가
        save_model(pipeline, model_path)            # 모델 저장

        # 특성 중요도 추출 + png 저장 (2번 시각화와의 연결 지점)
        imp_df = plot_feature_importance(pipeline, IMPORTANCE_PATH)

        metrics["model_path"] = model_path                       # 결과에 경로 추가
        metrics["importance_path"] = IMPORTANCE_PATH             # 중요도 그래프 경로
        # 상위 5개 특성만 (이름, 중요도) 리스트로 저장 → 리포트에서 바로 사용
        metrics["top_features"] = (
            imp_df.head(5).to_dict("records") if not imp_df.empty else []
        )
        return metrics

    except Exception as e:
        # 파이프라인 전 과정에서 발생하는 예외를 한 곳에서 처리
        print(f"[ML Pipeline 오류] {e}")
        raise