"""
使用 HTTPS 接口进行登录和对话创建，WSS 接口进行长对话通信的 Demo
使用 httpx 和 websockets 实现
"""

import asyncio
import json
import httpx
import websockets
from typing import Optional, Dict, Any
from urllib.parse import urljoin


class ChatClient:
    """聊天客户端类，封装登录、创建对话和WebSocket通信功能"""
    
    def __init__(self, base_url: str):
        """
        初始化客户端
        
        Args:
            base_url: API基础URL，例如 "https://tpt.supcon.com"
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.ws_base = self.base_url.replace('https://', 'wss://').replace('http://', 'ws://')
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self.ws: Optional[websockets.WebSocketServerProtocol] = None
        # 写死的cookie基础部分
        self.base_cookie = "tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; Authorization-M=32257d1b-50c9-4948-a0c1-ad8f7d268e17; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B"
        
    async def login(self, username: str, pass64: str) -> Dict[str, Any]:
        """
        登录接口
        
        Args:
            username: 用户名
            pass64: base64编码的密码
            
        Returns:
            登录响应数据
        """
        url = "https://tpt.supcon.com/tpt-app/chat-tool-app/system-manager/umsAdmin/login"
        
        headers = {
            "Cookie": f"{self.base_cookie}",
            "Authorization-M": "32257d1b-50c9-4948-a0c1-ad8f7d268e17",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://tpt.supcon.com",
            "Referer": "https://tpt.supcon.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        payload = {
            "data": {
                "username": username,
                "pass64": pass64,
                "agree": True,
                "remember": False
            }
        }
        
        async with httpx.AsyncClient(verify=True, timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # 保存token和用户信息
                if data.get("isSuccess") or data.get("success"):
                    self.token = data.get("content", {}).get("token")
                    self.user_id = data.get("content", {}).get("id")
                    print(f"登录成功: 用户ID={self.user_id}, Token已保存")
                else:
                    raise ValueError(f"登录失败: {data.get('msg', '未知错误')}")
                
                return data
                
            except httpx.HTTPStatusError as e:
                print(f"登录失败: HTTP {e.response.status_code}")
                raise
            except Exception as e:
                print(f"登录异常: {str(e)}")
                raise
    
    async def create_conversation(self, title: str = "pid") -> Dict[str, Any]:
        """
        创建对话接口
        
        Args:
            title: 对话标题，默认为"pid"
            
        Returns:
            创建对话的响应数据
        """
        if not self.token:
            raise ValueError("请先登录")
        
        url = "https://tpt.supcon.com/tpt-app/chat-tool-work/api/conversation"
        
        # Cookie包含基础部分和tpt-token
        cookie = f"{self.base_cookie}; tpt-token={self.token}"
        
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
                # POST请求创建会话
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # 提取会话ID
                conversation_id = data.get("id")
                if not conversation_id:
                    raise ValueError("创建会话失败：未返回会话ID")
                
                self.conversation_id = conversation_id
                print(f"POST请求成功，会话ID: {conversation_id}")
                
                # PUT请求更新会话
                update_payload = {
                    "id": conversation_id,
                    "title": title
                }
                
                update_response = await client.put(
                    url,
                    json=update_payload,
                    headers=headers
                )
                update_response.raise_for_status()
                update_data = update_response.json()
                
                if update_data.get("status") == "success":
                    print(f"PUT请求成功，会话创建完成")
                else:
                    print(f"PUT请求响应: {update_data}")
                
                return {
                    "post_response": data,
                    "put_response": update_data,
                    "conversation_id": conversation_id
                }
                
            except httpx.HTTPStatusError as e:
                print(f"创建对话失败: HTTP {e.response.status_code}")
                raise
            except Exception as e:
                print(f"创建对话异常: {str(e)}")
                raise
    
    async def connect_websocket(self) -> None:
        """
        建立WebSocket连接
        """
        if not self.token or not self.conversation_id:
            raise ValueError("请先登录并创建对话")
        
        # 构建WebSocket URL，通常需要包含token和conversation_id
        ws_url = f"{self.ws_base}/ws/chat"
        params = {
            "token": self.token,
            "conversation_id": self.conversation_id
        }
        
        # 将参数添加到URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        ws_url = f"{ws_url}?{query_string}"
        
        try:
            print(f"正在连接WebSocket: {ws_url}")
            self.ws = await websockets.connect(
                ws_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            print("WebSocket连接成功")
            
        except Exception as e:
            print(f"WebSocket连接失败: {str(e)}")
            raise
    
    async def send_message(self, message: str) -> None:
        """
        通过WebSocket发送消息
        
        Args:
            message: 要发送的消息内容
        """
        if not self.ws:
            raise ValueError("WebSocket未连接，请先调用connect_websocket()")
        
        try:
            payload = {
                "type": "message",
                "content": message,
                "conversation_id": self.conversation_id
            }
            
            await self.ws.send(json.dumps(payload))
            print(f"消息已发送: {message}")
            
        except Exception as e:
            print(f"发送消息失败: {str(e)}")
            raise
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        接收WebSocket消息
        
        Returns:
            接收到的消息数据，如果连接关闭则返回None
        """
        if not self.ws:
            raise ValueError("WebSocket未连接")
        
        try:
            message = await self.ws.recv()
            data = json.loads(message)
            print(f"收到消息: {data}")
            return data
            
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
            return None
        except Exception as e:
            print(f"接收消息异常: {str(e)}")
            return None
    
    async def listen_messages(self, callback=None) -> None:
        """
        持续监听WebSocket消息
        
        Args:
            callback: 消息回调函数，接收消息数据作为参数
        """
        if not self.ws:
            raise ValueError("WebSocket未连接")
        
        print("开始监听消息...")
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    print(f"收到消息: {data}")
                    
                    if callback:
                        await callback(data) if asyncio.iscoroutinefunction(callback) else callback(data)
                        
                except json.JSONDecodeError:
                    print(f"收到非JSON消息: {message}")
                except Exception as e:
                    print(f"处理消息异常: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
        except Exception as e:
            print(f"监听消息异常: {str(e)}")
    
    async def close_websocket(self) -> None:
        """关闭WebSocket连接"""
        if self.ws:
            await self.ws.close()
            self.ws = None
            print("WebSocket连接已关闭")
    
    async def close(self) -> None:
        """关闭所有连接"""
        await self.close_websocket()


async def main():
    """主函数示例"""
    # 初始化客户端
    client = ChatClient(base_url="https://api.example.com")
    
    try:
        # 1. 登录
        await client.login(username="your_username", password="your_password")
        
        # 2. 创建对话
        await client.create_conversation(title="测试对话")
        
        # 3. 建立WebSocket连接
        await client.connect_websocket()
        
        # 4. 定义消息处理回调
        async def handle_message(data: Dict[str, Any]):
            """处理接收到的消息"""
            msg_type = data.get("type")
            if msg_type == "message":
                print(f"收到对话消息: {data.get('content')}")
            elif msg_type == "error":
                print(f"收到错误: {data.get('error')}")
            elif msg_type == "ping":
                # 响应ping消息
                await client.ws.send(json.dumps({"type": "pong"}))
        
        # 5. 发送一条测试消息
        await client.send_message("你好，这是一条测试消息")
        
        # 6. 监听消息（异步任务）
        listen_task = asyncio.create_task(client.listen_messages(handle_message))
        
        # 7. 发送更多消息示例
        await asyncio.sleep(1)
        await client.send_message("这是第二条消息")
        
        # 8. 保持连接一段时间（实际使用时可以根据需要调整）
        await asyncio.sleep(5)
        
        # 9. 取消监听任务并关闭连接
        listen_task.cancel()
        await client.close_websocket()
        
    except KeyboardInterrupt:
        print("\n用户中断")
        await client.close()
    except Exception as e:
        print(f"程序异常: {str(e)}")
        await client.close()


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())

