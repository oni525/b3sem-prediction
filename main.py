import pandas as pd

# 抽出対象の5大リーグのリスト
target_leagues = [
    "Bundesliga",
    "Premier League",
    "LaLiga",
    "Serie A",
    "Ligue 1"
]

# 抽出対象のシーズンのリスト
target_seasons = [
    "21/22",
    "22/23",
    "23/24",
    "24/25",
    "25/26"
]

# 元のCSVファイル名（ご自身のファイル名に変更してください）
input_filename = 'player_performances.csv' 
# 出力するCSVファイル名
output_filename = 'output_leagues_seasons.csv'

try:
    # CSVファイルを読み込む
    df = pd.read_csv(input_filename)

    # 条件1: 5大リーグであること
    condition_league = df['competition_name'].isin(target_leagues)
    
    # 条件2: 指定シーズンであること
    condition_season = df['season_name'].isin(target_seasons)

    # 両方の条件（condition_league AND condition_season）を満たす行を抽出
    # & 演算子で条件を組み合わせます
    filtered_df = df[condition_league & condition_season]

    # フィルタリングされたデータを新しいCSVファイルとして出力
    filtered_df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"処理が完了しました。")
    print(f"元の行数: {len(df)}")
    print(f"抽出後の行数（5大リーグ かつ 指定シーズン）: {len(filtered_df)}")
    print(f"'{output_filename}' として保存されました。")

except FileNotFoundError:
    print(f"エラー: '{input_filename}' が見つかりません。ファイル名を確認してください。")
except KeyError as e:
    print(f"エラー: 列が見つかりません - {e}。CSVの列名を確認してください。")
except Exception as e:
    print(f"エラーが発生しました: {e}")