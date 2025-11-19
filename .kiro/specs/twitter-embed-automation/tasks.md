# 実装タスクリスト

## 概要

本ドキュメントは、Twitter埋め込みコード自動取得システムの実装タスクを定義します。各タスクは段階的に実装され、テストを含みます。

## タスク

- [x] 1. プロジェクト構造とコア設定のセットアップ
  - 必要なディレクトリ構造を作成
  - 依存パッケージを`requirements.txt`に追加（requests、python-dotenvなど）
  - 環境変数設定用の`.env.example`ファイルを作成
  - _要件: 5.3_

- [x] 2. データモデルの実装
  - `src/models/embed_result.py`を作成し、`EmbedCodeResult`と`MultipleEmbedCodeResult`データクラスを実装
  - `src/models/oembed_response.py`を作成し、`OEmbedResponse`と`RateLimitInfo`データクラスを実装
  - _要件: 1.2, 1.3_

- [ ]* 2.1 データモデルのユニットテストを作成
  - `tests/unit/test_models.py`を作成
  - データクラスのインスタンス化と属性アクセスをテスト
  - _要件: 1.2, 1.3_

- [x] 3. URL検証とツイートID抽出の実装
  - `src/utils/validators.py`を作成
  - ツイートURL検証関数を実装（正規表現パターンマッチング）
  - ツイートID抽出関数を実装（twitter.com、x.com、モバイル版をサポート）
  - _要件: 1.1, 1.5_

- [x] 3.0 URL検証のユニットテストを作成
  - `tests/unit/test_validators.py`を作成
  - URL検証とツイートID抽出の各種ケースをテスト
  - _要件: 1.1, 1.5_

- [ ]* 3.1 URL検証のプロパティテストを作成
  - **プロパティ1: ツイートID抽出の一貫性**
  - **検証要件: 1.1**
  - `tests/property/test_url_parsing_properties.py`を作成
  - Hypothesisを使用して様々なURL形式をテスト
  - 有効なツイートURLからツイートIDが正しく抽出されることを検証
  - _要件: 1.1_

- [ ]* 3.2 無効URL拒否のプロパティテストを作成
  - **プロパティ4: 無効URL拒否の完全性**
  - **検証要件: 1.5**
  - `tests/property/test_url_parsing_properties.py`に追加
  - 無効なURLが全て拒否されることをテスト
  - _要件: 1.5_

- [x] 4. カスタム例外クラスの実装





  - `src/exceptions/errors.py`にTwitter埋め込み機能用の例外クラスを追加
  - InvalidURLError、NetworkError、APITimeoutError、RateLimitError、FileWriteErrorなどを定義
  - 各例外クラスに適切なエラーメッセージを設定
  - _要件: 1.4, 10.1, 10.2, 10.3_

- [x] 5. リトライロジックの実装
  - `src/utils/retry.py`を作成
  - `RetryStrategy`クラスを実装（指数バックオフ）
  - リトライデコレーターを実装
  - _要件: 10.1_

- [ ]* 5.1 リトライロジックのユニットテストを作成
  - `tests/unit/test_retry.py`を作成
  - リトライ回数と遅延時間の計算をテスト
  - モックを使用してリトライ動作を検証
  - _要件: 10.1_

- [x] 6. Twitter API クライアントの実装






  - `src/clients/twitter_api_client.py`を作成
  - `TwitterAPIClient`クラスを実装
  - oEmbed API呼び出し機能を実装（`get_oembed`メソッド）
  - レート制限チェック機能を実装（`check_rate_limit`メソッド）
  - リトライロジックを統合
  - _要件: 1.2, 10.1, 10.2_

- [ ]* 6.1 Twitter APIクライアントのユニットテストを作成
  - `tests/unit/test_twitter_api_client.py`を作成
  - モックを使用してAPI呼び出しをテスト
  - 正常系とエラーハンドリングをテスト
  - レート制限処理をテスト
  - _要件: 1.2, 10.1, 10.2_

