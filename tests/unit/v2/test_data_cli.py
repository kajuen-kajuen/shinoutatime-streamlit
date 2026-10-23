"""data の CLI(書き込みのサブコマンド)のテスト。架空のデータを tmp_path に置いて動かす"""

import pytest

from src.cli.data import main
from src.core.validation import validate_dataset
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
        assert _run(tmp_path, "add-artist", "Gamma") == 0

        assert _run(tmp_path, "drop-artist", "a0003") == 0

        assert "a0003(Beta)を消しました" in capsys.readouterr().out
        artists = TableRepository(str(tmp_path)).load()["artists"]
        assert list(artists["artist_id"]) == ["a0001", "a0002", "a0004"]

    def test_drop_largest_artist_fails_without_saving(self, tmp_path, sample_dataset, capsys):
        """いちばん大きい ID は消せない(次に足すと同じ ID が使われるため)"""
        TableRepository(str(tmp_path)).save(sample_dataset)
        assert _run(tmp_path, "add-artist", "Beta") == 0
        before = (tmp_path / "artists.tsv").read_bytes()

        assert _run(tmp_path, "drop-artist", "a0003") == 1

        assert "a0003 はいちばん大きい ID" in capsys.readouterr().err
        assert (tmp_path / "artists.tsv").read_bytes() == before

    def test_merge_song_largest_id_fails_without_saving(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)
        before = (tmp_path / "songs.tsv").read_bytes()

        assert _run(tmp_path, "merge-song", "s0001", "s0002") == 1

        assert "s0002 はいちばん大きい ID" in capsys.readouterr().err
        assert (tmp_path / "songs.tsv").read_bytes() == before

    def test_drop_used_artist_fails_without_saving(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)
        before = (tmp_path / "artists.tsv").read_bytes()

        assert _run(tmp_path, "drop-artist", "a0002") == 1

        assert "s0002" in capsys.readouterr().err
        assert (tmp_path / "artists.tsv").read_bytes() == before


def _snapshot(tmp_path) -> dict:
    """5つの TSV の中身(保存しなかったことを確かめる)"""
    return {p.name: p.read_bytes() for p in sorted(tmp_path.glob("*.tsv"))}


class TestSetCommand:
    def test_set_saves_value(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)

        assert _run(tmp_path, "set", "performances", "yt:AAAAAAAAAAA,20", "part", "1chorus") == 0

        assert "performances yt:AAAAAAAAAAA,20 の part: 「」→「1chorus」" in capsys.readouterr().out
        perf = TableRepository(str(tmp_path)).load()["performances"].set_index(["content_id", "seq"])
        assert perf.loc[("yt:AAAAAAAAAAA", "20"), "part"] == "1chorus"

    @pytest.mark.parametrize("argv, message", [
        (("songs", "s0001", "kind", "不正"), "kind は"),
        (("performances", "yt:AAAAAAAAAAA,10", "song_id", "s9999"), "参照先"),
        (("contents", "yt:AAAAAAAAAAA", "url", "javascript:alert(1)"), "url の形"),
    ])
    def test_invalid_value_is_not_saved(self, tmp_path, sample_dataset, capsys, argv, message):
        """set は値そのものを確かめないので、保存の前の検査で止まること"""
        TableRepository(str(tmp_path)).save(sample_dataset)
        before = _snapshot(tmp_path)

        assert _run(tmp_path, "set", *argv) == 1

        out = capsys.readouterr().out
        assert message in out and "保存しませんでした" in out
        assert _snapshot(tmp_path) == before


class TestMergeCommands:
    def test_merge_song_moves_performances_and_aliases(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)
        sample = TableRepository(str(tmp_path)).load()
        sample["songs"].loc[len(sample["songs"])] = {c: "" for c in sample["songs"].columns} | {
            "song_id": "s0003", "title": "はじまりの歌", "artist_id": "a0001", "kind": "カバー"}
        TableRepository(str(tmp_path)).save(sample)

        assert _run(tmp_path, "merge-song", "s0002", "s0001") == 0

        assert "s0001 を s0002 にまとめました(歌唱 4 件を付け替え)" in capsys.readouterr().out
        dataset = TableRepository(str(tmp_path)).load()
        assert "s0001" not in set(dataset["songs"]["song_id"])
        assert "s0001" not in set(dataset["performances"]["song_id"])
        assert set(dataset["aliases"]["song_id"]) == {"s0002"}
        assert not [i for i in validate_dataset(dataset) if i.level == "error"]

    def test_merge_artist_moves_songs(self, tmp_path, sample_dataset, capsys):
        TableRepository(str(tmp_path)).save(sample_dataset)
        assert _run(tmp_path, "add-artist", "Beta") == 0

        assert _run(tmp_path, "merge-artist", "a0003", "a0001") == 0

        assert "a0001 を a0003 にまとめました(曲 1 件を付け替え)" in capsys.readouterr().out
        dataset = TableRepository(str(tmp_path)).load()
        assert list(dataset["artists"]["artist_id"]) == ["a0002", "a0003"]
        assert dataset["songs"].set_index("song_id").loc["s0001", "artist_id"] == "a0003"
        assert not [i for i in validate_dataset(dataset) if i.level == "error"]

    @pytest.mark.parametrize("keep, drop, message", [
        ("a0001", "a0002", "a0002 はいちばん大きい ID"),
        ("a0001", "a0001", "同じアーティストは指定できません"),
    ])
    def test_merge_artist_refusal_is_not_saved(self, tmp_path, sample_dataset, capsys, keep, drop, message):
        TableRepository(str(tmp_path)).save(sample_dataset)
        before = _snapshot(tmp_path)

        assert _run(tmp_path, "merge-artist", keep, drop) == 1

        assert message in capsys.readouterr().err
        assert _snapshot(tmp_path) == before


class TestNormalizeAndValidate:
    def test_normalize_sorts_rows(self, tmp_path, sample_dataset, capsys):
        repo = TableRepository(str(tmp_path))
        repo.save(sample_dataset)
        lines = (tmp_path / "artists.tsv").read_text(encoding="utf-8").splitlines()
        (tmp_path / "artists.tsv").write_text("\n".join([lines[0], *reversed(lines[1:])]) + "\n", encoding="utf-8")

        assert _run(tmp_path, "normalize") == 0

        assert list(repo.load()["artists"]["artist_id"]) == ["a0001", "a0002"]
        assert _run(tmp_path, "validate") == 0
        assert "問題はありません" in capsys.readouterr().out

    def test_validate_returns_1_on_error(self, tmp_path, sample_dataset, capsys):
        sample_dataset["contents"].loc[0, "date"] = "2025/5/1"
        TableRepository(str(tmp_path)).save(sample_dataset)

        assert _run(tmp_path, "validate") == 1

        assert "date の形が正しくありません" in capsys.readouterr().out
