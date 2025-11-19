# 手動テスト

このディレクトリには、手動で実行するテストスクリプトが含まれています。

## 概要

手動テストは、自動テスト（pytest）とは異なり、対話的に実行結果を確認できるテストスクリプトです。開発中のデバッグや、特定の機能の動作確認に使用します。

## テストファイル

### test_data_service_manual.py

DataServiceクラスの基本動作を確認する手動テストです。

**実行方法:**
```bash
# Docker環境
docker-compose exec shinouta-time python tests/manual/test_data_service_manual.py

# ローカル環境
python tests/manual/test_data_service_manual.py
```

**検証内容:**
- 配信データの読み込み
- 楽曲データの読み込み
- 楽曲リストデータの読み込み
- データの結合

### test_data_pipeline_manual.py

DataPipelineクラスの動作を確認する手動テストです。

**実行方法:**
```bash
# Docker環境
docker-compose exec shinouta-time python tests/manual/test_data_pipeline_manual.py

# ローカル環境
python tests/manual/test_data_pipeline_manual.py
```

**検証内容:**
- パイプラインの実行
- 必須カラムの存在確認
- データサンプルの表示
- キャッシュ機能の動作確認

## 使用場面

手動テストは以下の場合に使用します：

1. **開発中のデバッグ**: 新機能の実装中に動作を確認したい場合
2. **データの確認**: 実際のデータがどのように処理されるか確認したい場合
3. **パフォーマンス確認**: 処理時間やメモリ使用量を確認したい場合
4. **対話的な確認**: 実行結果を目視で確認したい場合

## 自動テストとの違い

| 項目 | 自動テスト (pytest) | 手動テスト |
|------|-------------------|-----------|
| 実行方法 | `pytest tests/` | `python tests/manual/xxx.py` |
| 結果確認 | 自動（PASS/FAIL） | 手動（目視確認） |
| 用途 | CI/CD、リグレッション防止 | デバッグ、開発中の確認 |
| 出力 | 簡潔 | 詳細（データサンプル含む） |

## 注意事項

- 手動テストは自動テストの代わりにはなりません
- 本番環境では実行しないでください
- 実際のデータファイルが必要です（data/ディレクトリ）
