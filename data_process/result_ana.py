# encoding: utf-8

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import json

from DEFINE import TEST_RESULT_PATH
from data_process.formatter import conversation_analyze


def main():

    for index, file in enumerate(os.listdir(TEST_RESULT_PATH)):
        data = json.load(open(os.path.join(TEST_RESULT_PATH, file), "r", encoding="utf-8"))
        try:
            ana = conversation_analyze(data)
            print(f"[INDEX {index}]", "~" * 30)
            print(ana)
        except Exception as e:
            print(file, e)


main()