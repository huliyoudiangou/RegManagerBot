# Emby API 客户端
import threading
import requests
from datetime import datetime, timedelta

from app.utils.scheduler import get_scheduler
from .base import BaseAPIClient
from config import settings
from app.utils.logger import logger

scheduler = get_scheduler()
class EmbyAPIClient(BaseAPIClient):
    """
    Emby API 客户端
    """

    def __init__(self):
        super().__init__(settings.EMBY_API_URL, username=settings.EMBY_API_USERNAME, password=settings.EMBY_API_PASSWORD, token=settings.EMBY_API_KEY, auth_type='token')
        self._token_lock = threading.Lock()
        self.session = requests.Session()
        # self.session.headers.update({"X-Emby-Client": "Emby Web", "X-Emby-Device-Name": "Firefox Windows", "X-Emby-Device-Id": "1606ef80-1738-4279-b6c5-b4e920969dab", "X-Emby-Client-Version": "4.8.10.0"})
        if self.auth_type == 'token':
            self.token = settings.EMBY_API_KEY
            self.session.headers.update({"X-Emby-Token": f"{self.token}"})
            params = {"Limit": 1}
            result = self.get_users(params=params)
            if result and result['status'] == 'success':
                logger.info(f"Emby 使用 Key 认证，登录成功")
        else:
            self.token = self._login()  # 初始化时登录并获取 token
        # scheduler.add_job(job_name="Emby_keep_live", interval=settings.CLEAN_INTERVAL, job_func=self._keep_alive)
        logger.info("EmbyAPIClient 初始化完成") # 初始化时登录并获取 token

    def _login(self):
        """登录 Emby 并获取 token"""
        endpoint = "/Users/AuthenticateByName"
        url = f"{self.api_url}{endpoint}"
        data = {"Username": self.username, "Pw": self.password}
        params = {"X-Emby-Client": "Emby Web", "X-Emby-Device-Name": "Firefox Windows", "X-Emby-Device-Id": "1606ef80-1738-4279-b6c5-b4e920969dab", "X-Emby-Client-Version": "4.8.10.0"}
        try:
            # self.session.headers.update({"X-Emby-Client": "Emby Web", "X-Emby-Device-Name": "Firefox Windows", "X-Emby-Device-Id": "1606ef80-1738-4279-b6c5-b4e920969dab", "X-Emby-Client-Version": "4.8.10.0"})
            response = self.session.post(url, json=data, params=params)
            response.raise_for_status()
            token = response.json().get("AccessToken")
            logger.info(f"Emby 登录成功")
            self.session.headers.update({"X-Emby-Token": f"{token}"})
            return token
        except requests.exceptions.RequestException as e:
            print(f"Emby 登录失败: {e}")
            return None
    
    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        """发送 API 请求"""
        url = f"{self.api_url}{endpoint}"
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"})
 
        # 如果 token 存在，则添加到请求头
        _headers = {"X-Emby-Token": f"{self.token}"} if self.token else {}
        if headers:
          _headers.update(headers) # 如果传入了 headers，则合并

        response = None
        try:
            response = self.session.request(method, url, params=params, json=data, headers=_headers)
            # 根据状态码返回不同的结果
            if response.status_code == 200:
                return {"status": "success", "data": response.json(), "headers": response.headers}
            elif response.status_code == 204:
                return {"status": "success", "data": "", "headers": response.headers}
            elif response.status_code == 401:
                max_retries = 3
                retries = 0

                while retries < max_retries:
                    logger.warning(f"Emby token 过期，尝试第{retries}次重新登录...")
                    self.token = self._login()
                    if self.token:
                        logger.info("Emby 重新登录成功，使用新 token 重新发送请求")
                        return self._make_request(method, endpoint, params, data, headers)
                    else:
                        logger.warning(f"尝试第{retries}次重新登录失败...")
                        retries += 1
            else:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException as e:
            logger.error(f"Emby API 请求失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_user(self, user_id):
        """获取单个 Emby 用户信息"""
        endpoint = f"/Users/{user_id}"
        return self._make_request("GET", endpoint)

    def get_users(self, params=None):
        """获取所有 Emby 用户列表"""
        endpoint = "/Users/Query"
        return self._make_request("GET", endpoint, params=params)

    def get_user_by_username(self, username):
        """根据用户名获取 Emby 用户信息"""
        users = self.get_users()
        if users and users['status'] == 'success':
            for index, user in enumerate(users['data']['Items']):
                if user['Name'] == username:
                    return users['data'][index]
        return None
        
    def create_user(self, username, password):
        """创建 Emby 用户"""
        endpoint = "/Users/New"
        # 简化数据，只保留必要的参数
        copy_from_user_id = settings.EMBY_COPY_FROM_ID
        user_data = {
            "Name": f"{username}",
            "CopyFromUserId": copy_from_user_id,
            "UserCopyOptions": "UserPolicy,UserConfiguration"
            }
        data = {k: v for k, v in user_data.items() if v is not None}
        logger.debug(f"Emby 创建用户: {data}")
        resp = self._make_request("POST", endpoint, data=data)
        try:
            self.update_password(resp['data']['Id'], password)
        except requests.exceptions.RequestException as e:
            logger.error(f"Emby API 请求失败: {e}")
            return {"status": "error", "message": str(e)}
        return resp

    def update_user(self, action, user_id, user_data):
        """更新 Emby 用户信息"""
        endpoint = f"/Users/{user_id}/{action}"
        return self._make_request("POST", endpoint, data=user_data)


    def auth_user(self, username, password):
        """认证用户并获取id"""
        endpoint = "/Users/AuthenticateByName"
        url = f"{self.api_url}{endpoint}"
        data = {"Username": username, "Pw": password}
        params = {"X-Emby-Client": "Emby Web", "X-Emby-Device-Name": "Firefox Windows", "X-Emby-Device-Id": "1606ef80-1738-4279-b6c5-b4e920969dab", "X-Emby-Client-Version": "4.8.10.0"}
        try:
            response = requests.post(url, json=data, params=params)
            response.raise_for_status()
            user_id = response.json().get("Id")
            logger.info(f"用户认证成功")
            return {"id": user_id}
        except requests.exceptions.RequestException as e:
            print(f"用户认证失败: {e}")
            return None

    def update_username_or_password(self, user_id, username=None, password=None):
        """更新 Emby 用户信息(目前只更新用户名和密码)"""
        endpoint = f"/Users/{user_id}"
        # 更新时需要把用户的id也传进去
        if username and not password:
            data = {
                "Name": f"{username}",
                "Configuration": {},
                "Policy": {},
                "Type": "User"
                }
            result = self._make_request("POST", endpoint, data=data)
        elif password:
            result = self.update_password(user_id, password)
        return result

    def delete_user(self, user_id):
        """删除 Emby 用户"""
        endpoint = f"/Users/{user_id}/Delete"
        return self._make_request("POST", endpoint)
    
    def update_password(self, user_id, password):
        """更新 Emby 用户密码"""
        endpoint = f"/Users/{user_id}/Password"
        # 更新时需要把用户的id也传进去
        data = {
            "NewPw": f"{password}"
            }
        logger.debug(f"Emby 更新用户密码: {data}")
        return self._make_request("POST", endpoint, data=data)
    
    def block_user(self, user_id):
        """禁用 Emby 用户"""
        data = {
            "IsDisabled": True
            }
        return self.update_user("Policy", user_id, data)
    
    def unblock_user(self, user_id):
        """启用 Emby 用户"""
        data = {
            "IsDisabled": False
            }
        return self.update_user("Policy", user_id, data)


if __name__ == "__main__":
    emby = EmbyAPIClient()
    print(emby.get_users())
    data = {
        "Name": "test"
    }
    print(emby.create_user())
    