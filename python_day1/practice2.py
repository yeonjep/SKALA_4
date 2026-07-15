"""
[실습 2] 파일 I/O, 예외 처리, Pydantic 검증 파이프라인

Python_Practice1_Data.json의 sales 데이터를 불러와 일부 데이터를 검증한다.

주요 기능
1. 예외 처리를 적용한 데이터 파일 로딩
2. Pydantic v2를 이용한 SalesRecord 스키마 정의
3. 유효한 데이터와 오류 데이터를 분리
4. 유효 데이터는 CSV, 오류 데이터는 JSON으로 저장
5. 저장한 CSV를 다시 읽어 데이터 건수 확인
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "Python_Practice1_Data.json"
VALID_FILE = BASE_DIR / "valid_sales.csv"
ERROR_FILE = BASE_DIR / "errors.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 1. 예외 처리 + 파일 읽기
# --------------------------------------------------

def safe_load_csv(file_path: Path) -> list[dict[str, Any]] | None:
    """
    데이터 파일을 안전하게 읽어 sales 리스트를 반환한다.

    파일이 없거나 형식이 잘못된 경우 None을 반환하고,
    성공한 경우 딕셔너리 리스트를 반환한다.
    """

    namespace: dict[str, Any] = {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        # 제공된 파일이 sales = [...] 형태이므로
        # 별도의 namespace에서 파일 내용을 실행한다.
        exec(file_content, {"__builtins__": {}}, namespace)

        sales = namespace["sales"]

        if not isinstance(sales, list):
            raise TypeError("sales 데이터가 리스트 형식이 아닙니다.")

        logger.info("데이터 파일 로딩 성공: %d건", len(sales))
        return sales

    except FileNotFoundError:
        logger.error("파일을 찾을 수 없습니다: %s", file_path)
        return None

    except KeyError:
        logger.error("파일 안에 sales 데이터가 없습니다.")
        return None

    except SyntaxError as error:
        logger.error("파일 문법 오류: %s", error)
        return None

    except TypeError as error:
        logger.error("데이터 형식 오류: %s", error)
        return None

    finally:
        logger.info("로딩 종료")


# --------------------------------------------------
# 2. Pydantic v2 스키마 정의
# --------------------------------------------------

class SalesRecord(BaseModel):
    """매출 데이터 한 건을 검증하는 Pydantic 모델."""

    date: str = Field(min_length=1)
    region: str = Field(min_length=1)
    amount: int = Field(gt=0)
    category: str | None = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        """date가 YYYY-MM-DD 형식인지 확인한다."""

        parts = value.split("-")

        if (
            len(parts) != 3
            or len(parts[0]) != 4
            or len(parts[1]) != 2
            or len(parts[2]) != 2
            or not all(part.isdigit() for part in parts)
        ):
            raise ValueError("date는 YYYY-MM-DD 형식이어야 합니다.")

        return value

    @field_validator("region")
    @classmethod
    def validate_region(cls, value: str) -> str:
        """공백으로만 구성된 region을 허용하지 않는다."""

        if not value.strip():
            raise ValueError("region은 비어 있을 수 없습니다.")

        return value.strip()


# --------------------------------------------------
# 실습용 검증 데이터 구성
# --------------------------------------------------

def create_raw_data(sales: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    원본 sales 데이터로부터 검증용 데이터 7건을 만든다.

    정상 데이터 4건과 오류 데이터 3건을 구성하여
    Pydantic 검증 성공 및 실패 상황을 모두 확인한다.
    """

    raw_data = [
        {
            "date": f"{sale['month']}-01",
            "region": sale["region"],
            "amount": sale["amount"],
            "category": sale.get("category"),
        }
        for sale in sales[:4]
    ]

    # category는 선택 필드이므로 첫 번째 데이터에서 제거해도 정상이다.
    raw_data[0].pop("category")

    # 오류 데이터 1: date가 비어 있음
    invalid_date = {
        "date": "",
        "region": sales[4]["region"],
        "amount": sales[4]["amount"],
        "category": sales[4]["category"],
    }

    # 오류 데이터 2: region이 비어 있음
    invalid_region = {
        "date": f"{sales[5]['month']}-01",
        "region": "",
        "amount": sales[5]["amount"],
        "category": sales[5]["category"],
    }

    # 오류 데이터 3: amount가 0 이하
    invalid_amount = {
        "date": f"{sales[6]['month']}-01",
        "region": sales[6]["region"],
        "amount": 0,
        "category": sales[6]["category"],
    }

    raw_data.extend([
        invalid_date,
        invalid_region,
        invalid_amount,
    ])

    return raw_data


