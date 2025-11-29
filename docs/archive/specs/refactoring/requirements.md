# リファクタリング要件定義書

## はじめに

本ドキュメントは、「しのうたタイム」アプリケーションのコードベースをリファクタリングするための要件を定義します。現在のコードは機能的には動作していますが、保守性、テスト可能性、拡張性の観点から改善の余地があります。

## 用語集

- **System**: しのうたタイムアプリケーション
- **DataService**: データ読み込みと変換を担当するサービスクラス
- **SearchService**: 検索ロジックを担当するサービスクラス
- **URLGenerator**: URL生成ロジックを担当するユーティリティクラス
- **SongNumberGenerator**: 曲目番号生成ロジックを担当するユーティリティクラス
- **ビジネスロジック**: UIから独立したデータ処理ロジック
- **プレゼンテーション層**: Streamlit UIコンポーネント

## 要件

### 要件1: データサービスの分離

**ユーザーストーリー:** 開発者として、データ読み込みロジックを独立したモジュールに分離したい。これにより、テストが容易になり、再利用性が向上する。

#### 受入基準

1. THE System SHALL data_service.pyモジュールを作成する
2. THE System SHALL DataServiceクラスを実装する
3. THE DataService SHALL TSVファイルからデータを読み込むメソッドを提供する
4. THE DataService SHALL 配信データと楽曲データを結合するメソッドを提供する
5. THE DataService SHALL エラーハンドリングを内部で処理する
6. THE DataService SHALL 読み込んだデータをDataFrame形式で返す
7. WHEN ファイルが存在しない, THE DataService SHALL Noneを返し、エラー情報を保持する

### 要件2: 検索サービスの分離

**ユーザーストーリー:** 開発者として、検索ロジックを独立したモジュールに分離したい。これにより、検索機能のテストと拡張が容易になる。

#### 受入基準

1. THE System SHALL search_service.pyモジュールを作成する
2. THE System SHALL SearchServiceクラスを実装する
3. THE SearchService SHALL キーワードによるフィルタリングメソッドを提供する
4. THE SearchService SHALL 複数フィールドに対する検索をサポートする
5. THE SearchService SHALL 大文字小文字を区別しない検索を実行する
6. THE SearchService SHALL 検索対象フィールドを動的に指定できる
7. THE SearchService SHALL 検索結果をDataFrame形式で返す

### 要件3: ユーティリティ関数の分離

**ユーザーストーリー:** 開発者として、汎用的なユーティリティ関数を独立したモジュールに分離したい。これにより、コードの重複を削減し、保守性が向上する。

#### 受入基準

1. THE System SHALL utils.pyモジュールを作成する
2. THE System SHALL タイムスタンプ変換関数を提供する
3. THE System SHALL URL生成関数を提供する
4. THE System SHALL 曲目番号生成関数を提供する
5. THE System SHALL 日付変換関数を提供する
6. THE System SHALL 各関数が単一の責務を持つ
7. THE System SHALL 各関数が純粋関数として実装される（副作用なし）

### 要件4: データ処理パイプラインの構築

**ユーザーストーリー:** 開発者として、データ処理の流れを明確なパイプラインとして実装したい。これにより、処理の流れが理解しやすくなり、デバッグが容易になる。

#### 受入基準

1. THE System SHALL data_pipeline.pyモジュールを作成する
2. THE System SHALL DataPipelineクラスを実装する
3. THE DataPipeline SHALL データ読み込み、結合、変換、ソートの各ステップを明確に分離する
4. THE DataPipeline SHALL 各ステップの結果を検証する
5. THE DataPipeline SHALL エラー発生時に適切なエラーメッセージを提供する
6. THE DataPipeline SHALL 処理済みデータをキャッシュする
7. THE DataPipeline SHALL パイプライン全体を実行するメソッドを提供する

### 要件5: UIコンポーネントの分離

**ユーザーストーリー:** 開発者として、再利用可能なUIコンポーネントを独立したモジュールに分離したい。これにより、UIの一貫性が保たれ、保守性が向上する。

#### 受入基準

1. THE System SHALL ui_components.pyモジュールを作成する
2. THE System SHALL 検索フォームコンポーネントを提供する
3. THE System SHALL 結果表示テーブルコンポーネントを提供する
4. THE System SHALL ページネーションコンポーネントを提供する
5. THE System SHALL Twitter埋め込みコンポーネントを提供する
6. THE System SHALL 各コンポーネントが独立して動作する
7. THE System SHALL 各コンポーネントがパラメータで動作をカスタマイズできる

### 要件6: 設定管理の一元化

**ユーザーストーリー:** 開発者として、アプリケーション設定を一元管理したい。これにより、設定変更が容易になり、環境ごとの設定切り替えが可能になる。

#### 受入基準

