import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.repositories.live_repository import LiveRepository
from src.models.song_list_models import LiveInfo
from src.exceptions.errors import DataLoadError

class TestLiveRepository:
    @pytest.fixture
    def repository(self, tmp_path):
        """テスト用のリポジトリインスタンスを作成"""
        file_path = tmp_path / "test_live.tsv"
        return LiveRepository(str(file_path))

    def test_load_all_success(self, repository, tmp_path):
        """正常系: TSVファイルを正しく読み込めること"""
        # Setup
        file_path = tmp_path / "test_live.tsv"
        content = (
            "ID\t配信日\tタイトル\tURL\n"
            "1\t2023/1/1\tTitle1\thttps://example.com/1\n"
            "2\t2023/12/31\tTitle2\thttps://example.com/2"
        )
        file_path.write_text(content, encoding='utf-8')

        # Execute
        result = repository.load_all()

        # Verify
        assert len(result) == 2
        
        assert result[0].id == 1
        assert result[0].date == datetime(2023, 1, 1)
        assert result[0].title == "Title1"
        assert result[0].url == "https://example.com/1"
        
        assert result[1].id == 2
        assert result[1].date == datetime(2023, 12, 31)
        assert result[1].title == "Title2"
        assert result[1].url == "https://example.com/2"

    def test_load_all_file_not_found(self, repository):
        """異常系: ファイルが存在しない場合はエラーになること"""
        # Note: LiveRepository raises DataLoadError intentionally unlike SongListRepository which returned empty list
        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "ファイルが存在しません" in str(excinfo.value)

    def test_load_all_invalid_header(self, repository, tmp_path):
        """異常系: ヘッダーが不正な場合はエラーになること"""
        file_path = tmp_path / "test_live.tsv"
        content = "Invalid\tHeader\n1\t2023/1/1"
        file_path.write_text(content, encoding='utf-8')

        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "ファイル形式が不正です" in str(excinfo.value)

    def test_load_all_parsing_error(self, repository, tmp_path):
        """異常系: 行の解析に失敗した場合はエラーになること"""
        file_path = tmp_path / "test_live.tsv"
        # 不正な日付形式
        content = (
            "ID\t配信日\tタイトル\tURL\n"
            "1\tINVALID_DATE\tTitle1\tURL1"
        )
        file_path.write_text(content, encoding='utf-8')

        with pytest.raises(DataLoadError) as excinfo:
            repository.load_all()
        assert "解析に失敗しました" in str(excinfo.value)

    def test_get_by_id_success(self, repository, tmp_path):
        """正常系: IDで配信情報を取得できること"""
        # Setup
        file_path = tmp_path / "test_live.tsv"
        content = (
            "ID\t配信日\tタイトル\tURL\n"
            "10\t2023/1/1\tTitle1\tURL1\n"
            "20\t2023/1/2\tTitle2\tURL2"
        )
        file_path.write_text(content, encoding='utf-8')

        # Execute
        result = repository.get_by_id(20)

        # Verify
        assert result is not None
        assert result.id == 20
        assert result.title == "Title2"

    def test_get_by_id_not_found(self, repository, tmp_path):
        """正常系: 存在しないIDの場合はNoneを返すこと"""
        # Setup
        file_path = tmp_path / "test_live.tsv"
        content = (
            "ID\t配信日\tタイトル\tURL\n"
            "1\t2023/1/1\tTitle1\tURL1"
        )
        file_path.write_text(content, encoding='utf-8')

        # Execute
        result = repository.get_by_id(999)

        # Verify
        assert result is None

    def test_detect_encoding_utf8(self, repository, tmp_path):
        """正常系: UTF-8エンコーディングを正しく検出できること"""
        file_path = tmp_path / "test_live.tsv"
        file_path.write_text("テスト", encoding='utf-8')
        assert repository._detect_encoding() == 'utf-8'

    def test_parse_date_invalid_format(self, repository):
        """異常系: 不正な日付形式の場合"""
        with pytest.raises(ValueError) as excinfo:
            repository._parse_date("2023-01-01")  # Splitting by slash will fail
        assert "日付形式が不正です" in str(excinfo.value)

    def test_parse_date_invalid_values(self, repository):
        """異常系: 存在しない日付の場合"""
        with pytest.raises(ValueError) as excinfo:
            repository._parse_date("2023/2/30")  # invalid date
        assert "日付の解析に失敗しました" in str(excinfo.value)
