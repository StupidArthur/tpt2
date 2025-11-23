# encoding: utf-8
"""
检查CSV文件中的workflow JSON是否在数据库中存在

该模块用于：
1. 读取matched_workflows_*.csv文件
2. 解析CSV中的JSON字符串（处理CSV的双引号转义）
3. 标准化JSON格式以便与数据库比较
4. 使用get_workflow_by_json检查是否存在于数据库中
"""

import os
import csv
import json
from typing import List, Dict, Optional, Tuple
from workflow_db import WorkflowDB


def normalize_json_string(json_str: str) -> Optional[str]:
    """
    标准化JSON字符串格式
    
    CSV中的JSON格式问题：
    1. CSV使用双引号转义（""）来表示一个双引号
    2. JSON字符串内部还有转义的引号（\"）
    
    处理步骤：
    1. 先解析CSV转义（"" -> "）
    2. 解析JSON字符串
    3. 重新序列化为标准格式
    
    Args:
        json_str: 原始JSON字符串（可能包含CSV转义）
    
    Returns:
        标准化后的JSON字符串，如果解析失败返回None
    """
    try:
        # 步骤1: CSV转义处理 - CSV中的双引号转义（""）需要先处理
        # 但Python的csv.reader已经自动处理了，所以这里直接解析JSON
        
        # 步骤2: 解析JSON字符串
        parsed = json.loads(json_str)
        
        # 步骤3: 重新序列化为标准格式（确保格式一致）
        normalized = json.dumps(parsed, ensure_ascii=False, sort_keys=False)
        
        return normalized
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON解析失败: {e}")
        print(f"    原始字符串: {json_str[:200]}...")
        return None
    except Exception as e:
        print(f"  ✗ 标准化失败: {e}")
        return None


def load_csv_workflows(csv_path: str) -> List[Dict]:
    """
    从CSV文件加载workflow数据
    
    Args:
        csv_path: CSV文件路径
    
    Returns:
        workflow记录列表，每个记录包含title, workflow_json, catalog
    """
    workflows = []
    
    if not os.path.exists(csv_path):
        print(f"✗ CSV文件不存在: {csv_path}")
        return workflows
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('title', '').strip()
                workflow_json_raw = row.get('workflow_json', '').strip()
                catalog = row.get('catalog', '').strip()
                
                if not workflow_json_raw:
                    print(f"  ⚠ 跳过空JSON: {title[:50]}...")
                    continue
                
                # 标准化JSON字符串
                normalized_json = normalize_json_string(workflow_json_raw)
                
                if normalized_json:
                    workflows.append({
                        'title': title,
                        'workflow_json': normalized_json,
                        'workflow_json_raw': workflow_json_raw,  # 保留原始格式用于调试
                        'catalog': catalog
                    })
                else:
                    print(f"  ⚠ 跳过无效JSON: {title[:50]}...")
    
    except Exception as e:
        print(f"✗ 读取CSV文件失败: {e}")
    
    return workflows


def check_workflows_in_db(csv_path: str, db: WorkflowDB = None) -> Tuple[List[Dict], List[Dict]]:
    """
    检查CSV中的workflow是否在数据库中存在
    
    Args:
        csv_path: CSV文件路径
        db: WorkflowDB实例，如果为None则创建新实例
    
    Returns:
        (已存在的workflow列表, 不存在的workflow列表)
    """
    if db is None:
        db = WorkflowDB()
    
    # 加载CSV数据
    print(f"正在加载CSV文件: {csv_path}")
    csv_workflows = load_csv_workflows(csv_path)
    print(f"✓ 共加载 {len(csv_workflows)} 条记录\n")
    
    if not csv_workflows:
        print("✗ CSV文件中没有有效数据")
        return [], []
    
    # 检查每个workflow
    found_workflows = []
    not_found_workflows = []
    
    print("正在检查数据库...")
    print("=" * 80)
    
    for idx, wf in enumerate(csv_workflows, 1):
        title = wf['title']
        workflow_json = wf['workflow_json']
        catalog = wf['catalog']
        
        print(f"\n[{idx}/{len(csv_workflows)}] {title[:60]}...")
        print(f"  Catalog: {catalog}")
        
        # 检查数据库中是否存在
        existing = db.get_workflow_by_json(workflow_json)
        
        if existing:
            print(f"  ✓ 已存在于数据库: {existing['id']}")
            found_workflows.append({
                'title': title,
                'workflow_json': workflow_json,
                'catalog': catalog,
                'db_id': existing['id'],
                'db_record': existing
            })
        else:
            print(f"  ✗ 不存在于数据库")
            not_found_workflows.append({
                'title': title,
                'workflow_json': workflow_json,
                'workflow_json_raw': wf.get('workflow_json_raw', ''),
                'catalog': catalog
            })
    
    print("\n" + "=" * 80)
    print(f"\n检查完成:")
    print(f"  总计: {len(csv_workflows)} 条")
    print(f"  已存在: {len(found_workflows)} 条")
    print(f"  不存在: {len(not_found_workflows)} 条")
    
    return found_workflows, not_found_workflows


def export_not_found_to_csv(not_found_workflows: List[Dict], output_path: str = None):
    """
    将不存在的workflow导出到CSV文件
    
    Args:
        not_found_workflows: 不存在的workflow列表
        output_path: 输出文件路径，如果为None则自动生成
    """
    if not not_found_workflows:
        print("\n所有workflow都已存在于数据库中，无需导出")
        return
    
    if output_path is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(os.path.dirname(__file__), f"not_found_in_db_{timestamp}.csv")
    
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'workflow_json', 'catalog'])
            
            for wf in not_found_workflows:
                writer.writerow([
                    wf['title'],
                    wf['workflow_json'],
                    wf['catalog']
                ])
        
        print(f"\n✓ 已导出不存在的workflow到: {output_path}")
    except Exception as e:
        print(f"\n✗ 导出失败: {e}")


def main():
    """主函数"""
    import glob
    
    print("=" * 80)
    print("CSV Workflow 数据库检查工具")
    print("=" * 80)
    
    # 查找最新的matched_workflows CSV文件
    tool_dir = os.path.dirname(__file__)
    csv_files = glob.glob(os.path.join(tool_dir, "matched_workflows_*.csv"))
    
    if not csv_files:
        print("✗ 未找到matched_workflows_*.csv文件")
        print(f"  请确保CSV文件在目录: {tool_dir}")
        return
    
    # 按修改时间排序，取最新的
    csv_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_csv = csv_files[0]
    
    print(f"\n使用CSV文件: {os.path.basename(latest_csv)}")
    
    # 检查workflow
    db = WorkflowDB()
    found_workflows, not_found_workflows = check_workflows_in_db(latest_csv, db)
    
    # 导出不存在的workflow
    if not_found_workflows:
        export_not_found_to_csv(not_found_workflows)
    
    # 显示统计信息
    if found_workflows:
        print("\n已存在的workflow统计（按catalog）:")
        catalog_count = {}
        for wf in found_workflows:
            catalog = wf['catalog']
            catalog_count[catalog] = catalog_count.get(catalog, 0) + 1
        
        for catalog, count in sorted(catalog_count.items()):
            print(f"  {catalog}: {count} 条")
    
    if not_found_workflows:
        print("\n不存在的workflow统计（按catalog）:")
        catalog_count = {}
        for wf in not_found_workflows:
            catalog = wf['catalog']
            catalog_count[catalog] = catalog_count.get(catalog, 0) + 1
        
        for catalog, count in sorted(catalog_count.items()):
            print(f"  {catalog}: {count} 条")


if __name__ == "__main__":
    main()

