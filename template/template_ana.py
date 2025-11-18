# encoding: utf-8

import os
import json
from tokenize import endpats

with open("all_ds.json", "r", encoding="utf-8") as f:
    data_ds = json.load(f)

with open("all_with_name.json", "r", encoding="utf-8") as f:
    data_all = json.load(f)


# c1, c2 = 0, 0
# for k, v in data_all.items():
#     if data_ds.get(k):
#         c1 += 1
#     else:
#         c2 += 1
#         print(v['items'][0])
#
# print(c1, c2)
#
#
# print(len(data_all))

# for k, v in data_ds.items():
#     print(v['items'][0])


tree = {}

for k, v in data_ds.items():
    catalog = v['catalog']
    if not tree.get(catalog):
        tree[catalog] = {k: v}
    else:
        tree[catalog][k] = v


for k, v in tree.items():
    print(k, len(v))
    for kk, vv in v.items():
        print(vv['items'][0])