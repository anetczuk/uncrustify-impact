#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


"$SCRIPT_DIR"/cpp_diff/calculate.py

"$SCRIPT_DIR"/uncrustify_cfg/generate.sh

"$SCRIPT_DIR"/uncrustify_impact/generate.sh

"$SCRIPT_DIR"/uncrustify_impact_simple/generate.sh

"$SCRIPT_DIR"/uncrustify_paramsspace/generate.sh

"$SCRIPT_DIR"/uncrustify_diff/generate.sh

"$SCRIPT_DIR"/uncrustify_fit/generate.sh


## generate small images
#$SCRIPT_DIR/generate_small.sh


echo -e "generation completed"
