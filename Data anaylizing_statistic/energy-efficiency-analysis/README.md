# Energy Efficiency Analysis

건물의 형태·면적·유리창 구성 등 건축 특성이 난방 부하(Heating Load)와 냉방 부하(Cooling Load)에 미치는 영향을 기초통계 기반으로 분석하고, 이를 바탕으로 선형회귀 예측 모델을 개발하는 프로젝트입니다.

> SKALA 데이터 분석 및 기초통계 과정 · 실습과제

---

## 목차

- [개요](#개요)
- [데이터셋](#데이터셋)
- [프로젝트 구조](#프로젝트-구조)
- [환경설정](#환경설정)
- [실행 방법](#실행-방법)
- [팀 역할 & 파이프라인](#팀-역할--파이프라인)
- [분석 제약사항](#분석-제약사항)
- [산출물](#산출물)
- [평가 기준](#평가-기준)
- [참고자료](#참고자료)

---

## 개요

- **목표**: 에너지 데이터셋에서 변수 간 관계를 통계 기반으로 확인하고, 도메인 관점에서 해석하여 유효한 변수를 선별한 뒤, 이를 토대로 회귀분석을 진행하여 모델 성능을 확인한다.
- **핵심 질문**: 어떤 건물 특성이 에너지 효율성(난방/냉방 부하)에 가장 큰 영향을 미치는가?
- **모델링 방식**: LinearRegression 기반 Separate Models (Y1, Y2 각각 독립 예측)

## 데이터셋

- **Source**: [UCI Machine Learning Repository — Energy Efficiency Dataset](https://archive.ics.uci.edu/dataset/242/energy+efficiency)
- **규모**: 768 rows × 10 columns, 결측치 없음
- **생성 방식**: Ecotect 시뮬레이션으로 생성된 12개 건물 형태 기반 768개 케이스

| 변수 | 설명                                         | 타입       |
| ---- | -------------------------------------------- | ---------- |
| X1   | Relative Compactness (상대적 집약도)         | Continuous |
| X2   | Surface Area (표면적)                        | Continuous |
| X3   | Wall Area (벽 면적)                          | Continuous |
| X4   | Roof Area (지붕 면적)                        | Continuous |
| X5   | Overall Height (전체 높이)                   | Continuous |
| X6   | Orientation (방향)                           | Integer    |
| X7   | Glazing Area (유리창 면적)                   | Continuous |
| X8   | Glazing Area Distribution (유리창 면적 분포) | Integer    |
| Y1   | Heating Load (난방 부하)                     | Target     |
| Y2   | Cooling Load (냉방 부하)                     | Target     |

## 프로젝트 구조

```
energy-efficiency-analysis/
├── README.md
├── requirements.txt
├── data/
│   └── ENB2012_data.xlsx
├── eda_stats.py            # 기술통계 (중심화·퍼짐·분포/대칭)
├── visualization.py        # EDA 시각화
├── correlation.py          # 상관관계·다중공선성 분석
├── pipeline_separate.py    # 변수선택·전처리·Separate 회귀모델
├── main.ipynb              # 최종 통합 실행 노트북 (제출용)
├── scratch/                # 팀원 개인 프로토타입 노트북 (제출 대상 아님)
└── report/
    └── report_draft.md     # 최종 보고서 초안
```

## 환경설정

```bash
# Python 3.11 권장
pip install -r requirements.txt
```

`requirements.txt`에는 pandas, numpy, seaborn, matplotlib, scikit-learn, statsmodels가 포함되어 있습니다.

## 실행 방법

1. `data/` 폴더에 `ENB2012_data.xlsx`가 있는지 확인합니다.
2. 각 모듈(`eda_stats.py`, `visualization.py`, `correlation.py`, `pipeline_separate.py`)이 정상 동작하는지 개별적으로 확인합니다.
3. `main.ipynb`를 처음부터 끝까지(Restart & Run All) 실행하여 전체 파이프라인이 에러 없이 수행되는지 확인합니다.

## 팀 역할 & 파이프라인

| 순서 | 모듈                   | 담당                  | 주요 함수                                                                                                  |
| ---- | ---------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------- |
| ①    | `eda_stats.py`         | -                     | `load_data`, `central_tendency`, `dispersion`, `shape_stats`, `build_summary_table`                        |
| ②    | `visualization.py`     | -                     | `plot_distribution`, `plot_all_distributions`, `plot_scatter`, `plot_all_x_vs_y`                           |
| ③    | `correlation.py`       | -                     | `corr_matrix`, `plot_heatmap`, `flag_multicollinearity`, `group_correlated_features`, `target_correlation` |
| ④    | `pipeline_separate.py` | - (2인, Y1/Y2 각 1인) | `select_features`, `scale_features`, `get_dataset`, `train_and_evaluate`, `plot_residuals`                 |

**의존 관계**: ①②③은 원본 데이터로 병렬 진행 가능 → ③의 결과(`correlated_groups`, `target_corr`)가 ④의 `select_features` 입력값으로 사용됨.

**병합 방식**: 각 담당자는 `.py` 파일 + 함수 단위로 작업 후 개별 커밋. 함수 시그니처는 임의로 변경하지 않으며, 변경이 필요할 경우 사전 공지. 최종적으로 `main.ipynb`에서 전체 모듈을 import하여 통합.

## 분석 제약사항

과제 가이드라인에 따라 아래 사항을 반드시 준수합니다.

- 강의에서 다룬 기초통계 개념(평균, 중앙값, 표준편차, 왜도/첨도, 상관관계) 범위 내에서만 해석
- ANOVA, VIF, Tukey HSD 등 다루지 않은 고급 통계 기법 사용 금지
- **상관관계만으로 유효 변수를 선별하지 않음** — 통계량 기반 해석을 반드시 병행
- 회귀 결과 해석 시 선형회귀 기본가정(선형성·다중공선성·정규성·등분산성)을 고려

## 산출물

- **파일명 규칙**: `DS-Statistics-{캠퍼스}-{X반}-{이름1+이름2}.zip`
- **구성**: `*.pdf`(데이터 분석 결과 보고서) + `*.ipynb`(EDA & 모델링)
- **보고서 목차**: 맨 처음 "SUMMARY" 챕터 필수 (A4 1/3~1/2 분량) + 건물 특성-에너지 효율 관계 / EDA 기반 유효 변수 선별 / 모델링 결과 및 해석

## 평가 기준

| 항목               | 내용                                                                        | 배점    |
| ------------------ | --------------------------------------------------------------------------- | ------- |
| 통계 기반 EDA 해석 | 기초통계량(중심화·퍼짐·분포/대칭·상관관계)을 목적에 맞게 적용하여 해석      | 35      |
| 변수 간 관계 이해  | 2개 이상 변수 간 관계를 숫자→현상→도메인 기반 해석으로 연결                 | 35      |
| 선형회귀 모델 개발 | 변수 선별 및 모델 개발을 회귀 가정사항을 고려하여 개발 (모델 성능은 미고려) | 30      |
| **합계**           |                                                                             | **100** |

## 참고자료

- [UCI Energy Efficiency Dataset](https://archive.ics.uci.edu/dataset/242/energy+efficiency)
- Tsanas, A. & Xifara, A. (2012). _Energy and Buildings_, vol. 49. DOI: 10.24432/C51307
