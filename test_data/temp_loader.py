# encoding: utf-8

import os
import json
import pandas as pd
from data_process.formatter import conversation_analyze



def all_sentences():

    path = os.path.join(os.path.dirname(__file__), "锅炉.csv")
    df = pd.read_csv(path)
    return df['测试数据内容'].dropna().tolist()


def main():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "锅炉.csv"))
    with open(os.path.join(os.path.dirname(__file__), "guolu.json"), "r", encoding='utf-8') as f:
        result = json.load(f)
    standard = result.get("为了提高效率，我想实现锅炉回路的自动运行调整，能否帮我设计控制方案？")

    for idx, row in df.iterrows():

        name = row['测试数据内容']
        answer = result.get(name)

        df.loc[idx, '测试结果'] = '相同' if answer[1] == standard[1] and answer[2] == standard[2] else "不相同"

    df.to_csv(os.path.join(os.path.dirname(__file__), "锅炉结果.csv"), index=False, encoding='utf-8-sig')





if __name__ == "__main__":
    # print(all_sentences())
    # print(len(all_sentences()), len(set(all_sentences())))
    main()