# 実装タスクリスト

- [x] 1. データモデルとリポジトリの実装




  - ArtistSortMappingデータクラスとArtistSortMappingRepositoryクラスを実装
  - TSVファイルの読み込み・書き込み機能を実装
  - _要件: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 1.1 ArtistSortMappingデータクラスを作成


  - `src/models/artist_sort_models.py`を作成
  - `ArtistSortMapping`データクラスを定義（artist, sort_name）
  - _要件: 4.1_

- [x] 1.2 ArtistSortMappingRepositoryクラスを作成


  - `src/repositories/artist_sort_mapping_repository.py`を作成
  - `__init__()`, `load_mappings()`, `save_mapping()`, `delete_mapping()`, `get_all_mappings()`, `get_mapping()`メソッドを実装
  - TSV形式でのファイル読み込み・書き込みを実装
  - UTF-8エンコーディングを使用
  - _要件: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

- [x] 1.3 重複エントリと空行の処理を実装

  - 重複したアーティスト名がある場合、最後のエントリを有効とする
  - 空行を無視する処理を実装
  - _要件: 4.4, 4.5_

- [x] 1.4 エラーハンドリングを実装

  - ファイル不存在時は空のマッピングを返す
  - ファイル形式エラー時はValueErrorを発生
  - ファイル書き込みエラー時はIOErrorを発生
  - 適切なログ出力を実装
  - _要件: 1.2, 1.3, 6.1, 6.2, 6.3, 6.4_

- [x] 1.5 ArtistSortMappingRepositoryのプロパティテストを作成


  - **Property 1: ファイル読み込みの往復一貫性**
  - **検証: 要件 1.1, 1.4**
  - `tests/property/test_artist_sort_mapping_repository_properties.py`を作成
  - Hypothesisを使用して、任意のマッピング辞書について往復一貫性をテスト

- [x] 1.6 マッピング追加のプロパティテストを作成


  - **Property 2: マッピング追加の永続性**
  - **検証: 要件 1.4**
  - 任意のアーティスト名とソート名について、追加後に読み込むとマッピングが含まれることをテスト

- [x] 1.7 マッピング更新のプロパティテストを作成



  - **Property 3: マッピング更新の上書き**
  - **検証: 要件 1.5**
  - 任意の既存マッピングについて、更新後に読み込むと新しいソート名が使用されることをテスト

- [x] 1.8 マッピング削除のプロパティテストを作成


  - **Property 4: マッピング削除の除去**
  - **検証: 要件 3.3**
  - 任意の既存マッピングについて、削除後に読み込むとマッピングが含まれないことをテスト

- [x] 1.9 不正形式のプロパティテストを作成


  - **Property 7: 不正形式のエラー処理**
  - **検証: 要件 1.3**
  - 任意の不正な形式のファイルについて、読み込み時にValueErrorが発生することをテスト

- [x] 1.10 ArtistSortMappingRepositoryのユニットテストを作成


  - `tests/unit/test_artist_sort_mapping_repository.py`を作成
  - 正常なTSVファイルの読み込みテスト
  - 空ファイルの読み込みテスト
  - 存在しないファイルの読み込みテスト
  - 新規マッピングの追加テスト
  - 既存マッピングの更新テスト
  - マッピングの削除テスト
  - 重複エントリの処理テスト
  - 空行の処理テスト
  - エンコーディングエラーのテスト
  - _要件: 1.1, 1.2, 1.3, 1.4, 1.5, 4.4, 4.5, 6.1, 6.2, 6.3_

- [x] 2. ArtistSortGeneratorの拡張



  - 既存のArtistSortGeneratorクラスを拡張
  - 修正マッピングを優先的に適用する機能を追加
  - _要件: 2.1, 2.2, 5.3_

- [x] 2.1 ArtistSortGeneratorにマッピングリポジトリのサポートを追加


  - `__init__()`メソッドに`mapping_repository`パラメータを追加（オプション）
  - `set_mapping_repository()`メソッドを実装
  - _要件: 5.1, 5.2_

- [x] 2.2 generate()メソッドを拡張


  - マッピングリポジトリが設定されている場合、まずマッピングを確認
  - マッピングが存在する場合はそれを返す
  - マッピングが存在しない場合は自動変換を実行
  - 適切なログ出力を実装
  - _要件: 2.1, 2.2_

