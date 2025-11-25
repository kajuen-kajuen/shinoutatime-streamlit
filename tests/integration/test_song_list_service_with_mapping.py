"""
SongListServiceと修正マッピングの統合テスト

修正マッピングが曲リスト生成に正しく適用され、
ソート順に反映されることをテストします。

要件: 5.3
"""

import tempfile
from pathlib import Path
import pytest
from datetime import datetime

from src.services.song_list_service import SongListService
from src.repositories.live_repository import LiveRepository
from src.repositories.timestamp_repository import TimestampRepository
from src.repositories.artist_sort_mapping_repository import ArtistSortMappingRepository
from src.models.song_list_models import LiveInfo, TimestampInfo


class TestSongListServiceWithMapping:
    """修正マッピングを使用した曲リスト生成の統合テスト"""
    
    def test_mapping_applied_to_song_list_generation(self):
        """
        修正マッピングが曲リスト生成に正しく適用されることをテスト
        
        要件: 5.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用のTSVファイルを作成
            live_file = tmpdir_path / "M_YT_LIVE.TSV"
            timestamp_file = tmpdir_path / "M_YT_LIVE_TIMESTAMP.TSV"
            mapping_file = tmpdir_path / "artist_sort_mapping.tsv"
            
            # M_YT_LIVE.TSVを作成
            live_file.write_text(
                "ID\t配信日\tタイトル\tURL\n"
                "1\t2024/1/1\t新年配信\thttps://youtube.com/watch?v=1\n"
                "2\t2024/1/15\t歌枠配信\thttps://youtube.com/watch?v=2\n",
                encoding='utf-8'
            )
            
            # M_YT_LIVE_TIMESTAMP.TSVを作成
            # 日本語アーティスト名と英語アーティスト名を混在させる
            timestamp_file.write_text(
                "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
                "1\t1\t00:05:30\t曲A\t米津玄師\n"
                "2\t1\t00:15:20\t曲B\tVaundy\n"
                "3\t2\t00:10:00\t曲C\tOfficial髭男dism\n",
                encoding='utf-8'
            )
            
            # 修正マッピングファイルを作成
            # 米津玄師の読み仮名を修正（自動変換では「こめつげんし」になる可能性がある）
            # Official髭男dismの読み仮名を修正
            mapping_file.write_text(
                "アーティスト名\tソート名\n"
                "米津玄師\tよねづけんし\n"
                "Official髭男dism\tおふぃしゃるひげだんでぃずむ\n",
                encoding='utf-8'
            )
            
            # リポジトリを作成
            live_repo = LiveRepository(str(live_file))
            timestamp_repo = TimestampRepository(str(timestamp_file))
            
            # SongListServiceを作成（修正マッピングファイルを指定）
            service = SongListService(
                live_repo,
                timestamp_repo,
                mapping_file_path=str(mapping_file)
            )
            
            # 曲リストを生成
            song_list = service.generate_song_list()
            
            # 結果を検証
            assert len(song_list) == 3
            
            # 修正マッピングが適用されていることを確認
            artist_sort_map = {song.artist: song.artist_sort for song in song_list}
            
            # 米津玄師のソート名が修正マッピングの値になっていることを確認
            assert artist_sort_map["米津玄師"] == "よねづけんし"
            
            # Official髭男dismのソート名が修正マッピングの値になっていることを確認
            assert artist_sort_map["Official髭男dism"] == "おふぃしゃるひげだんでぃずむ"
            
            # Vaundyはマッピングがないので、そのまま（英語のみ）
            assert artist_sort_map["Vaundy"] == "Vaundy"
    
    def test_mapping_affects_sort_order(self):
        """
        修正マッピングがソート順に反映されることをテスト
        
        要件: 5.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用のTSVファイルを作成
            live_file = tmpdir_path / "M_YT_LIVE.TSV"
            timestamp_file = tmpdir_path / "M_YT_LIVE_TIMESTAMP.TSV"
            mapping_file = tmpdir_path / "artist_sort_mapping.tsv"
            
            # M_YT_LIVE.TSVを作成
            live_file.write_text(
                "ID\t配信日\tタイトル\tURL\n"
                "1\t2024/1/1\t配信\thttps://youtube.com/watch?v=1\n",
                encoding='utf-8'
            )
            
            # M_YT_LIVE_TIMESTAMP.TSVを作成
            # ソート順をテストするために複数のアーティストを追加
            timestamp_file.write_text(
                "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
                "1\t1\t00:05:00\t曲1\tアーティストC\n"
                "2\t1\t00:10:00\t曲2\tアーティストA\n"
                "3\t1\t00:15:00\t曲3\tアーティストB\n",
                encoding='utf-8'
            )
            
            # 修正マッピングファイルを作成
            # ソート順を逆転させるマッピング
            # アーティストC -> "あ"（最初）
            # アーティストA -> "う"（最後）
            # アーティストB -> "い"（中間）
            mapping_file.write_text(
                "アーティスト名\tソート名\n"
                "アーティストC\tあ\n"
                "アーティストA\tう\n"
                "アーティストB\tい\n",
                encoding='utf-8'
            )
            
            # リポジトリを作成
            live_repo = LiveRepository(str(live_file))
            timestamp_repo = TimestampRepository(str(timestamp_file))
            
            # SongListServiceを作成（修正マッピングファイルを指定）
            service = SongListService(
                live_repo,
                timestamp_repo,
                mapping_file_path=str(mapping_file)
            )
            
            # 曲リストを生成
            song_list = service.generate_song_list()
            
            # ソート順を検証
            # 修正マッピングにより、ソート順は「あ」「い」「う」になるはず
            assert len(song_list) == 3
            assert song_list[0].artist == "アーティストC"  # "あ"
            assert song_list[1].artist == "アーティストB"  # "い"
            assert song_list[2].artist == "アーティストA"  # "う"

    
    def test_mapping_with_no_mapping_file(self):
        """
        修正マッピングファイルが存在しない場合のテスト
        
        要件: 5.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用のTSVファイルを作成
            live_file = tmpdir_path / "M_YT_LIVE.TSV"
            timestamp_file = tmpdir_path / "M_YT_LIVE_TIMESTAMP.TSV"
            mapping_file = tmpdir_path / "nonexistent_mapping.tsv"  # 存在しないファイル
            
            # M_YT_LIVE.TSVを作成
            live_file.write_text(
                "ID\t配信日\tタイトル\tURL\n"
                "1\t2024/1/1\t配信\thttps://youtube.com/watch?v=1\n",
                encoding='utf-8'
            )
            
            # M_YT_LIVE_TIMESTAMP.TSVを作成
            timestamp_file.write_text(
                "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
                "1\t1\t00:05:00\t曲1\t米津玄師\n"
                "2\t1\t00:10:00\t曲2\tVaundy\n",
                encoding='utf-8'
            )
            
            # リポジトリを作成
            live_repo = LiveRepository(str(live_file))
            timestamp_repo = TimestampRepository(str(timestamp_file))
            
            # SongListServiceを作成（存在しない修正マッピングファイルを指定）
            service = SongListService(
                live_repo,
                timestamp_repo,
                mapping_file_path=str(mapping_file)
            )
            
            # 曲リストを生成（エラーにならずに自動変換が使用される）
            song_list = service.generate_song_list()
            
            # 結果を検証
            assert len(song_list) == 2
            
            # 自動変換が使用されていることを確認
            # 米津玄師は自動変換される（pykakasiによる変換）
            # Vaundyは英語のみなのでそのまま
            artist_sort_map = {song.artist: song.artist_sort for song in song_list}
            assert "米津玄師" in artist_sort_map
            assert artist_sort_map["Vaundy"] == "Vaundy"
    
    def test_mapping_with_partial_coverage(self):
        """
        一部のアーティストのみマッピングがある場合のテスト
        
        要件: 5.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用のTSVファイルを作成
            live_file = tmpdir_path / "M_YT_LIVE.TSV"
            timestamp_file = tmpdir_path / "M_YT_LIVE_TIMESTAMP.TSV"
            mapping_file = tmpdir_path / "artist_sort_mapping.tsv"
            
            # M_YT_LIVE.TSVを作成
            live_file.write_text(
                "ID\t配信日\tタイトル\tURL\n"
                "1\t2024/1/1\t配信\thttps://youtube.com/watch?v=1\n",
                encoding='utf-8'
            )
            
            # M_YT_LIVE_TIMESTAMP.TSVを作成
            timestamp_file.write_text(
                "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
                "1\t1\t00:05:00\t曲1\t米津玄師\n"
                "2\t1\t00:10:00\t曲2\tあいみょん\n"
                "3\t1\t00:15:00\t曲3\tYOASOBI\n",
                encoding='utf-8'
            )
            
            # 修正マッピングファイルを作成（米津玄師のみマッピング）
            mapping_file.write_text(
                "アーティスト名\tソート名\n"
                "米津玄師\tよねづけんし\n",
                encoding='utf-8'
            )
            
            # リポジトリを作成
            live_repo = LiveRepository(str(live_file))
            timestamp_repo = TimestampRepository(str(timestamp_file))
            
            # SongListServiceを作成
            service = SongListService(
                live_repo,
                timestamp_repo,
                mapping_file_path=str(mapping_file)
            )
            
            # 曲リストを生成
            song_list = service.generate_song_list()
            
            # 結果を検証
            assert len(song_list) == 3
            
            artist_sort_map = {song.artist: song.artist_sort for song in song_list}
            
            # 米津玄師はマッピングが適用される
            assert artist_sort_map["米津玄師"] == "よねづけんし"
            
            # あいみょんとYOASOBIは自動変換が使用される
            assert "あいみょん" in artist_sort_map
            assert artist_sort_map["YOASOBI"] == "YOASOBI"  # 英語のみなのでそのまま
    
    def test_mapping_with_same_song_different_dates(self):
        """
        同じ曲が複数回歌唱された場合、最新の配信が選択されることをテスト
        
        要件: 5.3
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # テスト用のTSVファイルを作成
            live_file = tmpdir_path / "M_YT_LIVE.TSV"
            timestamp_file = tmpdir_path / "M_YT_LIVE_TIMESTAMP.TSV"
            mapping_file = tmpdir_path / "artist_sort_mapping.tsv"
            
            # M_YT_LIVE.TSVを作成（2つの配信）
            live_file.write_text(
                "ID\t配信日\tタイトル\tURL\n"
                "1\t2024/1/1\t古い配信\thttps://youtube.com/watch?v=old\n"
                "2\t2024/2/1\t新しい配信\thttps://youtube.com/watch?v=new\n",
                encoding='utf-8'
            )
            
            # M_YT_LIVE_TIMESTAMP.TSVを作成（同じ曲が2回）
            timestamp_file.write_text(
                "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
                "1\t1\t00:05:00\t夜に駆ける\tYOASOBI\n"
                "2\t2\t00:10:00\t夜に駆ける\tYOASOBI\n",
                encoding='utf-8'
            )
            
            # 修正マッピングファイルを作成
            mapping_file.write_text(
                "アーティスト名\tソート名\n"
                "YOASOBI\tよあそび\n",
                encoding='utf-8'
            )
            
            # リポジトリを作成
            live_repo = LiveRepository(str(live_file))
            timestamp_repo = TimestampRepository(str(timestamp_file))
            
            # SongListServiceを作成
            service = SongListService(
                live_repo,
                timestamp_repo,
                mapping_file_path=str(mapping_file)
            )
            
            # 曲リストを生成
            song_list = service.generate_song_list()
            
            # 結果を検証
            assert len(song_list) == 1  # 同じ曲なので1つだけ
            
            song = song_list[0]
            assert song.artist == "YOASOBI"
            assert song.song_name == "夜に駆ける"
            assert song.artist_sort == "よあそび"  # マッピングが適用されている
            
            # 最新の配信（2024/2/1）のURLが使用されていることを確認
            assert "new" in song.latest_url
            assert "old" not in song.latest_url
