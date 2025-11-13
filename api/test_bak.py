"""
测试接口 - 逐个验证API
"""

import asyncio
import json
import httpx
import websockets


async def test_login(username: str, pass64: str):
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


async def test_create_conversation(token: str, title: str = "pid"):
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


async def test_conversation_break(token: str, conversation_id: str):
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


async def test_websocket(token: str, conversation_id: str, text: str = "pid"):
    """
    测试WebSocket连接和消息发送
    
    Args:
        token: 登录后获取的token
        conversation_id: 会话ID
        text: 要发送的消息文本，默认为"pid"
    """
    # 打印输入参数
    print("=" * 50)
    print("test_websocket 输入参数:")
    print(f"  token: {token[:50]}...")
    print(f"  conversation_id: {conversation_id}")
    print(f"  text: {text}")
    print("=" * 50)
    
    # 初始化返回结果
    result_workflow = None
    result_confident = None
    
    # WebSocket URL
    ws_url = f"wss://tpt.supcon.com/tpt-app/chat-tool-socket-work/api/conversation/{conversation_id}/stream"
    
    # Cookie包含基础部分和tpt-token
    cookie = f"tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; Authorization-M=32257d1b-50c9-4948-a0c1-ad8f7d268e17; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B; tpt-token={token}"
    
    # WebSocket headers
    headers = {
        "Cookie": cookie
    }
    
    try:
        # print(f"\n正在连接WebSocket: {ws_url}")
        # print(f"会话ID: {conversation_id}")
        
        # 建立WebSocket连接
        async with websockets.connect(
            ws_url,
            additional_headers=headers,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10
        ) as ws:
            # print("✓ WebSocket连接成功")
            
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
            
            # print(f"\n正在发送消息: {json.dumps(message_payload, ensure_ascii=False, indent=2)}")
            await ws.send(json.dumps(message_payload))
            # print("✓ 消息已发送")
            
            # 持续接收消息
            # print("\n开始接收服务器消息...")
            # print("-" * 50)
            
            try:
                async for message in ws:
                    try:
                        data = json.loads(message)
                        msg_type = data.get("type")
                        
                        if msg_type == "conversation_status_changed":
                            # 打印status字段的值
                            status = data.get("status")
                            # print(f"\n[conversation_status_changed] status: {status}")
                            pass
                            
                        elif msg_type in ["new_message", "message_content_delta"]:
                            # 打印content字段的内容
                            content = data.get("content")
                            
                            # 检查特殊逻辑：content是dict，且有type key，且type值为workflow
                            if isinstance(content, dict) and content.get("type") == "workflow":
                                # print(f"\n{'!' * 10}")
                                # print(f"[{msg_type}] content (workflow):")
                                # print(json.dumps(content, ensure_ascii=False, indent=2))
                                # print(f"{'!' * 10}")
                                result_workflow = content
                                # 获取到result_workflow后，先调用break API，然后等待2秒，再跳出循环
                                await test_conversation_break(token, conversation_id)
                                await asyncio.sleep(2)
                                break
                            elif isinstance(content, dict) and content.get("type") == "view" and isinstance(content.get("view", {}).get("content"), dict) and content.get("view", {}).get("content", {}).get("title") == "置信度":
                                result_confident = content.get("view").get("content")
                            else:
                                # print(f"\n[{msg_type}] content:")
                                # print(content, end='')
                                pass
                                
                        else:
                            # 其他类型，打印完整消息
                            # print(f"\n[{msg_type or 'unknown'}] 完整消息:")
                            # print(json.dumps(data, ensure_ascii=False, indent=2))
                            pass
                            
                    except json.JSONDecodeError:
                        # print(f"\n收到非JSON消息: {message}")
                        pass
                    except Exception as e:
                        # print(f"\n处理消息异常: {str(e)}")
                        pass
            except websockets.exceptions.ConnectionClosed:
                # print("\nWebSocket连接已关闭")
                pass
            except KeyboardInterrupt:
                # print("\n用户中断接收")
                pass
        
        # 打印返回结果
        print("\n" + "=" * 50)
        print("test_websocket 返回结果:")
        print(f"  result_workflow: {json.dumps(result_workflow, ensure_ascii=False, indent=2) if result_workflow else None}")
        print(f"  result_confident: {json.dumps(result_confident, ensure_ascii=False, indent=2) if result_confident else None}")
        print("=" * 50)
        
        return result_workflow, result_confident
                
    except Exception as e:
        print(f"\n✗ WebSocket连接异常: {str(e)}")
        raise


async def main():
    """主函数"""
    # 测试登录
    username = "15700078644"
    pass64 = "YXJ0aHVy"  # base64编码的密码
    
    login_result = await test_login(username, pass64)
    
    # 如果登录成功，测试创建会话
    if login_result.get("isSuccess") or login_result.get("success"):
        token = login_result.get("content", {}).get("token")
        if token:

            # 从 cases.yaml 读取测试用例，每行一个
            import os
            cases_file = os.path.join(os.path.dirname(__file__), "cases.yaml")
            with open(cases_file, "r", encoding="utf-8") as f:
                test_cases = [line.strip() for line in f.readlines() if line.strip()]

            test_results = []

            for title in test_cases:

                conv_result = await test_create_conversation(token, title=title)
                
                # 如果创建会话成功，测试WebSocket连接
                if isinstance(conv_result, dict) and "conversation_id" in conv_result:
                    conversation_id = conv_result["conversation_id"]
                    result_workflow, result_confident = await test_websocket(token, conversation_id, text=title)
                
                test_results.append({
                    "title": title,
                    "result_workflow": result_workflow,
                    "result_confident": result_confident
                })

                print(f"测试结果: {test_results[-1]}")
            
            import json
            json.dump(test_results, open("test_results.json", "w", encoding='utf-8'), ensure_ascii=False, indent=2)
            
            print("测试完成，结果已保存到 test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
