# datrie compiling dependencies
sudo apt update && sudo apt install gcc clang llvm

# see https://github.com/astral-sh/uv/issues/7525#issuecomment-2373126442
export AR=/usr/bin/ar

uv sync