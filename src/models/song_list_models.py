"""
曲リスト自動生成システムのデータモデル

このモジュールは、V_SONG_LIST.TSV自動生成システムで使用される
すべてのデータモデルを定義します。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple


@dataclass
class LiveInfo:
    """
    YouTube配信の基本情報を表すデータモデル
    
    M_YT_LIVE.TSVから読み込まれる配信情報を格納します。
    
    Attributes:
        id: 配信の一意識別子
        date: 配信日時
        title: 配信のタイトル
        url: 配信のYouTube URL
    """
    id: int
    date: datetime
    title: str
    url: str


@dataclass
class TimestampInfo:
    """
    配信内の曲のタイムスタンプ情報を表すデータモデル
    
    M_YT_LIVE_TIMESTAMP.TSVから読み込まれるタイムスタンプ情報を格納します。
    
    Attributes:
        id: タイムスタンプレコードの一意識別子
        live_id: 対応する配信のID（LiveInfo.idへの参照）
        timestamp: 曲が開始される時刻（"HH:MM:SS"または"MM:SS"形式）
        song_name: 曲名
        artist: アーティスト名
    """
    id: int
    live_id: int
    timestamp: str
    song_name: str
    artist: str



@dataclass
class SongInfo:
    """
    曲の最新歌唱情報を表すデータモデル
    
    V_SONG_LIST.TSVに出力される曲情報を格納します。
    
    Attributes:
        artist: アーティスト名
        artist_sort: ソート用アーティスト名（ひらがな読み仮名）
        song_name: 曲名
        latest_url: 最新歌唱のタイムスタンプ付きYouTube URL
    """
    artist: str
    artist_sort: str
    song_name: str
    latest_url: str


@dataclass
class SimilarityWarning:
    """
    類似性チェックで検出された警告情報を表すデータモデル
    
    アーティスト名や曲名の類似性が高いペアを警告として記録します。
    
    Attributes:
        type: 警告の種類（'artist'または'song'）
        item1: 比較対象の1つ目の文字列
        item2: 比較対象の2つ目の文字列
        similarity: 類似度（0.0〜1.0の範囲）
    """
    type: str
    item1: str
    item2: str
    similarity: float


@dataclass
class DiffResult:
    """
    既存ファイルとの差分結果を表すデータモデル
    
    新旧V_SONG_LIST.TSVの比較結果を格納します。
    
    Attributes:
        added: 新規に追加された曲のリスト
        removed: 削除された曲のリスト
        updated: 更新された曲のリスト（(旧データ, 新データ)のタプル）
    """
    added: List[SongInfo]
    removed: List[SongInfo]
    updated: List[Tuple[SongInfo, SongInfo]]
