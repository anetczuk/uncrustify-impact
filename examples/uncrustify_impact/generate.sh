#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


OUT_DIR="$SCRIPT_DIR/impact"

rm -fr "$OUT_DIR"


uncrustify -c $SCRIPT_DIR/override.cfg --update-config-with-doc > $SCRIPT_DIR/config.cfg

$SCRIPT_DIR/../../src/uncrustifyimpact.py impact --file $SCRIPT_DIR/example.cpp \
												 --config $SCRIPT_DIR/config.cfg \
												 --outputdir $OUT_DIR \
												 --randomseed 0 \
												 --ignoreparams code_width cmt_width indent_columns
