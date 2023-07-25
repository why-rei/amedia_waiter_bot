#! /usr/bin/bash

root=$(pwd)

source "$root"/venv/bin/activate

export PYTHONPATH=$root

python3.11 "$root"/core/webhook.py
