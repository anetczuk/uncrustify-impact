#
# Copyright (c) 2023, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
from enum import Enum, unique, auto
from dataclasses import dataclass
from typing import List, Any, Dict

import difflib
import pprint


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@unique
class LineModifier(Enum):
    SAME = auto()
    CHANGED = auto()
    ADDED = auto()
    REMOVED = auto()


@dataclass
class LineState:
    file_name: str
    state: LineModifier

    def is_modifier(self, modifier: LineModifier):
        return self.state == modifier

    def is_same(self):
        return self.state == LineModifier.SAME

    def is_added(self):
        return self.state == LineModifier.ADDED

    def is_modified(self):
        return self.state in (LineModifier.CHANGED, LineModifier.REMOVED)


class LineModifiers:
    def __init__(self):
        self.modifiers: List[LineState] = []

    def is_empty(self) -> bool:
        return not self.modifiers

    def has_modifier(self, modifier: LineModifier):
        for item in self.modifiers:
            if item.is_modifier(modifier):
                return True
        return False

    def has_same(self):
        for item in self.modifiers:
            if item.is_same():
                return True
        return False

    def has_added(self):
        for item in self.modifiers:
            if item.is_added():
                return True
        return False

    def has_modified(self):
        for item in self.modifiers:
            if item.is_modified():
                return True
        return False

    def count_changes(self, label):
        state_set = set()
        for item in self.modifiers:
            if item.file_name != label:
                continue
            if item.state == LineModifier.SAME:
                continue
            state_set.add(item.state)
        return len(state_set)

    def get_modifier_files(self, modifier: LineModifier) -> List[str]:
        ret_list = []
        for item in self.modifiers:
            if item.is_modifier(modifier):
                ret_list.append(item.file_name)
        return ret_list

    def get_modified_files(self) -> List[str]:
        ret_list = []
        for item in self.modifiers:
            if item.is_modified():
                ret_list.append(item.file_name)
        return ret_list

    def add_state(self, label, modifier: LineModifier):
        self.modifiers.append(LineState(label, modifier))

    def to_list_raw(self):
        ret_list = []
        for item in self.modifiers:
            ret_list.append((item.file_name, item.state.name))
        return ret_list

    def to_str(self):
        return pprint.pformat(self.modifiers, indent=4)


class ModifyStream:
    def __init__(self):
        self.modify_list: List[Any] = []

    def add(self, line_number, modifier: LineModifier):
        if modifier == LineModifier.SAME:
            self._append(line_number, modifier)
            return self.flush()

        if modifier == LineModifier.CHANGED:  # "?" question mark
            if len(self.modify_list) == 1:
                # line modification case - question mark line indicating removed content
                # there will be line with question mark indicating added content
                return []
            if len(self.modify_list) != 0:
                # print("modify_list:", self.modify_list)
                raise RuntimeError("invalid state")
            # skip question mark line
            return []
            # line_num = self.modify_list[0][0]
            # self.modify_list.clear()
            # self._append(line_num, modifier)
            # return self.flush()

        if modifier == LineModifier.ADDED:
            if not self.modify_list:
                self._append(line_number, modifier)
                return self.flush()
            prev_mod = self.modify_list[-1]
            if prev_mod[1] == LineModifier.REMOVED:
                # self._append(line_number, modifier)
                # return []
                line_num = prev_mod[0]
                self.modify_list.clear()
                self._append(line_num, LineModifier.CHANGED)
                return self.flush()
            return self._append(line_number, modifier)

        if modifier == LineModifier.REMOVED:
            if not self.modify_list:
                # empty list - wait for next modifier
                self._append(line_number, modifier)
                return []
            ret_list = self.flush()
            self._append(line_number, modifier)
            return ret_list

        raise RuntimeError(f"unknown modifier: {modifier}")

    def flush(self) -> List[Any]:
        ret_list = self.modify_list[:]
        self.modify_list.clear()
        return ret_list

    def _append(self, line_number, modifier: LineModifier):
        self.modify_list.append((line_number, modifier))


