# 実装タスクリスト

- [x] 1. データモデルの実装
  - src/models/excel_to_tsv_models.pyを作成し、ConversionResult、ValidationWarning、SheetMappingのデータクラスを定義する
  - _要件: 全要件_

- [x] 2. Excelリポジトリの実装
  - src/repositories/excel_repository.pyを作成し、ExcelRepositoryクラスを実装する
  - openpyxlを使用してExcelファイルを読み込む機能を実装する
  - シート名の取得、シートの存在確認、シートデータの読み込み機能を実装する
  - _要件: 2.1, 2.2, 2.3, 2.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 2.1 Excelリポジトリのプロパティベーステストを実装
  - **プロパティ 1: Excelシート読み込みの完全性**
  - **検証: 要件 2.1, 2.2**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - ランダムなExcelデータを生成してシート読み込みの完全性を検証する
  - _要件: 2.1, 2.2_

- [x] 3. TSVリポジトリの実装
  - src/repositories/tsv_repository.pyを作成し、TsvRepositoryクラスを実装する
  - UTF-8エンコーディングでTSVファイルを書き込む機能を実装する
  - タブ区切り、改行文字のエスケープ、特殊文字の処理を実装する
  - _要件: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 3.1 TSVリポジトリのプロパティベーステストを実装
  - **プロパティ 2: TSVファイル形式の正確性**
  - **検証: 要件 3.1, 3.2**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - 生成されたTSVファイルのフォーマットを検証する
  - _要件: 3.1, 3.2_

- [ ]* 3.2 ヘッダー行保持のプロパティベーステストを実装
  - **プロパティ 3: ヘッダー行の保持**
  - **検証: 要件 3.5**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - ヘッダー行が正しく出力されることを検証する
  - _要件: 3.5_

- [x] 4. バックアップリポジトリの実装
  - src/repositories/backup_repository.pyを作成し、BackupRepositoryクラスを実装する
  - タイムスタンプ付きバックアップファイルの作成機能を実装する
  - バックアップディレクトリの自動作成機能を実装する
  - _要件: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 4.1 バックアップのプロパティベーステストを実装
  - **プロパティ 6: バックアップの作成**
  - **検証: 要件 7.1, 7.2**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - バックアップファイルが正しく作成されることを検証する
  - _要件: 7.1, 7.2_

- [ ]* 4.2 バックアップ完全性のプロパティベーステストを実装
  - **プロパティ 7: バックアップの完全性**
  - **検証: 要件 7.1**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - バックアップファイルの内容が元のファイルと同じことを検証する
  - _要件: 7.1_

- [x] 5. データ検証機能の実装
  - ExcelToTsvServiceにvalidate_sheet_dataメソッドを実装する
  - フィールド数の検証機能を実装する
  - データ型の検証機能（IDが数値か、など）を実装する
  - URL形式の検証機能を実装する
  - _要件: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 5.1 フィールド数一貫性のプロパティベーステストを実装
  - **プロパティ 4: フィールド数の一貫性**
  - **検証: 要件 4.1**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - M_YT_LIVE.TSVの各行が4つのフィールドを持つことを検証する
  - _要件: 4.1_

- [ ]* 5.2 タイムスタンプフィールド数一貫性のプロパティベーステストを実装
  - **プロパティ 5: タイムスタンプフィールド数の一貫性**
  - **検証: 要件 4.2**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - M_YT_LIVE_TIMESTAMP.TSVの各行が5つのフィールドを持つことを検証する
  - _要件: 4.2_

- [x] 6. Excel to TSVサービスの実装
  - src/services/excel_to_tsv_service.pyを作成し、ExcelToTsvServiceクラスを実装する
  - convert_excel_to_tsvメソッドを実装する
  - シートマッピングの設定を実装する
  - 変換処理のメインロジックを実装する
  - _要件: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 6.1 エラー時のファイル保持のプロパティベーステストを実装
  - **プロパティ 8: エラー時のファイル保持**
  - **検証: 要件 8.4**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - エラー発生時に既存ファイルが保持されることを検証する
  - _要件: 8.4_

- [x] 7. 後続処理（song_list_generator）の実装
  - ExcelToTsvServiceにrun_song_list_generatorメソッドを実装する
  - subprocessを使用してsong_list_generatorを実行する機能を実装する
  - 実行結果の取得とエラーハンドリングを実装する
  - _要件: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]* 7.1 後続処理実行のプロパティベーステストを実装
  - **プロパティ 9: 後続処理の実行**
  - **検証: 要件 9.1, 9.2**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - song_list_generatorが正しく実行されることを検証する
  - _要件: 9.1, 9.2_

- [ ]* 7.2 後続処理エラー分離のプロパティベーステストを実装
  - **プロパティ 10: 後続処理のエラー分離**
  - **検証: 要件 9.4**
  - tests/property/test_excel_to_tsv_properties.pyにテストを追加する
  - song_list_generatorのエラー時にTSVファイルが保持されることを検証する
  - _要件: 9.4_

- [x] 8. CLIの実装
  - src/cli/excel_to_tsv_cli.pyを作成し、コマンドラインインターフェースを実装する
  - create_parser関数を実装してコマンドライン引数を定義する
  - main関数を実装してメイン処理を実行する
  - 進捗表示とログ出力を実装する
  - _要件: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 8.1 CLIのユニットテストを実装
  - tests/unit/test_excel_to_tsv_cli.pyを作成する
  - コマンドライン引数の解析をテストする
  - ヘルプメッセージの表示をテストする
  - ドライランモードをテストする
  - _要件: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9. ユニットテストの実装
  - tests/unit/test_excel_to_tsv_service.pyを作成する
  - 変換処理の正常系・異常系をテストする
  - データ検証機能をテストする
  - URL検証機能をテストする
  - song_list_generator実行をテストする
  - _要件: 全要件_

- [x] 10. 統合テストの実装
  - tests/integration/test_excel_to_tsv_integration.pyを作成する
  - 正常系のエンドツーエンドテストを実装する
  - バックアップ機能のテストを実装する
  - エラーリカバリのテストを実装する
  - _要件: 全要件_

- [x] 11. ドキュメントの作成
  - README.mdにExcel to TSV変換ツールの使用方法を追加する
  - コマンドライン引数の説明を追加する
  - 使用例を追加する
  - トラブルシューティングガイドを追加する
  - _要件: 全要件_

- [x] 12. 最終チェックポイント - すべてのテストが通ることを確認
  - すべてのテストが通ることを確認する
  - 質問があればユーザーに確認する