- [ ]* 6.2 ネットワークエラーのリトライプロパティテストを作成
  - **プロパティ23: ネットワークエラーのリトライ**
  - **検証要件: 10.1**
  - `tests/property/test_api_properties.py`を作成
  - 様々なネットワークエラーでリトライが実行されることをテスト
  - _要件: 10.1_

- [x] 7. ファイルリポジトリの実装






  - `src/repositories/file_repository.py`を作成
  - `FileRepository`クラスを実装
  - ファイル読み書き機能を実装（`read_embed_code`、`write_embed_code`、`read_height`、`write_height`）
  - バックアップ作成機能を実装（`create_backup`）
  - _要件: 1.3, 6.3, 9.2_

- [ ]* 7.1 ファイルリポジトリのユニットテストを作成
  - `tests/unit/test_file_repository.py`を作成
  - ファイル読み書きの基本動作をテスト
  - バックアップ作成をテスト
  - エラーハンドリングをテスト
  - _要件: 1.3, 6.3_

- [ ]* 7.2 ファイル保存のラウンドトリッププロパティテストを作成
  - **プロパティ2: ファイル保存のラウンドトリップ**
  - **検証要件: 1.3**
  - `tests/property/test_file_operations_properties.py`を作成
  - 任意の内容を保存して読み込み、元の内容と一致することをテスト
  - _要件: 1.3_

- [ ]* 7.3 表示高さ保存のラウンドトリッププロパティテストを作成
  - **プロパティ21: 表示高さ保存のラウンドトリップ**
  - **検証要件: 9.2**
  - `tests/property/test_file_operations_properties.py`に追加
  - 任意の高さ値を保存して読み込み、元の値と一致することをテスト
  - _要件: 9.2_

- [ ]* 7.4 エラー時のファイル不変性プロパティテストを作成
  - **プロパティ3: エラー時のファイル不変性**
  - **検証要件: 1.4**
  - `tests/property/test_file_operations_properties.py`に追加
  - エラー発生時に既存ファイルが変更されないことをテスト
  - _要件: 1.4_

- [ ]* 7.5 バックアップ作成のプロパティテストを作成
  - **プロパティ17: バックアップ作成の一貫性**
  - **検証要件: 6.3**
  - `tests/property/test_file_operations_properties.py`に追加
  - 任意の保存操作でバックアップが作成されることをテスト
  - _要件: 6.3_

- [ ]* 7.6 ファイルエラー処理のプロパティテストを作成
  - **プロパティ24: ファイルエラーの適切な処理**
  - **検証要件: 10.3**
  - `tests/property/test_file_operations_properties.py`に追加
  - 様々なファイルエラーが適切に処理されることをテスト
  - _要件: 10.3_

- [x] 8. Twitter埋め込みサービスの実装






  - `src/services/twitter_embed_service.py`を作成
  - `TwitterEmbedService`クラスを実装
  - 単一ツイート取得機能を実装（`fetch_embed_code`）
  - 複数ツイート取得機能を実装（`fetch_multiple_embed_codes`）
  - ファイル保存機能を実装（`save_embed_code`）
  - URL検証とツイートID抽出機能を統合（`validate_tweet_url`、`extract_tweet_id`）
  - _要件: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 9.4_

- [ ]* 8.1 サービス層のユニットテストを作成
  - `tests/unit/test_twitter_embed_service.py`を作成
  - モックを使用してサービスロジックをテスト
  - 単一ツイート取得、複数ツイート取得、ファイル保存をテスト
  - _要件: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_

- [ ]* 8.2 複数URL処理の完全性プロパティテストを作成
  - **プロパティ5: 複数URL処理の完全性**
  - **検証要件: 2.1**
  - `tests/property/test_service_properties.py`を作成
  - 任意のURLリストが全て処理されることをテスト
  - _要件: 2.1_

- [ ]* 8.3 埋め込みコード連結の完全性プロパティテストを作成
  - **プロパティ6: 埋め込みコード連結の完全性**
  - **検証要件: 2.2**
  - `tests/property/test_service_properties.py`に追加
  - 任意の埋め込みコードリストが全て連結されることをテスト
  - _要件: 2.2_

