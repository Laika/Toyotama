#!/bin/bash

INIT_DIR=$(pwd)
cd ..
sphinx-apidoc -f -o ./docs/ ./toyotama/
sphinx-build -b html ./docs/ ./docs/_build/
cd ${INIT_DIR}
