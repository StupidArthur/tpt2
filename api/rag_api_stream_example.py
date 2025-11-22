"""
RAG API 流式接口使用示例
"""

from rag_api_client import rag_chat_stream


def main():
    """主函数：调用流式接口并打印所有消息"""
    content = "杭州高新技术产业开发区（滨江）档案馆成立于哪一年？"
    
    print("=" * 60)
    print("开始接收流式响应：")
    print("=" * 60)
    print()
    
    # 方式1：实时打印（推荐）
    for line in rag_chat_stream(content):
        print(line, end='', flush=True)  # end='' 不换行，flush=True 立即输出
    
    print("\n")
    print("=" * 60)
    print("响应接收完成")
    print("=" * 60)


def main_with_accumulate():
    """主函数：累积完整响应后再打印"""
    content = "杭州高新技术产业开发区（滨江）档案馆成立于哪一年？"
    
    print("=" * 60)
    print("开始接收流式响应：")
    print("=" * 60)
    print()
    
    full_response = ""
    for line in rag_chat_stream(content):
        full_response += line
        print(line, end='', flush=True)  # 实时打印
    
    print("\n")
    print("=" * 60)
    print("完整响应内容：")
    print("=" * 60)
    print(full_response)
    print("=" * 60)


def main_line_by_line():
    """主函数：逐行打印（每行换行）"""
    content = "杭州高新技术产业开发区（滨江）档案馆成立于哪一年？"
    
    print("=" * 60)
    print("开始接收流式响应（逐行模式）：")
    print("=" * 60)
    print()
    
    for line in rag_chat_stream(content):
        print(line)  # 每行自动换行
    
    print()
    print("=" * 60)
    print("响应接收完成")
    print("=" * 60)


if __name__ == "__main__":
    # 使用默认的实时打印方式
    main()
    
    # 如果需要其他方式，可以取消注释：
    # main_with_accumulate()  # 累积后打印
    # main_line_by_line()     # 逐行打印

