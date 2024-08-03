#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


uncrustify --show-config > $SCRIPT_DIR/default.cfg

$SCRIPT_DIR/../../src/uncrustifyimpact.py genparamsspace > $SCRIPT_DIR/params_space.json