# --------------------------------------------------
# 3. 검증 파이프라인
# --------------------------------------------------

def validate_records(
    raw_data: list[dict[str, Any]],
) -> tuple[list[SalesRecord], list[dict[str, Any]]]:
    """
    raw_data를 SalesRecord 모델로 검증한다.

    검증 성공 데이터는 valid에 저장하고,
    검증 실패 데이터는 원본 행과 오류 내용을 errors에 저장한다.
    """

    valid: list[SalesRecord] = []
    errors: list[dict[str, Any]] = []

    for row_number, row in enumerate(raw_data, start=1):
        try:
            record = SalesRecord.model_validate(row)
            valid.append(record)

        except ValidationError as error:
            logger.error(
                "%d번째 데이터 검증 실패\n%s",
                row_number,
                error,
            )

            errors.append({
                "row": row,
                "error": error.errors(),
            })

    return valid, errors


# --------------------------------------------------
# 4. 결과 파일 저장
# --------------------------------------------------

def save_valid_records(
    records: list[SalesRecord],
    file_path: Path,
) -> None:
    """검증을 통과한 데이터를 CSV 파일로 저장한다."""

    field_names = [
        "date",
        "region",
        "amount",
        "category",
    ]

    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=field_names,
        )

        writer.writeheader()

        for record in records:
            writer.writerow(record.model_dump())

    logger.info("유효 데이터 저장 완료: %s", file_path)


def save_errors(
    errors: list[dict[str, Any]],
    file_path: Path,
) -> None:
    """검증에 실패한 데이터를 JSON 파일로 저장한다."""

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            errors,
            file,
            ensure_ascii=False,
            indent=4,
        )

    logger.info("오류 데이터 저장 완료: %s", file_path)


# --------------------------------------------------
# 저장된 CSV 재로딩
# --------------------------------------------------

def reload_valid_records(
    file_path: Path,
) -> list[dict[str, str]]:
    """저장된 CSV 파일을 다시 읽어 딕셔너리 리스트로 반환한다."""

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


# --------------------------------------------------
# 프로그램 실행
# --------------------------------------------------

def main() -> None:
    """데이터 로딩부터 검증, 저장, 재로딩까지 수행한다."""

    sales = safe_load_csv(DATA_FILE)

    # 파일 로딩 실패 여부 확인
    assert sales is not None, "데이터 파일 로딩에 실패했습니다."

    raw_data = create_raw_data(sales)

    valid, errors = validate_records(raw_data)

    print("\n[검증 결과]")
    print(f"전체 데이터: {len(raw_data)}건")
    print(f"정상 데이터: {len(valid)}건")
    print(f"오류 데이터: {len(errors)}건")

    # Checkpoint: 정상 4건, 오류 3건인지 확인
    assert len(valid) == 4, "정상 데이터는 4건이어야 합니다."
    assert len(errors) == 3, "오류 데이터는 3건이어야 합니다."

    save_valid_records(valid, VALID_FILE)
    save_errors(errors, ERROR_FILE)

    reloaded = reload_valid_records(VALID_FILE)

    print("\n[재로딩 결과]")
    print(f"CSV에서 다시 읽은 데이터: {len(reloaded)}건")

    # Checkpoint: 저장 후 다시 읽은 데이터가 4건인지 확인
    assert len(reloaded) == 4, "재로딩한 데이터는 4건이어야 합니다."

    print("\n[유효 데이터]")

    for record in valid:
        print(record.model_dump())

    print("\n모든 Checkpoint를 통과했습니다.")


if __name__ == "__main__":
    main()