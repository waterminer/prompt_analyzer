#!/bin/bash

venv="./venv" #You can modify this path to customize the venv location

if [ ! -d "$venv" ]; then
    python3 -m venv "$venv"
    init_venv=true
fi

source "$venv/bin/activate"

if [ "$init_venv" = true ]; then
    python3 -m pip install --upgrade pip
    python3 -m pip install -r ./requirements.txt
fi

python3 ./__init__.py
