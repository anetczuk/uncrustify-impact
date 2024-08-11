#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


echo "running example uncrustify_impact"


OUT_DIR="$SCRIPT_DIR/impact"

rm -fr "$OUT_DIR"


uncrustify -c $SCRIPT_DIR/override.cfg --update-config-with-doc > $SCRIPT_DIR/config.cfg


cd $SCRIPT_DIR/../../src/


if [[ $* == *--profile* ]]; then
	../tools/profiler.sh \
	-m uncrustimpact impact --file $SCRIPT_DIR/example.cpp \
							--config $SCRIPT_DIR/config.cfg \
							--outputdir $OUT_DIR \
							--ignoreparams code_width cmt_width indent_columns
else
	python3 -m uncrustimpact impact --file $SCRIPT_DIR/example.cpp \
									--config $SCRIPT_DIR/config.cfg \
									--outputdir $OUT_DIR \
									--ignoreparams code_width cmt_width indent_columns
fi
