"""
例外パッケージ

アプリケーション固有の例外クラスを提供します。
"""

from src.exceptions.errors import (
    ShinoutaTimeError,
    DataLoadError,
    ConfigurationError,
)

__all__ = [
    "ShinoutaTimeError",
    "DataLoadError",
    "ConfigurationError",
]
