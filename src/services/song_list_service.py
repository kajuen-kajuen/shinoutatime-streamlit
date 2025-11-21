"""
曲リスト生成サービスモジュール

配信情報とタイムスタンプ情報を結合し、曲リストを生成します。
"""

import logging
import re
from typing import List, Dict, Tuple
from datetime import datetime

from src.models.song_list_models import (
    LiveInfo, TimestampInfo, SongInfo, SimilarityWarning, DiffResult
)
from src.repositories.live_repository import LiveRepository
from src.repositories.timestamp_repository import TimestampRepository
from src.repositories.song_list_repository import SongListRepository
from src.utils.artist_sort_generator import ArtistSortGenerator
from src.utils.url_generator import URLGenerator
from src.utils.similarity_checker import SimilarityChecker

logger = logging.getLogger(__name__)


class SongListService:
    """
    曲リスト生成サービス
    
    配信情報とタイムスタンプ情報を結合し、曲ごとの最新歌唱情報を生成します。
    """
    
    def __init__(
        self, 
        live_repo: LiveRepository, 
        timestamp_repo: TimestampRepository
    ):
        """
        サービスを初期化
        
        Args:
            live_repo: 配信情報リポジトリ
            timestamp_repo: タイムスタンプ情報リポジトリ
        """
        self.live_repo = live_repo
        self.timestamp_repo = timestamp_repo
        self.artist_sort_generator = ArtistSortGenerator()
        self.url_generator = URLGenerator()
        self.similarity_checker = SimilarityChecker()
        self.logger = logging.getLogger(__name__)
    
    def generate_song_list(self) -> List[SongInfo]:
        """
        曲リストを生成
        
        配信情報とタイムスタンプ情報を結合し、曲ごとの最新歌唱情報を生成します。
        
        Returns:
            曲情報のリスト
        """
        # データを読み込む
        self.logger.info("配信情報を読み込んでいます...")
        live_infos = self.live_repo.load_all()
        
        self.logger.info("タイムスタンプ情報を読み込んでいます...")
        timestamp_infos = self.timestamp_repo.load_all()
        
        # 配信情報をIDでマッピング
        live_map: Dict[int, LiveInfo] = {live.id: live for live in live_infos}
        
        # データを結合
        self.logger.info("データを結合しています...")
        combined_data = self._join_data(timestamp_infos, live_map)
        
        # 空データをフィルタリング
        self.logger.info("空データをフィルタリングしています...")
        filtered_data = self._filter_empty_data(combined_data)
        
        self.logger.info(f"結合されたレコード数: {len(filtered_data)}")
        
        # 曲名を正規化して最新歌唱を選択
        self.logger.info("曲名を正規化して最新歌唱を選択しています...")
        song_list = self._select_latest_songs_with_normalization(filtered_data)
        
        self.logger.info(f"生成された曲数: {len(song_list)}")
        
        # ソート処理
        self.logger.info("曲リストをソートしています...")
        sorted_song_list = self._sort_songs(song_list)
        
        return sorted_song_list
    
    def _join_data(
        self, 
        timestamp_infos: List[TimestampInfo], 
        live_map: Dict[int, LiveInfo]
    ) -> List[Tuple[TimestampInfo, LiveInfo]]:
        """
        タイムスタンプ情報と配信情報を結合
        
        Args:
            timestamp_infos: タイムスタンプ情報のリスト
            live_map: 配信IDをキーとした配信情報のマップ
            
        Returns:
            (TimestampInfo, LiveInfo)のタプルのリスト
        """
        combined = []
        skipped_count = 0
        
        for ts_info in timestamp_infos:
            # 対応する配信情報を取得
            live_info = live_map.get(ts_info.live_id)
            
            if live_info is None:
                # 対応する配信情報が存在しない場合は警告を出力してスキップ
                self.logger.warning(
                    f"タイムスタンプID {ts_info.id} に対応する配信情報が見つかりません "
                    f"(LIVE_ID: {ts_info.live_id})"
                )
                skipped_count += 1
                continue
            
            combined.append((ts_info, live_info))
        
        if skipped_count > 0:
            self.logger.warning(f"スキップされたレコード数: {skipped_count}")
        
        return combined
    
    def _filter_empty_data(
        self, 
        combined_data: List[Tuple[TimestampInfo, LiveInfo]]
    ) -> List[Tuple[TimestampInfo, LiveInfo]]:
        """
        空データをフィルタリング
        
        曲名またはアーティスト名が空白のレコードを除外します。
        
        Args:
            combined_data: 結合されたデータのリスト
            
        Returns:
            フィルタリングされたデータのリスト
        """
        filtered = []
        skipped_count = 0
        
        for ts_info, live_info in combined_data:
            # 曲名またはアーティスト名が空白の場合はスキップ
            if not ts_info.song_name or not ts_info.artist:
                self.logger.warning(
                    f"タイムスタンプID {ts_info.id} の曲名またはアーティスト名が空白です "
                    f"(曲名: '{ts_info.song_name}', アーティスト: '{ts_info.artist}')"
                )
                skipped_count += 1
                continue
            
            filtered.append((ts_info, live_info))
        
        if skipped_count > 0:
            self.logger.warning(f"空データでスキップされたレコード数: {skipped_count}")
        
        return filtered
    
    def _select_latest_songs(
        self, 
        combined_data: List[Tuple[TimestampInfo, LiveInfo]]
    ) -> List[SongInfo]:
        """
        同じ曲の複数レコードから最新を選択
        
        アーティストと曲名の組み合わせごとに、配信日が最も新しいレコードを選択します。
        配信日が同じ場合は、配信IDが大きい方を選択します。
        
        Args:
            combined_data: 結合されたデータのリスト
            
        Returns:
            曲情報のリスト
        """
        # (アーティスト, 曲名) をキーとして、最新のレコードを保持
        song_map: Dict[Tuple[str, str], Tuple[TimestampInfo, LiveInfo]] = {}
        
        for ts_info, live_info in combined_data:
            key = (ts_info.artist, ts_info.song_name)
            
            # 既存のレコードがない場合は追加
            if key not in song_map:
                song_map[key] = (ts_info, live_info)
                continue
            
            # 既存のレコードと比較
            existing_ts, existing_live = song_map[key]
            
            # 配信日で比較
            if live_info.date > existing_live.date:
                # 新しい配信日の場合は置き換え
                song_map[key] = (ts_info, live_info)
            elif live_info.date == existing_live.date:
                # 配信日が同じ場合は配信IDで比較
                if live_info.id > existing_live.id:
                    song_map[key] = (ts_info, live_info)
        
        # SongInfoオブジェクトに変換
        song_list = []
        for (artist, song_name), (ts_info, live_info) in song_map.items():
            # ソート用アーティスト名を生成
            artist_sort = self.artist_sort_generator.generate(artist)
            
            # タイムスタンプ付きURLを生成
            latest_url = self.url_generator.generate_timestamped_url(
                live_info.url, 
                ts_info.timestamp
            )
            
            song_info = SongInfo(
                artist=artist,
                artist_sort=artist_sort,
                song_name=song_name,
                latest_url=latest_url
            )
            song_list.append(song_info)
        
        return song_list
    
    def normalize_song_name(self, song_name: str) -> Tuple[str, bool]:
        """
        曲名を正規化（バリエーション表記を除去）
        
        (1chorus)、(short ver)、(1phrase)などのバリエーション表記を検出し、
        正規化された曲名とバリエーション表記の有無を返します。
        
        Args:
            song_name: 元の曲名
            
        Returns:
            (正規化された曲名, バリエーション表記があったか)のタプル
            
        Examples:
            >>> service.normalize_song_name("夜に駆ける")
            ('夜に駆ける', False)
            >>> service.normalize_song_name("夜に駆ける(1chorus)")
            ('夜に駆ける', True)
            >>> service.normalize_song_name("夜に駆ける (short ver)")
            ('夜に駆ける', True)
        """
        # バリエーション表記のパターン
        # (1chorus), (short ver), (1phrase), (TV size), (full ver) など
        pattern = r'\s*\([^)]*(?:chorus|ver|phrase|size|edit|mix|version)[^)]*\)\s*'
        
        # パターンにマッチするか確認
        has_variation = bool(re.search(pattern, song_name, re.IGNORECASE))
        
        # バリエーション表記を除去
        normalized = re.sub(pattern, '', song_name, flags=re.IGNORECASE).strip()
        
        return normalized, has_variation
    
    def _select_latest_songs_with_normalization(
        self, 
        combined_data: List[Tuple[TimestampInfo, LiveInfo]]
    ) -> List[SongInfo]:
        """
        曲名を正規化して同じ曲の複数レコードから最新を選択
        
        バリエーション表記を考慮して、正規版を優先的に選択します。
        
        Args:
            combined_data: 結合されたデータのリスト
            
        Returns:
            曲情報のリスト
        """
        # (アーティスト, 正規化された曲名) をキーとして、レコードをグループ化
        song_groups: Dict[Tuple[str, str], List[Tuple[TimestampInfo, LiveInfo, str, bool]]] = {}
        
        for ts_info, live_info in combined_data:
            # 曲名を正規化
            normalized_name, has_variation = self.normalize_song_name(ts_info.song_name)
            
            key = (ts_info.artist, normalized_name)
            
            if key not in song_groups:
                song_groups[key] = []
            
            song_groups[key].append((ts_info, live_info, ts_info.song_name, has_variation))
        
        # 各グループから最適なレコードを選択
        song_list = []
        for (artist, normalized_name), records in song_groups.items():
            # 正規版（バリエーション表記なし）を優先
            regular_records = [(ts, live, name, var) for ts, live, name, var in records if not var]
            variation_records = [(ts, live, name, var) for ts, live, name, var in records if var]
            
            selected_record = None
            
            if regular_records:
                # 正規版がある場合は、その中から最新を選択
                selected_record = self._select_latest_from_records(regular_records)
            elif variation_records:
                # 正規版がない場合は、バリエーション版の中から最新を選択
                selected_record = self._select_latest_from_records(variation_records)
            
            if selected_record:
                ts_info, live_info, original_name, _ = selected_record
                
                # ソート用アーティスト名を生成
                artist_sort = self.artist_sort_generator.generate(artist)
                
                # タイムスタンプ付きURLを生成
                latest_url = self.url_generator.generate_timestamped_url(
                    live_info.url, 
                    ts_info.timestamp
                )
                
                song_info = SongInfo(
                    artist=artist,
                    artist_sort=artist_sort,
                    song_name=original_name,  # 元の曲名を使用
                    latest_url=latest_url
                )
                song_list.append(song_info)
        
        return song_list
    
    def _select_latest_from_records(
        self, 
        records: List[Tuple[TimestampInfo, LiveInfo, str, bool]]
    ) -> Tuple[TimestampInfo, LiveInfo, str, bool]:
        """
        レコードリストから最新のものを選択
        
        配信日が最も新しいレコードを選択します。
        配信日が同じ場合は、配信IDが大きい方を選択します。
        
        Args:
            records: レコードのリスト
            
        Returns:
            最新のレコード
        """
        if not records:
            return None
        
        # 配信日の降順、配信IDの降順でソート
        sorted_records = sorted(
            records,
            key=lambda x: (x[1].date, x[1].id),
            reverse=True
        )
        
        return sorted_records[0]
    
    def _sort_songs(self, songs: List[SongInfo]) -> List[SongInfo]:
        """
        曲リストをソート
        
        ソート用アーティスト名の昇順、曲名の昇順でソートします。
        
        Args:
            songs: 曲情報のリスト
            
        Returns:
            ソートされた曲情報のリスト
        """
        # ソート用アーティスト名の昇順、曲名の昇順でソート
        sorted_songs = sorted(
            songs,
            key=lambda song: (song.artist_sort, song.song_name)
        )
        
        self.logger.info(f"曲リストをソートしました: {len(sorted_songs)}件")
        
        return sorted_songs
    
    def check_similarity(
        self, 
        songs: List[SongInfo], 
        threshold: float = 0.85
    ) -> List[SimilarityWarning]:
        """
        類似性チェックを実行
        
        アーティスト名と曲名の類似性をチェックし、閾値以上の類似度を持つ
        ペアを警告として返します。
        
        Args:
            songs: 曲情報のリスト
            threshold: 類似度の閾値（0.0-1.0、デフォルト: 0.85）
            
        Returns:
            類似性警告のリスト
        """
        warnings = []
        
        # アーティスト名の類似性チェック
        self.logger.info("アーティスト名の類似性をチェックしています...")
        artist_warnings = self._check_artist_similarity(songs, threshold)
        warnings.extend(artist_warnings)
        
        # 曲名の類似性チェック（同じアーティスト内で）
        self.logger.info("曲名の類似性をチェックしています...")
        song_warnings = self._check_song_similarity(songs, threshold)
        warnings.extend(song_warnings)
        
        if warnings:
            self.logger.warning(f"類似性警告が {len(warnings)} 件検出されました")
        else:
            self.logger.info("類似性警告は検出されませんでした")
        
        return warnings
    
    def _check_artist_similarity(
        self, 
        songs: List[SongInfo], 
        threshold: float
    ) -> List[SimilarityWarning]:
        """
        アーティスト名の類似性をチェック
        
        Args:
            songs: 曲情報のリスト
            threshold: 類似度の閾値
            
        Returns:
            アーティスト名の類似性警告のリスト
        """
        # ユニークなアーティスト名を取得
        artists = list(set(song.artist for song in songs))
        
        # 類似ペアを検出
        similar_pairs = self.similarity_checker.find_similar_pairs(artists, threshold)
        
        # SimilarityWarningオブジェクトに変換
        warnings = []
        for artist1, artist2, similarity in similar_pairs:
            warning = SimilarityWarning(
                type='artist',
                item1=artist1,
                item2=artist2,
                similarity=similarity
            )
            warnings.append(warning)
            self.logger.warning(
                f"類似したアーティスト名が検出されました: "
                f"'{artist1}' と '{artist2}' (類似度: {similarity:.2f})"
            )
        
        return warnings
    
    def _check_song_similarity(
        self, 
        songs: List[SongInfo], 
        threshold: float
    ) -> List[SimilarityWarning]:
        """
        曲名の類似性をチェック（同じアーティスト内で）
        
        Args:
            songs: 曲情報のリスト
            threshold: 類似度の閾値
            
        Returns:
            曲名の類似性警告のリスト
        """
        warnings = []
        
        # アーティストごとに曲名をグループ化
        artist_songs: Dict[str, List[str]] = {}
        for song in songs:
            if song.artist not in artist_songs:
                artist_songs[song.artist] = []
            artist_songs[song.artist].append(song.song_name)
        
        # 各アーティストの曲名について類似性をチェック
        for artist, song_names in artist_songs.items():
            # 同じアーティストで曲が2曲以上ある場合のみチェック
            if len(song_names) < 2:
                continue
            
            # 類似ペアを検出
            similar_pairs = self.similarity_checker.find_similar_pairs(song_names, threshold)
            
            # SimilarityWarningオブジェクトに変換
            for song1, song2, similarity in similar_pairs:
                warning = SimilarityWarning(
                    type='song',
                    item1=f"{artist} - {song1}",
                    item2=f"{artist} - {song2}",
                    similarity=similarity
                )
                warnings.append(warning)
                self.logger.warning(
                    f"類似した曲名が検出されました（{artist}）: "
                    f"'{song1}' と '{song2}' (類似度: {similarity:.2f})"
                )
        
        return warnings
    
    def compare_with_existing(
        self, 
        new_songs: List[SongInfo], 
        existing_file: str
    ) -> DiffResult:
        """
        既存ファイルとの差分を検出
        
        新しい曲リストと既存のV_SONG_LIST.TSVを比較し、
        追加・削除・更新された曲を検出します。
        
        Args:
            new_songs: 新しい曲情報のリスト
            existing_file: 既存のV_SONG_LIST.TSVファイルのパス
            
        Returns:
            差分結果
        """
        # 既存ファイルを読み込む
        song_list_repo = SongListRepository(existing_file)
        try:
            existing_songs = song_list_repo.load_all()
            self.logger.info(f"既存ファイルを読み込みました: {len(existing_songs)}件")
        except Exception as e:
            # ファイルが存在しない場合は空リストとして扱う
            self.logger.info(f"既存ファイルが読み込めませんでした（新規作成）: {e}")
            existing_songs = []
        
        # (アーティスト, 曲名) をキーとしてマッピング
        existing_map: Dict[Tuple[str, str], SongInfo] = {
            (song.artist, song.song_name): song 
            for song in existing_songs
        }
        new_map: Dict[Tuple[str, str], SongInfo] = {
            (song.artist, song.song_name): song 
            for song in new_songs
        }
        
        # 追加された曲を検出
        added = []
        for key, song in new_map.items():
            if key not in existing_map:
                added.append(song)
                self.logger.info(f"追加: {song.artist} - {song.song_name}")
        
        # 削除された曲を検出
        removed = []
        for key, song in existing_map.items():
            if key not in new_map:
                removed.append(song)
                self.logger.info(f"削除: {song.artist} - {song.song_name}")
        
        # 更新された曲を検出（URLが変更された場合）
        updated = []
        for key in set(existing_map.keys()) & set(new_map.keys()):
            old_song = existing_map[key]
            new_song = new_map[key]
            
            # URLまたはソート用アーティスト名が変更された場合
            if (old_song.latest_url != new_song.latest_url or 
                old_song.artist_sort != new_song.artist_sort):
                updated.append((old_song, new_song))
                self.logger.info(
                    f"更新: {new_song.artist} - {new_song.song_name} "
                    f"(URL: {old_song.latest_url} -> {new_song.latest_url})"
                )
        
        # 差分結果を作成
        diff_result = DiffResult(
            added=added,
            removed=removed,
            updated=updated
        )
        
        # サマリーをログ出力
        self.logger.info(
            f"差分検出完了: 追加 {len(added)}件, 削除 {len(removed)}件, 更新 {len(updated)}件"
        )
        
        return diff_result
