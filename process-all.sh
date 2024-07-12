#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


$SCRIPT_DIR/doc/generate-doc.sh

$SCRIPT_DIR/tools/mdpreproc.py $SCRIPT_DIR/README.md

# run tests in venv (it verifies required packages)
$SCRIPT_DIR/tools/installvenv.sh --no-prompt
$SCRIPT_DIR/venv/runtests.py

if [ -d "$SCRIPT_DIR/examples" ]; then
    $SCRIPT_DIR/examples/generate-all.sh
fi

$SCRIPT_DIR/tools/checkall.sh


echo "processing completed"
