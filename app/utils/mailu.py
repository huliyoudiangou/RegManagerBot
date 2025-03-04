import requests
from config import settings
from app.utils.logger import logger

_mailu = None

class MailuClient:
    """
    Mailu API Client
    """
    def __init__(self):
        self.mailu_url = settings.MAILU_URL
        self.mailu_token = settings.MAILU_TOKEN
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"{self.mailu_token}"})
    
    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        """发送 API 请求"""
        url = f"{self.mailu_url}{endpoint}"
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"})
        
        try:
            response = self.session.request(method, url, params=params, json=data, headers=headers)
            # logger.debug(f"code: {response.status_code}, data: {response.json()}")
            if response.status_code == 200:
                return {"status": "success", "data": response.json()}
            else:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException as e:
            if response.status_code == 409:
                logger.warning(f"user is duplicate.")
                return {"status": "duplicate", "message": response.json()['message']}
            logger.error(f"Mailu API 请求失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_users(self):
        """获取所有 Mailu Users"""
        endpoint = "/user"
        return self._make_request("GET", endpoint)
    
    def get_user(self, email):
        """获取 User的信息"""
        endpoint = f"/user/{email}"
        return self._make_request("GET", endpoint)
    
    def create_user(self, email, pw, quota_bytes=None):
        """创建Email用户"""
        endpoint = "/user"
        if quota_bytes is None:
            quota_bytes = 50000000
        data = {
            "email": email,
            "raw_password": pw,
            "quota_bytes": quota_bytes
            }
        return self._make_request("POST", endpoint, data=data)
    
    def delete_user(self, email):
        endpoint = f"/user/{email}"
        return self._make_request("DELETE", endpoint)
        

def create_mailu():
    """创建邮件实例，并赋值给全局变量_mailu"""
    global _mailu
    if not _mailu:
      _mailu = MailuClient()
    return _mailu

def get_mailu():
    """获取 mailu 实例"""
    global _mailu
    if not _mailu:
      _mailu = create_mailu()
    return _mailu
    