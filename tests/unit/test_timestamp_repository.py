import pytest
from unittest.mock import patch, MagicMock
from src.repositories.timestamp_repository import TimestampRepository
from src.models.song_list_models import TimestampInfo
from src.exceptions.errors import DataLoadError

class TestTimestampRepository:
    @pytest.fixture
    def repository(self, tmp_path):
        """テスト用のリポジトリインスタンスを作成"""
        file_path = tmp_path / "test_timestamp.tsv"
        return TimestampRepository(str(file_path))

    def test_load_all_success(self, repository, tmp_path):
        """正常系: TSVファイルを正しく読み込めること"""
        # Setup
        file_path = tmp_path / "test_timestamp.tsv"
        content = (
            "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
            "1\t100\t00:01\tSong1\tArtist1\n"
            "2\t100\t00:05\tSong2\tArtist2\n"
            "3\t200\t01:00\tSong3\tArtist3"
        )
        file_path.write_text(content, encoding='utf-8')

        # Execute
        result = repository.load_all()

        # Verify
        assert len(result) == 3
        
        assert result[0].id == 1
        assert result[0].live_id == 100
        assert result[0].song_name == "Song1"
        
        assert result[2].id == 3
        assert result[2].live_id == 200

    def test_load_all_file_not_found(self, repository):
        """異常系: ファイルが存在しない場合はエラーになること"""
        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "ファイルが存在しません" in str(excinfo.value)

    def test_load_all_invalid_header(self, repository, tmp_path):
        """異常系: ヘッダーが不正な場合はエラーになること"""
        file_path = tmp_path / "test_timestamp.tsv"
        content = "Invalid\tHeader\n1\t100\t00:01"
        file_path.write_text(content, encoding='utf-8')

        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "ファイル形式が不正です" in str(excinfo.value)

    def test_load_all_parsing_error(self, repository, tmp_path):
        """異常系: 行の解析に失敗した場合はエラーになること"""
        file_path = tmp_path / "test_timestamp.tsv"
        # IDが数値でない
        content = (
            "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
            "NOT_INT\t100\t00:01\tSong1\tArtist1"
        )
        file_path.write_text(content, encoding='utf-8')

        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "解析に失敗しました" in str(excinfo.value)

    def test_get_by_live_id_found(self, repository, tmp_path):
        """正常系: 指定したLIVE_IDのデータのみを取得できること"""
        # Setup
        file_path = tmp_path / "test_timestamp.tsv"
        content = (
            "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
            "1\t100\t00:01\tSong1\tArtist1\n"
            "2\t200\t01:00\tSong2\tArtist2\n"
            "3\t100\t00:05\tSong3\tArtist3"
        )
        file_path.write_text(content, encoding='utf-8')

        # Execute
        result = repository.get_by_live_id(100)

        # Verify
        assert len(result) == 2
        assert {item.id for item in result} == {1, 3}
        for item in result:
            assert item.live_id == 100

    def test_get_by_live_id_not_found(self, repository, tmp_path):
        """正常系: 指定したLIVE_IDのデータがない場合は空リストを返すこと"""
        # Setup
        file_path = tmp_path / "test_timestamp.tsv"
        content = (
            "ID\tLIVE_ID\tタイムスタンプ\t曲名\tアーティスト\n"
            "1\t100\t00:01\tSong1\tArtist1"
        )
        file_path.write_text(content, encoding='utf-8')

        # Execute
        result = repository.get_by_live_id(999)

        # Verify
        assert result == []

    def test_detect_encoding_utf8(self, repository, tmp_path):
        """正常系: UTF-8エンコーディングを正しく検出できること"""
        file_path = tmp_path / "test_timestamp.tsv"
        file_path.write_text("テスト", encoding='utf-8')
        assert repository._detect_encoding() == 'utf-8'
