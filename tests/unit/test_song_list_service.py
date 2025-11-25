"""
SongListServiceのユニットテスト
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
import unittest.mock

from src.services.song_list_service import SongListService
from src.models.song_list_models import LiveInfo, TimestampInfo, SongInfo
from src.repositories.live_repository import LiveRepository
from src.repositories.timestamp_repository import TimestampRepository


class TestSongListService:
    """SongListServiceのテストクラス"""
    
    @pytest.fixture
    def mock_live_repo(self):
        """モックの配信情報リポジトリ"""
        repo = Mock(spec=LiveRepository)
        repo.load_all.return_value = [
            LiveInfo(
                id=1,
                date=datetime(2024, 1, 1),
                title="配信1",
                url="https://youtube.com/watch?v=abc"
            ),
            LiveInfo(
                id=2,
                date=datetime(2024, 1, 2),
                title="配信2",
                url="https://youtube.com/watch?v=def"
            )
        ]
        return repo
    
    @pytest.fixture
    def mock_timestamp_repo(self):
        """モックのタイムスタンプ情報リポジトリ"""
        repo = Mock(spec=TimestampRepository)
        repo.load_all.return_value = [
            TimestampInfo(
                id=1,
                live_id=1,
                timestamp="1:23:45",
                song_name="曲A",
                artist="アーティストA"
            ),
            TimestampInfo(
                id=2,
                live_id=2,
                timestamp="12:34",
                song_name="曲A",
                artist="アーティストA"
            ),
            TimestampInfo(
                id=3,
                live_id=1,
                timestamp="2:00:00",
                song_name="曲B",
                artist="アーティストB"
            )
        ]
        return repo
    
    @pytest.fixture
    def service(self, mock_live_repo, mock_timestamp_repo):
        """SongListServiceのインスタンス"""
        return SongListService(mock_live_repo, mock_timestamp_repo)
    
    def test_normalize_song_name_without_variation(self, service):
        """バリエーション表記がない曲名の正規化"""
        normalized, has_variation = service.normalize_song_name("夜に駆ける")
        assert normalized == "夜に駆ける"
        assert has_variation is False
    
    def test_normalize_song_name_with_chorus(self, service):
        """(1chorus)表記がある曲名の正規化"""
        normalized, has_variation = service.normalize_song_name("夜に駆ける(1chorus)")
        assert normalized == "夜に駆ける"
        assert has_variation is True
    
    def test_normalize_song_name_with_short_ver(self, service):
        """(short ver)表記がある曲名の正規化"""
        normalized, has_variation = service.normalize_song_name("夜に駆ける (short ver)")
        assert normalized == "夜に駆ける"
        assert has_variation is True
    
    def test_normalize_song_name_with_phrase(self, service):
        """(1phrase)表記がある曲名の正規化"""
        normalized, has_variation = service.normalize_song_name("曲名(1phrase)")
        assert normalized == "曲名"
        assert has_variation is True
    
    def test_normalize_song_name_idempotent(self, service):
        """曲名正規化の冪等性"""
        song_name = "夜に駆ける(1chorus)"
        normalized1, _ = service.normalize_song_name(song_name)
        normalized2, _ = service.normalize_song_name(normalized1)
        assert normalized1 == normalized2
    
    def test_generate_song_list_basic(self, service):
        """基本的な曲リスト生成"""
        songs = service.generate_song_list()
        
        # 2曲生成されることを確認（曲Aは最新のものが選ばれる）
        assert len(songs) == 2
        
        # アーティスト名と曲名が正しいことを確認
        artists = {song.artist for song in songs}
        assert "アーティストA" in artists
        assert "アーティストB" in artists
    
    def test_join_data_with_missing_live(self, service, mock_timestamp_repo):
        """対応する配信情報がない場合のデータ結合"""
        # 存在しないLIVE_IDを持つタイムスタンプ情報を追加
        mock_timestamp_repo.load_all.return_value.append(
            TimestampInfo(
                id=999,
                live_id=999,  # 存在しないLIVE_ID
                timestamp="1:00:00",
                song_name="曲C",
                artist="アーティストC"
            )
        )
        
        songs = service.generate_song_list()
        
        # 存在しないLIVE_IDのレコードはスキップされる
        assert all(song.artist != "アーティストC" for song in songs)
    
    def test_filter_empty_data(self, service, mock_timestamp_repo):
        """空データのフィルタリング"""
        # 空の曲名を持つタイムスタンプ情報を追加
        mock_timestamp_repo.load_all.return_value.append(
            TimestampInfo(
                id=100,
                live_id=1,
                timestamp="3:00:00",
                song_name="",  # 空の曲名
                artist="アーティストD"
            )
        )
        
        songs = service.generate_song_list()
        
        # 空の曲名のレコードはスキップされる
        assert all(song.song_name != "" for song in songs)
        assert all(song.artist != "" for song in songs)
    
    def test_sort_songs_by_artist_sort_and_song_name(self, mock_live_repo, mock_timestamp_repo):
        """ソート用アーティスト名と曲名でソート"""
        # 複数のアーティストと曲を持つタイムスタンプ情報を設定
        mock_timestamp_repo.load_all.return_value = [
            TimestampInfo(
                id=1,
                live_id=1,
                timestamp="1:00:00",
                song_name="曲B",
                artist="米津玄師"  # よねづけんし
            ),
            TimestampInfo(
                id=2,
                live_id=1,
                timestamp="2:00:00",
                song_name="曲A",
                artist="米津玄師"  # よねづけんし
            ),
            TimestampInfo(
                id=3,
                live_id=1,
                timestamp="3:00:00",
                song_name="曲C",
                artist="Vaundy"  # Vaundy
            ),
            TimestampInfo(
                id=4,
                live_id=1,
                timestamp="4:00:00",
                song_name="曲D",
                artist="YOASOBI"  # YOASOBI
            )
        ]
        
        service = SongListService(mock_live_repo, mock_timestamp_repo)
        songs = service.generate_song_list()
        
        # ソート順を確認
        # 期待される順序: Vaundy, YOASOBI, 米津玄師（よねづけんし）
        # 同じアーティストの場合は曲名順: 曲A, 曲B
        assert len(songs) == 4
        
        # ソート用アーティスト名の昇順を確認
        for i in range(len(songs) - 1):
            current_artist_sort = songs[i].artist_sort
            next_artist_sort = songs[i + 1].artist_sort
            
            # 同じアーティストの場合は曲名の昇順を確認
            if current_artist_sort == next_artist_sort:
                assert songs[i].song_name <= songs[i + 1].song_name
            else:
                assert current_artist_sort <= next_artist_sort
    
    def test_sort_songs_same_artist_multiple_songs(self, mock_live_repo, mock_timestamp_repo):
        """同じアーティストの複数の曲が曲名順にソートされることを確認"""
        # 同じアーティストの複数の曲を設定
        mock_timestamp_repo.load_all.return_value = [
            TimestampInfo(
                id=1,
                live_id=1,
                timestamp="1:00:00",
                song_name="夜に駆ける",
                artist="YOASOBI"
            ),
            TimestampInfo(
                id=2,
                live_id=1,
                timestamp="2:00:00",
                song_name="アイドル",
                artist="YOASOBI"
            ),
            TimestampInfo(
                id=3,
                live_id=1,
                timestamp="3:00:00",
                song_name="群青",
                artist="YOASOBI"
            )
        ]
        
        service = SongListService(mock_live_repo, mock_timestamp_repo)
        songs = service.generate_song_list()
        
        # すべて同じアーティストであることを確認
        assert all(song.artist == "YOASOBI" for song in songs)
        
        # 曲名が昇順にソートされていることを確認
        song_names = [song.song_name for song in songs]
        assert song_names == sorted(song_names)

    def test_check_similarity(self, service):
        """類似性チェックのテスト"""
        songs = [
            SongInfo(artist="ArtistA", artist_sort="A", song_name="SongA", latest_url="url1"),
            SongInfo(artist="ArtistB", artist_sort="B", song_name="SongB", latest_url="url2"),
            SongInfo(artist="ArtistA", artist_sort="A", song_name="SongA (cover)", latest_url="url3"), # Similar to SongA
        ]
        
        # Mock similarity checker to return a match
        service.similarity_checker.find_similar_pairs = Mock(return_value=[
            ("SongA", "SongA (cover)", 0.9)
        ])
        
        warnings = service.check_similarity(songs)
        
        # Check if warnings are generated
        assert len(warnings) > 0
        # We might get artist warnings too because the mock returns the same result for both calls
        # So we check if at least one warning is of type 'song'
        song_warnings = [w for w in warnings if w.type == 'song']
        assert len(song_warnings) > 0
        assert song_warnings[0].similarity == 0.9

    def test_compare_with_existing(self, service):
        """既存ファイルとの差分検出テスト"""
        new_songs = [
            SongInfo(artist="A", artist_sort="A", song_name="Song1", latest_url="url1"), # Existing
            SongInfo(artist="B", artist_sort="B", song_name="Song2", latest_url="url2"), # New
        ]
        
        # Mock SongListRepository to return existing songs
        with unittest.mock.patch('src.services.song_list_service.SongListRepository') as MockRepo:
            mock_repo_instance = MockRepo.return_value
            mock_repo_instance.load_all.return_value = [
                SongInfo(artist="A", artist_sort="A", song_name="Song1", latest_url="url1"),
                SongInfo(artist="C", artist_sort="C", song_name="Song3", latest_url="url3"), # Removed
            ]
            
            diff = service.compare_with_existing(new_songs, "dummy_path")
            
            assert len(diff.added) == 1
            assert diff.added[0].song_name == "Song2"
            
            assert len(diff.removed) == 1
            assert diff.removed[0].song_name == "Song3"
            
            assert len(diff.updated) == 0

    def test_select_latest_from_records_empty(self, service):
        """空のレコードリストからの選択テスト"""
        result = service._select_latest_from_records([])
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
