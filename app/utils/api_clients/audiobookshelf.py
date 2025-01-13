# audiobookshelf 客户端

import threading
import requests
from datetime import datetime, timedelta

from app.utils.scheduler import get_scheduler
from .base import BaseAPIClient
from config import settings
from app.utils.logger import logger

scheduler = get_scheduler()

class AudiobookshelfAPIClient(BaseAPIClient):
    """
    Audiobookshelf API 客户端
    """

    def __init__(self):
        super().__init__(settings.AUDIOBOOKSHELF_API_URL, username=settings.AUDIOBOOKSHELF_API_USERNAME, password=settings.AUDIOBOOKSHELF_API_PASSWORD, token=settings.AUDIOBOOKSHELF_API_KEY, auth_type='token')
        self._token_lock = threading.Lock()
        self.session = requests.Session()
        
        if self.auth_type == 'token':
            self.token = settings.AUDIOBOOKSHELF_API_KEY
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            result = self.get_libraries()
            if result and result['status'] == 'success':
                logger.info(f"Audiobookshelf 使用 Key 认证，登录成功")
        else:
            self.token = self._login()  # 初始化时登录并获取 token
        if self._get_copy_config():
            self.config = self._get_copy_config()
        else:
            self.config = None
        logger.info("AudiobookshelfAPIClient 初始化完成")

    def _login(self):
        """登录 Audiobookshelf 并获取 token"""
        endpoint = "/login"
        url = f"{self.api_url}{endpoint}"
        data = {"username": self.username, "password": self.password}
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            token = response.json().get("token")
            logger.info(f"Audiobookshelf 登录成功")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return token
        except requests.exceptions.RequestException as e:
            logger.error(f"Audiobookshelf 登录失败: {e}")
            return None
    
    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        """发送 API 请求"""
        url = f"{self.api_url}{endpoint}"
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"})
        
        _headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        if headers:
            _headers.update(headers)  # 如果传入了 headers，则合并
        response = None
        try:
            response = self.session.request(method, url, params=params, json=data, headers=_headers)
            # logger.debug(f"{response.status_code}")
            # 根据状态码返回不同的结果
            if response.status_code == 200:
                return {"status": "success", "data": response.json(), "headers": response.headers}
            # elif response.status_code == 204:
            #     return {"status": "success", "data": "", "headers": response.headers}
            elif response.status_code == 401:
                max_retries = 3
                retries = 0

                while retries < max_retries:
                    logger.warning(f"Audiobookshelf token 过期，尝试第{retries}次重新登录...")
                    self.token = self._login()
                    if self.token:
                        logger.info("Audiobookshelf 重新登录成功，使用新 token 重新发送请求")
                        return self._make_request(method, endpoint, params, data, headers)
                    else:
                        logger.warning(f"尝试第{retries}次重新登录失败...")
                        retries += 1
            else:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException as e:
            logger.error(f"Audiobookshelf API 请求失败: {e}")
            return {"status": "error", "message": str(e)}

    def _get_copy_config(self):
        from_id = settings.AUDIOBOOKSHELF_COPY_FROM_ID
        if from_id:
            logger.debug(f"发现用户配置模块，使用模板创建用户")
            resp = self.get_user(from_id)
            return resp['data']['permissions']
        else:
            logger.warning(f"未发现用户配置模块，使用默认模板创建用户")
            return None
            
    def get_libraries(self):
        """获取所有 Audiobookshelf 库"""
        endpoint = "/api/libraries"
        return self._make_request("GET", endpoint)

    def get_library_items(self, library_id):
        """获取指定库中的所有项目"""
        endpoint = f"/api/libraries/{library_id}/items"
        return self._make_request("GET", endpoint)

    def get_item(self, item_id):
        """获取指定项目的详细信息"""
        endpoint = f"/api/items/{item_id}"
        return self._make_request("GET", endpoint)

    def get_user(self, user_id):
        """获取 Audiobookshelf 用户"""
        endpoint = f"/api/users/{user_id}"
        logger.debug(f"Audiobookshelf 获取用户: {user_id}")
        return self._make_request("GET", endpoint)
    
    def get_users(self, online=False):
        """获取 所有 Audiobookshelf 用户"""
        if not online:
            endpoint = f"/api/users/{online}"
            logger.debug(f"Audiobookshelf 获取所有在线用户")
        endpoint = f"/api/users"
        logger.debug(f"Audiobookshelf 获取所有用户")
        return self._make_request("GET", endpoint)
    
    def create_user(self, username, password):
        """创建 Audiobookshelf 用户"""
        endpoint = "/api/users"
        user_data = {
            "username": username,
            "password": password,
            "type": "user",
            "isActive": True,
            "permissions": self.config
        }
        data = {k: v for k, v in user_data.items() if v is not None}
        logger.debug(f"Audiobookshelf 创建用户: {data}")
        return self._make_request("POST", endpoint, data=data)
    
    def update_user(self, user_id, user_data):
        """更新 Audiobookshelf 用户信息"""
        endpoint = f"/api/users/{user_id}"
        data = {k: v for k, v in user_data.items() if v is not None}
        logger.debug(f"Audiobookshelf 更新用户: {data}")
        return self._make_request("PATCH", endpoint, data=data)
        
    def update_username_or_password(self, user_id, username=None, password=None):
        """更新 Audiobookshelf 用户信息"""
        endpoint = f"/api/users/{user_id}"
        user_data = {
            "username": username,
            "password": password,
            "permissions": self.config
        }
        data = {k: v for k, v in user_data.items() if v is not None}
        logger.debug(f"Audiobookshelf 更新用户: {data}")
        return self._make_request("PATCH", endpoint, data=data)

    def block_user(self, user_id):
        """禁用 Audiobookshelf 用户"""
        data = {
            "isActive": False
        }
        return self.update_user(user_id, data)
    
    def unblock_user(self, user_id):
        """启用 Audiobookshelf 用户"""
        data = {
            "isActive": True
        }
        return self.update_user(user_id, data)
    
    def delete_user(self, user_id):
        """删除 Audiobookshelf 用户"""
        endpoint = f"/api/users/{user_id}"
        return self._make_request("DELETE", endpoint)

if __name__ == "__main__":
    audiobookshelf = AudiobookshelfAPIClient()
    print(audiobookshelf.get_libraries())
    data = {
        "username": "test",
        "password": "test123",
        "roles": ["user"],
        "libraries": []
    }
    print(audiobookshelf.create_user(data))