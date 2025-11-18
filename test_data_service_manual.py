"""
DataServiceの手動テスト

このスクリプトは、DataServiceクラスが正しく動作するかを確認します。
"""

from src.config.settings import Config
from src.services.data_service import DataService

def test_data_service():
    """DataServiceの基本動作をテストする"""
    print("=== DataServiceの動作確認 ===\n")
    
    # 設定の初期化
    config = Config()
    print(f"設定を初期化しました")
    print(f"  配信データファイル: {config.lives_file_path}")
    print(f"  楽曲データファイル: {config.songs_file_path}")
    print(f"  楽曲リストファイル: {config.song_list_file_path}\n")
    
    # DataServiceの初期化
    service = DataService(config)
    print("DataServiceを初期化しました\n")
    
    # 配信データの読み込み
    print("1. 配信データの読み込み")
    lives_df = service.load_lives_data()
    if lives_df is not None:
        print(f"   ✓ 成功: {len(lives_df)}件の配信データを読み込みました")
        print(f"   列: {list(lives_df.columns)}")
    else:
        print(f"   ✗ 失敗: {service.get_last_error()}")
    print()
    
    # 楽曲データの読み込み
    print("2. 楽曲データの読み込み")
    songs_df = service.load_songs_data()
    if songs_df is not None:
        print(f"   ✓ 成功: {len(songs_df)}件の楽曲データを読み込みました")
        print(f"   列: {list(songs_df.columns)}")
    else:
        print(f"   ✗ 失敗: {service.get_last_error()}")
    print()
    
    # 楽曲リストデータの読み込み
    print("3. 楽曲リストデータの読み込み")
    song_list_df = service.load_song_list_data()
    if song_list_df is not None:
        print(f"   ✓ 成功: {len(song_list_df)}件の楽曲リストデータを読み込みました")
        print(f"   列: {list(song_list_df.columns)}")
    else:
        print(f"   ✗ 失敗: {service.get_last_error()}")
    print()
    
    # データの結合
    if lives_df is not None and songs_df is not None:
        print("4. データの結合")
        try:
            merged_df = service.merge_data(lives_df, songs_df)
            print(f"   ✓ 成功: {len(merged_df)}件のデータを結合しました")
            print(f"   列: {list(merged_df.columns)}")
            print(f"\n   最初の3行:")
            print(merged_df.head(3))
        except Exception as e:
            print(f"   ✗ 失敗: {e}")
    else:
        print("4. データの結合")
        print("   ⊘ スキップ: 配信データまたは楽曲データの読み込みに失敗しました")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_data_service()
