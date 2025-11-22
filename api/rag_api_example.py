"""
RAG API 使用示例
"""

import asyncio
from rag_api_client import rag_chat, rag_chat_simple


async def example_full():
    """完整示例：包含文件信息"""
    result = await rag_chat(
        content="杭州高新技术产业开发区（滨江）档案馆成立于哪一年？",
        selected_file_info_list=[],
        all_file_info_list=[]
    )
    print("完整示例结果:")
    print(result)
    return result


async def example_simple():
    """简单示例：不包含文件信息"""
    result = await rag_chat_simple(
        content="杭州高新技术产业开发区（滨江）档案馆成立于哪一年？"
    )
    print("简单示例结果:")
    print(result)
    return result


async def main():
    """主函数"""
    print("=" * 50)
    print("RAG API 调用示例")
    print("=" * 50)
    
    # 运行简单示例
    print("\n1. 简单示例（不包含文件信息）:")
    try:
        await example_simple()
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "=" * 50)
    
    # 运行完整示例
    print("\n2. 完整示例（包含文件信息）:")
    try:
        await example_full()
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())


