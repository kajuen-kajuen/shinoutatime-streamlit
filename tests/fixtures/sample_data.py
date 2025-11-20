"""
テスト用のサンプルTSVデータ

データサービスとパイプラインのテストで使用するサンプルデータを定義します。
"""

import tempfile
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd


# サンプル配信データ
SAMPLE_LIVES_DATA = {
    "ID": [1, 2, 3],
    "配信日": ["2024/01/01", "2024/01/15", "2024/02/01"],
    "タイトル": ["新年最初の配信", "歌枠配信", "雑談配信"],
    "URL": [
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=def456",
        "https://youtube.com/watch?v=ghi789"
    ]
}

# サンプル楽曲データ（タイムスタンプ付き）
SAMPLE_SONGS_DATA = {
    "ID": [1, 2, 3, 4, 5],
    "LIVE_ID": [1, 1, 2, 2, 2],
    "曲名": ["曲A", "曲B", "曲C", "曲D", "曲E"],
    "タイムスタンプ": ["00:10", "05:30", "02:15", "10:45", "20:00"]
}

# サンプル楽曲リストデータ
SAMPLE_SONG_LIST_DATA = {
    "ID": [1, 2, 3, 4, 5],
    "曲名": ["曲A", "曲B", "曲C", "曲D", "曲E"],
    "アーティスト": ["アーティスト1", "アーティスト2", "アーティスト1", "アーティスト3", "アーティスト2"],
    "ジャンル": ["ポップ", "ロック", "ポップ", "バラード", "ロック"]
}

# 空のデータ
EMPTY_DATA = {
    "ID": [],
    "配信日": [],
    "タイトル": [],
    "URL": []
}

# 欠損値を含むデータ
DATA_WITH_MISSING_VALUES = {
    "ID": [1, 2, 3],
    "配信日": ["2024/01/01", None, "2024/02/01"],
    "タイトル": ["配信1", "配信2", None],
    "URL": [
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=def456",
        None
    ]
}

# 大量のデータ（パフォーマンステスト用）
def create_large_dataset(num_rows: int = 1000) -> Dict[str, List[Any]]:
    """
    大量のテストデータを生成する
    
    Args:
        num_rows: 生成する行数
        
    Returns:
        大量のサンプルデータ
    """
    return {
        "ID": list(range(1, num_rows + 1)),
        "配信日": [f"2024/{(i % 12) + 1:02d}/{(i % 28) + 1:02d}" for i in range(num_rows)],
        "タイトル": [f"配信{i}" for i in range(1, num_rows + 1)],
        "URL": [f"https://youtube.com/watch?v=test{i:06d}" for i in range(1, num_rows + 1)]
    }


def create_sample_tsv_file(
    data: Dict[str, List[Any]],
    file_path: str = None,
    use_temp: bool = True
) -> str:
    """
    サンプルデータからTSVファイルを作成する
    
    Args:
        data: TSVファイルに書き込むデータ（辞書形式）
        file_path: ファイルパス（Noneの場合は一時ファイルを作成）
        use_temp: Trueの場合は一時ディレクトリを使用
        
    Returns:
        作成されたTSVファイルのパス
    """
    df = pd.DataFrame(data)
    
    if file_path is None:
        if use_temp:
            # 一時ファイルを作成
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.tsv',
                delete=False,
                encoding='utf-8'
            )
            file_path = temp_file.name
            temp_file.close()
        else:
            raise ValueError("file_pathまたはuse_temp=Trueを指定してください")
    
    # TSVファイルとして保存
    df.to_csv(file_path, sep='\t', index=False, encoding='utf-8')
    
    return file_path


def create_sample_dataframe(data: Dict[str, List[Any]]) -> pd.DataFrame:
    """
    サンプルデータからDataFrameを作成する
    
    Args:
        data: DataFrameに変換するデータ（辞書形式）
        
    Returns:
        作成されたDataFrame
    """
    return pd.DataFrame(data)


# 特殊なケース用のデータ

# 重複IDを含むデータ
DATA_WITH_DUPLICATE_IDS = {
    "ID": [1, 1, 2, 3],
    "配信日": ["2024/01/01", "2024/01/01", "2024/01/15", "2024/02/01"],
    "タイトル": ["配信1", "配信1（重複）", "配信2", "配信3"],
    "URL": [
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=def456",
        "https://youtube.com/watch?v=ghi789"
    ]
}

# 不正な日付形式を含むデータ
DATA_WITH_INVALID_DATES = {
    "ID": [1, 2, 3],
    "配信日": ["2024/01/01", "invalid-date", "2024/02/01"],
    "タイトル": ["配信1", "配信2", "配信3"],
    "URL": [
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=def456",
        "https://youtube.com/watch?v=ghi789"
    ]
}

# 特殊文字を含むデータ
DATA_WITH_SPECIAL_CHARS = {
    "ID": [1, 2, 3],
    "配信日": ["2024/01/01", "2024/01/15", "2024/02/01"],
    "タイトル": [
        "配信1 <特殊文字>",
        "配信2 \"引用符\"",
        "配信3 'シングルクォート'"
    ],
    "URL": [
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=def456",
        "https://youtube.com/watch?v=ghi789"
    ]
}

# Unicode文字を含むデータ
DATA_WITH_UNICODE = {
    "ID": [1, 2, 3],
    "配信日": ["2024/01/01", "2024/01/15", "2024/02/01"],
    "タイトル": [
        "配信1 🎉",
        "配信2 ✨",
        "配信3 🎊"
    ],
    "URL": [
        "https://youtube.com/watch?v=abc123",
        "https://youtube.com/watch?v=def456",
        "https://youtube.com/watch?v=ghi789"
    ]
}
