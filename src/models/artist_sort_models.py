"""アーティスト名ソート修正マッピングのデータモデル"""

from dataclasses import dataclass


@dataclass
class ArtistSortMapping:
    """アーティスト名ソート修正マッピング
    
    Attributes:
        artist: アーティスト名
        sort_name: ソート名
    """
    artist: str
    sort_name: str
