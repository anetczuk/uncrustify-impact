#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


echo "running example uncrustify_impact"


OUT_DIR="$SCRIPT_DIR/impact"

rm -fr "$OUT_DIR"


uncrustify -c "$SCRIPT_DIR/override.cfg" --update-config-with-doc > "$SCRIPT_DIR/config.cfg"


cd "$SCRIPT_DIR/../../src/"


ARGS=()
ARGS+=(impact)
ARGS+=(--files "$SCRIPT_DIR/example.cpp")
ARGS+=(--config "$SCRIPT_DIR/config.cfg")
ARGS+=(--outputdir "$OUT_DIR")
ARGS+=(--ignoreparams code_width cmt_width indent_columns)


if [[ $* == *--profile* ]]; then
 	../tools/profiler.sh --cprofile -m \
	uncrustimpact "${ARGS[@]}"
else
	python3 -m \
	uncrustimpact "${ARGS[@]}"
fi


result=$(checklink -r -q "$OUT_DIR"/index.html)
if [[ "$result" != "" ]]; then
	echo "broken links found:"
	echo "$result"
	exit 1
fi
# else: # empty string - no errors
echo "no broken links found"
