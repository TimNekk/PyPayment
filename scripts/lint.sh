set -e

if ! pip list | grep ruff; then
    python -m pip install --upgrade pip
    pip install ruff
fi

ruff check .