"""
主程序入口
"""
import json
import os
import re
import asyncio
from api_client import i_login, i_create_conversation, ws_conversation
from formatter import conversation_analyze


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除Windows不允许的字符"""
    # Windows不允许的字符: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    # 替换为下划线
    sanitized = re.sub(invalid_chars, '_', filename)
    # 移除首尾空格和点号
    sanitized = sanitized.strip(' .')
    return sanitized


cases_file = os.path.join(os.path.dirname(__file__), "..", "test_data", "demo1.yaml")
cases_file = os.path.normpath(cases_file)
print(f"读取测试用例文件: {cases_file}")
with open(cases_file, "r", encoding="utf-8") as f:
    test_cases = [line.strip() for line in f.readlines() if line.strip()]


async def main():
    """主函数"""
    # 测试登录
    username = "15700078644"
    pass64 = "YXJ0aHVy"  # base64编码的密码
    
    login_result = await i_login(username, pass64)
    
    # 如果登录成功，测试创建会话
    if login_result.get("isSuccess") or login_result.get("success"):
        token = login_result.get("content", {}).get("token")
        if token:

            # title = "基于 OTS 多煤种模拟，整定乙烯装置 PIC14063 的 PID 参数，适配 DCS 动态调整"
            for title in test_cases:

                try:

                    conv_result = await i_create_conversation(token, title=title)

                    # 如果创建会话成功，测试WebSocket连接
                    if isinstance(conv_result, dict) and "conversation_id" in conv_result:
                        conversation_id = conv_result["conversation_id"]
                        result_data = await ws_conversation(token, conversation_id, text=title)
                        # 确保目录存在
                        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_results")
                        os.makedirs(output_dir, exist_ok=True)
                        # 清理文件名，移除不允许的字符
                        safe_filename = sanitize_filename(title)
                        output_file = os.path.join(output_dir, f"{safe_filename}.json")
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(result_data, f, ensure_ascii=False, indent=2)
                        # for line in result_data:
                        #     print(line)
                        #
                        # conversation_info = conversation_analyze(result_data)
                        # print(conversation_info)
                except Exception as e:
                    print(title, e)


if __name__ == "__main__":
    asyncio.run(main())

