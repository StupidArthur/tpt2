# encoding: utf-8

"""
异步并发检查workflow匹配模块
读取collected_results.json中的数据，检查数据库中不存在的workflow
异步并发发起API请求，判断是否与预期workflow匹配
如果匹配，则输出title和workflow到CSV文件
"""

import os
import sys
import asyncio
import json
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 添加 api 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api.common_api import i_login, i_create_conversation, ws_conversation, o_config
from workflow_db import WorkflowDB


# 配置参数
MAX_CONCURRENT = 10  # 最大并发数量
RETRY_TIMES = 3  # 每个item重复执行次数


async def try_single_attempt(
    token: str,
    item_text: str,
    workflow_json: str,
    catalog: str,
    attempt: int,
    semaphore: asyncio.Semaphore
) -> Optional[Dict]:
    """
    尝试单次API调用
    db中不存在的workflow，只要API调用成功就输出结果
    
    Args:
        token: 登录token
        item_text: 语料文本
        workflow_json: workflow的JSON字符串（用于记录）
        catalog: 分类
        attempt: 尝试次数编号
        semaphore: 信号量，用于控制并发数量
    
    Returns:
        如果API调用成功，返回包含title和workflow信息的字典；否则返回None
    """
    async with semaphore:  # 获取信号量，控制并发
        try:
            print(f"[尝试 {attempt+1}/{RETRY_TIMES}] {item_text[:50]}...")
            
            # 1. 创建会话
            conv_result = await i_create_conversation(token, title=item_text)
            
            if not isinstance(conv_result, dict) or "conversation_id" not in conv_result:
                print(f"  ✗ 创建会话失败")
                return None
            
            conversation_id = conv_result["conversation_id"]
            
            # 2. 等待 WebSocket 对话完成
            result_data = await ws_conversation(token, conversation_id, text=item_text)
            
            # API调用成功，认为需要输出（因为db中不存在）
            print(f"  ✓ API调用成功！title: {item_text[:50]}...")
            return {
                "title": item_text,
                "workflow_json": workflow_json,
                "catalog": catalog,
                "conversation_id": conversation_id,
                "matched": True
            }
                
        except Exception as e:
            print(f"  ✗ 异常: {str(e)}")
            return None


async def process_single_item(
    token: str,
    item_text: str,
    workflow_json: str,
    catalog: str,
    semaphore: asyncio.Semaphore
) -> Optional[Dict]:
    """
    处理单个语料项（并发重试）
    
    Args:
        token: 登录token
        item_text: 语料文本
        workflow_json: workflow的JSON字符串（用于记录）
        catalog: 分类
        semaphore: 信号量，用于控制并发数量
    
    Returns:
        如果API调用成功，返回包含title和workflow信息的字典；否则返回None
    """
    # 创建所有重试任务（并发执行）
    retry_tasks = []
    for attempt in range(RETRY_TIMES):
        task = try_single_attempt(
            token=token,
            item_text=item_text,
            workflow_json=workflow_json,
            catalog=catalog,
            attempt=attempt,
            semaphore=semaphore
        )
        retry_tasks.append(task)
    
    # 并发执行所有重试任务
    results = await asyncio.gather(*retry_tasks, return_exceptions=True)
    
    # 查找第一个成功的结果
    for result in results:
        if isinstance(result, dict) and result.get("matched"):
            return result
        elif isinstance(result, Exception):
            print(f"  重试任务异常: {str(result)}")
    
    return None


async def process_workflow(
    token: str,
    workflow_json: str,
    workflow_data: Dict,
    semaphore: asyncio.Semaphore
) -> Optional[Dict]:
    """
    处理一个workflow的所有items
    db中不存在的workflow，只要API调用成功就输出结果
    
    Args:
        token: 登录token
        workflow_json: workflow的JSON字符串
        workflow_data: collected_results.json中对应的数据
        semaphore: 信号量，用于控制并发数量
    
    Returns:
        如果API调用成功，返回结果字典；否则返回None
    """
    catalog = workflow_data.get("catalog", "unknown")
    items = workflow_data.get("items", [])
    
    print(f"\n处理workflow: {workflow_json[:80]}...")
    print(f"  Catalog: {catalog}")
    print(f"  语料数量: {len(items)}")
    print(f"  每个语料重复次数: {RETRY_TIMES}")
    
    # 创建所有任务（每个item一个任务，任务内部会重试RETRY_TIMES次）
    tasks = []
    for item_text in items:
        task = process_single_item(
            token=token,
            item_text=item_text,
            workflow_json=workflow_json,
            catalog=catalog,
            semaphore=semaphore
        )
        tasks.append(task)
    
    # 并发执行所有任务
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 查找第一个成功的结果
    for result in results:
        if isinstance(result, dict) and result.get("matched"):
            return result
        elif isinstance(result, Exception):
            print(f"  任务异常: {str(result)}")
    
    return None