- [x] 2.3 マッピング優先適用のプロパティテストを作成


  - **Property 5: マッピング優先の適用**
  - **検証: 要件 2.1**
  - `tests/property/test_artist_sort_generator_properties.py`を作成または更新
  - 任意のアーティスト名について、マッピングが存在する場合はマッピングのソート名が返されることをテスト

- [x] 2.4 自動生成フォールバックのプロパティテストを作成


  - **Property 6: 自動生成のフォールバック**
  - **検証: 要件 2.2**
  - 任意のアーティスト名について、マッピングが存在しない場合は自動生成されたソート名が返されることをテスト

- [x] 2.5 ArtistSortGeneratorのユニットテストを更新



  - `tests/unit/test_artist_sort_generator.py`を作成または更新
  - マッピングが存在する場合のテスト
  - マッピングが存在しない場合のテスト
  - マッピングリポジトリが設定されていない場合のテスト
  - _要件: 2.1, 2.2_

- [x] 3. コマンドラインインターフェースの実装

  - ArtistSortCLIクラスを実装
  - 修正マッピングの追加・更新・削除・一覧表示機能を実装
  - _要件: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3.1 ArtistSortCLIクラスを作成


  - `src/cli/artist_sort_cli.py`を作成
  - `__init__()`, `add_mapping()`, `list_mappings()`, `delete_mapping()`, `update_mapping()`, `run()`メソッドを実装
  - _要件: 3.1, 3.2, 3.3, 3.5_

- [x] 3.2 CLIのメインエントリーポイントを作成

  - `src/cli/artist_sort_cli.py`に`main()`関数を追加
  - argparseを使用してコマンドライン引数を処理
  - サブコマンド（add, list, delete, update）を実装
  - _要件: 3.1, 3.2, 3.3, 3.5_

- [x] 3.3 エラーハンドリングとユーザーフィードバックを実装

  - 存在しないマッピングの削除時にエラーメッセージを表示
  - 成功時に確認メッセージを表示
  - 日本語でのユーザー向けメッセージを実装
  - _要件: 3.4_

- [x] 3.4 ArtistSortCLIのユニットテストを作成


  - `tests/unit/test_artist_sort_cli.py`を作成
  - add_mapping()のテスト
  - list_mappings()のテスト
  - delete_mapping()のテスト
  - update_mapping()のテスト
  - 存在しないマッピングの削除テスト
  - _要件: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4. SongListServiceとの統合




  - SongListServiceがArtistSortGeneratorを使用する際に修正マッピングを適用
  - デフォルトの修正マッピングファイルパスを設定
  - _要件: 5.1, 5.2, 5.3_

- [x] 4.1 SongListServiceの初期化を更新


  - `__init__()`メソッドに`mapping_file_path`パラメータを追加（オプション）
  - デフォルトパスは`data/artist_sort_mapping.tsv`
  - ArtistSortMappingRepositoryを初期化
  - ArtistSortGeneratorにマッピングリポジトリを設定
  - _要件: 5.1, 5.2_

- [x] 4.2 ログ出力を追加


  - 修正マッピングの適用状況をログに記録
  - 適用されたマッピングの数を記録
  - _要件: 2.4, 5.4_

- [x] 4.3 SongListServiceの統合テストを作成






  - `tests/integration/test_song_list_service_with_mapping.py`を作成
  - 修正マッピングが曲リスト生成に正しく適用されることをテスト
  - 修正マッピングがソート順に反映されることをテスト
  - _要件: 5.3_

- [x] 5. ドキュメントの作成





  - 使用方法のドキュメントを作成
  - _要件: すべて_


- [x] 5.1 使用方法のドキュメントを作成

  - `docs/guides/artist-sort-correction-guide.md`を作成
  - CLIの使用方法を説明
  - 修正マッピングファイルの形式を説明
  - 使用例を記載


- [x] 5.2 READMEを更新

  - `README.md`に新機能の説明を追加
  - CLIコマンドの使用例を追加

- [x] 6. チェックポイント - すべてのテストが成功することを確認





  - すべてのテストが成功することを確認し、質問があればユーザーに尋ねる
