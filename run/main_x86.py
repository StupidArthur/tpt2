"""
主程序入口
"""
import json
import os
import re
import time
import asyncio
from api.common_api import i_login, i_create_conversation, ws_conversation, o_config
from data_process.formatter import conversation_analyze

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除Windows不允许的字符"""
    # Windows不允许的字符: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    # 替换为下划线
    sanitized = re.sub(invalid_chars, '_', filename)
    # 移除首尾空格和点号
    sanitized = sanitized.strip(' .')
    return sanitized


# cases_file = os.path.join(os.path.dirname(__file__), "..", "test_data", "demo2.yaml")
# cases_file = os.path.normpath(cases_file)
# print(f"读取测试用例文件: {cases_file}")
# with open(cases_file, "r", encoding="utf-8") as f:
#     test_cases = [line.strip() for line in f.readlines() if line.strip()]

from test_data.temp_loader import all_sentences

test_cases = all_sentences()

class STtime(object):

    def __init__(self):
        self.s = ''

stime = STtime()


async def process_single_test_case(token: str, title: str, semaphore: asyncio.Semaphore):
    """
    处理单个测试用例的完整流程
    
    Args:
        token: 登录token
        title: 测试用例标题
        semaphore: 信号量，用于控制并发数量
    """
    async with semaphore:  # 获取信号量，控制并发
        try:
            print(f"[开始处理] {title[:50]}...")
            
            # 创建会话
            conv_result = await i_create_conversation(token, title=title)

            # 如果创建会话成功，测试WebSocket连接
            if isinstance(conv_result, dict) and "conversation_id" in conv_result:
                conversation_id = conv_result["conversation_id"]
                result_data = await ws_conversation(token, conversation_id, text=title)
                
                # 确保目录存在
                import time

                dir_name = f"锅炉_{stime.s}"

                output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_results", dir_name)
                os.makedirs(output_dir, exist_ok=True)
                
                # 清理文件名，移除不允许的字符
                safe_filename = sanitize_filename(title)
                output_file = os.path.join(output_dir, f"{safe_filename}.json")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
                
                print(f"[完成] {title[:50]}...")
                return {"success": True, "title": title, "file": output_file}
            else:
                print(f"[失败] {title[:50]}... - 创建会话失败")
                return {"success": False, "title": title, "error": "创建会话失败"}
                
        except Exception as e:
            print(f"[异常] {title[:50]}... - {str(e)}")
            return {"success": False, "title": title, "error": str(e)}


async def main(max_concurrent: int = 1):
    """
    主函数
    
    Args:
        max_concurrent: 最大并发数量，默认为5
    """
    print(f"开始执行测试，并发数量: {max_concurrent}")

    stime.s = f"{int(time.time())}"
    
    # 测试登录
    o_config.set_env('x86')
    
    login_result = await i_login()
    
    # 如果登录成功，开始并发测试
    if login_result.get("isSuccess") or login_result.get("success"):
        token = login_result.get("content", {}).get("token")
        if token:
            # 创建信号量来控制并发数量
            semaphore = asyncio.Semaphore(max_concurrent)
            
            # 创建所有任务
            tasks = [
                process_single_test_case(token, title, semaphore)
                for title in test_cases
            ]
            
            # 并发执行所有任务，并收集结果
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计结果
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            fail_count = len(results) - success_count
            
            print("\n" + "=" * 60)
            print(f"测试完成！")
            print(f"总计: {len(results)} 个测试用例")
            print(f"成功: {success_count} 个")
            print(f"失败: {fail_count} 个")
            print("=" * 60)
            
            # 打印失败详情
            if fail_count > 0:
                print("\n失败的测试用例:")
                for r in results:
                    if isinstance(r, dict) and not r.get("success"):
                        print(f"  - {r.get('title', 'Unknown')}: {r.get('error', 'Unknown error')}")
                    elif isinstance(r, Exception):
                        print(f"  - 异常: {str(r)}")
        else:
            print("✗ 登录成功但未获取到token")
    else:
        print("✗ 登录失败")


if __name__ == "__main__":
    # 通过函数参数控制并发数量，例如：max_concurrent=10
    asyncio.run(main(max_concurrent=20))

