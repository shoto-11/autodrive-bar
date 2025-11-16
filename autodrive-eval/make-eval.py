import os
import eval 
import pandas as pd
# 作成したいフォルダのパスを指定
# この例では、'evaluated'フォルダの中に'new_folder'という名前のフォルダを作成します。

# フォルダがない場合は新しく作成
def make_folder(new_folder_path):
    # フォルダが存在しない場合のみ作成
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
        print(f"フォルダ '{new_folder_path}' を作成しました。")
    else:
        print(f"フォルダ '{new_folder_path}' は既に存在します。")
        # 上書き禁止にしたいなら、
        # return 1

# datasetフォルダの中身を読み込む
def read_dataset_folder(dataset_path):
    if not os.path.exists(dataset_path):
        print(f"エラー: データセットフォルダ '{dataset_path}' が見つかりません。")
        return []
        
    folder_names = [name for name in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, name))]
    return folder_names

# フォルダ名をファイル名としてCSVを作成し、指定のフォルダに保存
def write_csv_per_folder(new_folder_name):
    # 保存先フォルダを作成
    save_folder_path = os.path.join('evaluated', new_folder_name)
    dataset_path = os.path.join('dataset', new_folder_name)
    check_car_origin_csv_files = ['1-egoLog.csv','2-carLog.csv','3-truckLog.csv','4-carLog.csv']

    # すでにフォルダが存在する場合は何もしない
    if make_folder(save_folder_path):
        return 1

    # datasetフォルダの中身を読み込む
    folder_names_list = read_dataset_folder(dataset_path )

    if not folder_names_list:
        print("処理するフォルダがありません。")
        return
    
    # 各フォルダ名で個別のCSVファイルを作成
    for folder in folder_names_list:
        if "case22" in folder.lower():  # 大文字小文字区別したくない場合
            print(f"⚠️ {folder} をスキップしました。")
            continue
        # CSVファイルのパスを設定
        csv_file_name = f"{folder}.csv"
        csv_file_path = os.path.join(save_folder_path, csv_file_name)

        #check_dataset_path　= dataset/chi_20250521125055/eHMI_003_case1 までのパス
        check_dataset_path = os.path.join(dataset_path, folder)

        #evaluate_file_path　= dataset/chi_20250521125055/eHMI_003_case1/VR_HeadsetLog.csv
        evaluate_file_path = os.path.join(check_dataset_path, 'VR_HeadsetLog.csv') 
        #print(evaluate_file_path)
        evaluate_df = pd.read_csv(evaluate_file_path)
        evaluate_df.columns = evaluate_df.columns.str.strip()
        evaluate_df = eval.merge.resample_to_100ms(evaluate_df)

        ##<---------ここを繰り返し処理で書かないといけない
        car_df =[]
        for index , check_car_origin_csv_file in enumerate(check_car_origin_csv_files):
            check_car_dataset_file_path = os.path.join(check_dataset_path, check_car_origin_csv_file)
            car_check = eval.check_conditions(check_car_dataset_file_path)
            # 画面に入っているかを判定する
            header= 'car'+str(index+1)+'(' +car_check + ')' 
            car_situation = header + '_standard.csv' 
            car_df.append(eval.pre_check_screen(evaluate_df,car_situation,car_check,header))
        ### ----------->>>>>>>

        #button_file_path = 'dataset/chi_20250521125055/eHMI_003_case1/BottomdLog.csv'
        button_file_path = os.path.join(check_dataset_path, 'BottomdLog.csv')
        button_df = pd.read_csv(button_file_path)
        button_df.columns = button_df.columns.str.strip()
        #pd.set_option("display.max_rows", None)   # 全行表示
        button_df = eval.mark_button_event(evaluate_df, button_df, tol=0.050)
        result_df=eval.merge_df(car_df[0],car_df[1],car_df[2],car_df[3],button_df)
        result_df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")
        print(f"CSVファイル '{csv_file_path}' を作成しました。")

        # CSVファイルへの書き込み
       #with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            #writer = csv.writer(f)
            #df1 = pd.read_csv(evaluate_file_path)
            #resampled_df1 = merge.resample_to_100ms(df1)
            #resampled_df2 = pd.read_csv(standard_file_path)
            
            # ヘッダー行を書き込み
            #header = ['Time']
            #for index , check_car_origin_csv_file in enumerate(check_car_origin_csv_files):
                #check_car_dataset_file_path = os.path.join(check_dataset_path, check_car_origin_csv_file)
                #car_situation='car'+str(index+1)+'(' + eval.check_conditions(check_car_dataset_file_path) + ')'
                #header.append(car_situation)
                # 画面に入っているかを判定する
                # car_situation= car_situation + '_standard.csv' 
                # standard_file_path = os.path.join('standard/maked', car_situation)
                # evaluate_file_path = os.path.join(check_dataset_path, 'VR_HeadsetLog.csv')
                # eval.check_screen(evaluate_file_path, standard_file_path)

            #writer.writerow(header)

            # 各フォルダ内のファイルパスをCSVに書き込む
            #sub_folder_path = os.path.join('dataset', new_folder_name, folder)
            #file_list = [os.path.join(sub_folder_path, f) for f in os.listdir(sub_folder_path) if os.path.isfile(os.path.join(sub_folder_path, f))]
            
            #for file_path in file_list:
                # この行を、実際に書き込みたいデータに置き換えてください
                #writer.writerow([file_path, '', '', '', '', '']) 
        
        #print(f"CSVファイル '{csv_file_path}' を作成しました。")

new_folder_name= "chi_20251113160535_enomoto"
write_csv_per_folder(new_folder_name)