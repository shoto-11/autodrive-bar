import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from collections import defaultdict

def create_collision_rate_graph(target_car, target_state="move"):
    """
    指定された車両(target_car)が指定された状態(target_state)のCSVのみを対象とし、
    ボタンが押された割合をeHMI条件ごとに集計し、
    棒グラフを生成する。
    """
    
    output_dir = "graphs/collision/"
    os.makedirs(output_dir, exist_ok=True)
    
    # evaluated以下の全CSVを探索
    csv_files = glob.glob("evaluated/**/*.csv", recursive=True)

    # eHMI条件の定義
    categories = ["No eHMI", "Ego-only eHMI", "AGeHMI"]
    prefix_to_category = {
        "eHMI_001": "No eHMI",
        "eHMI_002": "Ego-only eHMI",
        "eHMI_003": "AGeHMI"
    }
    
    # eHMI条件ごとに、「早く押したファイル数(early)」と「総ファイル数(total)」をカウント
    results = {
        "No eHMI": {"early": 0, "total": 0},
        "Ego-only eHMI": {"early": 0, "total": 0},
        "AGeHMI": {"early": 0, "total": 0}
    }
    
    # 比較対象の列名 (例: "car1(move)")
    target_column_name = f"{target_car}({target_state})"
    
    # 時間の閾値（10.1秒未満 -> 0秒から10.0秒まで）
    # 0.1秒/行 のため、101行（インデックス0〜100）が対象
    time_limit_index = 101 

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if df.empty:
                continue
                
            # 1. 対象の列名 (例: "car1(move)") がヘッダーに含まれているか確認
            if target_column_name not in df.columns:
                continue # このファイルは集計対象外

            # 2. eHMIカテゴリを特定
            base = os.path.basename(file)
            prefix = "_".join(base.split("_")[:2])
            category_name = prefix_to_category.get(prefix)
            
            if not category_name:
                continue # eHMI_001〜003 以外のファイルは対象外

            # 3. 集計
            # このカテゴリの総ファイル数を+1
            results[category_name]["total"] += 1
            
            # 4. 「早く押したか」の判定
            # 最後の列(PrimaryButtonFlag)を取得
            primary_button_col = df.columns[-1]
            
            # 10.1秒未満（インデックス100まで）の範囲で、ボタンが1回でも押された(1になった)か
            # .any() は、範囲内に一つでも '1' (True) があれば True を返す
            is_early = df.iloc[:time_limit_index][primary_button_col].any()

            if is_early:
                results[category_name]["early"] += 1
                
        except Exception as e:
            print(f"Error processing file {file}: {e}")

    # 割合を計算 (Y軸のデータ)
    percentages = {}
    for cat in categories:
        total = results[cat]["total"]
        early = results[cat]["early"]
        if total > 0:
            # 早く押した数 / 総ファイル数 * 100
            percentages[cat] = (early / total) * 100
        else:
            percentages[cat] = 0
            
    # 結果の表示（確認用）
    print(f"\nResults for {target_car}({target_state}):")
    for cat in categories:
        print(f"  {cat}: {results[cat]['early']} / {results[cat]['total']} = {percentages[cat]:.2f}%")

    # 棒グラフの描画
    plt.figure(figsize=(10, 6))
    
    # 棒グラフの色を指定 (オプション)
    colors = ['#d3d3d3', '#a9a9a9', '#808080'] # グレー系
    
    bars = plt.bar(percentages.keys(), percentages.values(), color=colors, edgecolor='black')
    
    # 棒グラフの上に割合(%)のテキストを表示
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f'{yval:.1f}%', 
                 ha='center', va='bottom', fontsize=10)

    plt.title(f"Early Button Press Rate when {target_car} is '{target_state}'")
    plt.xlabel("eHMI Condition")
    plt.ylabel("The percentage of the potential collision rate (%)")
    plt.ylim(0, 100) # Y軸を0%から100%に固定
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)

    save_name = os.path.join(output_dir, f"BarChart_CollisionRate_{target_car}_{target_state}.png")
    plt.savefig(save_name)
    plt.close()
    
    print(f"Saved: {save_name}")

# --- 実行 ---
# car1, car2, car3, car4 が "move" だった場合のグラフをそれぞれ作成
target_cars = ["car1", "car2", "car3", "car4"]
for car in target_cars:
    create_collision_rate_graph(car, target_state="move")

print("\nAll processing complete.")