# encoding: utf-8

"""
根据匹配结果进行UI截图模块（手动确认模式）
读取matched_workflows_{timestamp}.csv文件，遍历显示信息，等待用户确认后截图并更新数据库
"""

import os
import sys
import time
import json
import csv
from typing import List, Dict, Optional
from printscreen import screenshot_with_mss

# 添加 api 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from workflow_db import WorkflowDB


# 全局变量
db = WorkflowDB()


def normalize_json_string(json_str: str) -> str:
    """
    标准化JSON字符串格式（处理CSV中的双引号转义）
    
    Args:
        json_str: 原始JSON字符串（可能包含CSV转义）
    
    Returns:
        标准化后的JSON字符串
    """
    try:
        # CSV中的JSON字符串可能包含双引号转义，先解析JSON
        parsed = json.loads(json_str)
        # 重新序列化为标准格式
        normalized = json.dumps(parsed, ensure_ascii=False, sort_keys=False)
        return normalized
    except json.JSONDecodeError:
        # 如果解析失败，直接返回原字符串
        return json_str


def load_matched_workflows(file_path: str) -> List[Dict]:
    """
    加载匹配结果文件（支持CSV和TXT格式）
    
    Args:
        file_path: 匹配结果文件路径
    
    Returns:
        匹配结果列表
    """
    results = []
    
    if not os.path.exists(file_path):
        print(f"✗ 文件不存在: {file_path}")
        return results
    
    # 根据文件扩展名选择解析方式
    if file_path.lower().endswith('.csv'):
        # CSV格式
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    title = row.get('title', '').strip()
                    workflow_json_raw = row.get('workflow_json', '').strip()
                    catalog = row.get('catalog', '').strip()
                    
                    if not title or not workflow_json_raw or not catalog:
                        continue
                    
                    # 标准化JSON字符串
                    workflow_json = normalize_json_string(workflow_json_raw)
                    
                    results.append({
                        "title": title,
                        "workflow_json": workflow_json,
                        "catalog": catalog
                    })
        except Exception as e:
            print(f"✗ 读取CSV文件失败: {e}")
            return results
    else:
        # TXT格式（制表符分隔）
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 跳过表头
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 3:
                    results.append({
                        "title": parts[0],
                        "workflow_json": parts[1],
                        "catalog": parts[2]
                    })
    
    return results