class FileState:
    def __init__(self, length):
        self.before: LineModifiers = LineModifiers()
        self.line_state: List[LineModifiers] = []
        for _ in range(0, length):
            self.line_state.append(LineModifiers())
        self._modify_stream = ModifyStream()
        self._line_counter = -1

    def count_changes(self, label):
        counted = self.before.count_changes(label)
        for item in self.line_state:
            counted += item.count_changes(label)
        return counted

    def to_dict_raw(self):
        ret_dict = {}
        ret_dict[-1] = self.before.to_list_raw()
        for index, item in enumerate(self.line_state):
            ret_dict[index] = item.to_list_raw()
        return ret_dict

    def to_dict_modifiers(self) -> Dict[int, LineModifiers]:
        ret_dict = {}
        ret_dict[-1] = self.before
        for index, item in enumerate(self.line_state):
            ret_dict[index] = item
        return ret_dict

    def parse_diff(self, file_name, diff_list):
        ### According to documentation:
        #
        # Each line of a Differ delta begins with a two-letter code:
        #
        #     '- '    line unique to sequence 1
        #     '+ '    line unique to sequence 2
        #     '  '    line common to both sequences
        #     '? '    line not present in either input sequence
        #
        changed = False
        self._line_counter = 0
        for line in diff_list:
            if line.startswith("  "):
                # line the same
                self._line_counter += 1
                self._add_state(file_name, LineModifier.SAME)
                continue
            if line.startswith("+ "):
                # line added
                self._add_state(file_name, LineModifier.ADDED)
                changed = True
                continue
            if line.startswith("- "):
                # line removed
                self._line_counter += 1
                self._add_state(file_name, LineModifier.REMOVED)
                changed = True
                continue
            if line.startswith("? "):
                # line modified
                # self._line_counter += 1
                self._add_state(file_name, LineModifier.CHANGED)
                changed = True
                continue
            raise RuntimeError("unknown marker")
        self._end_diff()
        return changed

    def _add_state(self, label, modifier):
        if self._line_counter == 0 and modifier == LineModifier.ADDED:
            line_state: LineModifiers = self._get_modifier_item(self._line_counter)
            line_state.add_state(label, modifier)
            return

        modify_list = self._modify_stream.add(self._line_counter, modifier)
        for item in modify_list:
            item_line = item[0]
            item_modify = item[1]
            line_state: LineModifiers = self._get_modifier_item(item_line)
            line_state.add_state(label, item_modify)
            self._line_counter = item_line

    def _end_diff(self):
        pass

    def _get_modifier_item(self, line_number) -> LineModifiers:
        if line_number == 0:
            return self.before
        return self.line_state[line_number - 1]


class Changes:
    def __init__(self, file_name, base_lines):
        self.base_file_name = file_name
        self.base_lines = base_lines
        file_length = len(base_lines)
        self.file_state = FileState(file_length)

    def get_content_line(self, line_index):
        return self.base_lines[line_index]

    def count_changes(self, label):
        return self.file_state.count_changes(label)

    def add_diff(self, file_name, content_lines):
        ## checks whole file
        diff_list = self.calculate_diff(content_lines)

        ## does not compare whole file
        # diff = difflib.context_diff( file1_text, file2_text,
        #                              fromfile = 'file1.txt',
        #                              tofile='file2.txt',
        #                              lineterm='')

        ## does not compare whole file
        # diff = difflib.unified_diff( file1_text, file2_text,
        #                              fromfile = 'file1.txt',
        #                              tofile='file2.txt',
        #                              n=0)

        return self.file_state.parse_diff(file_name, diff_list)

    def to_dict_raw(self):
        return self.file_state.to_dict_raw()

    def to_list_raw(self, removed_as_changed=False, do_not_repeat=True):
        changes_dict = self.to_dict_modifiers()

        ret_list = []

        # item: LineModifiers
        for index, item in changes_dict.items():
            if item.is_empty():
                continue

            line_content = self.get_content_line(index)

            appended = False

            if removed_as_changed is False:
                changed_files = item.get_modifier_files(LineModifier.CHANGED)
                if changed_files:
                    if do_not_repeat:
                        changed_files = set(changed_files)
                        changed_files = list(changed_files)
                    changed_files.sort()
                    ret_list.append((index + 1, line_content, LineModifier.CHANGED, changed_files))
                    appended = True

                removed_files = item.get_modifier_files(LineModifier.REMOVED)
                if removed_files:
                    if do_not_repeat:
                        removed_files = set(removed_files)
                        removed_files = list(removed_files)
                    removed_files.sort()
                    ret_list.append((index + 1, line_content, LineModifier.REMOVED, removed_files))
                    appended = True
            else:
                modified_files = item.get_modified_files()
                if modified_files:
                    if do_not_repeat:
                        modified_files = set(modified_files)
                        modified_files = list(modified_files)
                    modified_files.sort()
                    ret_list.append((index + 1, line_content, LineModifier.CHANGED, modified_files))
                    appended = True

            added_files = item.get_modifier_files(LineModifier.ADDED)
            if added_files:
                if do_not_repeat:
                    added_files = set(added_files)
                    added_files = list(added_files)
                added_files.sort()
                if item.has_modifier(LineModifier.SAME):
                    if not ret_list or ret_list[-1][0] != index + 1:
                        # add "same" if there is no modification of the same line
                        ret_list.append((index + 1, line_content, LineModifier.SAME, None))
                ret_list.append((None, "", LineModifier.ADDED, added_files))
                appended = True

            if appended:
                continue

            if item.has_modifier(LineModifier.SAME):
                ret_list.append((index + 1, line_content, LineModifier.SAME, None))
                continue

            raise RuntimeError(f"invalid state - unhandled case: {index}: {item.to_str()}")

        return ret_list

    def to_dict_modifiers(self) -> Dict[int, LineModifiers]:
        return self.file_state.to_dict_modifiers()

    def print_diff_raw(self, content_lines):
        diff_list = self.calculate_diff(content_lines)
        for index, line in enumerate(diff_list):
            print(f"{index} >{line}", end="")

    def print_diff(self, nice=True):
        data_dict = self.file_state.to_dict_raw()
        if nice:
            out = pprint.pformat(data_dict, indent=4)
            print(out)
        else:
            print(data_dict)

    def calculate_diff(self, content_lines):
        diff = difflib.ndiff(self.base_lines, content_lines)
        return list(diff)
