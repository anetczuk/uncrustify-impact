#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


echo "running example uncrustify_impact"


OUT_DIR="$SCRIPT_DIR/fit"

rm -fr "$OUT_DIR"


cd "$SCRIPT_DIR/../../src/"


ARGS=()
ARGS+=(fit)
ARGS+=(--files "$SCRIPT_DIR/example.cpp")
ARGS+=(--config "$SCRIPT_DIR/config.cfg")
ARGS+=(--outputdir "$OUT_DIR")
# ARGS+=(--ignoreparams code_width cmt_width indent_columns)


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


## generate image from html
PAGE_PATH="$OUT_DIR/index.html"
if [ -f "$PAGE_PATH" ]; then
	OUT_IMG_PATH="$OUT_DIR/index.png"
    cutycapt --url=file://"$PAGE_PATH" --out="$OUT_IMG_PATH"
    mogrify -trim "$OUT_IMG_PATH"
    convert "$OUT_IMG_PATH" -strip -trim "$OUT_IMG_PATH"
    exiftool -overwrite_original -all= "$OUT_IMG_PATH"
fi

PAGE_PATH="$OUT_DIR/params/indent_columns/index.html"
if [ -f "$PAGE_PATH" ]; then
	OUT_IMG_PATH="$OUT_DIR/indent_columns.png"
    cutycapt --url=file://"$PAGE_PATH" --out="$OUT_IMG_PATH"
    mogrify -trim "$OUT_IMG_PATH"
    convert "$OUT_IMG_PATH" -strip -trim "$OUT_IMG_PATH"
    exiftool -overwrite_original -all= "$OUT_IMG_PATH"
fi


## generate small images
"$SCRIPT_DIR"/../generate_small.sh
