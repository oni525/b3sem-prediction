import pandas as pd
import numpy as np

# --- ファイル名設定 ---
# 前のステップで作成したメインデータ
INPUT_FILE = 'defender_final_analysis_data.csv'
# プロフィールデータ (誕生日情報を取得するため)
PROFILE_FILE = 'player_profiles.csv'
# 出力ファイル名
OUTPUT_FILE = 'defender_dataset_with_age.csv'

def calculate_season_end_year(season_name):
    """
    シーズン名 (例: "23/24") から後ろの年 (2024) を取得して返す関数
    """
    try:
        if pd.isna(season_name):
            return np.nan
        
        # 文字列型に変換
        season_str = str(season_name)
        
        # "/" で分割できる場合 (例: "23/24")
        if '/' in season_str:
            # 後ろの部分を取得 ("24")
            year_part = season_str.split('/')[1]
            
            # 2桁の場合は2000年代とみなして2000を加算
            # (1990年代のデータも混在する場合は条件分岐が必要ですが、
            #  今回は市場価値データがある最近のものという前提で処理します)
            year_num = int(year_part)
            if year_num < 100:
                return 2000 + year_num
            return year_num
            
        # "/" がない場合 (もしあればそのまま数値化)
        else:
            return int(season_str)
            
    except Exception:
        return np.nan

try:
    print("データを読み込んでいます...")
    # 1. ファイル読み込み
    df_main = pd.read_csv(INPUT_FILE)
    df_profile = pd.read_csv(PROFILE_FILE)

    # 2. プロフィールから player_id と date_of_birth だけを抽出
    # (player_idの重複を除外)
    df_dob = df_profile[['player_id', 'date_of_birth']].drop_duplicates(subset=['player_id'])
    
    print("誕生日情報を結合しています...")
    # 3. メインデータに誕生日情報を結合
    df_merged = pd.merge(df_main, df_dob, on='player_id', how='left')

    # 4. 年齢計算処理
    print("年齢を計算しています...")
    
    # A. シーズン終了年を計算
    # applyを使って1行ずつ処理
    season_end_years = df_merged['season_name'].apply(calculate_season_end_year)
    
    # B. 誕生年を取得
    # date_of_birth列を日付型に変換 (エラーがある場合はNaTにする)
    dob_datetime = pd.to_datetime(df_merged['date_of_birth'], errors='coerce')
    birth_years = dob_datetime.dt.year
    
    # C. 年齢 = シーズン終了年 - 誕生年
    df_merged['age'] = season_end_years - birth_years

    # 5. 一時的に結合した date_of_birth 列は不要であれば削除
    # (残したい場合はこの行をコメントアウトしてください)
    df_merged = df_merged.drop(columns=['date_of_birth'])

    # 6. 結果を保存
    # 列の並び順を調整（ageを一番後ろへ明示的に配置したい場合）
    # 現在のカラムリストを取得し、'age' があれば一度除外して末尾に追加
    cols = [c for c in df_merged.columns if c != 'age'] + ['age']
    df_final = df_merged[cols]
    
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    print("\n処理が完了しました。")
    print(f"出力ファイル: {OUTPUT_FILE}")
    print(f"データの行数: {len(df_final)}")
    
    # 年齢計算できなかった行の確認
    nan_age_count = df_final['age'].isna().sum()
    if nan_age_count > 0:
        print(f"注意: {nan_age_count} 行で年齢が計算できませんでした（誕生日またはシーズンの情報不足）。")

except FileNotFoundError as e:
    print(f"エラー: ファイルが見つかりません - {e.filename}")
except Exception as e:
    print(f"エラーが発生しました: {e}")