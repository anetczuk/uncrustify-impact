#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


echo "running example uncrustify_impact"


OUT_DIR="$SCRIPT_DIR/diff"

rm -fr "$OUT_DIR"


uncrustify -c "$SCRIPT_DIR/override.cfg" --update-config-with-doc > "$SCRIPT_DIR/config.cfg"


cd "$SCRIPT_DIR/../../src/"


if [[ $* == *--profile* ]]; then
	../tools/profiler.sh \
	-m uncrustimpact diff --files "$SCRIPT_DIR/example.cpp" \
						  --config "$SCRIPT_DIR/config.cfg" \
						  --outputdir "$OUT_DIR"
else
	python3 -m uncrustimpact diff --files "$SCRIPT_DIR/example.cpp" \
								  --config "$SCRIPT_DIR/config.cfg" \
								  --outputdir "$OUT_DIR"
fi


result=$(checklink -r -q "$OUT_DIR"/index.html)
if [[ "$result" != "" ]]; then
	echo "broken links found:"
	echo "$result"
	exit 1
fi
# else: # empty string - no errors
echo "no broken links found"


## generate image from html
if [ -f "$OUT_DIR/index.html" ]; then
    cutycapt --url=file://"$OUT_DIR"/index.html --out="$OUT_DIR/index.png"
    convert "$OUT_DIR/index.png" -strip -trim "$OUT_DIR/index.png"
fi

if [ -f "$OUT_DIR/example_cpp/index.html" ]; then
    cutycapt --url=file://"$OUT_DIR"/example_cpp/index.html --out="$OUT_DIR/file_index.png"
    convert "$OUT_DIR/file_index.png" -strip -trim "$OUT_DIR/file_index.png"
fi


## generate small images
"$SCRIPT_DIR"/../generate_small.sh
