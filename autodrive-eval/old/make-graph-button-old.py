import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from collections import defaultdict

# 出力フォルダ
output_dir = "graphs/PrimaryButtonFlag"
os.makedirs(output_dir, exist_ok=True)

# evaluated以下の全CSVを探索
csv_files = glob.glob("evaluated/**/*.csv", recursive=True)

header_groups = defaultdict(lambda: defaultdict(list))

for file in csv_files:
    df = pd.read_csv(file)
    header = ",".join(df.columns)

    # eHMI_001 を抽出
    base = os.path.basename(file)
    prefix = "_".join(base.split("_")[:2])

    header_groups[header][prefix].append(file)


# グラフ生成
for header, prefix_dict in header_groups.items():

    plt.figure(figsize=(14, 6))

    for prefix, files in prefix_dict.items():

        dfs = []
        for file in files:
            df = pd.read_csv(file)
            dfs.append(df["PrimaryButtonFlag"])

        combined = pd.concat(dfs, axis=1)

        # ★ 修正： 100 から引く（反転）
        percentage = 100 - combined.mean(axis=1) * 100

        time = percentage.index * 0.1

        plt.plot(time, percentage, label=prefix, linewidth=2)

    plt.title("PrimaryButtonFlag % per Group (Inverted)\nHeader: " + header)
    plt.xlabel("Time (s)")
    plt.ylabel("the percentage of the potential collision rate (%)")
    plt.ylim(0, 100)
    plt.grid(True)
    plt.legend()

    safe_header = header.replace(",", "_")
    save_name = os.path.join(output_dir, f"AverageGraph_{safe_header}.png")

    plt.savefig(save_name)
    plt.close()

    print(f"Saved: {save_name}")
