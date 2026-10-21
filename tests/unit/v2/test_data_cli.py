"""data の CLI(書き込みのサブコマンド)のテスト。架空のデータを tmp_path に置いて動かす"""

from src.cli.data import main
from src.repositories.table_repository import TableRepository


def _run(tmp_path, *argv) -> int:
    return main(["--dir", str(tmp_path), *argv])


class TestArtistCommands:
    def test_add_artist_saves_row(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)

        assert _run(tmp_path, "add-artist", "新しいバンド", "--sort-name", "あたらしいばんど") == 0

        assert "a0003 を足しました: 新しいバンド(あたらしいばんど)" in capsys.readouterr().out
        artists = TableRepository(str(tmp_path)).load()["artists"].set_index("artist_id")
        assert artists.loc["a0003", "name"] == "新しいバンド"

    def test_add_existing_artist_fails_without_saving(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)
        before = (tmp_path / "artists.tsv").read_bytes()

        assert _run(tmp_path, "add-artist", "テストバンド") == 1

        assert "a0001" in capsys.readouterr().err
        assert (tmp_path / "artists.tsv").read_bytes() == before

    def test_drop_unused_artist(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)
        assert _run(tmp_path, "add-artist", "Beta") == 0

        assert _run(tmp_path, "drop-artist", "a0003") == 0

        assert "a0003(Beta)を消しました" in capsys.readouterr().out
        artists = TableRepository(str(tmp_path)).load()["artists"]
        assert list(artists["artist_id"]) == ["a0001", "a0002"]

    def test_drop_used_artist_fails_without_saving(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)
        before = (tmp_path / "artists.tsv").read_bytes()

        assert _run(tmp_path, "drop-artist", "a0002") == 1

        assert "s0002" in capsys.readouterr().err
        assert (tmp_path / "artists.tsv").read_bytes() == before
