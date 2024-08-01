#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


$SCRIPT_DIR/cpp_diff/calculate.py

$SCRIPT_DIR/uncrustify_cfg/generate.sh

$SCRIPT_DIR/uncrustify_impact/generate.sh
