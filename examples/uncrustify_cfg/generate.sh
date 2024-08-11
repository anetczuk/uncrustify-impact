#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


echo "running example uncrustify_cfg"


uncrustify --show-config > $SCRIPT_DIR/default.cfg


cd $SCRIPT_DIR/../../src/

python3 -m uncrustimpact genparamsspace > $SCRIPT_DIR/params_space.json
