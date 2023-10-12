#!/usr/bin/env bash

function start () {
    virtualenv -p `which python3.9` .venv
    source .venv/bin/activate
    pip install --upgrade pip

    case `uname` in
    Linux )
        pip install -r requirements.txt
        ;;
    Darwin )
        pip install --global-option=build_ext \
                    --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib" \
                    --global-option="-I/usr/local/opt/zlib/include" --global-option="-L/usr/local/opt/zlib/lib" -r requirements.txt
        ;;
    *)
    exit 1
    ;;
    esac

    export FLASK_APP=main.py
    export FLASK_ENV=development
    flask run
}

case "$1" in
    start)
        start
        ;;
    *)
    echo "Usage: run.sh {start}"
    exit 1
esac