def take_screenshot(catalog: str, filename: str) -> Optional[str]:
    """
    进行截图（用户已手动定位到正确的页面）
    
    Args:
        catalog: 分类
        filename: 文件名
    
    Returns:
        截图保存路径，失败返回None
    """
    try:
        # 确保目录存在
        picture_dir = os.path.join(os.path.dirname(__file__), "picture", catalog)
        os.makedirs(picture_dir, exist_ok=True)
        
        # 截图（使用固定的截图区域）
        save_path = os.path.join(picture_dir, filename)
        screenshot_with_mss(region=(2300, 500, 1485, 1400), save_path=save_path)
        print(f"  ✓ 截图已保存: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"  ✗ 截图出错: {e}")
        return None


def get_items_from_collected_results(workflow_json: str) -> List[str]:
    """
    从collected_results.json获取items
    
    Args:
        workflow_json: 标准化的workflow JSON字符串
    
    Returns:
        items列表
    """
    json_path = os.path.join(os.path.dirname(__file__), "collected_results.json")
    items = []
    
    if not os.path.exists(json_path):
        return items
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            collected_data = json.load(f)
            
            # 尝试直接匹配
            if workflow_json in collected_data:
                items = collected_data[workflow_json].get('items', [])
            else:
                # 如果直接匹配失败，尝试标准化匹配
                # collected_results.json中的key可能是原始格式，需要标准化后比较
                normalized_key = None
                for key in collected_data.keys():
                    try:
                        normalized_key_candidate = normalize_json_string(key)
                        if normalized_key_candidate == workflow_json:
                            normalized_key = key
                            break
                    except:
                        continue
                
                if normalized_key:
                    items = collected_data[normalized_key].get('items', [])
    
    except Exception as e:
        print(f"  ⚠ 读取collected_results.json失败: {e}")
    
    return items


def print_workflow_info(result: Dict, idx: int, total: int):
    """
    打印workflow信息
    
    Args:
        result: workflow记录
        idx: 当前索引
        total: 总数
    """
    print("\n" + "=" * 80)
    print(f"第 {idx}/{total} 条记录")
    print("=" * 80)
    print(f"Title: {result['title']}")
    print(f"Catalog: {result['catalog']}")
    print(f"Workflow JSON:")
    
    # 尝试格式化打印JSON，使其更易读
    workflow_json = result['workflow_json']
    try:
        # 解析JSON并格式化打印
        parsed_json = json.loads(workflow_json)
        formatted_json = json.dumps(parsed_json, ensure_ascii=False, indent=2)
        print(formatted_json)
    except:
        # 如果解析失败，直接打印原始字符串
        print(workflow_json)
    
    print("=" * 80)


def main(matched_file: str = None):
    """
    主函数
    
    Args:
        matched_file: 匹配结果文件路径，如果为None则查找最新的文件
    """
    print("=" * 80)
    print("Workflow截图模块（手动确认模式）")
    print("=" * 80)
    print("\n使用说明:")
    print("  1. 脚本会遍历CSV文件中的每条记录")
    print("  2. 显示title、catalog、workflow_json信息")
    print("  3. 请在浏览器中查看当前会话的workflow是否匹配")
    print("  4. 输入 1 表示需要截图存档，输入 0 表示跳过")
    print("  5. 输入 q 退出程序")
    print("=" * 80)
    
    # 1. 查找匹配结果文件
    if matched_file is None:
        # 查找最新的matched_workflows文件（支持CSV和TXT格式）
        tool_dir = os.path.dirname(__file__)
        matched_files = [
            f for f in os.listdir(tool_dir)
            if f.startswith("matched_workflows_") and (f.endswith(".csv") or f.endswith(".txt"))
        ]
        
        if not matched_files:
            print("\n✗ 未找到匹配结果文件")
            print("  请先运行 workflow_async_check.py 生成匹配结果文件")
            return
        
        # 按修改时间排序，取最新的
        matched_files.sort(key=lambda x: os.path.getmtime(os.path.join(tool_dir, x)), reverse=True)
        matched_file = os.path.join(tool_dir, matched_files[0])
        print(f"\n使用最新的匹配结果文件: {matched_files[0]}")
    else:
        if not os.path.exists(matched_file):
            print(f"\n✗ 文件不存在: {matched_file}")
            return
    
    # 2. 加载匹配结果
    print(f"\n正在加载匹配结果: {matched_file}")
    matched_results = load_matched_workflows(matched_file)
    
    if not matched_results:
        print("✗ 未找到匹配结果")
        return
    
    print(f"✓ 共加载 {len(matched_results)} 条匹配记录")
    
    # 3. 检查数据库，过滤已存在的记录
    print("\n正在检查数据库中已存在的workflow...")
    workflows_to_process = []
    skipped_count = 0
    
    for result in matched_results:
        existing = db.get_workflow_by_json(result['workflow_json'])
        if existing is None:
            workflows_to_process.append(result)
        else:
            skipped_count += 1
    
    print(f"  需要处理: {len(workflows_to_process)} 条")
    print(f"  已存在（跳过）: {skipped_count} 条")
    
    if not workflows_to_process:
        print("\n✓ 所有workflow都已存在于数据库中！")
        return
    
    # 4. 开始处理
    print("\n" + "=" * 80)
    print("开始处理，请准备好浏览器...")
    print("=" * 80)
    
    input("\n按回车键开始处理...")
    
    success_count = 0
    skipped_by_user = 0
    
    for idx, result in enumerate(workflows_to_process, 1):
        # 打印信息
        print_workflow_info(result, idx, len(workflows_to_process))
        
        # 等待用户输入
        while True:
            user_input = input("\n请确认是否需要截图存档 (1=是, 0=跳过, q=退出): ").strip().lower()
            
            if user_input == 'q':
                print("\n用户退出程序")
                print(f"\n处理统计:")
                print(f"  已处理: {idx - 1} 条")
                print(f"  成功截图: {success_count} 条")
                print(f"  用户跳过: {skipped_by_user} 条")
                return
            elif user_input == '1':
                # 需要截图存档
                # 获取下一个可用的ID
                next_id = db.get_next_id(result['catalog'])
                print(f"\n  下一个ID: {next_id}")
                
                # 等待用户准备好页面
                input("  请在浏览器中定位到正确的workflow页面，然后按回车开始截图...")
                
                # 截图
                screenshot_path = take_screenshot(result['catalog'], next_id)
                
                if screenshot_path:
                    # 从collected_results.json获取items
                    items = get_items_from_collected_results(result['workflow_json'])
                    
                    # 更新数据库
                    db.add_workflow(next_id, result['workflow_json'], result['catalog'], items)
                    print(f"  ✓ 已更新数据库: {next_id}")
                    success_count += 1
                else:
                    print(f"  ✗ 截图失败，未更新数据库")
                
                break
            elif user_input == '0':
                # 跳过
                print("  ⏭ 已跳过")
                skipped_by_user += 1
                break
            else:
                print("  ⚠ 无效输入，请输入 1、0 或 q")
    
    # 5. 显示统计信息
    print("\n" + "=" * 80)
    print("处理完成！")
    print("=" * 80)
    print(f"总计: {len(workflows_to_process)} 条")
    print(f"成功截图: {success_count} 条")
    print(f"用户跳过: {skipped_by_user} 条")
    print("=" * 80)


if __name__ == "__main__":
    # 直接设置参数
    matched_file = "matched_workflows_20251123_105807.csv"  # 匹配结果文件路径，None表示使用最新的文件
    
    main(matched_file=matched_file)
