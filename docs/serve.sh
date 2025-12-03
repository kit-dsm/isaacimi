#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_DIR}

check_pip() {
    for PACKAGE_NAME in "$@"; do
        if ! python3 -m pip show $PACKAGE_NAME &> /dev/null; then
            if ! python3 -m pip install $PACKAGE_NAME; then
                echo "Failed to install $PACKAGE_NAME via pip"
                exit 1
            fi
        fi
    done
}

check_pip mkdocs-material mkdocstrings-python mkdocs-gen-files mkdocs-literate-nav mkdocs-section-index mkdocs-click

if ! python3 -m pip show isaacimi &> /dev/null; then
    if ! python3 -m pip install -e ..; then
        echo "Failed to install isaacimi via pip"
        exit 1
    fi
fi

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

mkdocs serve
exit $?