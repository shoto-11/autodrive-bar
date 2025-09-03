import os
import pandas as pd
import merge
def make_standard(new_file_name, RU_file_name, LD_file_name):
    # ファイルのパスを定義
    csv_file_name = f"{new_file_name}.csv"
    csv_file_path = os.path.join('standard/maked', csv_file_name)

    combined_df = merge.make_combined_csv(RU_file_name, LD_file_name)
    # 保存フォルダ作成
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    
    # CSV保存
    combined_df.to_csv(csv_file_path, index=False, encoding='utf-8')
    
    print(f"CSVファイル '{csv_file_path}' が正常に作成されました。")

# 実行例
# car1(stop)_standard.csv の形で出力するように
combined_data = "combined_data_test"
RU_data= "RU_data.csv"
LD_data= "LD_data.csv"

make_standard(combined_data, RU_data, LD_data )
