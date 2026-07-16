"""
Day 1 데이터 수집 파이프라인에서 사용하는 Pydantic 모델

- WeatherRecord: 시간대별 서울 날씨
- CountryRecord: 대한민국 국가 정보
- IPRecord: IP 기반 지역 정보
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

# Open-Meteo의 시간대별 날씨 데이터를 검증
class WeatherRecord(BaseModel):
    
    source: Literal["weather"] = "weather"
    time: datetime
    temperature: float = Field(ge=-100, le=70)
    precipitation_probability: float = Field(ge=0, le=100)


# RestCountries의 국가 정보를 검증
class CountryRecord(BaseModel):
    
    source: Literal["country"] = "country"
    name: str = Field(min_length=1)
    capital: str = Field(min_length=1)
    population: int = Field(gt=0)
    region: str = Field(min_length=1)


# ip-api의 IP 기반 지역 정보를 검증
class IPRecord(BaseModel):
    
    source: Literal["ip"] = "ip"
    status: Literal["success"]
    query: str = Field(min_length=1)
    country: str = Field(min_length=1)
    city: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    isp: str = Field(min_length=1)