"""
同步 API 客户端使用示例
"""

import time
from sync_api_client import SyncAPIClient


def main():
    """主函数示例"""
    total_start_time = time.time()
    
    # 创建客户端实例
    client = SyncAPIClient()
    
    # 1. 登录
    username = "15700078644"
    pass64 = "YXJ0aHVy"
    
    login_start = time.time()
    login_result = client.login(username, pass64)
    login_duration = time.time() - login_start
    print(f"[总时长统计] 登录耗时: {login_duration:.2f}秒")
    
    # 检查登录是否成功
    if not client.token:
        print("登录失败，程序退出")
        return
    
    # 2. 创建对话并建立 WebSocket 连接
    title = "PID整定"
    chat_start = time.time()
    result_data = client.create_conversation_and_chat(title, text=title)
    chat_duration = time.time() - chat_start
    print(f"[总时长统计] 对话耗时: {chat_duration:.2f}秒")
    
    # 3. 打印结果
    print("\n" + "=" * 60)
    print("对话结果：")
    print("=" * 60)
    if result_data:
        for item in result_data:
            print(item)
    else:
        print("（无数据）")
    print("=" * 60)
    
    # 4. 打印总体统计
    total_duration = time.time() - total_start_time
    print("\n" + "=" * 60)
    print("总体时长统计：")
    print("=" * 60)
    print(f"登录耗时: {login_duration:.2f}秒")
    print(f"对话耗时: {chat_duration:.2f}秒")
    if client.total_duration:
        print(f"WebSocket 耗时: {client.total_duration:.2f}秒")
    print(f"总耗时: {total_duration:.2f}秒")
    if client.exit_reason:
        print(f"退出原因: {client.exit_reason}")
    print(f"收到消息数: {len(result_data)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

