import pandas as pd
import os
import merge
# 車の状態を返す stop / move / none
def check_conditions(base_path, tol=0.01):

    # CSV読み込み
    df = pd.read_csv(base_path)

    # 列名の前後スペースを削除
    df.columns = df.columns.str.strip()

    # 必要な列を取り出し
    time = df["Elapsed Time (s)"].values
    pos_z = df["Position (Z)"].values

    # --- 条件1: Z座標の符号変化チェック ---
    sign_change = ((pos_z[:-1] * pos_z[1:]) < 0).any()

    if sign_change:
        # --- 条件2: 3秒以上止まっているかチェック ---
        stop_flag = False
        last_move_index = 0
        
        for i in range(1, len(time)):
            # Zの変化が tol 以下なら「止まっている」とみなす
            if abs(pos_z[i] - pos_z[i-1]) < tol:
                if time[i] - time[last_move_index] >= 3.0:
                    stop_flag = True
                    break
            else:
                last_move_index = i  # 動いたのでリセット

        if stop_flag:
            return "stop"
        else:
            return "move"
    else:
        return "none"

# 画面に入っているかを判定する　0/1/-1
# evaluate_df =.../VR_HeadsetLog.csv
# standard_df =.../car1(stop)_standard.csv
def check_screen(evaluate_df, standard_df, header):
    """
    VRヘッドセットのログデータと基準データを比較し、
    特定の回転条件を満たすかを判定する関数。
    データ数が異なる場合は、短いほうのデータ数に合わせて処理を実行します。

    Args:
        evaluate_df (pd.DataFrame): VRヘッドセットのログデータを含むDataFrame。
        standard_df (pd.DataFrame): 基準となる画面の範囲データを含むDataFrame。
        header (str): 出力されるデータフレームの列名。

    Returns:
        pd.DataFrame: 判定結果（1または0）を含むDataFrame。
                      必要な列が見つからない場合はエラーメッセージを返します。
    """
        # 短いほうのデータフレームの行数を取得
    min_len = min(len(evaluate_df), len(standard_df))
    # 必要な列がデータフレームに存在するか確認
    required_cols_eval = ['Rotation (X)', 'Rotation (Y)']
    required_cols_std = ['LD-Rotation (X)', 'RU-Rotation (X)', 'LD-Rotation (Y)', 'RU-Rotation (Y)']
    
    if not all(col in evaluate_df.columns for col in required_cols_eval):
        return "エラー: evaluate_df に必要な列が見つかりません。"
    
    if not all(col in standard_df.columns for col in required_cols_std):
        return "エラー: standard_df に必要な列が見つかりません。"
    # 短いほうの行数に合わせてデータをスライス
    evaluate_df_sliced = evaluate_df.head(min_len).reset_index(drop=True)
    standard_df_sliced = standard_df.head(min_len).reset_index(drop=True)
    #print(evaluate_df_sliced)
    #print(standard_df_sliced)
    # X軸の条件: LD-rotation-x > Rotation (X) > RU-rotation-x
    condition_x = (standard_df_sliced['LD-Rotation (X)'] <= evaluate_df_sliced['Rotation (X)']) & \
                  (evaluate_df_sliced['Rotation (X)'] <= standard_df_sliced['RU-Rotation (X)'])
    
    # Y軸の条件: LD-rotation-y > Rotation (Y) > RU-rotation-y
    condition_y = (standard_df_sliced['LD-Rotation (Y)'] >= evaluate_df_sliced['Rotation (Y)']) & \
                  (evaluate_df_sliced['Rotation (Y)'] >= standard_df_sliced['RU-Rotation (Y)'])

    # 両方の条件が真である場合に1、そうでなければ0とする
    result = (condition_x & condition_y).astype(int)

    # 結果を新しいデータフレームとして作成
    result_df = pd.DataFrame(result, columns=[header])
    
    return result_df
