#!/bin/bash

set -e

show_help() {
    echo "Usage: ./install.sh [OPTIONS]"
    echo
    echo "Used to install isaacimi into the same Python environment as Isaac Sim."
    echo "Requires sudo permission."
    echo
    echo "Options:"
    echo "  --test      Install extras for testing."
    echo "  --help      Show this message and exit."
}

PACKAGE_EXTRAS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --help)
            show_help
            exit 0
            ;;
        --test)
            PACKAGE_EXTRAS+=("test")
            ;;
        *)
            echo "Unknown option: $1"
            echo
            show_help
            exit 1
            ;;
    esac
    shift
done

SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ISAACIMI_DIR="$(dirname "$SCRIPTS_DIR")"

# find the python executable provided my Isaac Sim
extract_isaacsim_python_exe() {
    if [[ -n "$VIRTUAL_ENV" ]] && python -c "import carb" &>/dev/null; then
        # Case 1: Isaac Sim was installed via pip
        # TODO: test for cases where Isaac Sim was installed in system Python
        echo "[INFO] Isaac Sim detected via pip in virtual environment: $VIRTUAL_ENV"
        local isaacsim_python_exe=$(which python)
    else
        # Case 2: Isaac Sim was installed via pre-built binaries and simlink to the isaacsim directory was created
        local isaacsim_python_exe=${ISAACIMI_DIR}/_isaac_sim/python.sh
    fi

    if [ ! -f "${isaacsim_python_exe}" ]; then
        echo -e "[ERROR] Unable to find any Python executable at path: '${isaacsim_python_exe}'" >&2
        echo -e "\tThis could be due to the following reasons:" >&2
        echo -e "\t1. If Isaac Sim was installed via pip, the Python environment is not activated." >&2
        echo -e "\t2. If Isaac Sim was installed via pre-built binaries, the Python executable is not available at the default path: ${ISAACIMI_DIR}/_isaac_sim/python.sh" >&2
        echo -e "\t   Ensure a symlink is setup with: ln -s path/to/isaacsim ${ISAACIMI_DIR}/_isaac_sim" >&2
    fi

    echo ${isaacsim_python_exe}
}

create_symlink() {
    TARGET=$1
    LINK_NAME=$2

    if [ -L "$LINK_NAME" ]; then
        if [ "$(readlink -f $LINK_NAME)" = "$TARGET" ]; then
            echo "The symlink between $TARGET and $LINK_NAME already exists."
            return 0
        else
            echo "The symlink $LINK_NAME does not point to target $TARGET."
            rm $LINK_NAME
        fi
    fi

    ln -s $TARGET $LINK_NAME
    echo "Updated symlink."
    return 0
}

isaacsim_python_exe=$(extract_isaacsim_python_exe)
echo "[INFO] Using pip to install isaacimi into the same Python environment used by Isaac Sim..."
echo "[INFO] Using Python interpreter: $isaacsim_python_exe"

if [ ${#PACKAGE_EXTRAS[@]} -eq 0 ]; then
    ${isaacsim_python_exe} -m pip install -e ${ISAACIMI_DIR}
else
    PACKAGE_EXTRAS_STRING=$(IFS=, ; echo "${PACKAGE_EXTRAS[*]}")
    echo "[INFO] Installing isaacimi with extras: [$PACKAGE_EXTRAS_STRING]"
    ${isaacsim_python_exe} -m pip install -e ${ISAACIMI_DIR}[${PACKAGE_EXTRAS_STRING}]
fi

# TODO: setup vscode if not in Docker container

chmod +x "$SCRIPTS_DIR/isaacimi"
create_symlink "$SCRIPTS_DIR/isaacimi" "/usr/local/bin/isaacimi"

# TODO: setup shell completion

echo "isaacimi has been set up!"





