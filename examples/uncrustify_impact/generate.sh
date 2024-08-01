#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


uncrustify -c $SCRIPT_DIR/override.cfg --update-config-with-doc > $SCRIPT_DIR/config.cfg

$SCRIPT_DIR/../../src/uncrustifyimpact.py impact --file $SCRIPT_DIR/example.cpp \
												 --config $SCRIPT_DIR/config.cfg \
												 --outputdir $SCRIPT_DIR/impact \
												 --randomseed 0 \
												 --ignoreparams cmt_width cmt_cpp_to_c nl_max code_width indent_cmt_with_tabs \
												 						  indent_columns sp_before_tr_emb_cmt sp_before_semi \
												 						  nl_before_func_body_def nl_func_type_name \
												 						  indent_sing_line_comments indent_braces \
												 						  sp_cmt_cpp_start nl_remove_extra_newlines \
												 						  nl_return_expr pos_arith \
												 						  nl_end_of_file