def pre_check_screen(evaluate_df,car_situation,car_check,header):
    #  standard_file_path = 'standard/maked/combined_data_test.csv'
    # noneのときは初めから-1の列を生成する
    if car_check=='none':
        return pd.DataFrame([-1] *len(evaluate_df), columns=[header])
    else:
        standard_file_path = os.path.join('standard/maked', car_situation)
        standard_df = pd.read_csv(standard_file_path)
        standard_df.columns = standard_df.columns.str.strip()
        return check_screen(evaluate_df, standard_df, header)
    
    

def mark_button_event(rotation_df, button_df, tol=0.050):
    """
    rotation_df : 基準となる回転ログ（DatetimeIndexがTimeの想定）
    button_df   : ボタンログ (列: ["Time","Hand","Button"])
    tol         : 許容時間幅 [秒]
    """

    # ボタンログのTimeをdatetimeに変換
    button_df = button_df.copy()
    button_df["Time"] = pd.to_datetime(button_df["Time"], format="%H:%M:%S.%f")
    base_times = rotation_df.index

    results = []
    for t in base_times:
        t_min = t - pd.Timedelta(seconds=tol)
        t_max = t + pd.Timedelta(seconds=tol)
        #print("-----------------")
        #print(t_min,t_max)

        match = button_df[
            (button_df["Time"] >= t_min) &
            (button_df["Time"] <= t_max) &
            (button_df["Button"] == " Primary Button") 
            #(button_df["Hand"] == "Hand")  # Hand 条件が必要なら
        ]
        results.append(1 if not match.empty else 0)

    # PrimaryButtonFlag だけを返す
    return pd.DataFrame({"PrimaryButtonFlag": results})

def merge_df(car1_df,car2_df,car3_df,car4_df,button_df):
    min_len = min(len(car1_df), len(car2_df),len(car3_df),len(car4_df),len(button_df))
    sampled_car1_df = car1_df.iloc[:min_len]
    sampled_car2_df = car2_df.iloc[:min_len]
    sampled_car3_df = car3_df.iloc[:min_len]
    sampled_car4_df = car4_df.iloc[:min_len]
    sampled_button_df = button_df.iloc[:min_len]

    combined_df = pd.concat(
        [sampled_car1_df.reset_index(drop=True),
        sampled_car2_df.reset_index(drop=True),
        sampled_car3_df.reset_index(drop=True),
        sampled_car4_df.reset_index(drop=True),
        sampled_button_df.reset_index(drop=True)],
        axis=1
    )
    # --- 確認 ---
    return combined_df


# データセットフォルダ内のファイルパス
#base_path = "2-carLog.csv"
#print(check_conditions(base_path))
#evaluate_file_path = 'dataset/chi_20250521125055/eHMI_003_case1/VR_HeadsetLog.csv'
#standard_file_path = 'standard/maked/car1(move)_standard.csv'
#df1 = pd.read_csv(evaluate_file_path)
#df2 = pd.read_csv(standard_file_path)
#df1.columns = df1.columns.str.strip()
#df2.columns = df2.columns.str.strip()
#sampled_df1 = merge.resample_to_100ms(df1)
#print(sampled_df1)
#print(df2)
#car1_df=pre_check_screen(sampled_df1,'car1(none)','none')
#car2_df=check_screen(sampled_df1,df2,'car2(stop)')
#car3_df=check_screen(sampled_df1,df2,'car3(stop)')
#car4_df=check_screen(sampled_df1,df2,'car4(stop)')

#print(check_screen(sampled_df1,df2,'car1(stop)'))


#button_file_path = 'dataset/chi_20250521125055/eHMI_003_case1/BottomdLog.csv'
#rotation_df= sampled_df1
#button_df = pd.read_csv(button_file_path)
#button_df.columns = button_df.columns.str.strip()
#pd.set_option("display.max_rows", None)   # 全行表示
#button_df = mark_button_event(rotation_df, button_df, tol=0.050)

#print(merge_df(car1_df,car2_df,car3_df,car4_df,button_df))