- [ ]* 8.4 部分的失敗時の正確性プロパティテストを作成
  - **プロパティ7: 部分的失敗時の正確性**
  - **検証要件: 2.3**
  - `tests/property/test_service_properties.py`に追加
  - 成功と失敗が混在するケースで正しく処理されることをテスト
  - _要件: 2.3_

- [ ]* 8.5 最大高さ選択のプロパティテストを作成
  - **プロパティ22: 最大高さ選択の正確性**
  - **検証要件: 9.4**
  - `tests/property/test_service_properties.py`に追加
  - 任意の高さリストから最大値が選択されることをテスト
  - _要件: 9.4_

- [x] 9. ログ記録機能の実装






  - `src/config/logging_config.py`にTwitter埋め込み機能用のロガー設定を追加
  - ログローテーション機能を実装（10MB、5世代）
  - エラーログ記録関数を実装
  - 取得履歴のログ記録機能を実装
  - _要件: 7.1, 10.4, 10.5_

- [ ]* 9.1 取得操作のログ記録プロパティテストを作成
  - **プロパティ18: 取得操作のログ記録**
  - **検証要件: 7.1**
  - `tests/property/test_logging_properties.py`を作成
  - 任意の取得操作がログに記録されることをテスト
  - _要件: 7.1_

- [ ]* 9.2 全エラーのログ記録プロパティテストを作成
  - **プロパティ26: 全エラーのログ記録**
  - **検証要件: 10.5**
  - `tests/property/test_logging_properties.py`に追加
  - 任意のエラーがログに記録されることをテスト
  - _要件: 10.5_

- [ ]* 9.3 予期しないエラーのログ記録プロパティテストを作成
  - **プロパティ25: 予期しないエラーのログ記録**
  - **検証要件: 10.4**
  - `tests/property/test_logging_properties.py`に追加
  - 予期しないエラーが適切にログに記録されることをテスト
  - _要件: 10.4_

- [x] 10. CLIインターフェースの実装





  - `src/cli/twitter_embed_cli.py`を作成
  - コマンドライン引数解析を実装（argparse使用）
  - 進行状況表示機能を実装
  - 終了コード管理を実装
  - TwitterEmbedServiceを統合
  - _要件: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 10.1 CLIのユニットテストを作成
  - `tests/unit/test_cli.py`を作成
  - 引数解析の基本動作をテスト
  - 引数不足時のエラー処理をテスト
  - _要件: 3.1, 3.2_

- [ ]* 10.2 コマンドライン引数解析のプロパティテストを作成
  - **プロパティ8: コマンドライン引数解析の正確性**
  - **検証要件: 3.1**
  - `tests/property/test_cli_properties.py`を作成
  - 任意の有効な引数パターンが正しく解析されることをテスト
  - _要件: 3.1_

- [ ]* 10.3 進行状況出力のプロパティテストを作成
  - **プロパティ9: 進行状況出力の一貫性**
  - **検証要件: 3.3**
  - `tests/property/test_cli_properties.py`に追加
  - 任意の処理で進行状況が出力されることをテスト
  - _要件: 3.3_

- [ ]* 10.4 成功時の終了コードプロパティテストを作成
  - **プロパティ10: 成功時の終了コード**
  - **検証要件: 3.4**
  - `tests/property/test_cli_properties.py`に追加
  - 任意の成功ケースで終了コード0が返されることをテスト
  - _要件: 3.4_

- [ ]* 10.5 失敗時の終了コードプロパティテストを作成
  - **プロパティ11: 失敗時の終了コード**
  - **検証要件: 3.5**
  - `tests/property/test_cli_properties.py`に追加
  - 任意の失敗ケースで非ゼロの終了コードが返されることをテスト
  - _要件: 3.5_

