"""
将 test_results.json 转换为 YAML 格式的结果验证模板
按照 catalog -> (json+branch) -> [title, confidence] 的结构组织数据
"""

import json
import os
import yaml


def json_to_yaml_template(json_file: str, yaml_file: str = None):
    """
    将 test_results.json 转换为 YAML 格式的结果验证模板
    
    Args:
        json_file: JSON 文件路径
        yaml_file: 输出的 YAML 文件路径，如果为 None 则自动生成
    """
    # 读取 JSON 文件
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 构建结果字典
    result_dict = {}
    
    for item in data:
        # 提取关键信息
        title = item.get("title", "")
        catalog = item.get("result_workflow", {}).get("catalog", "") if item.get("result_workflow") else ""
        json_str = item.get("result_workflow", {}).get("json", "") if item.get("result_workflow") else ""
        branch_str = item.get("result_workflow", {}).get("branch", "") if item.get("result_workflow") else ""
        confidence = item.get("result_confident", {}).get("description", "") if item.get("result_confident") else ""
        
        # 如果缺少关键信息，跳过
        if not catalog or not json_str or not branch_str:
            continue
        
        # 构建结果项
        result_item = {
            "title": title,
            "confidence": confidence
        }
        
        # 构建嵌套结构
        if catalog not in result_dict:
            result_dict[catalog] = []
        
        # 查找是否已存在相同的 json+branch 组合
        found = False
        for json_branch_item in result_dict[catalog]:
            if json_branch_item.get("json") == json_str and json_branch_item.get("branch") == branch_str:
                json_branch_item["items"].append(result_item)
                found = True
                break
        
        # 如果不存在，创建新的 json+branch 组合
        if not found:
            json_branch_item = {
                "json": json_str,
                "branch": branch_str,
                "items": [result_item]
            }
            result_dict[catalog].append(json_branch_item)
    
    # 确定输出文件名
    if yaml_file is None:
        base_name = os.path.splitext(json_file)[0]
        yaml_file = f"{base_name}_template.yaml"
    
    # 写入 YAML 文件
    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(result_dict, f, allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2)
    
    print(f"YAML 模板文件已生成: {yaml_file}")
    print(f"共 {len(data)} 条原始数据")
    print(f"共 {len(result_dict)} 个 catalog 分类")
    
    # 统计每个分类下的条目数
    total_items = 0
    for catalog, json_branch_list in result_dict.items():
        catalog_items = sum(len(item.get("items", [])) for item in json_branch_list)
        total_items += catalog_items
        print(f"  - {catalog}: {len(json_branch_list)} 个分支组合, {catalog_items} 个测试用例")
    
    print(f"总计: {total_items} 个测试用例")


if __name__ == "__main__":
    # 默认使用当前目录下的 test_results.json
    json_file = os.path.join(os.path.dirname(__file__), "test_results.json")
    
    if os.path.exists(json_file):
        json_to_yaml_template(json_file)
    else:
        print(f"错误: 找不到文件 {json_file}")

