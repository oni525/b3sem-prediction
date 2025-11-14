import pandas as pd

# --- 設定項目 ---

# 1. パフォーマンスデータ（5大リーグ・指定シーズンで絞り込み済み）
performance_file = 'output_leagues_seasons.csv'

# 2. プロフィールデータ（main_position情報を取得するため）
# ユーザーの指示に基づき 'player_profiles.csv' に変更
profile_file = 'player_profiles.csv' 

# 3. 抽出したいメインポジションのリスト
target_main_positions = [
    "Attack",
    "Defender",
    "Midfield",
    "Goalkeeper"
]

# 4. 出力ファイルのプレフィックス（接頭辞）
output_prefix = 'performances_main_pos_'

# --- ここから処理 ---

try:
    # ステップ1: パフォーマンスデータの読み込み
    print(f"パフォーマンスファイル '{performance_file}' を読み込んでいます...")
    df_perf = pd.read_csv(performance_file)
    print(f"パフォーマンスデータの行数: {len(df_perf)}")

    # ステップ2: プロフィールデータの読み込み
    print(f"プロフィールファイル '{profile_file}' を読み込んでいます...")
    df_prof = pd.read_csv(profile_file)

    # ステップ3: プロフィールデータから必要な列（player_id と 'main_position'）のみ抽出
    # (メモリ効率化のため)
    df_prof_main_pos = df_prof[['player_id', 'main_position']].drop_duplicates()
    print(f"プロフィールデータのユニークプレイヤー数: {len(df_prof_main_pos)}")

    # ステップ4: パフォーマンスデータと 'main_position' 情報を 'player_id' でマージ(結合)
    # how='left': パフォーマンスデータ(左側)を基準に結合
    print("パフォーマンスデータに 'main_position' 情報を結合しています...")
    merged_df = pd.merge(df_perf, df_prof_main_pos, on='player_id', how='left')

    # ステップ5: 'main_position' ごとに分割してCSVに出力
    print("'main_position' ごとにファイルを分割しています...")

    # まず、抽出対象の4ポジションのみに絞り込む
    df_for_split = merged_df[merged_df['main_position'].isin(target_main_positions)]

    # .groupby() を使って 'main_position' 列の値ごとにデータを反復処理
    for position_name, group_df in df_for_split.groupby('main_position'):
        
        # 出力ファイル名を決定 (例: performances_main_pos_Attack.csv)
        output_filename = f"{output_prefix}{position_name}.csv"
        
        # 該当するポジションのパフォーマンスデータをCSVとして保存
        # (結合時に追加された 'main_position' 列もそのまま出力されます)
        group_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        
        print(f"  -> '{output_filename}' を保存しました (行数: {len(group_df)})")

    # ポジション情報がなかった(マージできなかった) or 4ポジション以外だった行の確認
    missing_position_count = len(merged_df) - len(df_for_split)
    if missing_position_count > 0:
        print(f"\n注意: 'main_position' が指定の4カテゴリ以外、")
        print(f"      またはプロフィール情報が見つからなかったパフォーマンスが {missing_position_count} 行ありました。")
        print(f"      （これらは出力されていません）")

    print("\n処理が完了しました。")

except FileNotFoundError as e:
    print(f"エラー: ファイルが見つかりません - {e.filename}")
    print(f"'{performance_file}' と '{profile_file}' が正しいか確認してください。")
except KeyError as e:
    print(f"エラー: 列が見つかりません - {e}")
    print("CSVファイルに 'player_id' または 'main_position' 列が存在するか確認してください。")
except Exception as e:
    print(f"エラーが発生しました: {e}")