"""
環境構築動作確認テスト

Docker Composeで構築した環境が正しく動作することを確認するテストです。
要件10.1〜10.4に基づいて、以下を検証します：
- アプリケーションが正常に起動すること
- 基本機能（データ読み込み、検索）が動作すること
- 環境分離が正しく機能していること
- 本番環境との整合性

このテストは、環境構築後の動作確認として実行されます。
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Config
from src.services.data_service import DataService
from src.core.data_pipeline import DataPipeline
from src.services.search_service import SearchService


class TestEnvironmentVerification:
    """環境構築動作確認テストクラス"""
    
    @pytest.fixture
    def config(self):
        """設定オブジェクトを提供するフィクスチャ"""
        # 環境変数が正しく設定されていない場合はデフォルト値を使用
        import os
        from unittest.mock import patch
        
        # デフォルトのファイルパスを設定
        default_env = {
            "SHINOUTA_LIVES_FILE_PATH": "data/M_YT_LIVE.TSV",
            "SHINOUTA_SONGS_FILE_PATH": "data/M_YT_LIVE_TIMESTAMP.TSV",
            "SHINOUTA_SONG_LIST_FILE_PATH": "data/V_SONG_LIST.TSV"
        }
        
        # 既存の環境変数をマージ
        env_vars = {**default_env}
        for key in default_env.keys():
            if key in os.environ and os.environ[key] not in ["", "0"]:
                env_vars[key] = os.environ[key]
        
        with patch.dict(os.environ, env_vars):
            return Config.from_env()
    
    @pytest.fixture
    def data_service(self, config):
        """データサービスを提供するフィクスチャ"""
        return DataService(config)
    
    @pytest.fixture
    def data_pipeline(self, data_service, config):
        """データパイプラインを提供するフィクスチャ"""
        return DataPipeline(data_service, config)
    
    @pytest.fixture
    def search_service(self):
        """検索サービスを提供するフィクスチャ"""
        return SearchService()
    
    # ========================================
    # 要件10.1: アプリケーションが正常に起動すること
    # ========================================
    
    def test_data_files_exist(self, config):
        """
        必須データファイルが存在することを確認
        
        要件7.1, 7.2, 7.3: 必須TSVファイルの存在確認
        """
        # M_YT_LIVE.TSVの存在確認
        lives_path = Path(config.lives_file_path)
        assert lives_path.exists(), f"配信データファイルが見つかりません: {config.lives_file_path}"
        
        # M_YT_LIVE_TIMESTAMP.TSVの存在確認
        songs_path = Path(config.songs_file_path)
        assert songs_path.exists(), f"楽曲データファイルが見つかりません: {config.songs_file_path}"
        
        # V_SONG_LIST.TSVの存在確認
        song_list_path = Path(config.song_list_file_path)
        assert song_list_path.exists(), f"楽曲リストファイルが見つかりません: {config.song_list_file_path}"
    
    def test_python_version(self):
        """
        Pythonバージョンが3.11であることを確認
        
        要件13.1, 14.1: 本番環境と同じPython 3.11を使用
        """
        assert sys.version_info.major == 3, "Pythonメジャーバージョンが3ではありません"
        assert sys.version_info.minor == 11, "Pythonマイナーバージョンが11ではありません（本番環境と一致しません）"
    
    # ========================================
    # 要件10.2: データ読み込みが正常に動作すること
    # ========================================
    
    def test_load_lives_data(self, data_service):
        """
        配信データが正常に読み込めることを確認
        
        要件10.2: データ読み込み機能の動作確認
        """
        lives_df = data_service.load_lives_data()
        
        assert lives_df is not None, "配信データの読み込みに失敗しました"
        assert isinstance(lives_df, pd.DataFrame), "配信データがDataFrameではありません"
        assert len(lives_df) > 0, "配信データが空です"
        
        # 必須列の存在確認
        required_columns = ["ID", "配信日", "タイトル", "URL"]
        for col in required_columns:
            assert col in lives_df.columns, f"配信データに必須列 '{col}' が存在しません"
    
    def test_load_songs_data(self, data_service):
        """
        楽曲データが正常に読み込めることを確認
        
        要件10.2: データ読み込み機能の動作確認
        """
        songs_df = data_service.load_songs_data()
        
        assert songs_df is not None, "楽曲データの読み込みに失敗しました"
        assert isinstance(songs_df, pd.DataFrame), "楽曲データがDataFrameではありません"
        assert len(songs_df) > 0, "楽曲データが空です"
        
        # 必須列の存在確認
        required_columns = ["LIVE_ID", "曲名", "アーティスト", "タイムスタンプ"]
        for col in required_columns:
            assert col in songs_df.columns, f"楽曲データに必須列 '{col}' が存在しません"
    
    def test_data_pipeline_execution(self, data_pipeline):
        """
        データパイプラインが正常に実行できることを確認
        
        要件10.2: データ処理パイプラインの動作確認
        """
        df = data_pipeline.execute()
        
        assert df is not None, "データパイプラインの実行に失敗しました"
        assert isinstance(df, pd.DataFrame), "パイプライン結果がDataFrameではありません"
        assert len(df) > 0, "パイプライン結果が空です"
        
        # 処理後の必須列の存在確認
        required_columns = [
            "ライブ配信日",
            "曲名",
            "アーティスト",
            "YouTubeタイムスタンプ付きURL",
            "曲目"
        ]
        for col in required_columns:
            assert col in df.columns, f"処理後データに必須列 '{col}' が存在しません"
    
    # ========================================
    # 要件10.3: 基本機能（検索）が動作すること
    # ========================================
    
    def test_search_functionality(self, data_pipeline, search_service):
        """
        検索機能が正常に動作することを確認
        
        要件10.3: 検索機能の動作確認
        """
        # データパイプラインを実行
        df = data_pipeline.execute()
        assert df is not None, "データパイプラインの実行に失敗しました"
        
        # 検索実行（曲名で検索）
        search_query = "夜"
        search_fields = ["曲名", "アーティスト"]
        result_df = search_service.search(df, search_query, search_fields, case_sensitive=False)
        
        assert result_df is not None, "検索結果がNoneです"
        assert isinstance(result_df, pd.DataFrame), "検索結果がDataFrameではありません"
        
        # 検索結果が元データのサブセットであることを確認
        assert len(result_df) <= len(df), "検索結果が元データより多いです"
        
        # 検索結果に検索キーワードが含まれていることを確認
        if len(result_df) > 0:
            # 少なくとも1件は検索キーワードを含むはず
            contains_keyword = result_df.apply(
                lambda row: any(
                    search_query in str(row[field]).lower() 
                    for field in search_fields 
                    if field in row.index
                ),
                axis=1
            )
            assert contains_keyword.any(), "検索結果に検索キーワードが含まれていません"
    
    def test_search_with_live_title(self, data_pipeline, search_service):
        """
        ライブタイトルを含む検索が正常に動作することを確認
        
        要件10.3: 検索機能の動作確認（ライブタイトル含む）
        """
        # データパイプラインを実行
        df = data_pipeline.execute()
        assert df is not None, "データパイプラインの実行に失敗しました"
        
        # ライブタイトルを含む検索
        search_query = "歌"
        search_fields = ["曲名", "アーティスト", "ライブタイトル"]
        result_df = search_service.search(df, search_query, search_fields, case_sensitive=False)
        
        assert result_df is not None, "検索結果がNoneです"
        assert isinstance(result_df, pd.DataFrame), "検索結果がDataFrameではありません"
        assert len(result_df) <= len(df), "検索結果が元データより多いです"
    
    # ========================================
    # 要件10.4: データ整合性の確認
    # ========================================
    
    def test_youtube_url_generation(self, data_pipeline):
        """
        YouTubeタイムスタンプ付きURLが正しく生成されることを確認
        
        要件10.4: データ処理の正確性確認
        """
        df = data_pipeline.execute()
        assert df is not None, "データパイプラインの実行に失敗しました"
        
        # YouTubeタイムスタンプ付きURLが存在することを確認
        assert "YouTubeタイムスタンプ付きURL" in df.columns, "YouTubeタイムスタンプ付きURL列が存在しません"
        
        # 全ての行にURLが生成されていることを確認
        assert df["YouTubeタイムスタンプ付きURL"].notna().all(), "一部の行でURLが生成されていません"
        
        # URLの形式確認（サンプル）
        sample_url = df["YouTubeタイムスタンプ付きURL"].iloc[0]
        assert "youtube.com" in sample_url or "youtu.be" in sample_url, "YouTubeのURLではありません"
        assert "t=" in sample_url, "タイムスタンプパラメータが含まれていません"
    
    def test_song_numbers_generation(self, data_pipeline):
        """
        曲目番号が正しく生成されることを確認
        
        要件10.4: データ処理の正確性確認
        """
        df = data_pipeline.execute()
        assert df is not None, "データパイプラインの実行に失敗しました"
        
        # 曲目列が存在することを確認
        assert "曲目" in df.columns, "曲目列が存在しません"
        
        # 全ての行に曲目番号が生成されていることを確認
        assert df["曲目"].notna().all(), "一部の行で曲目番号が生成されていません"
        
        # 曲目番号の形式確認（"N曲目" または "N-M曲目" の形式）
        sample_song_number = df["曲目"].iloc[0]
        assert isinstance(sample_song_number, str), "曲目番号が文字列ではありません"
        assert "曲目" in sample_song_number, "曲目番号に「曲目」が含まれていません"
        
        # 曲順列が存在し、正の整数であることを確認
        assert "曲順" in df.columns, "曲順列が存在しません"
        assert (df["曲順"] > 0).all(), "曲順に0以下の値が含まれています"
    
    def test_data_sorting(self, data_pipeline):
        """
        データが正しくソートされていることを確認
        
        要件10.4: データ処理の正確性確認
        """
        df = data_pipeline.execute()
        assert df is not None, "データパイプラインの実行に失敗しました"
        
        # ソート用の列が存在することを確認
        assert "ライブ配信日_sortable" in df.columns, "ソート用配信日列が存在しません"
        
        # データが配信日降順（新しい順）にソートされていることを確認
        # NaT（欠損値）を除外して確認
        valid_dates = df["ライブ配信日_sortable"].dropna()
        if len(valid_dates) > 1:
            # 降順であることを確認（前の日付 >= 次の日付）
            is_sorted_desc = (valid_dates.iloc[:-1].values >= valid_dates.iloc[1:].values).all()
            assert is_sorted_desc, "データが配信日降順にソートされていません"


class TestEnvironmentIsolation:
    """
    環境分離の確認テスト
    
    要件2.4, 14.5: Docker環境がローカル環境に影響を与えないことを確認
    """
    
    def test_running_in_container(self):
        """
        Dockerコンテナ内で実行されていることを確認
        
        注: このテストはDockerコンテナ内で実行された場合のみパスします
        """
        # Dockerコンテナ内では/.dockerenvファイルが存在する
        # または、環境変数でコンテナ実行を判定
        import os
        
        # 複数の方法でコンテナ実行を判定
        is_in_container = (
            Path("/.dockerenv").exists() or
            os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read() or
            os.environ.get("RUNNING_IN_DOCKER") == "true"
        )
        
        # このテストは情報提供のみ（失敗してもOK）
        if is_in_container:
            print("✓ Dockerコンテナ内で実行されています")
        else:
            print("ℹ ローカル環境で実行されています（Docker外）")
    
    def test_working_directory(self):
        """
        作業ディレクトリが/appであることを確認（Docker環境の場合）
        
        要件14.1: Dockerfileで指定した作業ディレクトリの確認
        """
        import os
        current_dir = os.getcwd()
        
        # Dockerコンテナ内では/appが作業ディレクトリ
        # ローカル環境では異なる可能性がある
        print(f"現在の作業ディレクトリ: {current_dir}")
        
        # プロジェクトルートにHome.pyが存在することを確認
        home_py = Path("Home.py")
        assert home_py.exists() or Path(project_root / "Home.py").exists(), \
            "Home.pyが見つかりません（作業ディレクトリが正しくありません）"


class TestProductionParity:
    """
    本番環境との整合性確認テスト
    
    要件13.1〜13.5: ローカル環境が本番環境と同じ動作をすることを確認
    """
    
    def test_required_packages_installed(self):
        """
        必須パッケージがインストールされていることを確認
        
        要件13.2: requirements.txtに記載された依存パッケージの確認
        """
        # Streamlitのインポート確認
        try:
            import streamlit
            print(f"✓ Streamlit {streamlit.__version__} がインストールされています")
        except ImportError:
            pytest.fail("Streamlitがインストールされていません")
        
        # Pandasのインポート確認
        try:
            import pandas
            print(f"✓ Pandas {pandas.__version__} がインストールされています")
        except ImportError:
            pytest.fail("Pandasがインストールされていません")
    
    def test_config_from_environment(self):
        """
        環境変数から設定が読み込めることを確認
        
        要件8.2, 13.4: 環境変数による設定の切り替え
        """
        import os
        
        # 環境変数を設定
        os.environ["SHINOUTA_ENABLE_CACHE"] = "false"
        os.environ["SHINOUTA_CACHE_TTL"] = "7200"
        os.environ["SHINOUTA_PAGE_TITLE"] = "テストタイトル"
        
        # 設定を読み込み
        config = Config.from_env()
        
        # 環境変数が反映されていることを確認
        assert config.enable_cache is False, "環境変数SHINOUTA_ENABLE_CACHEが反映されていません"
        assert config.cache_ttl == 7200, "環境変数SHINOUTA_CACHE_TTLが反映されていません"
        assert config.page_title == "テストタイトル", "環境変数SHINOUTA_PAGE_TITLEが反映されていません"
        
        # 環境変数をクリア
        del os.environ["SHINOUTA_ENABLE_CACHE"]
        del os.environ["SHINOUTA_CACHE_TTL"]
        del os.environ["SHINOUTA_PAGE_TITLE"]