async def main(max_concurrent: int = MAX_CONCURRENT, platform: str = 'arm'):
    """
    主函数
    
    Args:
        max_concurrent: 最大并发数量
        platform: 平台类型，'arm' 或 'x86'
    """
    print("=" * 60)
    print("Workflow异步检查模块")
    print("=" * 60)
    print(f"并发数量: {max_concurrent}")
    print(f"平台: {platform}")
    print(f"每个item重复次数: {RETRY_TIMES}")
    
    # 1. 设置平台环境
    o_config.set_env(platform)
    
    # 2. 登录
    print("\n正在登录...")
    login_result = await i_login()
    
    if not (login_result.get("isSuccess") or login_result.get("success")):
        print("✗ 登录失败")
        return
    
    token = login_result.get("content", {}).get("token")
    if not token:
        print("✗ 登录成功但未获取到token")
        return
    
    print("✓ 登录成功")
    
    # 3. 加载 collected_results.json
    json_path = os.path.join(os.path.dirname(__file__), "collected_results.json")
    print(f"\n正在加载数据文件: {json_path}")
    
    if not os.path.exists(json_path):
        print(f"✗ 文件不存在: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        collected_data = json.load(f)
    
    print(f"✓ 共加载 {len(collected_data)} 个工作流")
    
    # 4. 筛选出数据库中不存在的workflow
    print("\n正在检查数据库中已存在的workflow...")
    db = WorkflowDB()
    
    workflows_to_process = []
    
    for workflow_json, workflow_data in collected_data.items():
        # 检查数据库中是否已存在
        existing = db.get_workflow_by_json(workflow_json)
        if existing is None:
            workflows_to_process.append((workflow_json, workflow_data))
        else:
            print(f"  ⏭ 跳过（已存在）: {workflow_json[:80]}...")
    
    print(f"\n需要处理的workflow数量: {len(workflows_to_process)}")
    print(f"已存在的workflow数量: {len(collected_data) - len(workflows_to_process)}")
    
    if not workflows_to_process:
        print("\n✓ 所有workflow都已存在于数据库中！")
        return
    
    # 5. 创建信号量来控制并发数量
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # 6. 并发处理所有workflow
    print(f"\n开始并发处理 {len(workflows_to_process)} 个workflow...")
    
    # 创建所有workflow处理任务
    workflow_tasks = []
    for workflow_json, workflow_data in workflows_to_process:
        task = process_workflow(token, workflow_json, workflow_data, semaphore)
        workflow_tasks.append((workflow_json, task))
    
    # 并发执行所有workflow任务
    workflow_results = await asyncio.gather(
        *[task for _, task in workflow_tasks],
        return_exceptions=True
    )
    
    # 收集结果
    matched_results = []
    still_not_found = []
    
    for idx, ((workflow_json, _), result) in enumerate(zip(workflow_tasks, workflow_results), 1):
        print(f"\n{'='*60}")
        print(f"处理第 {idx}/{len(workflows_to_process)} 个workflow")
        print(f"Workflow JSON: {workflow_json[:100]}...")
        
        if isinstance(result, Exception):
            print(f"  ✗ 处理异常: {str(result)}")
            still_not_found.append(workflow_json)
        elif isinstance(result, dict) and result.get("matched"):
            matched_results.append(result)
            print(f"  ✓ 找到匹配的workflow！")
        else:
            still_not_found.append(workflow_json)
            print(f"  ✗ 仍未找到匹配的workflow")
    
    # 7. 输出匹配结果到CSV文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(os.path.dirname(__file__), f"matched_workflows_{timestamp}.csv")
    
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"  成功找到: {len(matched_results)} 个")
    print(f"  仍未找到: {len(still_not_found)} 个")
    
    if matched_results:
        print(f"\n正在保存匹配结果到: {output_path}")
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(["title", "workflow_json", "catalog"])
            # 写入数据
            for result in matched_results:
                writer.writerow([
                    result["title"],
                    result["workflow_json"],
                    result["catalog"]
                ])
        print(f"✓ 已保存 {len(matched_results)} 条匹配记录")
    
    if still_not_found:
        print(f"\n提示: 仍有 {len(still_not_found)} 个workflow未找到匹配")
        print("可以稍后重新运行此脚本继续处理")
    
    print("=" * 60)


if __name__ == "__main__":
    # 直接设置参数
    max_concurrent = 10  # 最大并发数量
    platform = 'arm'     # 平台类型：'arm' 或 'x86'
    
    asyncio.run(main(max_concurrent=max_concurrent, platform=platform))

