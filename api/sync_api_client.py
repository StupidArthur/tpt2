"""
同步 API 客户端模块 - 非异步版本
"""

import json
import time
import httpx
import websocket
import threading
from typing import Dict, List, Optional


class SyncAPIClient:
    """同步 API 客户端类"""
    
    BASE_URL = "https://tpt.supcon.com"
    BASE_COOKIE = "tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; Authorization-M=32257d1b-50c9-4948-a0c1-ad8f7d268e17; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B"
    BASE_HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    def __init__(self):
        self.token: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self.result_data: List = []
        self.ws_closed = False
        self.last_message_time: Optional[float] = None
        self.last_path = '-'
        self.exit_reason: Optional[str] = None
        self.total_duration: Optional[float] = None
    
    def _get_headers(self) -> Dict:
        """获取请求头"""
        cookie = f"{self.BASE_COOKIE}; tpt-token={self.token}" if self.token else self.BASE_COOKIE
        return {**self.BASE_HEADERS, "Cookie": cookie}
    
    def login(self, username: str, pass64: str) -> Dict:
        """登录"""
        url = f"{self.BASE_URL}/tpt-app/chat-tool-app/system-manager/umsAdmin/login"
        payload = {"data": {"username": username, "pass64": pass64, "agree": True, "remember": False}}
        
        with httpx.Client(verify=True, timeout=30.0) as client:
            response = client.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            if data.get("isSuccess") or data.get("success"):
                self.token = data.get("content", {}).get("token")
                print(f"✓ [login] 成功" if self.token else "⚠ [login] 未找到token")
            else:
                print(f"✗ [login] 失败: {data.get('msg', '未知错误')}")
            
            return data
    
    def _on_message(self, ws, message):
        """WebSocket 消息处理"""
        try:
            self.last_message_time = time.time()
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "message_status_changed" and data.get('status') == "interaction":
                ws.close()
            elif msg_type == "message_content_delta":
                path = data.get('path')
                operation = data.get('operation')
                
                if operation == "update":
                    self.result_data.append([path, data.get('content')])
                elif operation == "append":
                    if self.last_path != path and self.result_data:
                        self.result_data[-1].extend([path, ""])
                    self.last_path = path
                    if self.result_data and self.result_data[-1]:
                        self.result_data[-1][-1] += data.get('content', '')
        except (json.JSONDecodeError, Exception):
            pass
    
    def _on_close(self, ws, *args):
        """WebSocket 关闭"""
        self.ws_closed = True
    
    def create_conversation_and_chat(self, title: str, text: Optional[str] = None) -> List:
        """创建对话并建立 WebSocket 连接"""
        if not self.token:
            raise Exception("请先调用 login() 登录")
        
        text = text or title
        headers = self._get_headers()
        
        with httpx.Client(verify=True, timeout=30.0) as client:
            # 调用 rec-expert
            try:
                client.post(
                    f"{self.BASE_URL}/tpt-app/chat-tool-llm-commend/llm/rec-expert",
                    json={"data": {
                        "deviceType": "乙烯装置", "industryInvolved": "石化行业", "applyRole": "自控工程师",
                        "package": '{"乙烯装置":[]}', "deviceTypes": ["乙烯装置"], "packages": {"乙烯装置": []},
                        "expert": "工业知识专家", "role": "自控工程师", "companyName": "中控技术股份有限公司",
                        "equipment": "乙烯装置", "industry": "石化行业", "company": "中控技术", "technology": "智能控制系统"
                    }},
                    headers=headers
                )
            except:
                pass
            
            # 创建会话
            url = f"{self.BASE_URL}/tpt-app/chat-tool-work/api/conversation"
            response = client.post(url, json={"title": title}, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self.conversation_id = data.get("id") or data.get("conversationId") or data.get("conversation_id")
            if not self.conversation_id:
                return []
            
            client.put(url, json={"id": self.conversation_id, "title": title}, headers=headers)
        
        # WebSocket 连接
        self.result_data = []
        self.ws_closed = False
        self.last_message_time = None
        self.last_path = '-'
        
        ws_url = f"wss://tpt.supcon.com/tpt-app/chat-tool-socket-work/api/conversation/{self.conversation_id}/stream"
        ws = websocket.WebSocketApp(
            ws_url,
            header=[f"Cookie: {headers['Cookie']}"],
            on_message=self._on_message,
            on_close=self._on_close
        )
        
        thread = threading.Thread(target=lambda: ws.run_forever(ping_interval=20, ping_timeout=10))
        thread.daemon = True
        thread.start()
        time.sleep(1)
        
        ws.send(json.dumps({
            "message": {
                "content": [{"type": "text", "text": text}]
            },
            "parent_id": None,
            "type": "user_input",
            "use_deep_explore": False,
            "user_locale": "zh-CN",
            "conver_mode": "match",
            "work_files": []
        }))

        # 等待完成
        start_time = time.time()
        first_message_time = None
        
        while not self.ws_closed:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 记录第一条消息时间
            if self.last_message_time and first_message_time is None:
                first_message_time = self.last_message_time
                print(f"[WebSocket] 收到第一条消息，耗时: {first_message_time - start_time:.2f}秒")
            
            # 退出条件1：收到过消息且120秒内没收到新消息（延长）
            if self.last_message_time and current_time - self.last_message_time > 120:
                self.exit_reason = f"消息接收超时（{current_time - self.last_message_time:.1f}秒内未收到新消息）"
                print(f"[WebSocket] {self.exit_reason}")
                break
            
            # 退出条件2：如果还没收到任何消息，180秒超时（延长）
            if not self.last_message_time and elapsed > 180:
                self.exit_reason = f"连接超时（{elapsed:.1f}秒内未收到任何消息）"
                print(f"[WebSocket] {self.exit_reason}")
                break
            
            # 退出条件3：总超时（1800秒，30分钟）
            if elapsed > 1800:
                self.exit_reason = f"达到最大超时时间（{elapsed:.1f}秒）"
                print(f"[WebSocket] {self.exit_reason}")
                break
            
            time.sleep(0.1)
        
        self.total_duration = time.time() - start_time
        ws.close()
        thread.join(timeout=5)
        
        # 调用 break API
        try:
            with httpx.Client(verify=True, timeout=30.0) as client:
                client.post(
                    f"{self.BASE_URL}/tpt-app/chat-tool-work/api/conversation/{self.conversation_id}/break",
                    json={}, headers=headers
                )
        except:
            pass
        
        print(f"[create_conversation_and_chat] 完成，总耗时: {self.total_duration:.2f}秒，收到 {len(self.result_data)} 条消息")
        return self.result_data
