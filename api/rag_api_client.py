"""
RAG API 客户端模块 - 包含行业领域问答相关的 API 调用
"""

import httpx
from typing import List, Dict, Optional


async def rag_chat(
    content: str,
    user_id: str = "207",
    tenant_id: str = "0",
    selected_file_info_list: Optional[List[Dict[str, str]]] = None,
    all_file_info_list: Optional[List[Dict[str, str]]] = None,
    timeout: float = 30.0
) -> Dict:
    """
    调用 RAG 行业领域问答接口
    
    Args:
        content: 用户消息内容
        user_id: 用户ID，默认为 "207"
        tenant_id: 租户ID，默认为 "0"
        selected_file_info_list: 选中的文件信息列表，格式为 [{"bucket": "...", "name": "...", "object": "..."}]
        all_file_info_list: 所有文件信息列表，格式为 [{"bucket": "...", "name": "...", "object": "..."}]
        timeout: 请求超时时间（秒），默认 30 秒
    
    Returns:
        Dict: API 响应结果
    

    """
    url = "https://tpt.supcon.com/api/industry_domain_qa/saas/general/chat"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
        "messages": [
            {
                "content": content,
                "role": "user"
            }
        ],
        "user_id": user_id,
        "tenant_id": tenant_id
    }
    
    # 添加文件信息（如果提供）
    if selected_file_info_list is not None:
        payload["selected_file_info_list"] = selected_file_info_list
    
    if all_file_info_list is not None:
        payload["all_file_info_list"] = all_file_info_list
    
    # 打印请求信息（仅打印短内容）
    if len(content) <= 50:
        print(f"[rag_chat] content={content}")
    else:
        print(f"[rag_chat] content={content[:50]}...")
    
    try:
        async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"[rag_chat] 请求成功，状态码: {response.status_code}")
            return result
            
    except httpx.HTTPStatusError as e:
        print(f"[rag_chat] HTTP 错误: {e.response.status_code} - {e.response.text}")
        raise
    except httpx.RequestError as e:
        print(f"[rag_chat] 请求错误: {str(e)}")
        raise
    except Exception as e:
        print(f"[rag_chat] 未知错误: {str(e)}")
        raise


async def rag_chat_simple(
    content: str,
    user_id: str = "207",
    tenant_id: str = "0",
    timeout: float = 30.0
) -> Dict:
    """
    简化版本的 RAG 聊天接口（不包含文件信息）
    
    Args:
        content: 用户消息内容
        user_id: 用户ID，默认为 "207"
        tenant_id: 租户ID，默认为 "0"
        timeout: 请求超时时间（秒），默认 30 秒
    
    Returns:
        Dict: API 响应结果
    
    Example:
    """
    return await rag_chat(
        content=content,
        user_id=user_id,
        tenant_id=tenant_id,
        selected_file_info_list=None,
        all_file_info_list=None,
        timeout=timeout
    )


def rag_chat_stream(
    content: str,
    user_id: str = "207",
    tenant_id: str = "0",
    timeout: float = 30.0
):
    """
    同步流式调用 RAG 接口
    
    Args:
        content: 用户消息内容
        user_id: 用户ID，默认 "207"
        tenant_id: 租户ID，默认 "0"
        timeout: 超时时间（秒）
    
    Yields:
        str: 流式响应的每一行数据
    """
    url = "http://supcon-rag-indu-dev.supcon5t.com/api/industry_domain_qa/saas/general/chat"
    payload = {
        "messages": [{"content": content, "role": "user"}],
        "user_id": user_id,
        "tenant_id": tenant_id,
        "selected_file_info_list": [],
        "all_file_info_list": []
    }
    
    with httpx.Client(verify=False, timeout=timeout) as client:
        with client.stream("POST", url, json=payload, headers={"Content-Type": "application/json"}) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    yield line

