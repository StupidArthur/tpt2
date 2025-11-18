# encoding: utf-8

import os
import pandas as pd



def all_sentences():

    out = []

    path = os.path.dirname(__file__)
    for _ in os.listdir(path):
        if _.endswith('.csv'):
            raw = pd.read_csv(os.path.join(path, _))
            out.extend(raw['测试数据内容'].dropna().tolist())

    return out


if __name__ == "__main__":
    print(len(all_sentences()))
    print(len(set(all_sentences())))
