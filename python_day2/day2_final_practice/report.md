# Day 2 종합 실습 - NYC Yellow Taxi (2026-05) 분석 리포트

## 1. 데이터 준비
- Pandas 로딩 shape: (4090836, 11)
- Polars 로딩 shape: (4090836, 11)
- 결측치·중복·이상치 정제 후 행 수: 2,795,607

## 2. 통계 분석
### 수치형 변수 간 상관계수
|  | trip_distance | fare_amount | tip_amount | total_amount |
| --- | --- | --- | --- | --- |
| trip_distance | 1.0000 | 0.4817 | 0.1675 | 0.4495 |
| fare_amount | 0.4817 | 1.0000 | 0.4123 | 0.9389 |
| tip_amount | 0.1675 | 0.4123 | 1.0000 | 0.6487 |
| total_amount | 0.4495 | 0.9389 | 0.6487 | 1.0000 |

### t-test (신용카드 vs 현금 결제의 팁 금액 차이)
- t-통계량: 2172.5544
- p-value: 0.0000
- 해석: 신용카드와 현금 결제의 팁 금액 차이는 통계적으로 유의미합니다.

## 3. ML Pipeline 평가
- 정확도: 0.8887
- F1 스코어: 0.9406

## 4. 산출물
- Seaborn 차트: output/seaborn_chart.png
- Plotly 차트: output/plotly_chart.html
- 저장된 모델: output/payment_type_pipeline.joblib