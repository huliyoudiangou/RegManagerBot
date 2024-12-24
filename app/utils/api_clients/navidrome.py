# Navidrome API 客户端
import requests
from .base import BaseAPIClient
from config import settings
from app.utils.logger import logger

# 需要安装的模块：requests
# pip install requests

class NavidromeAPIClient(BaseAPIClient):
    """
    Navidrome API 客户端
    """

    def __init__(self):
        super().__init__(settings.NAVIDROME_API_URL, username=settings.NAVIDROME_API_USERNAME, password=settings.NAVIDROME_API_PASSWORD, auth_type='token')
        self.token = self._login()  # 初始化时登录并获取 token

    def _login(self):
        """登录 Navidrome 并获取 token"""
        endpoint = "/auth/login"
        url = f"{self.api_url}{endpoint}"
        data = {"username": self.username, "password": self.password}

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json().get("token")
        except requests.exceptions.RequestException as e:
            print(f"Navidrome 登录失败: {e}")
            return None

    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        """发送 API 请求"""
        url = f"{self.api_url}{endpoint}"

        # 如果 token 存在，则添加到请求头
        _headers = {"x-nd-authorization": f"Bearer {self.token}"} if self.token else {}
        if headers:
          _headers.update(headers) # 如果传入了 headers，则合并

        try:
            response = requests.request(method, url, params=params, json=data, headers=_headers)
            response.raise_for_status()

            # 根据状态码返回不同的结果
            if response.status_code == 200:
                return {"status": "success", "data": response.json()}
            else:
                return {"status": "error", "message": "请求失败", "data": response.json()}

        except requests.exceptions.RequestException as e:
            if response.status_code == 401:  # 假设 401 表示 token 过期
                print("Navidrome token 过期，尝试重新登录...")
                self.token = self._login()
                if self.token:
                    return self._make_request(method, endpoint, params, data, headers)  # 使用新 token 重新发送请求
            print(f"Navidrome API 请求失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_user(self, user_id):
        """获取单个 Navidrome 用户信息"""
        endpoint = f"/api/user/{user_id}"
        return self._make_request("GET", endpoint)

    def get_users(self):
        """获取所有 Navidrome 用户列表"""
        endpoint = "/api/user"
        return self._make_request("GET", endpoint)

    def create_user(self, user_data):
        """创建 Navidrome 用户"""
        endpoint = "/api/user"
        # 简化数据，只保留必要的参数
        data = {
            "userName": user_data["userName"],
            "name": user_data.get("name", user_data["userName"]),  # 如果 name 不存在，则使用 userName
            "password": user_data["password"],
            "email": user_data.get("email"),
            "isAdmin": user_data.get("isAdmin", False),
        }
        return self._make_request("POST", endpoint, data=data)

    def update_user(self, user_id, user_data):
        """更新 Navidrome 用户信息"""
        endpoint = f"/api/user/{user_id}"
        # 更新时需要把用户的id也传进去
        data = user_data.copy()
        data['id'] = user_id
        return self._make_request("PUT", endpoint, data=data)

    def delete_user(self, user_id):
        """删除 Navidrome 用户"""
        endpoint = f"/api/user/{user_id}"
        return self._make_request("DELETE", endpoint)