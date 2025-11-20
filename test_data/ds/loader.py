# encoding: utf-8

import os
from multiprocessing.reduction import duplicate

import pandas as pd



def all_sentences():

    out = []

    path = os.path.dirname(__file__)
    for _ in os.listdir(path):
        if _.endswith('.csv'):
            raw = pd.read_csv(os.path.join(path, _))
            out.extend(raw['测试数据内容'].dropna().tolist())

    return out


def sentences(_type: str):
    """

    Args:
        _type: one of
        ['control_ds.csv', 'evaluation_ds.csv', 'optimization_ds.csv', 'prediction_ds.csv', 'simulation_ds.csv', 'statistic_ds.csv']
    Returns:

    """
    raw = pd.read_csv(os.path.join(os.path.dirname(__file__), _type))
    return raw['测试数据内容'].dropna().tolist()


def same_sentence_analyze(_type: str):
    """

    Args:
        _type: with sentences

    Returns:

    """
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), _type))
    duplicate_rows = df[df.duplicated(subset='测试数据内容', keep=False)]

    duplicate_rows_sorted = duplicate_rows.sort_values('测试数据内容')

    print(duplicate_rows_sorted)



if __name__ == "__main__":
    # print(len(all_sentences()))
    # print(len(set(all_sentences())))
    # for _ in ['control_ds.csv', 'evaluation_ds.csv', 'optimization_ds.csv', 'prediction_ds.csv', 'simulation_ds.csv', 'statistic_ds.csv']:
    #     data = sentences(_)
    #     print(
    #         _,
    #         len(data),
    #         len(set(data))
    #     )
    same_sentence_analyze('optimization_ds.csv')
