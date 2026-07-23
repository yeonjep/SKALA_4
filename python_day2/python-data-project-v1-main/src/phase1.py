import os
import time
import urllib.request
import pandas as pd
import polars as pl

def prepare_taxi_data():
    """
    NYC Taxi 데이터를 다운로드하고 정제하여 data 폴더에 저장합니다.
    """
    # 1. 경로 설정: 운영체제와 상관없이 안전하게 경로를 잡습니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "../data")
    
    # 만약 data 폴더가 없다면 자동으로 생성합니다. (에러 방지)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-05.parquet"
    raw_file_name = os.path.join(data_dir, "yellow_tripdata_2026-05.parquet")
    output_file_name = os.path.join(data_dir, "cleaned_taxi.parquet")
    
    # 2. 데이터 다운로드
    if not os.path.exists(raw_file_name):
        print("Downloading NYC Taxi Parquet data...")
        urllib.request.urlretrieve(url, raw_file_name)
        print("Download complete.")
    else:
        print("Data file already exists. Skipping download.")

    # 3. 로딩 속도 비교 (Pandas vs Polars)
    print("Comparing loading performance...")
    
    start_time = time.time()
    df_pd = pd.read_parquet(raw_file_name)
    pandas_time = time.time() - start_time
    
    start_time = time.time()
    df_pl = pl.read_parquet(raw_file_name)
    polars_time = time.time() - start_time
    
    print(f"Pandas loading time: {pandas_time:.4f} sec")
    print(f"Polars loading time: {polars_time:.4f} sec")
    print(f"Polars is {pandas_time / polars_time:.1f}x faster.\n")

    # 4. 데이터 정제
    cols_to_keep = [
        'tpep_pickup_datetime', 'tpep_dropoff_datetime', 
        'passenger_count', 'trip_distance', 
        'fare_amount', 'tip_amount', 'total_amount'
    ]
    
    # 존재하는 컬럼만 선택
    valid_cols = [col for col in cols_to_keep if col in df_pd.columns]
    df_clean = df_pd[valid_cols].copy()

    # 중복 및 결측치 제거
    df_clean = df_clean.drop_duplicates()  
    df_clean = df_clean.dropna()           

    # 이상치 처리
    if 'trip_distance' in df_clean.columns and 'fare_amount' in df_clean.columns:
        df_clean = df_clean[(df_clean['trip_distance'] > 0) & (df_clean['fare_amount'] > 0)]

    print(f"Data cleaning finished. Total rows: {len(df_clean):,}")
    
    # 5. 정제된 데이터 저장 (data 폴더 내부에 저장)
    df_clean.to_parquet(output_file_name)
    print(f"Cleaned data saved at: {output_file_name}")
    
    return df_clean

if __name__ == "__main__":
    prepare_taxi_data()