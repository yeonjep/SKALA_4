"""
[실습 1] 자료구조 집계 · 컴프리헨션 · 제너레이터

Python_Practice1_Data.json의 sales 데이터를 활용하여
다음 작업을 수행한다.

1. 리스트/딕셔너리 컴프리헨션
2. Counter와 defaultdict 활용
3. 제너레이터와 리스트의 메모리 비교
4. 월별·카테고리별 매출 집계
"""

from collections import Counter, defaultdict
import sys


# 교수님이 제공한 데이터 파일 불러오기
# 파일 내용이 sales = [...] 형태이므로 exec()를 사용한다.
namespace = {}

try:
    with open("Python_Practice1_Data.json", "r", encoding="utf-8") as file:
        exec(file.read(), {}, namespace)

    sales = namespace["sales"]

except FileNotFoundError:
    print("데이터 파일을 찾을 수 없습니다.")
    sys.exit()

except KeyError:
    print("파일 내부에 sales 데이터가 없습니다.")
    sys.exit()

except SyntaxError:
    print("데이터 파일 형식이 올바르지 않습니다.")
    sys.exit()


# --------------------------------------------------
# 1. 리스트/딕셔너리 컴프리헨션
# --------------------------------------------------

# amount가 1000 이상인 거래만 필터링
filtered_sales = [
    sale
    for sale in sales
    if sale["amount"] >= 1000
]

# 전체 지역 목록 생성
regions = {
    sale["region"]
    for sale in sales
}

# 지역별 총매출 계산
region_total = {
    region: sum(
        sale["amount"]
        for sale in sales
        if sale["region"] == region
    )
    for region in regions
}


# --------------------------------------------------
# 2. Counter + defaultdict
# --------------------------------------------------

# 지역별 거래 건수 계산
region_count = Counter(
    sale["region"]
    for sale in sales
)

# 카테고리별 amount 목록 저장
category_amounts = defaultdict(list)

for sale in sales:
    category_amounts[sale["category"]].append(sale["amount"])


# --------------------------------------------------
# 3. 제너레이터와 리스트 메모리 비교
# --------------------------------------------------

def high_amount_generator(data):
    """
    amount가 1000보다 큰 거래를
    한 건씩 반환하는 제너레이터 함수
    """
    for sale in data:
        if sale["amount"] > 1000:
            yield sale


# 리스트 버전
high_amount_list = [
    sale
    for sale in sales
    if sale["amount"] > 1000
]

# 제너레이터 버전
high_amount_gen = high_amount_generator(sales)

# 객체 자체의 메모리 크기 비교
list_size = sys.getsizeof(high_amount_list)
generator_size = sys.getsizeof(high_amount_gen)


# --------------------------------------------------
# 4. 월별·카테고리별 총매출 집계
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
# 5. 거래 금액 TOP 3
# --------------------------------------------------

top3 = sorted(
    sales,
    key=lambda sale: sale["amount"],
    reverse=True
)[:3]


# --------------------------------------------------
# 6. Checkpoint 검증
# --------------------------------------------------

# 데이터 개수 확인
assert len(sales) == 100

# 지역별 총매출 일부 확인
assert region_total["서울"] == 20060
assert region_total["인천"] == 14530

# Counter.most_common() 순서 확인
assert region_count.most_common(3) == [
    ("서울", 14),
    ("부산", 13),
    ("대구", 13)
]

# 제너레이터가 리스트보다 작은지 확인
assert generator_size < list_size

# TOP 3 금액 내림차순 확인
assert [
    sale["amount"]
    for sale in top3
] == [2500, 2200, 2200]


# --------------------------------------------------
# 7. 결과 출력
# --------------------------------------------------

print("1. amount가 1000 이상인 거래")
print(f"총 {len(filtered_sales)}건")

for sale in filtered_sales:
    print(sale)


print("\n2. 지역별 총매출")

for region, total in sorted(region_total.items()):
    print(f"{region}: {total:,}")


print("\n3. 지역별 거래 건수")

for region, count in region_count.most_common():
    print(f"{region}: {count}건")


print("\n4. 카테고리별 amount 목록")

for category, amounts in category_amounts.items():
    print(f"{category}: {amounts}")


print("\n5. 리스트와 제너레이터 메모리 비교")
print(f"리스트 크기: {list_size} bytes")
print(f"제너레이터 크기: {generator_size} bytes")


print("\n6. 월별·카테고리별 총매출")

for month in sorted(monthly_category_total):
    print(f"[{month}]")

    for category, total in sorted(
        monthly_category_total[month].items()
    ):
        print(f"  {category}: {total:,}")


print("\n7. 거래 금액 TOP 3")

for rank, sale in enumerate(top3, start=1):
    print(f"{rank}위: {sale}")


print("\n모든 Checkpoint를 통과했습니다.")