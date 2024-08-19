#!/bin/bash


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


src_dir="$SCRIPT_DIR/../src"
examples_dir="$SCRIPT_DIR/../examples"


# shellcheck disable=SC2038
find "$src_dir" -name "*.py" | xargs sed -i 's/[ \t]*$//'

# shellcheck disable=SC2038
find "$examples_dir" -name "*.py" | xargs sed -i 's/[ \t]*$//'

# shellcheck disable=SC2038
find "$SCRIPT_DIR" -name "*.py" | xargs sed -i 's/[ \t]*$//'


echo "done"
