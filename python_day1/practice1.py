"""
[실습 1] 자료구조 집계 · 컴프리헨션 · 제너레이터

Python_Practice1_Data.json의 sales 데이터를 활용하여 다음 작업을 수행한다.

1. amount가 1000 이상인 거래 필터링
2. 지역별 총매출 계산
3. Counter를 활용한 지역별 거래 건수 계산
4. defaultdict를 활용한 카테고리별 금액 목록 생성
5. 제너레이터와 리스트의 메모리 크기 비교
6. 월별·카테고리별 총매출 집계
7. 거래 금액 상위 3건 출력

변경 내용
- 컴프리헨션, Counter, defaultdict, generator를 활용하도록 작성
- 계산 결과를 assert로 검증
- 파일 및 데이터 오류에 대한 예외 처리 추가
"""

from collections import Counter, defaultdict
from pathlib import Path
import sys


# --------------------------------------------------
# 데이터 파일 불러오기
# --------------------------------------------------

# 실행 위치와 관계없이 현재 Python 파일과 같은 폴더의
# 데이터 파일을 찾도록 경로를 설정한다.
data_path = Path(__file__).with_name("Python_Practice1_Data.json")
data = {}

try:
    # 제공된 데이터 파일은 sales = [...] 형태이므로
    # 파일 내용을 실행한 후 sales 변수를 가져온다.
    with open(data_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, data)

    sales = data["sales"]

except FileNotFoundError:
    print(f"오류: 데이터 파일을 찾을 수 없습니다.\n경로: {data_path}")
    sys.exit()

except KeyError:
    print("오류: 데이터 파일 안에 sales 데이터가 없습니다.")
    sys.exit()

except SyntaxError:
    print("오류: 데이터 파일의 형식이 올바르지 않습니다.")
    sys.exit()


# --------------------------------------------------
# 1. 리스트 컴프리헨션
# amount가 1000 이상인 거래만 필터링
# --------------------------------------------------

filtered_sales = [
    sale
    for sale in sales
    if sale["amount"] >= 1000
]


# --------------------------------------------------
# 2. 딕셔너리 컴프리헨션
# 지역별 총매출 계산
# --------------------------------------------------

# 집합 컴프리헨션으로 중복되지 않는 지역 목록을 만든다.
regions = {
    sale["region"]
    for sale in sales
}

# 각 지역에 해당하는 거래 금액의 합계를 계산한다.
region_total = {
    region: sum(
        sale["amount"]
        for sale in sales
        if sale["region"] == region
    )
    for region in regions
}


# --------------------------------------------------
# 3. Counter
# 지역별 거래 건수 계산
# --------------------------------------------------

region_count = Counter(
    sale["region"]
    for sale in sales
)


# --------------------------------------------------
# 4. defaultdict
# 카테고리별 amount 목록 생성
# --------------------------------------------------

category_amounts = defaultdict(list)

for sale in sales:
    category_amounts[sale["category"]].append(sale["amount"])


# --------------------------------------------------
# 5. 제너레이터
# amount가 1000보다 큰 거래를 하나씩 반환
# --------------------------------------------------

def high_amount_generator(data):
    """amount가 1000보다 큰 거래를 한 건씩 반환한다."""

    for sale in data:
        if sale["amount"] > 1000:
            yield sale


# 같은 조건의 데이터를 리스트와 제너레이터로 각각 생성한다.
high_amount_list = [
    sale
    for sale in sales
    if sale["amount"] > 1000
]

high_amount_gen = high_amount_generator(sales)

# 제너레이터를 list로 변환하지 않고 객체 자체의 크기를 비교한다.
list_size = sys.getsizeof(high_amount_list)
generator_size = sys.getsizeof(high_amount_gen)


# --------------------------------------------------
# 6. 중첩 defaultdict
# 월별·카테고리별 총매출 집계
# --------------------------------------------------

monthly_category_total = defaultdict(
    lambda: defaultdict(int)
)

for sale in sales:
    month = sale["month"]
    category = sale["category"]
    amount = sale["amount"]

    monthly_category_total[month][category] += amount


# --------------------------------------------------
# 7. 거래 금액 상위 3건
# amount를 기준으로 내림차순 정렬
# --------------------------------------------------

top3_sales = sorted(
    sales,
    key=lambda sale: sale["amount"],
    reverse=True
)[:3]


# --------------------------------------------------
# 8. Checkpoint 검증
# 계산 결과가 정확한지 assert로 확인
# --------------------------------------------------

expected_region_total = {
    "서울": 20060,
    "부산": 10930,
    "대구": 12660,
    "인천": 14530,
    "광주": 9620,
    "대전": 11140,
    "울산": 11700,
    "세종": 10820
}

assert region_total == expected_region_total, "지역별 총매출 계산 오류"

assert region_count.most_common(3) == [
    ("서울", 14),
    ("부산", 13),
    ("대구", 13)
], "지역별 거래 건수 또는 정렬 순서 오류"

assert generator_size < list_size, "제너레이터 메모리 비교 오류"

assert [
    sale["amount"]
    for sale in top3_sales
] == [2500, 2200, 2200], "상위 3건 정렬 오류"


# --------------------------------------------------
# 9. 결과 출력
# --------------------------------------------------

print("=" * 50)
print("1. amount가 1000 이상인 거래")
print("=" * 50)
print(f"총 {len(filtered_sales)}건")

for sale in filtered_sales:
    print(sale)


print("\n" + "=" * 50)
print("2. 지역별 총매출")
print("=" * 50)

for region, total in sorted(region_total.items()):
    print(f"{region}: {total:,}")


print("\n" + "=" * 50)
print("3. 지역별 거래 건수")
print("=" * 50)

# 거래 건수가 많은 지역부터 출력한다.
for region, count in region_count.most_common():
    print(f"{region}: {count}건")


print("\n" + "=" * 50)
print("4. 카테고리별 amount 목록")
print("=" * 50)

for category, amounts in category_amounts.items():
    print(f"{category}: {amounts}")


print("\n" + "=" * 50)
print("5. 리스트와 제너레이터 메모리 비교")
print("=" * 50)
print(f"리스트 크기: {list_size} bytes")
print(f"제너레이터 크기: {generator_size} bytes")


print("\n" + "=" * 50)
print("6. 월별·카테고리별 총매출")
print("=" * 50)

for month in sorted(monthly_category_total):
    print(f"[{month}]")

    for category, total in sorted(
        monthly_category_total[month].items()
    ):
        print(f"  {category}: {total:,}")


print("\n" + "=" * 50)
print("7. 거래 금액 상위 3건")
print("=" * 50)

for rank, sale in enumerate(top3_sales, start=1):
    print(
        f"{rank}위: "
        f"지역={sale['region']}, "
        f"카테고리={sale['category']}, "
        f"금액={sale['amount']:,}, "
        f"월={sale['month']}"
    )


print("\n모든 Checkpoint를 통과했습니다.")