"""
DataPipelineクラスの手動テスト

実際のデータファイルを使用してDataPipelineクラスの動作を確認します。
"""

from src.config.settings import Config
from src.services.data_service import DataService
from src.core.data_pipeline import DataPipeline


def test_data_pipeline():
    """DataPipelineの基本動作をテスト"""
    print("=== DataPipeline 手動テスト開始 ===\n")
    
    # 設定とサービスの初期化
    print("1. 設定とサービスを初期化中...")
    config = Config()
    data_service = DataService(config)
    pipeline = DataPipeline(data_service, config)
    print("   初期化完了\n")
    
    # パイプライン実行
    print("2. パイプラインを実行中...")
    df = pipeline.execute()
    
    if df is None:
        print("   エラー: パイプライン実行に失敗しました")
        return False
    
    print(f"   パイプライン実行完了: {len(df)}件のデータを処理\n")
    
    # 結果の検証
    print("3. 結果を検証中...")
    
    # 必須カラムの存在確認
    required_columns = [
        "楽曲ID",
        "LIVE_ID",
        "曲名",
        "アーティスト",
        "タイムスタンプ",
        "ライブタイトル",
        "元ライブURL",
        "ライブ配信日",
        "ライブ配信日_original",
        "ライブ配信日_sortable",
        "タイムスタンプ_秒",
        "YouTubeタイムスタンプ付きURL",
        "曲順",
        "ライブ番号",
        "曲目",
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"   エラー: 必須カラムが不足しています: {missing_columns}")
        return False
    
    print("   全ての必須カラムが存在します")
    
    # データの内容確認
    print(f"\n4. データサンプル（最初の3件）:")
    print(df[["曲名", "アーティスト", "曲目", "ライブ配信日"]].head(3).to_string())
    
    # キャッシュのテスト
    print("\n5. キャッシュ機能をテスト中...")
    df2 = pipeline.execute()
    if df2 is None:
        print("   エラー: 2回目の実行に失敗しました")
        return False
    
    print(f"   キャッシュから取得: {len(df2)}件")
    
    # キャッシュクリアのテスト
    print("\n6. キャッシュクリア機能をテスト中...")
    pipeline.clear_cache()
    print("   キャッシュをクリアしました")
    
    print("\n=== DataPipeline 手動テスト完了 ===")
    print("全てのテストが成功しました！")
    return True


if __name__ == "__main__":
    success = test_data_pipeline()
    exit(0 if success else 1)
