# 분석 리포트

생성 시각: {{ generated_at }}

## 1. 데이터 준비
- 데이터셋: {{ data.dataset }}
- 행/열 수: {{ data.rows }} / {{ data.columns }}
- 결측치 처리 및 현황: {{ data.missing }}
- 중복 처리 및 현황: {{ data.duplicates }}
- Pandas / Polars 비교: {{ data.pandas_polars }}

{% if data.missing_detail %}
### 결측치 상세
{{ data.missing_detail }}

{% endif %}
{% if data.duplicates_detail %}
### 중복 상세
{{ data.duplicates_detail }}

{% endif %}
{% if data.pandas_polars_detail %}
### Pandas / Polars 비교 상세
{{ data.pandas_polars_detail }}

{% endif %}
## 2. 기본 EDA 및 시각화
### 주요 관찰
{{ eda.observations }}

### 예상 시각화 산출물
{% for path in eda.expected_outputs %}
- {{ path }}
{% endfor %}

### 확인된 시각화 산출물
- 이동 거리 분포 PNG: {{ eda.seaborn_chart_path }}
- 시간대별 평균 요금 HTML: {{ eda.plotly_chart_path }}

### Seaborn 이동 거리 분포
{% if eda.has_seaborn_chart %}
![Seaborn 이동 거리 분포]({{ eda.seaborn_chart_path }})
{% else %}
미제공
{% endif %}

### Plotly 시간대별 평균 요금
{% if eda.has_plotly_chart %}
[Plotly 인터랙티브 차트]({{ eda.plotly_chart_path }})
{% else %}
미제공
{% endif %}

{% if eda.extra %}
### EDA 상세 결과
{{ eda.extra }}

{% endif %}
## 3. 통계 분석
### 기술통계: 평균, 표준편차, 분위수
{{ stats.descriptive }}

### 변수 간 상관계수
{{ stats.correlations }}

### t-test
- p-value: {{ stats.t_test_p_value }}
- 해석: {{ stats.t_test_interpretation }}

{% if stats.t_test_detail %}
### t-test 상세 결과
{{ stats.t_test_detail }}

{% endif %}
## 4. ML Pipeline
- 작업 유형: {{ ml.task_type }}
- 사용 모델: {{ ml.model_name }}
- 저장된 모델 경로: {{ ml.model_path }}

### Pipeline 구성
{{ ml.pipeline_steps }}

### 평가 지표
{{ ml.metrics }}

{% if ml.classification_report %}
### 분류 리포트
```text
{{ ml.classification_report }}
```

{% endif %}
{% if ml.top_features %}
### 상위 특성 중요도
| 특성 | 중요도 |
| --- | --- |
{% for feature in ml.top_features %}
| {{ feature.feature }} | {{ "%.6f"|format(feature.importance) }} |
{% endfor %}

{% endif %}
### 특성 중요도 그래프
{% if ml.has_importance_chart %}
![Feature importance]({{ ml.importance_path }})
{% else %}
미제공
{% endif %}

{% if ml.extra %}
### ML 상세 결과
{{ ml.extra }}

{% endif %}
## 5. 자동화 및 재현성
- 입력 디렉터리: `{{ reproducibility.outputs_dir }}`
- 리포트 파일: `{{ reproducibility.report_path }}`
- 로그 파일: `{{ reproducibility.log_path }}`
- 실행 명령어: `{{ reproducibility.command }}`
