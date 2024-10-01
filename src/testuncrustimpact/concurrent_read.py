#!/usr/bin/env python3
#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

from multiprocessing import Pool
import tempfile

import random
import string


def read_file(file_path, proc_id, num_times):
    print(f"process {proc_id} started")
    for _ in range(0, num_times):
        with open(file_path, "r", encoding="utf-8") as in_file:
            in_file.readlines()
    print(f"process {proc_id} finished")


def main():
    with tempfile.NamedTemporaryFile() as temp_file:
        file_path = temp_file.name
        print("generating random file", file_path)
        with open(file_path, "w", encoding="utf-8") as out_file:
            content = "".join(random.choices(string.ascii_letters, k=1024 * 1024))  # initializing size of string
            out_file.write(content)

        print("starting pool")
        with Pool() as process_pool:
            result_queue = []

            for i in range(0, 10):
                async_result = process_pool.apply_async(read_file, [file_path, i, 100])
                result_queue.append(async_result)

            for async_result in result_queue:
                async_result.get()

            print("pool finished")


if __name__ == "__main__":
    main()
