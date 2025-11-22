# encoding: utf-8

import os
import sys
import asyncio
import json
import time
from datetime import datetime
from typing import Tuple, Optional
from driver4 import Driver4
from printscreen import screenshot_with_mss

# 添加 api 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api.common_api import i_login, i_create_conversation, ws_conversation, o_config
from workflow_db import WorkflowDB


# 全局变量
driver_path = "f:\\chrome144\\chromedriver.exe"  # 你的驱动路径
driver = Driver4()
token = None
db = WorkflowDB()

# 配置参数
RETRY_TIMES = 3  # 每个item重复执行次数


async def login():
    """通过 API 登录"""
    global token
    
    # 注意：arm 平台环境已在 main() 函数中设置，这里不需要重复设置
    print("正在通过 API 登录（arm 平台）...")
    login_result = await i_login()
    
    if login_result.get("isSuccess") or login_result.get("success"):
        token = login_result.get("content", {}).get("token")
        if token:
            print("API 登录成功！")
            return True
        else:
            print("登录失败：未获取到 token")
            return False
    else:
        print(f"登录失败：{login_result}")
        return False


async def try_single_item(text: str) -> Tuple[bool, Optional[object]]:
    """
    尝试单个语料，返回 (是否成功, result_data)
    只要API调用成功就认为成功（因为db中不存在说明需要处理）
    
    Returns:
        (bool, result_data): (是否成功, 解析结果)
    """
    global token
    
    if not token:
        print("错误：未登录，请先调用 login()")
        return False, None
    
    print(f"  尝试语料: {text[:50]}...")
    
    try:
        # 1. 通过 API 创建 conversation 并等待到 ws 结束
        conv_result = await i_create_conversation(token, title=text)
        
        if isinstance(conv_result, dict) and "conversation_id" in conv_result:
            conversation_id = conv_result["conversation_id"]
            print(f"    会话创建成功，conversation_id: {conversation_id}")
            
            # 等待 WebSocket 对话完成
            result_data = await ws_conversation(token, conversation_id, text=text)
            print("    WebSocket 对话完成")
            
            # API调用成功，认为需要处理（因为db中不存在）
            print(f"    ✓ API调用成功！")
            return True, result_data
        else:
            print(f"    创建会话失败: {conv_result}")
            return False, None
    except Exception as e:
        print(f"    API 调用出错: {e}")
        return False, None


async def take_screenshot(catalog: str, filename: str):
    """进行 UI 操作并截图"""
    try:
        print("  开始 UI 操作...")
        
        # 点击第一个会话
        driver.click('//div[@class="content-item-b"]/div[@class="content-list-item"][1]')
        time.sleep(1)
        
        # 点击工作流标签
        driver.click("(//*[text()='工作流'])[last()]")
        time.sleep(2)  # 等待工作流加载
        
        # 确保目录存在
        picture_dir = os.path.join(os.path.dirname(__file__), "picture", catalog)
        os.makedirs(picture_dir, exist_ok=True)
        
        # 截图
        save_path = os.path.join(picture_dir, filename)
        screenshot_with_mss(region=(2300, 500, 1485, 1400), save_path=save_path)
        print(f"  截图已保存: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"  UI 操作出错: {e}")
        return None


async def process_not_found_workflow(workflow_json: str, workflow_data: dict, retry_times: int = RETRY_TIMES):
    """
    处理一个未找到的workflow
    db中不存在的workflow，只要API调用成功就进入截图流程
    
    Args:
        workflow_json: workflow的JSON字符串（作为key）
        workflow_data: collected_results.json中对应的数据
        retry_times: 每个item重复执行次数
    
    Returns:
        bool: 是否成功截图
    """
    catalog = workflow_data.get("catalog", "unknown")
    items = workflow_data.get("items", [])
    
    print(f"  Catalog: {catalog}")
    print(f"  语料数量: {len(items)}")
    print(f"  每个语料重复次数: {retry_times}")
    
    # 遍历每个语料，每个语料重复retry_times次
    for item_text in items:
        for attempt in range(retry_times):
            print(f"\n  尝试语料 (第{attempt + 1}/{retry_times}次): {item_text[:50]}...")
            
            success, result_data = await try_single_item(item_text)
            
            if success:
                # API调用成功，进行截图
                print(f"  ✓ API调用成功，进入截图流程！")
                
                # 获取下一个可用的ID
                next_id = db.get_next_id(catalog)
                print(f"  下一个ID: {next_id}")
                
                # 截图
                screenshot_path = await take_screenshot(catalog, next_id)
                
                if screenshot_path:
                    # 更新数据库
                    db.add_workflow(next_id, workflow_json, catalog, items)
                    print(f"  ✓ 已更新数据库: {next_id}")
                    return True
            
            time.sleep(1)  # 每次尝试之间的间隔
        
        time.sleep(2)  # 语料之间的间隔
    
    return False


async def main():
    """主函数"""
    # 1. 设置 arm 平台环境
    o_config.set_env('arm')
    
    # 2. 构建浏览器 URL
    url = f"{o_config.https_header}/tpt-app/#/home/chat/main"
    print(f"使用 URL: {url}")
    
    # 3. 打开浏览器
    driver.open(url, driver_path)
    time.sleep(2)
    
    # 4. 通过 API 登录
    login_success = await login()
    if not login_success:
        print("登录失败，程序退出")
        driver.quit()
        return
    
    # 5. 等待用户手动登录和设置（如果需要）
    input("请在浏览器中确认登录状态、设置好偏好设置、拉宽工作流区域，然后按回车继续...")
    
    # 6. 加载 collected_results.json
    json_path = os.path.join(os.path.dirname(__file__), "collected_results.json")
    print(f"\n正在加载数据文件: {json_path}")
    
    if not os.path.exists(json_path):
        print(f"文件不存在: {json_path}")
        driver.quit()
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        collected_data = json.load(f)
    
    print(f"共加载 {len(collected_data)} 个工作流")
    
    # 7. 筛选出数据库中不存在的workflow
    print("\n正在检查数据库中已存在的workflow...")
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
        driver.quit()
        return
    
    # 8. 处理每个未找到的workflow
    found_count = 0
    still_not_found = []
    
    for idx, (workflow_json, workflow_data) in enumerate(workflows_to_process, 1):
        print(f"\n{'='*60}")
        print(f"处理第 {idx}/{len(workflows_to_process)} 个workflow")
        print(f"Workflow JSON: {workflow_json[:100]}...")
        
        # 处理这个workflow
        success = await process_not_found_workflow(workflow_json, workflow_data, RETRY_TIMES)
        
        if success:
            found_count += 1
            print(f"  ✓ 成功找到并截图")
        else:
            still_not_found.append(workflow_json)
            print(f"  ✗ 仍未找到匹配的workflow")
        
        time.sleep(2)  # 工作流之间的间隔
    
    # 9. 输出统计信息
    print(f"\n处理完成:")
    print(f"  成功找到: {found_count} 个")
    print(f"  仍未找到: {len(still_not_found)} 个")
    
    if still_not_found:
        print(f"\n提示: 仍有 {len(still_not_found)} 个workflow未找到匹配")
        print("可以稍后重新运行此脚本继续处理")
    
    # 10. 关闭浏览器
    print("\n关闭浏览器...")
    driver.quit()


if __name__ == "__main__":
    asyncio.run(main())

