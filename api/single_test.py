"""
测试接口 - 逐个验证API
"""

import asyncio
import json
import httpx
import websockets


async def i_login(username: str, pass64: str):
    """
    测试登录接口
    
    Args:
        username: 用户名
        pass64: base64编码的密码
    """
    url = "https://tpt.supcon.com/tpt-app/chat-tool-app/system-manager/umsAdmin/login"
    
    # 写死的headers
    headers = {
        "Cookie": "tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B",
        "Authorization-M": "32257d1b-50c9-4948-a0c1-ad8f7d268e17",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://tpt.supcon.com",
        "Referer": "https://tpt.supcon.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    # payload结构
    payload = {
        "data": {
            "username": username,
            "pass64": pass64,
            "agree": True,  # 写死
            "remember": False  # 写死
        }
    }
    
    async with httpx.AsyncClient(verify=True, timeout=30.0) as client:
        try:
            print(f"正在登录: username={username}")
            print(f"请求URL: {url}")
            print(f"请求Headers: {headers}")
            print(f"请求Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应Headers: {dict(response.headers)}")
            
            response.raise_for_status()
            data = response.json()
            
            print(f"\n响应结果:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 提取token信息
            if data.get("isSuccess") or data.get("success"):
                token = data.get("content", {}).get("token")
                if token:
                    print(f"\n✓ 登录成功，Token: {token[:50]}...")
                else:
                    print("\n⚠ 登录成功但未找到token")
            else:
                print(f"\n✗ 登录失败: {data.get('msg', '未知错误')}")
            
            return data
            
        except httpx.HTTPStatusError as e:
            print(f"\n✗ HTTP错误: {e.response.status_code}")
            print(f"错误响应: {e.response.text}")
            raise
        except Exception as e:
            print(f"\n✗ 异常: {str(e)}")
            raise


async def i_create_conversation(token: str, title: str = "pid"):
    """
    测试创建会话接口
    
    Args:
        token: 登录后获取的token
        title: 会话标题，默认为"pid"
    """
    url = "https://tpt.supcon.com/tpt-app/chat-tool-work/api/conversation"
    
    # Cookie包含基础部分和tpt-token
    cookie = f"tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; Authorization-M=32257d1b-50c9-4948-a0c1-ad8f7d268e17; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B; tpt-token={token}"
    
    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://tpt.supcon.com",
        "Referer": "https://tpt.supcon.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    payload = {
        "title": title
    }
    
    async with httpx.AsyncClient(verify=True, timeout=30.0) as client:
        try:
            print(f"\n正在创建会话: title={title}")
            print(f"请求URL: {url}")
            print(f"请求Headers: {headers}")
            print(f"请求Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"响应Headers: {dict(response.headers)}")
            
            response.raise_for_status()
            data = response.json()
            
            print(f"\n响应结果:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 提取会话ID信息
            if data.get("isSuccess") or data.get("success") or response.status_code == 200:
                conversation_id = data.get("id") or data.get("conversationId") or data.get("conversation_id")
                if conversation_id:
                    print(f"\n✓ POST请求成功，会话ID: {conversation_id}")
                    
                    # 第二次调用：PUT请求更新会话
                    print(f"\n正在更新会话: id={conversation_id}, title={title}")
                    update_payload = {
                        "id": conversation_id,
                        "title": title
                    }
                    print(f"请求Payload: {json.dumps(update_payload, ensure_ascii=False, indent=2)}")
                    
                    update_response = await client.put(
                        url,
                        json=update_payload,
                        headers=headers
                    )
                    
                    print(f"\nPUT响应状态码: {update_response.status_code}")
                    update_response.raise_for_status()
                    update_data = update_response.json()
                    
                    print(f"\nPUT响应结果:")
                    print(json.dumps(update_data, ensure_ascii=False, indent=2))
                    
                    if update_data.get("status") == "success":
                        print(f"\n✓ 会话更新成功")
                    else:
                        print(f"\n⚠ 会话更新响应: {update_data}")
                    
                    return {"post_response": data, "put_response": update_data, "conversation_id": conversation_id}
                else:
                    print("\n⚠ 会话创建成功但未找到会话ID")
                    return data
            else:
                print(f"\n✗ 会话创建失败: {data.get('msg', '未知错误')}")
                return data
            
        except httpx.HTTPStatusError as e:
            print(f"\n✗ HTTP错误: {e.response.status_code}")
            print(f"错误响应: {e.response.text}")
            raise
        except Exception as e:
            print(f"\n✗ 异常: {str(e)}")
            raise


async def i_conversation_break(token: str, conversation_id: str):
    """
    结束会话的WebSocket连接
    
    Args:
        token: 登录后获取的token
        conversation_id: 会话ID
    """
    url = f"https://tpt.supcon.com/tpt-app/chat-tool-work/api/conversation/{conversation_id}/break"
    
    # Cookie包含基础部分和tpt-token
    cookie = f"tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; Authorization-M=32257d1b-50c9-4948-a0c1-ad8f7d268e17; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B; tpt-token={token}"
    
    headers = {
        "Cookie": cookie,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://tpt.supcon.com",
        "Referer": "https://tpt.supcon.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    payload = {}
    
    async with httpx.AsyncClient(verify=True, timeout=30.0) as client:
        try:
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data
            
        except httpx.HTTPStatusError as e:
            print(f"\n✗ conversation_break HTTP错误: {e.response.status_code}")
            print(f"错误响应: {e.response.text}")
            raise
        except Exception as e:
            print(f"\n✗ conversation_break异常: {str(e)}")
            raise


async def ws_conversation(token: str, conversation_id: str, text: str = "pid"):
    """
    测试WebSocket连接和消息发送
    
    Args:
        token: 登录后获取的token
        conversation_id: 会话ID
        text: 要发送的消息文本，默认为"pid"
    
    Returns:
        包含完整消息流的数据结构（方案一：按消息组织）
    """
    import time
    
    # 打印输入参数
    print("=" * 50)
    print("test_websocket 输入参数:")
    print(f"  token: {token[:50]}...")
    print(f"  conversation_id: {conversation_id}")
    print(f"  text: {text}")
    print("=" * 50)
    
    # 初始化返回数据结构
    result_data = {
        "conversation_id": conversation_id,
        "test_case": text,
        "messages": {},  # 按 message_id 组织
        "events": [],  # 所有事件的顺序列表
        "extracted_info": {
            "workflow": None,
            "confidence": "",
            "think_chain_name": ""
        }
    }
    
    # 状态跟踪
    has_workflow = False
    last_message_time = None
    message_timeout = 10  # 10秒超时
    
    # WebSocket URL
    ws_url = f"wss://tpt.supcon.com/tpt-app/chat-tool-socket-work/api/conversation/{conversation_id}/stream"
    
    # Cookie包含基础部分和tpt-token
    cookie = f"tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; Authorization-M=32257d1b-50c9-4948-a0c1-ad8f7d268e17; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B; tpt-token={token}"
    
    # WebSocket headers
    headers = {
        "Cookie": cookie
    }
    
    result_data = None
    try:
        # 建立WebSocket连接
        async with websockets.connect(
            ws_url,
            additional_headers=headers,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10
        ) as ws:
            # 发送消息
            message_payload = {
                "message": {
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                },
                "parent_id": None,
                "type": "user_input",
                "use_deep_explore": False,
                "user_locale": "zh-CN"
            }
            
            await ws.send(json.dumps(message_payload))
            
            # 持续接收消息，带超时机制
            last_path = '-'
            result_data = []

            try:
                while True:
                    # 检查是否已收到 workflow
                    if has_workflow:
                        await asyncio.sleep(1)
                        break
                    
                    # 检查超时
                    if last_message_time:
                        elapsed = time.time() - last_message_time
                        if elapsed >= message_timeout:
                            print(f"\n⚠ 10秒内未收到新消息，超时退出")
                            break
                    
                    try:
                        # 接收消息，设置超时避免无限等待
                        message = await asyncio.wait_for(ws.recv(), timeout=30)
                    except asyncio.TimeoutError:
                        # 超时后继续检查条件
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("\nWebSocket连接已关闭")
                        break
                    
                    try:
                        current_time = time.time()
                        last_message_time = current_time
                        
                        data = json.loads(message)
                        msg_type = data.get("type")

                        """
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        对话管理
                        """

                        if "conversation_status_changed" == msg_type:
                            print(f"[CONVERSATION_STATUS_CHANGED] <ONLY ONE> {data}")

                        elif "new_message" == msg_type:
                            # 一个conversation两个message 第一个是问 第二个是答，所以可以看到message_status_changed也会有两个，第一个是done，第二个是chat
                            print(f"[NEW_MESSAGE] <TWICE> {data}")

                        elif "message_status_changed" == msg_type:
                            # done chat interaction
                            if data.get('status') == "interaction":
                                break
                            print(f"[MESSAGE_STATUS_CHANGED] ({data.get('status')}) {data}")

                        elif msg_type == "message_content_delta":
                            # 主要逻辑在这里，所有回答(到交互之前)的内容都在这里
                            path = data.get('path')
                            operation = data.get('operation')

                            if operation == "update":
                                result_data.append([path, data.get('content')])
                                # print(f"[UPDATE] {path} {data.get('content')}\n")
                            elif operation == "append":
                                if last_path != path:
                                    result_data[-1].append(path)
                                    result_data[-1].append("")
                                    # print(f"[APPEND] [PATH] {path}\n")
                                last_path = path
                                result_data[-1][-1] += data.get('content')
                                # print(data.get('content'), end="")

                        else:
                            print("[NOT IMPLEMENT]", msg_type, data)
                            
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"\n处理消息异常: {str(e)}")
                        pass
                
            except websockets.exceptions.ConnectionClosed:
                print("\nWebSocket连接已关闭")
            except KeyboardInterrupt:
                print("\n用户中断接收")
            except Exception as e:
                print(f"\n处理消息时发生异常: {str(e)}")
                raise
                
    except Exception as e:
        print(f"\n✗ WebSocket连接异常: {str(e)}")
        raise
    finally:
        # 无论以何种方式退出，都调用 break API
        try:
            print(f"\n正在调用 break_conversation API...")
            await i_conversation_break(token, conversation_id)
            print(f"✓ break_conversation API 调用成功，等待2秒后退出...")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"\n⚠ 调用 break_conversation API 时发生异常: {str(e)}")
    
    return result_data


async def main():
    """主函数"""
    import os
    import yaml
    
    # 测试登录
    username = "15700078644"
    pass64 = "YXJ0aHVy"  # base64编码的密码
    
    login_result = await i_login(username, pass64)
    
    # 如果登录成功，测试创建会话
    if login_result.get("isSuccess") or login_result.get("success"):
        token = login_result.get("content", {}).get("token")
        if token:

            title = "基于 OTS 多煤种模拟，整定乙烯装置 PIC14063 的 PID 参数，适配 DCS 动态调整"

            conv_result = await i_create_conversation(token, title=title)

            # 如果创建会话成功，测试WebSocket连接
            if isinstance(conv_result, dict) and "conversation_id" in conv_result:
                conversation_id = conv_result["conversation_id"]
                result_data = await ws_conversation(token, conversation_id, text=title)
                print(result_data)
                # for line in result_data:
                #     print(line)


if __name__ == "__main__":
    asyncio.run(main())
