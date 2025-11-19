"""
CLIモジュールのエントリーポイント

python -m src.cli.twitter_embed_cli として実行するためのファイル
"""

import sys
from src.cli.twitter_embed_cli import main

if __name__ == "__main__":
    sys.exit(main())
