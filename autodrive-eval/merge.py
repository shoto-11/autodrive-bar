import pandas as pd
import os
def resample_to_100ms(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrameを0.1秒間隔でサンプリング（nearest補間）する"""
    df.columns = df.columns.str.strip()
    df['Time'] = pd.to_datetime(df['Time'], format="%H:%M:%S.%f")
    df = df.set_index('Time')

    start = df.index.min().ceil("s")
    end   = df.index.max().floor("s")
    target_times = pd.date_range(start, end, freq="100ms")

    return (
        df.reindex(df.index.union(target_times))
          .sort_index()
          .interpolate("nearest")
          .loc[target_times]
    )

def make_combined_csv(RU_file_name: str, LD_file_name: str):
    # --- 例として2つのCSVを読み込む ---
    df1 = pd.read_csv(os.path.join('standard/origin', RU_file_name))
    df2 = pd.read_csv(os.path.join('standard/origin', LD_file_name))

    # --- 関数で処理 ---
    sampled_df1 = resample_to_100ms(df1)
    sampled_df2 = resample_to_100ms(df2)

    # --- 行数をそろえる（短い方に合わせる）---
    min_len = min(len(sampled_df1), len(sampled_df2))
    sampled_df1 = sampled_df1.iloc[:min_len]
    sampled_df2 = sampled_df2.iloc[:min_len]

    # 必要な列名をリストで定義
    columns_to_extract = ['Rotation (X)', 'Rotation (Y)']

    # 特定の列だけを抽出した新しいデータフレームを作成
    extracted_df1 = sampled_df1[columns_to_extract]
    extracted_df2 = sampled_df2[columns_to_extract]
    # 新しいヘッダー名を定義
    new_headers_df1 = ['RU-Rotation (X)', 'RU-Rotation (Y)']
    new_headers_df2 = ['LD-Rotation (X)', 'LD-Rotation (Y)']

    # ヘッダーを直接変更
    extracted_df1.columns = new_headers_df1
    extracted_df2.columns = new_headers_df2

    # --- 横に結合 ---
    combined_df = pd.concat(
        [extracted_df1.reset_index(drop=True),
        extracted_df2.reset_index(drop=True)],
        axis=1
    )
    # --- 確認 ---
    return combined_df

print(make_combined_csv('RU_data.csv', 'LD_data.csv'))