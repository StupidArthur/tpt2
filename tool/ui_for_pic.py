# encoding: utf-8

import os
import sys
import asyncio
import re
import json
from driver4 import Driver4
import time
import typing as tp

from printscreen import screenshot_with_mss

# 添加 api 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api.common_api import i_login, i_create_conversation, ws_conversation, o_config
from data_process.formatter import conversation_analyze


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除Windows不允许的字符"""
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    sanitized = sanitized.strip(' .')
    return sanitized




# 全局变量
driver_path = "f:\\chrome144\\chromedriver.exe"  # 你的驱动路径
driver = Driver4()
token = None


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


def check_workflow_match(result_info, expected_workflow: str, expected_branch_rules: str) -> bool:
    """检查解析出的工作流是否与预期匹配"""
    # 标准化 branch_rules（空字符串或 None 转为 '[]'）
    result_branch = result_info.branch_rules or '[]'
    expected_branch = expected_branch_rules or '[]'
    
    # 比较 workflow 和 branch_rules
    workflow_match = result_info.workflow == expected_workflow
    branch_match = result_branch == expected_branch
    
    return workflow_match and branch_match


async def try_single_item(text: str, expected_workflow: str, expected_branch_rules: str) -> tp.Tuple[bool, object]:
    """
    尝试单个语料，返回 (是否匹配, result_data)
    
    Returns:
        (bool, result_data): (是否匹配, 解析结果)
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
            
            # 2. 解析结果
            result_info = conversation_analyze(result_data)
            
            # 3. 检查是否匹配
            is_match = check_workflow_match(result_info, expected_workflow, expected_branch_rules)
            
            if is_match:
                print(f"    ✓ 匹配成功！")
                return True, result_data
            else:
                print(f"    ✗ 不匹配")
                return False, result_data
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


async def main():
    """主函数"""
    # 1. 设置 arm 平台环境（需要在打开浏览器前设置，以便获取正确的 URL）
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
    
    with open(json_path, 'r', encoding='utf-8') as f:
        collected_data = json.load(f)
    
    print(f"共加载 {len(collected_data)} 个工作流")
    
    # 7. 准备输出文件路径
    picture_base_dir = os.path.join(os.path.dirname(__file__), "picture")
    os.makedirs(picture_base_dir, exist_ok=True)
    
    name_map_path = os.path.join(picture_base_dir, "name_map.txt")
    not_found_path = os.path.join(picture_base_dir, "not_found.txt")
    
    # 初始化 name_map.txt 文件（如果不存在，写入表头）
    if not os.path.exists(name_map_path):
        with open(name_map_path, 'w', encoding='utf-8') as f:
            f.write("文件名\t工作流标识\n")
        print(f"已创建 name_map.txt 文件")
    
    # 初始化 not_found.txt 文件（如果不存在，创建空文件）
    if not os.path.exists(not_found_path):
        with open(not_found_path, 'w', encoding='utf-8') as f:
            pass
        print(f"已创建 not_found.txt 文件")
    
    # 8. 遍历每个工作流
    for workflow_key, workflow_data in collected_data.items():
        print(f"\n{'='*60}")
        print(f"处理工作流: {workflow_key[:100]}...")
        
        # 解析 key 获取预期的 workflow 和 branch_rules
        try:
            expected_dict = json.loads(workflow_key)
            expected_workflow = expected_dict.get("workflow", "")
            expected_branch_rules = expected_dict.get("branch_rules", "[]")
        except Exception as e:
            print(f"  解析 key 失败: {e}")
            continue
        
        catalog = workflow_data.get("catalog", "unknown")
        items = workflow_data.get("items", [])
        
        print(f"  Catalog: {catalog}")
        print(f"  语料数量: {len(items)}")
        
        # 9. 尝试每个语料，直到匹配或用完
        matched = False
        matched_item = None
        
        for item_text in items:
            is_match, result_data = await try_single_item(
                item_text, 
                expected_workflow, 
                expected_branch_rules
            )
            
            if is_match:
                matched = True
                matched_item = item_text
                break
            
            time.sleep(1)  # 语料之间的间隔
        
        # 10. 如果匹配，进行截图
        if matched:
            # 确定文件名（catalog_1.png, catalog_2.png, ...）
            catalog_dir = os.path.join(picture_base_dir, catalog)
            os.makedirs(catalog_dir, exist_ok=True)
            
            # 查找已有的文件数量
            existing_files = [f for f in os.listdir(catalog_dir) if f.startswith(f"{catalog}_") and f.endswith(".png")]
            file_number = len(existing_files) + 1
            filename = f"{catalog}_{file_number}.png"
            
            # 截图
            screenshot_path = await take_screenshot(catalog, filename)
            
            if screenshot_path:
                # 立即写入 name_map.txt
                with open(name_map_path, 'a', encoding='utf-8') as f:
                    f.write(f"{filename}\t{workflow_key}\n")
                print(f"  ✓ 已立即写入 name_map.txt: {filename}")
        else:
            # 11. 如果所有语料都不匹配，立即写入 not_found.txt
            print(f"  ✗ 所有语料都不匹配，立即写入 not_found.txt")
            with open(not_found_path, 'a', encoding='utf-8') as f:
                f.write(f"{workflow_key}\n")
            print(f"  ✓ 已立即写入 not_found.txt")
        
        time.sleep(2)  # 工作流之间的间隔
    
    # 12. 关闭浏览器
    print("\n所有任务完成，关闭浏览器...")
    driver.quit()


if __name__ == "__main__":
    asyncio.run(main())

