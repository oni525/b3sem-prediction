import pandas as pd
#import numpy as np

# --- ファイル名設定 ---
PERFORMANCE_FILE = 'performances_main_pos_Defender.csv'
MARKET_VALUE_FILE = 'player_market_value.csv'  # 市場価値の時系列データが含まれるファイル
OUTPUT_FILE = 'defender_performances_with_value.csv'

# --- シーズンを決定する関数 (6月区切り) ---
def map_date_to_season(date):
    """
    日付オブジェクトを受け取り、6月区切りのシーズン名（例: '22/23'）を返します。
    7月〜12月: シーズン開始年 (YY)
    1月〜6月: シーズン終了年 (ZZ)
    """
    year = date.year
    month = date.month
    
    # 7月以降は、現在の年がシーズン開始年 (YY/YY+1)
    if month >= 7:
        season_start = str(year)[-2:]
        season_end = str(year + 1)[-2:]
    # 6月以前は、現在の年がシーズン終了年 (YY-1/YY)
    else:
        season_start = str(year - 1)[-2:]
        season_end = str(year)[-2:]
        
    return f"{season_start}/{season_end}"

try:
    # 1. パフォーマンスデータを読み込む
    df_perf = pd.read_csv(PERFORMANCE_FILE)
    print(f"パフォーマンスデータ (元): {len(df_perf)} 行")

    # 2. 市場価値データを読み込む
    # 注意: player_market_value.csv に 'date_unix' と 'value' 列があることを前提とします
    df_market = pd.read_csv(MARKET_VALUE_FILE)

    # 3. 日付をシーズン名に変換
    # 'date_unix' (Unix Time) を datetime型に変換
    df_market['date'] = pd.to_datetime(df_market['date_unix'])    
    df_market['season_name'] = df_market['date'].apply(map_date_to_season)
    print("市場価値データにシーズン情報を付与しました。")

    # 4. 同一シーズン内の市場価値を平均化して集約
    # シーズン内で複数の市場価値がある場合、平均値 (mean) を代表値とします。
    # 
    df_market_expanded = df_market[['player_id', 'season_name', 'value', 'date']]
    print(f"集約された市場価値データ: {len(df_market)} 行")

    # 5. パフォーマンスデータと市場価値データを結合
    # player_id と season_name をキーに結合します。
    merged_df = pd.merge(
        df_perf,
        df_market_expanded,
        on=['player_id', 'season_name'],
        how='left'  # パフォーマンスデータ (左側) を基準に結合
    )
    
    # 結合後の列名を 'value' に変更
    merged_df = merged_df.rename(columns={'mean_market_value': 'value'})

    # 6. 市場価値 (value) が欠損している行を削除する
    rows_before_drop = len(merged_df)
    df_final = merged_df.dropna(subset=['value'])
    rows_after_drop = len(df_final)

    print(f"\n市場価値の欠損行を削除しました。")
    print(f"削除前: {rows_before_drop} 行")
    print(f"削除後: {rows_after_drop} 行")
    print(f"削除された行数: {rows_before_drop - rows_after_drop} 行")

    # >>>>>>>>>>>>>>>>> ここまで新しい処理を追加 <<<<<<<<<<<<<<<<<


    # 7. 必要な列順に調整 (元のステップ6)
    output_columns = [
        'player_id', 'season_name', 'competition_id', 'competition_name', 
        'team_id', 'team_name', 'nb_in_group', 'nb_on_pitch', 'goals', 'assists', 
        'own_goals', 'subed_in', 'subed_out', 'yellow_cards', 'second_yellow_cards', 
        'direct_red_cards', 'penalty_goals', 'minutes_played', 'goals_conceded', 
        'clean_sheets', 'main_position', 'value'
    ]

    df_final = df_final[output_columns]

    # 8. CSVとして出力 (元のステップ7)
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\n処理が完了しました。")
    print(f"最終出力ファイル '{OUTPUT_FILE}' を保存しました。")
    print(f"最終データ行数: {len(df_final)}")
    
    # 結合できなかった行の確認
    unmatched_rows = df_final['value'].isna().sum()
    if unmatched_rows > 0:
         print(f"警告: {unmatched_rows} 行については、対応する市場価値情報が見つかりませんでした。")

except FileNotFoundError as e:
    print(f"エラー: ファイルが見つかりません - {e.filename}。ファイル名を確認してください。")
except KeyError as e:
    print(f"エラー: 必要な列が見つかりません - {e}。CSVのヘッダーを確認してください。")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")