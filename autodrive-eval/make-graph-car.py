import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from collections import defaultdict

# 出力フォルダ
def car_watch(carname):
    output_dir = "graphs/" + carname
    os.makedirs(output_dir, exist_ok=True)

    # evaluated以下の全CSVを探索
    csv_files = glob.glob("evaluated/**/*.csv", recursive=True)

    header_groups = defaultdict(lambda: defaultdict(list))
    
    categories = ["No eHMI", "Ego-only eHMI", "AGeHMI"]
    
    prefix_to_category = {
        "eHMI_001": "No eHMI",
        "eHMI_002": "Ego-only eHMI",
        "eHMI_003": "AGeHMI"
    }

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if df.empty:
                continue
            
            # ヘッダーを取得 (例: "car1(stop),car2(stop),PrimaryButtonFlag")
            header = ",".join(df.columns)
            base = os.path.basename(file)
            prefix = "_".join(base.split("_")[:2]) 

            if prefix in prefix_to_category:
                category_name = prefix_to_category[prefix]
                header_groups[header][category_name].append(file)
                
        except pd.errors.EmptyDataError:
            print(f"Skipping empty file: {file}")
        except Exception as e:
            print(f"Error processing file {file}: {e}")

    # グラフ生成
    car_dict = {"car1": 0, "car2": 1, "car3": 2, "car4": 3}

    for header, prefix_dict in header_groups.items():

        data_to_plot = defaultdict(list)
        
        try:
            col_index = car_dict[carname]
        except KeyError:
            print(f"Warning: '{carname}' not in car_dict. Skipping.")
            continue

        for category_name, files in prefix_dict.items():
            for file in files:
                try:
                    df = pd.read_csv(file)
                    if df.empty:
                        continue
                    
                    duration = df.iloc[:, col_index].sum() * 0.1
                    data_to_plot[category_name].append(duration)
                    
                except Exception as e:
                    print(f"Error reading or processing file {file} for duration: {e}")

        plot_data = []
        plot_labels = []
        
        for cat in categories: 
            if cat in data_to_plot and data_to_plot[cat]: 
                plot_data.append(data_to_plot[cat])
                plot_labels.append(cat)

        if not plot_data:
            continue

        # ★ 変更点：タイトルとファイル名用に、headerから ",PrimaryButtonFlag" を削除
        # (スニペットに基づき ",PrimaryButtonFlag" を対象とします)
        display_header = header.replace(",PrimaryButtonFlag", "")

        # 箱ひげ図の描画
        plt.figure(figsize=(10, 6))
        
        plt.boxplot(
            plot_data, 
            labels=plot_labels,
            whiskerprops={'color': 'black', 'linestyle': '-'},  
            capprops={'color': 'black'},                       
            boxprops={'color': 'black'},                       
            medianprops={'color': 'black'}                     
        )

        # ★ 変更点：加工した display_header をタイトルに使用
        plt.title(f"Observation Duration for {carname}\nHeader: {display_header}")
        plt.xlabel("eHMI Condition") 
        plt.ylabel("Observation Duration (s)") 
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # ★ 変更点：加工した display_header をファイル名に使用
        safe_header = display_header.replace(",", "_").replace(" ", "")
        save_name = os.path.join(output_dir, f"BoxPlot_watch{carname}_{safe_header}.png")

        plt.savefig(save_name)
        plt.close()

        print(f"Saved: {save_name}")

# car_dict={"car1":0,"car2":1,"car3":2,"car4":3}
print("Processing for car1...")
car_watch("car1")
print("Processing for car2...")
car_watch("car2")
print("Processing for car3...")
car_watch("car3")
print("Processing for car4...")
car_watch("car4")

print("All processing complete.")