1. THE System SHALL config.pyモジュールを作成する
2. THE System SHALL ファイルパスの設定を一元管理する
3. THE System SHALL 表示設定（初期表示件数、追加表示件数など）を一元管理する
4. THE System SHALL ページ設定（タイトル、アイコンなど）を一元管理する
5. THE System SHALL 環境変数からの設定読み込みをサポートする
6. THE System SHALL デフォルト値を提供する
7. THE System SHALL 設定値の検証を行う

### 要件7: エラーハンドリングの統一

**ユーザーストーリー:** 開発者として、エラーハンドリングを統一的な方法で実装したい。これにより、エラー処理の一貫性が保たれ、デバッグが容易になる。

#### 受入基準

1. THE System SHALL exceptions.pyモジュールを作成する
2. THE System SHALL カスタム例外クラスを定義する
3. THE System SHALL DataLoadError例外を提供する
4. THE System SHALL DataProcessingError例外を提供する
5. THE System SHALL ConfigurationError例外を提供する
6. THE System SHALL 各例外が適切なエラーメッセージを含む
7. THE System SHALL エラーログ機能を提供する

### 要件8: テストの追加

**ユーザーストーリー:** 開発者として、各モジュールに対する単体テストを追加したい。これにより、リファクタリング後の動作を保証し、将来の変更に対する安全性が向上する。

#### 受入基準

1. THE System SHALL testsディレクトリを作成する
2. THE System SHALL DataServiceのテストを提供する
3. THE System SHALL SearchServiceのテストを提供する
4. THE System SHALL ユーティリティ関数のテストを提供する
5. THE System SHALL DataPipelineのテストを提供する
6. THE System SHALL 各テストが独立して実行可能である
7. THE System SHALL テストカバレッジが80%以上である

### 要件9: ドキュメントの更新

**ユーザーストーリー:** 開発者として、リファクタリング後のコードベースに対応したドキュメントを更新したい。これにより、新しい構造が理解しやすくなる。

#### 受入基準

1. THE System SHALL README.mdを更新する
2. THE System SHALL 新しいモジュール構造を説明する
3. THE System SHALL 各モジュールの責務を明確にする
4. THE System SHALL 開発者向けガイドを提供する
5. THE System SHALL アーキテクチャ図を更新する
6. THE System SHALL APIドキュメントを生成する
7. THE System SHALL 移行ガイドを提供する

### 要件10: 後方互換性の維持

**ユーザーストーリー:** 開発者として、リファクタリング後も既存の機能が正常に動作することを保証したい。これにより、ユーザーへの影響を最小限に抑える。

#### 受入基準

1. THE System SHALL 既存の全機能を維持する
2. THE System SHALL UIの見た目と動作を維持する
3. THE System SHALL データファイルの形式を維持する
4. THE System SHALL 既存のURLパスを維持する
5. THE System SHALL パフォーマンスを維持または改善する
6. THE System SHALL 既存のエラーメッセージを維持する
7. WHEN リファクタリングが完了する, THE System SHALL 既存のテストケースが全て通過する

### 要件11: コードの可読性向上

**ユーザーストーリー:** 開発者として、コードの可読性を向上させたい。これにより、新しい開発者がコードベースを理解しやすくなる。

#### 受入基準

1. THE System SHALL 各関数の長さを50行以下に制限する
2. THE System SHALL 各クラスの責務を単一に保つ
3. THE System SHALL 意味のある変数名と関数名を使用する
4. THE System SHALL 複雑なロジックにコメントを追加する
5. THE System SHALL docstringを全ての公開関数とクラスに追加する
6. THE System SHALL 型ヒントを追加する
7. THE System SHALL コーディング規約（PEP 8）に準拠する

### 要件12: パフォーマンスの最適化

**ユーザーストーリー:** 開発者として、リファクタリングの機会にパフォーマンスを最適化したい。これにより、ユーザー体験が向上する。

#### 受入基準

1. THE System SHALL データ読み込みをキャッシュする
2. THE System SHALL 不要なデータ変換を削減する
3. THE System SHALL 効率的なデータ構造を使用する
4. THE System SHALL 遅延評価を適用する
5. THE System SHALL メモリ使用量を最適化する
6. THE System SHALL 初期表示時間を3秒以内に保つ
7. THE System SHALL 検索応答時間を1秒以内に保つ

### 要件13: ロギングの追加

**ユーザーストーリー:** 開発者として、アプリケーションの動作をロギングしたい。これにより、問題の診断とデバッグが容易になる。

#### 受入基準

1. THE System SHALL loggingモジュールを使用する
2. THE System SHALL ログレベル（DEBUG、INFO、WARNING、ERROR）を適切に使用する
3. THE System SHALL データ読み込み時にログを出力する
4. THE System SHALL エラー発生時に詳細なログを出力する
5. THE System SHALL パフォーマンス情報をログに記録する
6. THE System SHALL ログファイルをローテーションする
7. THE System SHALL 本番環境ではINFOレベル以上のログのみを出力する
