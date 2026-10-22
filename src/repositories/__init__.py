"""
リポジトリパッケージ

ファイルへのアクセスを担当するリポジトリ。v2 は table_repository、ほかは v1(フェーズ3で消す)。
使うものは `from src.repositories.table_repository import TableRepository` のように個別に import する
(ここでまとめて import すると、画面が v1 とその依存(openpyxl・chardet)まで読み込むため)。
"""