- [x] 11. 認証情報管理の実装






  - `src/config/settings.py`に認証情報読み込み機能を追加
  - 環境変数からの認証情報読み込み機能を実装
  - 認証情報の検証機能を実装
  - 認証情報のログ非出力を保証
  - _要件: 5.1, 5.2, 5.3, 5.4_

- [ ]* 11.1 認証情報管理のユニットテストを作成
  - `tests/unit/test_auth.py`を作成
  - 環境変数未設定時のエラー処理をテスト
  - 認証情報の読み込みをテスト
  - _要件: 5.1, 5.2_

- [ ]* 11.2 環境変数からの認証情報読み込みプロパティテストを作成
  - **プロパティ13: 環境変数からの認証情報読み込み**
  - **検証要件: 5.1**
  - `tests/property/test_auth_properties.py`を作成
  - 任意のAPIアクセスで環境変数から認証情報が読み込まれることをテスト
  - _要件: 5.1_

- [ ]* 11.3 認証情報のログ非出力プロパティテストを作成
  - **プロパティ14: 認証情報のログ非出力**
  - **検証要件: 5.4**
  - `tests/property/test_auth_properties.py`に追加
  - 任意のログ出力に認証情報が含まれないことをテスト
  - _要件: 5.4_

- [x] 12. Streamlit管理画面の実装
  - `src/ui/twitter_embed_admin.py`を作成
  - 認証機能を実装（パスワード認証）
  - URL入力フォームを実装
  - 結果表示とプレビュー機能を実装
  - TwitterEmbedServiceを統合
  - _要件: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 12.1 管理画面のユニットテストを作成
  - `tests/unit/test_admin_page.py`を作成
  - 認証機能をテスト
  - フォーム処理をテスト
  - _要件: 4.1, 4.2, 4.4, 4.5_

- [ ]* 12.2 認証情報のアクセス制御プロパティテストを作成
  - **プロパティ12: 認証情報のアクセス制御**
  - **検証要件: 4.5**
  - `tests/property/test_ui_properties.py`を作成
  - 任意のアクセスで認証チェックが実施されることをテスト
  - _要件: 4.5_

- [x] 13. HTML検証機能の実装






  - `src/utils/html_validator.py`を作成
  - HTML検証関数を実装
  - 不正なHTML検出機能を実装
  - 警告メッセージ表示機能を実装
  - _要件: 6.1, 6.2_

- [ ]* 13.1 HTML検証のユニットテストを作成
  - `tests/unit/test_html_validator.py`を作成
  - 正常なHTMLと不正なHTMLの検証をテスト
  - _要件: 6.1, 6.2_

- [ ]* 13.2 HTML検証のプロパティテストを作成
  - **プロパティ15: HTML検証の実行**
  - **検証要件: 6.1**
  - `tests/property/test_validation_properties.py`を作成
  - 任意の埋め込みコード取得でHTML検証が実行されることをテスト
  - _要件: 6.1_

- [ ]* 13.3 不正HTML検出のプロパティテストを作成
  - **プロパティ16: 不正HTML検出の完全性**
  - **検証要件: 6.2**
  - `tests/property/test_validation_properties.py`に追加
  - 任意の不正なHTMLが検出されることをテスト
  - _要件: 6.2_

- [x] 14. チェックポイント - コア機能のテスト実行





  - 全てのテストが成功することを確認
  - ユーザーに質問があれば確認

- [ ]* 15. 統合テストの作成
  - `tests/integration/test_twitter_embed_integration.py`を作成
  - CLIからの実行をテスト
  - サービス層とリポジトリ層の統合をテスト
  - エンドツーエンドのフローをテスト
  - _要件: 全体_

- [x] 16. ドキュメントの作成





  - `docs/twitter-embed-automation.md`を作成（使用方法、セットアップ手順）
  - CLIのヘルプメッセージを充実
  - README.mdにTwitter埋め込み機能のセクションを追加
  - _要件: 全体_

- [x] 17. 最終チェックポイント - 全テストの実行





  - 全てのテストが成功することを確認
  - カバレッジレポートを確認
  - ユーザーに質問があれば確認
