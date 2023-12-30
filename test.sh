#!/bin/bash

set -eux

mypy fil
isort fil test_fil.py
black fil test_fil.py
ruff check --fix fil test_fil.py
coverage run $(which pytest)
coverage html
