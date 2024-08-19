#!/bin/bash

set -eu


##
## Find PNG files and generate small versions suitable for GitHub readmes.
##


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


#big_suffix="-big."
small_suffix="-small."

found_images=$(find "$SCRIPT_DIR" -name "*.png")
# shellcheck disable=SC2068
for filename in ${found_images[@]}; do
    if [[ $filename == *"$small_suffix"* ]]; then
        continue
    fi
    small_name=${filename/".png"/"${small_suffix}png"}

    ##if [[ $filename != *"$big_suffix"* ]]; then
    ##    continue
    ##fi
    ##small_name=${filename/$big_suffix/$small_suffix}

    echo "converting: $filename -> $small_name"
    convert "$filename" -strip -resize 700 "$small_name"
done
