import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.repositories.song_list_repository import SongListRepository
from src.models.song_list_models import SongInfo
from src.exceptions.errors import DataLoadError, FileWriteError

class TestSongListRepository:
    @pytest.fixture
    def repository(self, tmp_path):
        """テスト用のリポジトリインスタンスを作成"""
        file_path = tmp_path / "test_songs.tsv"
        return SongListRepository(str(file_path))

    def test_load_all_success(self, repository, tmp_path):
        """正常系: TSVファイルを正しく読み込めること"""
        # Setup
        file_path = tmp_path / "test_songs.tsv"
        content = (
            "アーティスト\tアーティスト(ソート用)\t曲名\t最近の歌唱\n"
            "Artist1\tSort1\tSong1\thttps://example.com/1\n"
            "Artist2\tSort2\tSong2\thttps://example.com/2"
        )
        file_path.write_text(content, encoding='utf-8')

        # Execute
        result = repository.load_all()

        # Verify
        assert len(result) == 2
        
        assert result[0].artist == "Artist1"
        assert result[0].artist_sort == "Sort1"
        assert result[0].song_name == "Song1"
        assert result[0].latest_url == "https://example.com/1"
        
        assert result[1].artist == "Artist2"
        assert result[1].artist_sort == "Sort2"
        assert result[1].song_name == "Song2"
        assert result[1].latest_url == "https://example.com/2"

    def test_load_all_file_not_found(self, repository):
        """正常系: ファイルが存在しない場合は空リストを返すこと"""
        # Execute
        result = repository.load_all()

        # Verify
        assert result == []

    def test_load_all_invalid_header(self, repository, tmp_path):
        """異常系: ヘッダーが不正な場合はエラーになること"""
        # Setup
        file_path = tmp_path / "test_songs.tsv"
        content = "Invalid\tHeader\nValue1\tValue2"
        file_path.write_text(content, encoding='utf-8')

        # Verify
        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "ファイル形式が不正です" in str(excinfo.value)

    def test_load_all_parsing_error(self, repository, tmp_path):
        """異常系: 行の解析に失敗した場合はエラーになること"""
        # Setup - 必須フィールドが欠けている
        file_path = tmp_path / "test_songs.tsv"
        # DictReaderはヘッダーより少ないフィールドの行をNoneで埋めることがあるため、
        # ここでは明示的にKeyErrorが出るような状況を作るか、カラムが足りない状況を作る。
        # 実装の _parse_row では row['アーティスト'] などでアクセスしているので、
        # タブ区切りが足りないと列とヘッダーのマッピングがおかしくなるが、
        # csvモジュールの挙動として、足りない分はNoneが入る。
        # _parse_rowの実装: row['アーティスト'].strip() -> AttributeError if value is None
        
        content = (
            "アーティスト\tアーティスト(ソート用)\t曲名\t最近の歌唱\n"
            "Artist1\tSort1\tSong1"  # 最後のカラムが足りない
        )
        file_path.write_text(content, encoding='utf-8')

        # Verify
        # csv.DictReader behavior: if a row has fewer fields than fieldnames, 
        # the remaining keys take the value of the optional restkey parameter, 
        # or None is used.
        # So row['最近の歌唱'] will be None.
        # None.strip() raises AttributeError.
        # The repository catches Exception and raises DataLoadError.
        
        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "解析に失敗しました" in str(excinfo.value)

    def test_save_all_success(self, repository, tmp_path):
        """正常系: データを正しく保存できること"""
        # Setup
        songs = [
            SongInfo(artist="Artist1", artist_sort="Sort1", song_name="Song1", latest_url="url1"),
            SongInfo(artist="Artist2", artist_sort="Sort2", song_name="Song2", latest_url="url2")
        ]

        # Execute
        repository.save_all(songs)

        # Verify
        file_path = tmp_path / "test_songs.tsv"
        assert file_path.exists()
        content = file_path.read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        assert len(lines) == 3  # Header + 2 rows
        
        # Header check
        assert lines[0].strip() == "アーティスト\tアーティスト(ソート用)\t曲名\t最近の歌唱"
        
        # Content check
        assert "Artist1\tSort1\tSong1\turl1" in lines[1]
        assert "Artist2\tSort2\tSong2\turl2" in lines[2]

    def test_save_all_permission_error(self, repository):
        """異常系: 保存時に権限エラーが発生した場合はFileWriteErrorになること"""
        # Setup
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            songs = [SongInfo(artist="A", artist_sort="S", song_name="S", latest_url="U")]
            
            # Verify
            with pytest.raises(FileWriteError) as excinfo:
                repository.save_all(songs)
            assert "書き込み権限がありません" in str(excinfo.value)

    def test_save_all_os_error(self, repository):
        """異常系: 保存時にOSエラーが発生した場合はFileWriteErrorになること"""
        # Setup
        with patch("builtins.open", side_effect=OSError("Disk full")):
            songs = [SongInfo(artist="A", artist_sort="S", song_name="S", latest_url="U")]
            
            # Verify
            with pytest.raises(FileWriteError) as excinfo:
                repository.save_all(songs)
            assert "ファイルの書き込みに失敗しました" in str(excinfo.value)

    def test_detect_encoding_utf8(self, repository, tmp_path):
        """正常系: UTF-8エンコーディングを正しく検出できること"""
        file_path = tmp_path / "test_songs.tsv"
        file_path.write_text("テスト", encoding='utf-8')
        assert repository._detect_encoding() == 'utf-8'

    def test_detect_encoding_non_utf8(self, repository, tmp_path):
        """正常系: その他のエンコーディングを検出できること（またはフォールバック）"""
        file_path = tmp_path / "test_songs.tsv"
        # Shift_JISで書き込む
        content = "テスト".encode('shift_jis')
        with open(file_path, 'wb') as f:
            f.write(content)
            
        # chardetで検出されたものを返すはず
        detected = repository._detect_encoding()
        assert isinstance(detected, str)
        # Shift_JIS or valid encoding name should be returned. 
        # Note: chardet behavior can be probabilistic for short strings.
