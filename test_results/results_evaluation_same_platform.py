# encoding: utf-8

import os
import json
from test_data.ds.loader import all_sentences
from DEFINE import TEST_RESULT_PATH


ALL_RESULTS_PATH = os.path.join(TEST_RESULT_PATH, "ds_x86_all")
VERSIONS = [os.path.join(ALL_RESULTS_PATH, x) for x in os.listdir(ALL_RESULTS_PATH)]


def file_num():
    for v in VERSIONS:
        print(v, len(os.listdir(v)))

file_num()
# 全都是1150

print(len(all_sentences()))
# 总的语料数是1260 相当于每一次跑都是少了110


# 然后检测一下每次少的是否一样 猜测应该是生成的语料本身就有重复 直接去重看一下

print(len(set(all_sentences())))

# 确实，去重后，数量就是1150了，那说明所有的问题都有数据
# 得去评估一下数据重复部分的原因，以及做一些数据的删减 该部分流程到test_data\ds下去查看
