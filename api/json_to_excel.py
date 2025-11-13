"""
将 test_results.json 转换为 Excel 文件
"""

import json
import os
import pandas as pd


def json_to_excel(json_file: str, excel_file: str = None):
    """
    将 test_results.json 转换为 Excel 文件
    
    Args:
        json_file: JSON 文件路径
        excel_file: 输出的 Excel 文件路径，如果为 None 则自动生成
    """
    # 读取 JSON 文件
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 提取数据
    rows = []
    for item in data:
        row = {
            "title": item.get("title", ""),
            "workflow": item.get("result_workflow", {}).get("workflow", "") if item.get("result_workflow") else "",
            "catalog": item.get("result_workflow", {}).get("catalog", "") if item.get("result_workflow") else "",
            "json": item.get("result_workflow", {}).get("json", "") if item.get("result_workflow") else "",
            "branch": item.get("result_workflow", {}).get("branch", "") if item.get("result_workflow") else "",
            "description": item.get("result_confident", {}).get("description", "") if item.get("result_confident") else ""
        }
        rows.append(row)
    
    # 创建 DataFrame
    df = pd.DataFrame(rows)
    
    # 确定输出文件名
    if excel_file is None:
        base_name = os.path.splitext(json_file)[0]
        excel_file = f"{base_name}.xlsx"
    
    # 写入 Excel
    df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"Excel 文件已生成: {excel_file}")
    print(f"共 {len(rows)} 行数据")


if __name__ == "__main__":
    # 默认使用当前目录下的 test_results.json
    json_file = os.path.join(os.path.dirname(__file__), "test_results.json")
    
    if os.path.exists(json_file):
        json_to_excel(json_file)
    else:
        print(f"错误: 找不到文件 {json_file}")

