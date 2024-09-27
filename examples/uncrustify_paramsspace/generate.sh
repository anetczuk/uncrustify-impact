#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


echo "running example uncrustify_paramsspace"


OUT_DIR="$SCRIPT_DIR/impact"

rm -fr "$OUT_DIR"


uncrustify -c "$SCRIPT_DIR/override.cfg" --update-config-with-doc > "$SCRIPT_DIR/config.cfg"


cd "$SCRIPT_DIR/../../src/"

python3 -m uncrustimpact impact --files "$SCRIPT_DIR/example.cpp" \
								--config "$SCRIPT_DIR/config.cfg" \
								--paramsspace "$SCRIPT_DIR/params_space.json" \
								--overridedefparamsspace \
								--outputdir "$OUT_DIR" \
								--ignoreparams indent_columns cmt_width cmt_cpp_to_c nl_max sp_before_semi


result=$(checklink -r -q "$OUT_DIR/index.html")
if [[ "$result" != "" ]]; then
	echo "broken links found:"
	echo "$result"
	exit 1
fi
# else: # empty string - no errors
echo "no broken links found"
