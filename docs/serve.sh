#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_DIR}


if ! python3 -m pip show mkdocs-material &> /dev/null; then
    if ! python3 -m pip install mkdocs-material; then
        echo "Failed to install mkdocs-material via pip"
        exit 1
    fi
fi

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

mkdocs serve
exit $?



