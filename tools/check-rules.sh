#!/bin/sh
# しのうたタイムの絶対制約(docs/prompts/_common-context.md)のうち、grep で確かめられるものを確かめる。
# 読み取りだけで、何も書き換えない。
#
# 使い方(Git Bash、リポジトリのどこからでも): sh tools/check-rules.sh
# コンテナ(python:3.11-slim)には git が無いので、ホストの Git Bash で流す。
# 確かめること:
#   - ブランチ: main・develop の上にいない(push されると本番・stg に反映される)
#   - 公開リポジトリ: 追跡中・未追跡(.gitignore 対象外)のファイルに、ローカルの絶対パス・
#     メールアドレス・トークンらしき文字列(Google API キーを含む)が無い。
#     .env・secrets.toml・取り込みのキャッシュ(data/ingest/cache・staged)を追跡していない
#   - コード(WARN): HTML の escape=False、Streamlit 内部クラス名(st-emotion-cache-*)、
#     キャッシュ関数の中の st.* の表示、ADMIN_PASSWORD の既定値
#     → 今のコードに既知の違反があるため WARN に留める。直したら ng に上げる
# 終了コード: 0 = 問題なし、1 = 問題あり(WARN は終了コードに影響しない)

cd "$(dirname "$0")/.." || exit 1

status=0
ng() { echo "  NG: $1"; status=1; }
ok() { echo "  OK: $1"; }
warn() { echo "  WARN: $1"; }

# 追跡中と未追跡(.gitignore 対象外)のテキストファイルを検索する。このスクリプト自身は除く
search() {
    git grep -n -I --untracked -E "$1" -- . ':!tools/check-rules.sh'
}

echo "== ブランチ"
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
case "$branch" in
    main|develop) ng "$branch の上にいる(作業は feature/ などの作業ブランチで行う)" ;;
    "") ng "ブランチが読めない" ;;
    *) ok "作業ブランチ: $branch" ;;
esac

echo "== 公開リポジトリ"
hits=$(search '[A-Za-z]:[\\/]+(Users|GitLocal)[\\/]|/c/(Users|GitLocal)/')
if [ -n "$hits" ]; then ng "ローカルの絶対パスがある:
$hits"; else ok "ローカルの絶対パスなし"; fi

hits=$(search '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' | grep -viE '@(example\.(com|org|net)|users\.noreply\.github\.com)|noreply@')
if [ -n "$hits" ]; then ng "メールアドレスがある:
$hits"; else ok "メールアドレスなし"; fi

hits=$(search 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[baprs]-[A-Za-z0-9-]{10,}')
if [ -n "$hits" ]; then ng "トークンらしき文字列がある:
$hits"; else ok "トークンらしき文字列なし"; fi

hits=$(git ls-files | grep -E '(^|/)\.env$|(^|/)secrets\.toml$|settings\.local\.json$')
if [ -n "$hits" ]; then ng "秘密の設定ファイルを追跡している:
$hits"; else ok ".env・secrets.toml・settings.local.json を追跡していない"; fi

hits=$(git ls-files 'data/ingest/cache' 'data/ingest/staged')
if [ -n "$hits" ]; then ng "取り込みのキャッシュ・下書き(コメント本文を含む)を追跡している:
$hits"; else ok "取り込みのキャッシュ・下書きを追跡していない"; fi

echo "== コード"
hits=$(git grep -n 'escape=False' -- '*.py' | grep -v '^[^:]*:[0-9]*:[[:space:]]*#')
if [ -n "$hits" ]; then warn "escape=False で HTML を組み立てている(データ中の < や & で表が壊れる):
$hits"; else ok "escape=False なし"; fi

hits=$(git grep -n 'st-emotion-cache-[a-z0-9]' -- '*.css' '*.py' | grep -v '^[^:]*:[0-9]*:[[:space:]]*\*')
if [ -n "$hits" ]; then warn "Streamlit 内部クラス名に依存した CSS がある(版を上げると壊れる):
$hits"; else ok "内部クラス名への依存なし"; fi

hits=$(git ls-files '*.py' | xargs awk '
    FNR == 1 { incache = 0; inbody = 0 }
    /^[[:space:]]*@st\.cache_(data|resource)/ { incache = 1; next }
    incache && /^[[:space:]]*def / { match($0, /^[[:space:]]*/); defind = RLENGTH; inbody = 1; incache = 0; next }
    inbody {
        if ($0 ~ /^[[:space:]]*$/) next
        match($0, /^[[:space:]]*/)
        if (RLENGTH <= defind) { inbody = 0; next }
        if ($0 ~ /st\.(error|warning|info|success|write|markdown|toast|exception)\(/) print FILENAME ":" FNR ":" $0
    }')
if [ -n "$hits" ]; then warn "キャッシュ関数の中で st.* を表示している(キャッシュが効くと出なくなる。例外を上げてページ側で表示する):
$hits"; else ok "キャッシュ関数の中の表示なし"; fi

hits=$(git grep -nE 'getenv\(["'\'']ADMIN_PASSWORD["'\''][[:space:]]*,' -- '*.py')
if [ -n "$hits" ]; then warn "ADMIN_PASSWORD に既定値がある(公開リポジトリなので既定値は誰でも読める):
$hits"; else ok "ADMIN_PASSWORD の既定値なし"; fi

if [ $status -eq 0 ]; then
    echo "結果: 問題なし"
else
    echo "結果: 問題あり。docs/prompts/_common-context.md の絶対制約に合わせて直す"
fi
exit $status
