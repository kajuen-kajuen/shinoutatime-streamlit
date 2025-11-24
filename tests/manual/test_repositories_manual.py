"""
リポジトリの手動テストスクリプト
"""

from src.repositories import LiveRepository, TimestampRepository, SongListRepository

def test_live_repository():
    """LiveRepositoryのテスト"""
    print("LiveRepositoryのテスト開始...")
    repo = LiveRepository("data/M_YT_LIVE.TSV")
    
    # すべての配信情報を読み込む
    lives = repo.load_all()
    print(f"  読み込んだ配信情報: {len(lives)}件")
    
    # 最初の配信情報を表示
    if lives:
        first = lives[0]
        print(f"  最初の配信: ID={first.id}, 日付={first.date}, タイトル={first.title[:30]}...")
    
    # IDで検索
    live = repo.get_by_id(1)
    if live:
        print(f"  ID=1の配信: {live.title[:30]}...")
    
    print("  ✓ LiveRepositoryのテスト完了\n")

def test_timestamp_repository():
    """TimestampRepositoryのテスト"""
    print("TimestampRepositoryのテスト開始...")
    repo = TimestampRepository("data/M_YT_LIVE_TIMESTAMP.TSV")
    
    # すべてのタイムスタンプ情報を読み込む
    timestamps = repo.load_all()
    print(f"  読み込んだタイムスタンプ情報: {len(timestamps)}件")
    
    # 最初のタイムスタンプ情報を表示
    if timestamps:
        first = timestamps[0]
        print(f"  最初のタイムスタンプ: ID={first.id}, LIVE_ID={first.live_id}, 曲名={first.song_name}")
    
    # 配信IDで検索
    ts_list = repo.get_by_live_id(1)
    print(f"  LIVE_ID=1のタイムスタンプ: {len(ts_list)}件")
    
    print("  ✓ TimestampRepositoryのテスト完了\n")

def test_song_list_repository():
    """SongListRepositoryのテスト"""
    print("SongListRepositoryのテスト開始...")
    repo = SongListRepository("data/V_SONG_LIST.TSV")
    
    # 既存の曲リストを読み込む
    songs = repo.load_all()
    print(f"  読み込んだ曲情報: {len(songs)}件")
    
    # 最初の曲情報を表示
    if songs:
        first = songs[0]
        print(f"  最初の曲: アーティスト={first.artist}, 曲名={first.song_name}")
    
    print("  ✓ SongListRepositoryのテスト完了\n")

if __name__ == "__main__":
    print("=" * 60)
    print("リポジトリ層の手動テスト")
    print("=" * 60 + "\n")
    
    try:
        test_live_repository()
        test_timestamp_repository()
        test_song_list_repository()
        
        print("=" * 60)
        print("すべてのテストが成功しました！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
