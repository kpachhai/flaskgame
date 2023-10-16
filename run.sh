#!/usr/bin/env bash

function installDependencies() {
    if [ ! -d ".venv" ]; then
        virtualenv -p `which python3.9` .venv
    fi

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
}

function venv_start () {  
    installDependencies
    echo "Running using virtual environment..."
    python run.py
}

function docker_start () {
    if ! command -v docker &> /dev/null; then
        echo "Docker is not installed."
        echo "Please install Docker for `uname` first and then try again."
        exit 1
    fi
    echo "Running using docker..."
    docker container stop flaskgame-cardduel || true && docker container rm -f flaskgame-cardduel || true
    docker build -t kpachhai/flaskgame-cardduel .
    docker run --name flaskgame-cardduel    \
        -v ${PWD}/.env:/src/.env            \
        -p 5000:5000                        \
        kpachhai/flaskgame-cardduel
}

function test() {
    installDependencies
    echo "Running tests..."
    pytest
}

case "$1" in
    venv)
        venv_start
        ;;
    docker)
        docker_start
        ;;
    test)
        test
        ;;
    *)
    echo "Usage: run.sh {venv|docker|test}"
    exit 1
esac