#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


SRC_DIR="$SCRIPT_DIR/../src"


generate_help() {
    HELP_PATH=$SCRIPT_DIR/cmdargs.md
    echo "" > ${HELP_PATH}

    COMMAND="python3 -m uncrustimpact"
    COMMAND_TEXT="python3 -m uncrustimpact"

    echo "## <a name=\"main_help\"></a> $COMMAND_TEXT --help" > ${HELP_PATH}
    echo -e "\`\`\`" >> ${HELP_PATH}

    cd $SRC_DIR
    $COMMAND --help >> ${HELP_PATH}

    echo -e "\`\`\`" >> ${HELP_PATH}


    tools=$($COMMAND --listtools)

    IFS=', ' read -r -a tools_list <<< "$tools"

    for item in ${tools_list[@]}; do
        echo $item
        echo -e "\n\n" >> ${HELP_PATH}
        echo "## <a name=\"${item}_help\"></a> $COMMAND_TEXT $item --help" >> ${HELP_PATH}
        echo -e "\`\`\`" >> ${HELP_PATH}
        $COMMAND $item --help >> ${HELP_PATH}
        echo -e "\`\`\`"  >> ${HELP_PATH}
    done
}


generate_help


$SCRIPT_DIR/generate_small.sh
