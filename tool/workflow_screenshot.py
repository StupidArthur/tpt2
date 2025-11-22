# encoding: utf-8

"""
根据匹配结果进行UI截图模块
读取matched_workflows_{timestamp}.txt文件，根据title找到对应的会话，进行截图并更新数据库
"""

import os
import sys
import time
import json
from typing import List, Dict, Optional
from driver4 import Driver4
from printscreen import screenshot_with_mss

# 添加 api 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api.common_api import o_config
from workflow_db import WorkflowDB


# 全局变量
driver_path = "f:\\chrome144\\chromedriver.exe"  # 你的驱动路径
driver = Driver4()
db = WorkflowDB()


def find_conversation_by_title(title: str) -> bool:
    """
    根据title在会话列表中查找对应的会话并点击
    
    Args:
        title: 会话标题
    
    Returns:
        是否找到并点击成功
    """
    try:
        # 等待会话列表加载
        time.sleep(1)
        
        # 查找包含指定title的会话项
        # 这里使用XPath查找包含指定文本的会话项
        xpath = f'//div[@class="content-list-item"]//*[contains(text(), "{title[:30]}")]'
        
        # 尝试点击
        try:
            driver.click(xpath)
            time.sleep(1)
            print(f"  ✓ 找到会话: {title[:50]}...")
            return True
        except:
            # 如果直接点击失败，尝试点击父元素
            try:
                # 查找包含title的会话项，然后点击其父元素
                xpath_parent = f'//div[@class="content-list-item"][.//*[contains(text(), "{title[:30]}")]]'
                driver.click(xpath_parent)
                time.sleep(1)
                print(f"  ✓ 找到会话（通过父元素）: {title[:50]}...")
                return True
            except Exception as e:
                print(f"  ✗ 未找到会话: {title[:50]}... - {str(e)}")
                return False
                
    except Exception as e:
        print(f"  ✗ 查找会话出错: {str(e)}")
        return False


def take_screenshot(catalog: str, filename: str) -> Optional[str]:
    """
    进行 UI 操作并截图
    
    Args:
        catalog: 分类
        filename: 文件名
    
    Returns:
        截图保存路径，失败返回None
    """
    try:
        print("  开始 UI 操作...")
        
        # 点击工作流标签
        driver.click("(//*[text()='工作流'])[last()]")
        time.sleep(2)  # 等待工作流加载
        
        # 确保目录存在
        picture_dir = os.path.join(os.path.dirname(__file__), "picture", catalog)
        os.makedirs(picture_dir, exist_ok=True)
        
        # 截图
        save_path = os.path.join(picture_dir, filename)
        screenshot_with_mss(region=(2300, 500, 1485, 1400), save_path=save_path)
        print(f"  ✓ 截图已保存: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"  ✗ UI 操作出错: {e}")
        return None


def load_matched_workflows(file_path: str) -> List[Dict]:
    """
    加载匹配结果文件
    
    Args:
        file_path: 匹配结果文件路径
    
    Returns:
        匹配结果列表
    """
    results = []
    
    if not os.path.exists(file_path):
        print(f"✗ 文件不存在: {file_path}")
        return results
    
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


def main(matched_file: str = None):
    """
    主函数
    
    Args:
        matched_file: 匹配结果文件路径，如果为None则查找最新的文件
    """
    print("=" * 60)
    print("Workflow截图模块")
    print("=" * 60)
    
    # 1. 查找匹配结果文件
    if matched_file is None:
        # 查找最新的matched_workflows文件
        tool_dir = os.path.dirname(__file__)
        matched_files = [
            f for f in os.listdir(tool_dir)
            if f.startswith("matched_workflows_") and f.endswith(".txt")
        ]
        
        if not matched_files:
            print("✗ 未找到匹配结果文件")
            print("  请先运行 workflow_async_check.py 生成匹配结果文件")
            return
        
        # 按修改时间排序，取最新的
        matched_files.sort(key=lambda x: os.path.getmtime(os.path.join(tool_dir, x)), reverse=True)
        matched_file = os.path.join(tool_dir, matched_files[0])
        print(f"使用最新的匹配结果文件: {matched_files[0]}")
    else:
        if not os.path.exists(matched_file):
            print(f"✗ 文件不存在: {matched_file}")
            return
    
    # 2. 加载匹配结果
    print(f"\n正在加载匹配结果: {matched_file}")
    matched_results = load_matched_workflows(matched_file)
    
    if not matched_results:
        print("✗ 未找到匹配结果")
        return
    
    print(f"✓ 共加载 {len(matched_results)} 条匹配记录")
    
    # 3. 设置平台环境（使用arm，因为通常截图在arm平台）
    o_config.set_env('arm')
    
    # 4. 构建浏览器 URL
    url = f"{o_config.https_header}/tpt-app/#/home/chat/main"
    print(f"\n使用 URL: {url}")
    
    # 5. 打开浏览器
    print("正在打开浏览器...")
    driver.open(url, driver_path)
    time.sleep(2)
    
    # 6. 等待用户手动登录和设置
    input("请在浏览器中确认登录状态、设置好偏好设置、拉宽工作流区域，然后按回车继续...")
    
    # 7. 处理每个匹配结果
    success_count = 0
    failed_count = 0
    
    for idx, result in enumerate(matched_results, 1):
        print(f"\n{'='*60}")
        print(f"处理第 {idx}/{len(matched_results)} 条记录")
        print(f"Title: {result['title'][:80]}...")
        print(f"Catalog: {result['catalog']}")
        
        # 根据title查找会话
        if not find_conversation_by_title(result['title']):
            print(f"  ✗ 未找到对应的会话，跳过")
            failed_count += 1
            continue
        
        # 获取下一个可用的ID
        next_id = db.get_next_id(result['catalog'])
        print(f"  下一个ID: {next_id}")
        
        # 截图
        screenshot_path = take_screenshot(result['catalog'], next_id)
        
        if screenshot_path:
            # 从collected_results.json获取items
            json_path = os.path.join(os.path.dirname(__file__), "collected_results.json")
            items = []
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    collected_data = json.load(f)
                    if result['workflow_json'] in collected_data:
                        items = collected_data[result['workflow_json']].get('items', [])
            
            # 更新数据库
            db.add_workflow(next_id, result['workflow_json'], result['catalog'], items)
            print(f"  ✓ 已更新数据库: {next_id}")
            success_count += 1
        else:
            failed_count += 1
        
        time.sleep(1)  # 记录之间的间隔
    
    # 8. 关闭浏览器
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"  成功截图: {success_count} 个")
    print(f"  失败: {failed_count} 个")
    print("=" * 60)
    
    print("\n关闭浏览器...")
    driver.quit()


if __name__ == "__main__":
    # 直接设置参数
    matched_file = None  # 匹配结果文件路径，None表示使用最新的文件
    
    main(matched_file=matched_file)

