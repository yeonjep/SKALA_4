from collections import Counter, defaultdict
import sys


# --------------------------------------------------
# 데이터 파일 불러오기
# --------------------------------------------------

# 제공된 파일이 sales = [...] 형태이므로
# 파일을 실행한 뒤 sales 데이터를 가져온다.
data = {}

with open("Python_Practice1_Data.json", "r", encoding="utf-8") as file:
    exec(file.read(), {}, data)

sales = data["sales"]


# --------------------------------------------------
# 1. 리스트 컴프리헨션
# amount가 1000 이상인 거래 추출
# --------------------------------------------------

filtered_sales = [
    sale
    for sale in sales
    if sale["amount"] >= 1000
]

print("1. amount가 1000 이상인 거래")

for sale in filtered_sales:
    print(sale)


# --------------------------------------------------
# 2. 딕셔너리 컴프리헨션
# 지역별 총매출 계산
# --------------------------------------------------

# 중복되지 않는 지역 목록 생성
regions = {
    sale["region"]
    for sale in sales
}

# 각 지역의 매출 합계 계산
region_total = {
    region: sum(
        sale["amount"]
        for sale in sales
        if sale["region"] == region
    )
    for region in regions
}

print("\n2. 지역별 총매출")

for region, total in region_total.items():
    print(f"{region}: {total:,}")


# --------------------------------------------------
# 3. Counter
# 지역별 거래 건수 계산
# --------------------------------------------------

region_count = Counter(
    sale["region"]
    for sale in sales
)

print("\n3. 지역별 거래 건수")

for region, count in region_count.items():
    print(f"{region}: {count}건")


# --------------------------------------------------
# 4. defaultdict
# 카테고리별 amount 목록 생성
# --------------------------------------------------

category_amounts = defaultdict(list)

for sale in sales:
    category = sale["category"]
    amount = sale["amount"]

    category_amounts[category].append(amount)

print("\n4. 카테고리별 amount 목록")

for category, amounts in category_amounts.items():
    print(f"{category}: {amounts}")


# --------------------------------------------------
# 5. 제너레이터
# amount가 1000보다 큰 거래를 하나씩 반환
# --------------------------------------------------

def high_amount_generator():
    for sale in sales:
        if sale["amount"] > 1000:
            yield sale


# 같은 조건을 리스트와 제너레이터로 생성
high_amount_list = [
    sale
    for sale in sales
    if sale["amount"] > 1000
]

high_amount_gen = high_amount_generator()

print("\n5. 리스트와 제너레이터의 메모리 크기 비교")
print(f"리스트 크기: {sys.getsizeof(high_amount_list)} bytes")
print(f"제너레이터 크기: {sys.getsizeof(high_amount_gen)} bytes")


# --------------------------------------------------
# 6. 중첩 defaultdict
# 월별·카테고리별 총매출 계산
# --------------------------------------------------

monthly_category_total = defaultdict(
    lambda: defaultdict(int)
)

for sale in sales:
    month = sale["month"]
    category = sale["category"]
    amount = sale["amount"]

    monthly_category_total[month][category] += amount

print("\n6. 월별·카테고리별 총매출")

for month in sorted(monthly_category_total):
    print(f"[{month}]")

    for category, total in monthly_category_total[month].items():
        print(f"{category}: {total:,}")


# --------------------------------------------------
# 7. 거래 금액 상위 3건
# --------------------------------------------------

top3_sales = sorted(
    sales,
    key=lambda sale: sale["amount"],
    reverse=True
)[:3]

print("\n7. 거래 금액 상위 3건")

for rank, sale in enumerate(top3_sales, start=1):
    print(f"{rank}위: {sale}")