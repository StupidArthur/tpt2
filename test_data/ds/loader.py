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


def merge_all_csvs(output_file: str = None):
    """
    合并所有CSV文件，在左侧添加一列显示文件名
    
    Args:
        output_file: 输出文件路径，如果为None则不保存，只返回DataFrame
    
    Returns:
        pd.DataFrame: 合并后的DataFrame
    """
    path = os.path.dirname(__file__)
    all_dfs = []
    
    # 读取所有CSV文件
    for filename in os.listdir(path):
        if filename.endswith('.csv'):
            file_path = os.path.join(path, filename)
            df = pd.read_csv(file_path)
            
            # 在左侧添加文件名列
            df.insert(0, '文件名', filename)
            
            all_dfs.append(df)
    
    # 合并所有DataFrame
    merged_df = pd.concat(all_dfs, ignore_index=True)
    
    # 如果指定了输出文件，则保存
    if output_file:
        merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"合并完成，已保存到: {output_file}")
        print(f"总共 {len(merged_df)} 行数据，来自 {len(all_dfs)} 个CSV文件")
    
    return merged_df



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
    # same_sentence_analyze('optimization_ds.csv')
    
    # 合并所有CSV文件示例
    # 方式1：保存到文件
    merge_all_csvs(os.path.join(os.path.dirname(__file__), 'merged_all.csv'))
    
    # 方式2：只返回DataFrame，不保存
    # merged_df = merge_all_csvs()
    # print(f"合并后的DataFrame形状: {merged_df.shape}")
    # print(merged_df.head())
