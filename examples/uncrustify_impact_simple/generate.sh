#!/bin/bash

set -eu


## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


echo "running example uncrustify_impact_simple"


OUT_DIR="$SCRIPT_DIR/impact"

rm -fr "$OUT_DIR"


uncrustify -c $SCRIPT_DIR/override.cfg --update-config-with-doc > $SCRIPT_DIR/config.cfg


cd $SCRIPT_DIR/../../src/

python3 -m uncrustimpact impact --file $SCRIPT_DIR/example.cpp \
								--config $SCRIPT_DIR/config.cfg \
								--outputdir $OUT_DIR \
								--considerparams align_assign_span align_left_shift align_on_tabstop cmt_cpp_to_c \
												 indent_braces indent_cmt_with_tabs indent_sing_line_comments \
												 indent_single_newlines indent_with_tabs mod_add_long_function_closebrace_comment \
												 mod_paren_on_return nl_before_func_body_def nl_end_of_file nl_fdef_brace \
												 nl_fdef_brace_cond nl_func_call_paren nl_func_call_start nl_func_def_empty \
												 nl_func_def_paren nl_func_def_paren_empty nl_func_type_name nl_max nl_max_blank_in_func \
												 nl_remove_extra_newlines nl_return_expr pos_arith pos_assign pos_comma \
												 sp_after_assign sp_after_comma sp_arith sp_assign sp_before_assign sp_before_comma \
												 sp_before_semi sp_before_tr_emb_cmt sp_cmt_cpp_start sp_func_call_paren \
												 sp_func_def_paren sp_func_def_paren_empty sp_inside_fparen sp_inside_fparens align_asm_colon


result=$(checklink -r -q $OUT_DIR/index.html)
if [[ "$result" != "" ]]; then
	echo "broken links found:"
	echo $result
	exit 1
fi
# else: # empty string - no errors
echo "no broken links found"


## generate image from html
if [ -f "$OUT_DIR/example_cpp/index.html" ]; then
    cutycapt --url=file://$OUT_DIR/example_cpp/index.html --out=$OUT_DIR/index.png
    convert "$OUT_DIR/index.png" -strip -trim "$OUT_DIR/index.png"
fi

if [ -f "$OUT_DIR/example_cpp/params/cmt_cpp_to_c.html" ]; then
    cutycapt --url=file://$OUT_DIR/example_cpp/params/cmt_cpp_to_c.html --out=$OUT_DIR/cmt_cpp_to_c.png
    convert "$OUT_DIR/cmt_cpp_to_c.png" -strip -trim "$OUT_DIR/cmt_cpp_to_c.png"
fi


## generate small images
$SCRIPT_DIR/../generate_small.sh
