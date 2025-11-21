import pandas as pd
import numpy as np

# --- ファイル名設定 ---
PERF_VALUE_FILE = 'defender_performances_with_value.csv'
INJURY_FILE = 'player_injuries.csv'
OUTPUT_FINAL_FILE = 'defender_final_analysis_data.csv'

try:
    # 1. パフォーマンス・市場価値データを読み込み、列を削除・整形
    print(f"パフォーマンス・市場価値データ '{PERF_VALUE_FILE}' を読み込んでいます...")
    df_perf_val = pd.read_csv(PERF_VALUE_FILE)
    
    # 削除対象の列
    columns_to_drop_perf = [
        'competition_id', 'competition_name', 'team_id', 'team_name', 'main_position'
    ]
    
    # 削除を実行
    df_base = df_perf_val.drop(columns=columns_to_drop_perf)
    print(f"不要な列を削除しました。現在の列数: {len(df_base.columns)}")

    # 2. 怪我データを読み込み、集計する
    print(f"怪我データ '{INJURY_FILE}' を読み込んでいます...")
    df_injury = pd.read_csv(INJURY_FILE)
    
    # 必要な列のみを選択
    df_injury_subset = df_injury[['player_id', 'season_name', 'days_missed', 'games_missed']]
    
    # player_idとseason_nameをキーに、days_missedとgames_missedを合計する
    df_injury_agg = df_injury_subset.groupby(['player_id', 'season_name'])[['days_missed', 'games_missed']].sum().reset_index()
    print(f"怪我データをシーズンごとに集計しました。集計後の行数: {len(df_injury_agg)}")

    # 3. データの結合
    # df_base (パフォーマンス) に df_injury_agg (怪我集計) を左結合する
    print("パフォーマンスデータに怪我データを結合しています...")
    df_merged = pd.merge(
        df_base,
        df_injury_agg,
        on=['player_id', 'season_name'],
        how='left'
    )
    
    # 4. 欠損値 (NaN) の処理
    # データがない場合は、days_missedとgames_missedを0に置換する
    df_merged['days_missed'] = df_merged['days_missed'].fillna(0)
    df_merged['games_missed'] = df_merged['games_missed'].fillna(0)
    
    # 5. 最終的なCSVの出力
    df_merged.to_csv(OUTPUT_FINAL_FILE, index=False, encoding='utf-8-sig')
    
    print("\n処理が完了しました。")
    print(f"最終的な分析用データ '{OUTPUT_FINAL_FILE}' を保存しました。")
    print(f"最終データ行数: {len(df_merged)}")

except FileNotFoundError as e:
    print(f"エラー: ファイルが見つかりません - {e.filename}。ファイル名を確認してください。")
except KeyError as e:
    print(f"エラー: 必要な列が見つかりません - {e}。CSVのヘッダーを確認してください。")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")