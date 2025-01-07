# Navidrome API 客户端
import threading
import requests
from datetime import datetime, timedelta

from app.utils.scheduler import get_scheduler
from .base import BaseAPIClient
from config import settings
from app.utils.logger import logger

# 需要安装的模块：requests
# pip install requests

scheduler = get_scheduler()
class NavidromeAPIClient(BaseAPIClient):
    """
    Navidrome API 客户端
    """

    def __init__(self):
        super().__init__(settings.NAVIDROME_API_URL, username=settings.NAVIDROME_API_USERNAME, password=settings.NAVIDROME_API_PASSWORD, auth_type='token')
        self._token_lock = threading.Lock()
        self.session = requests.Session()
        self.token = self._login()  # 初始化时登录并获取 token
        # self._start_keep_alive()
        scheduler.add_job(job_name="navidrome_keep_live", interval=settings.CLEAN_INTERVAL, job_func=self._keep_alive)
        logger.info("NavidromeAPIClient 初始化完成") # 初始化时登录并获取 token

    def _login(self):
        """登录 Navidrome 并获取 token"""
        endpoint = "/auth/login"
        url = f"{self.api_url}{endpoint}"
        data = {"username": self.username, "password": self.password}

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            token = response.json().get("token")
            logger.info(f"Navidrome 登录成功")
            self.session.headers.update({"x-nd-authorization": f"Bearer {token}"})
            return token
        except requests.exceptions.RequestException as e:
            print(f"Navidrome 登录失败: {e}")
            return None
    
    def start_clean_expired_users(self):
         if settings.ENABLE_EXPIRED_USER_CLEAN:
           self._setup_clean_expired_users_job() # 启动清理过期用户的定时任务
         else:
             self._remove_clean_expired_users_job()
    
    def _setup_clean_expired_users_job(self):
        """启动清理过期用户的定时器"""
        if settings.ENABLE_EXPIRED_USER_CLEAN:
            scheduler.add_job(job_name = "clean_expired_users", interval=settings.CLEAN_INTERVAL, job_func = self._clean_expired_users)
            logger.info(f"Navidrome 过期用户清理定时任务启动，时间间隔：{settings.CLEAN_INTERVAL} 秒")
        else:
            logger.info("Navidrome 过期用户清理定时任务未启动")
    
    def _remove_clean_expired_users_job(self):
       """移除清理过期用户的定时器"""
       scheduler.remove_job("clean_expired_users")

    def _clean_expired_users(self):
      """删除过期用户"""
      with self._token_lock:
          if self.token:
            logger.info("开始清理过期用户")
            expired_users = self._get_expired_users()
            if 'warning' in expired_users and expired_users['warning']:
                for user in expired_users['warning']:
                    logger.warning(f"用户名：{user['username']}将在3天后过期，请注意！")
            if 'expired' in expired_users and expired_users['expired']:
              for user in expired_users['expired']:
                logger.info(f"删除过期用户: username={user['username']}, service_user_id: {user['service_user_id']}")
                self.delete_user(user['service_user_id'])
          else:
            logger.error(f"无法获取token, 无法执行清理过期用户")

    
    def _get_expired_users(self):
        """获取过期用户和即将过期的用户(不包括管理员)"""
        expired_users = []
        warning_users = []
        users = self.get_users()
        logger.debug(f"day: {settings.EXPIRED_DAYS}, warning: {settings.WARNING_DAYS}")
        if users and users['status'] == 'success':
            now = datetime.now().astimezone()
            local_tz = now.tzinfo # 获取本地时区
            for user_data in users['data']:
                if not user_data['isAdmin']:
                    logger.debug(f"正在检查用户: {user_data['userName']}")
                    last_login_at = user_data.get('lastLoginAt')
                    last_access_at = user_data.get('lastAccessAt')
                    
                    def parse_datetime_str(time_str):
                        if not time_str:
                            return None

                        try:
                            time_str = time_str.replace('Z', '+00:00')
                            if '.' in time_str:
                                time_str = time_str[:time_str.find('.')]  # 删除微秒部分

                            dt = datetime.fromisoformat(time_str)
                            return dt.astimezone(local_tz).replace(second=0, microsecond=0)
                        except Exception as e:
                            logger.error(f"解析时间字符串失败: {time_str}，错误信息为 {e}")
                            return None

                    last_login_time = parse_datetime_str(last_login_at)
                    last_access_time = parse_datetime_str(last_access_at)
                    
                    # 获取最后登录或访问时间
                    last_time = max(last_login_time, last_access_time) if last_login_time and last_access_time else last_login_time if last_login_time else last_access_time if last_access_time else None

                    if last_time:
                        if (now - last_time) > timedelta(days=settings.EXPIRED_DAYS):
                            logger.debug(f"发现过期用户: {user_data['userName']}")
                            expired_users.append({'service_user_id': user_data['id'], 'username': user_data['userName']})
                        elif (now - last_time) < timedelta(days=settings.WARNING_DAYS):
                            logger.debug(f"发现即将过期用户: {user_data['userName']}")
                            warning_users.append({'service_user_id': user_data['id'], 'username': user_data['userName']})
                        else:
                            logger.debug(f"该用户正常: {user_data['userName']}")
                    else:
                        # 如果 lastLoginAt 和 lastAccessAt 都是 None，则立即删除
                        logger.debug(f"该用户从未登录过: {user_data['userName']}")
                        expired_users.append({'service_user_id': user_data['id'], 'username': user_data['userName']})
                else:
                    logger.debug(f"发现管理员账号：{user_data['userName']}")
        return {'expired':expired_users, 'warning':warning_users}
    
    def _keep_alive(self):
        """发送 Navidrome 保活请求"""
        with self._token_lock:
            if self.token:
              endpoint = "/api/keepalive/keepalive" # 使用用户列表接口来保活
              result = self._make_request("GET", endpoint)
              if result and result['status'] == 'success':
                logger.info("Navidrome 保活请求成功")
              else:
                  logger.warning(f"Navidrome 保活请求失败, result: {result} , 重新获取token")
                  self.token = self._login()
                  if self.token:
                    logger.info("Navidrome 重新登录成功")
                  else:
                      logger.error("Navidrome 重新登录失败")
        # self._start_keep_alive()

    def _start_keep_alive(self):
        """启动保活定时器"""
        # 设置保活时间间隔，例如每 60 分钟发送一次
        interval = 60 * 60
        self._keep_alive_timer = threading.Timer(interval, self._keep_alive)
        self._keep_alive_timer.daemon = True  # 设置为守护线程，防止主线程退出时阻塞
        self._keep_alive_timer.start()
        logger.info(f"Navidrome 保活定时器启动，时间间隔：{interval} 秒")
        
    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        """发送 API 请求"""
        url = f"{self.api_url}{endpoint}"

        # 如果 token 存在，则添加到请求头
        _headers = {"x-nd-authorization": f"Bearer {self.token}"} if self.token else {}
        if headers:
          _headers.update(headers) # 如果传入了 headers，则合并
        
        response = None
        try:
            response = self.session.request(method, url, params=params, json=data, headers=_headers)
            # 根据状态码返回不同的结果
            if response.status_code == 200:
                return {"status": "success", "data": response.json(), "headers": response.headers}

            elif response.status_code == 401:
                max_retries = 3
                retries = 0

                while retries < max_retries:
                    logger.warning(f"Navidrome token 过期，尝试第{retries}次重新登录...")
                    self.token = self._login()
                    if self.token:
                        logger.info("Navidrome 重新登录成功，使用新 token 重新发送请求")
                        return self._make_request(method, endpoint, params, data, headers)
                    else:
                        logger.warning(f"尝试第{retries}次重新登录失败...")
                        retries += 1
            else:
                raise requests.exceptions.RequestException
        except requests.exceptions.RequestException as e:
            logger.error(f"Navidrome API 请求失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_user(self, user_id):
        """获取单个 Navidrome 用户信息"""
        endpoint = f"/api/user/{user_id}"
        return self._make_request("GET", endpoint)

    def get_users(self):
        """获取所有 Navidrome 用户列表"""
        endpoint = "/api/user"
        return self._make_request("GET", endpoint)

    def get_user_by_username(self, username):
        """根据用户名获取 Navidrome 用户信息"""
        users = self.get_users()
        if users and users['status'] == 'success':
            for index, user in enumerate(users['data']):
                logger.info(f"index: {index}, user: {user}")
                if user['userName'] == username:
                    return users['data'][index]
        return None
    
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
    
    def get_albums(self, _end=1, _order="", _sort="", _start=0):
        """
        获取 Navidrome 专辑列表
        
        Args:
          _end: 获取数据结束位置
          _order: 排序规则
          _sort: 排序字段
          _start: 获取数据开始位置
        Returns:
            返回一个字典，其中 'data' 字段包含专辑列表，'x-total-count' 字段包含响应头中的总数
        """
        params = {
            "_end": _end,
            "_order": _order,
            "_sort": _sort,
            "_start": _start
        }
        endpoint = "/api/album"
        
        response = self._make_request("GET", endpoint, params=params)
        if response and response['status'] == 'success':
           return {
                "data": response['data'],
                 "x-total-count": response['headers']['x-total-count'] if 'x-total-count' in response['headers'] else 0
            }
        else:
           return None   
    
    def get_songs(self, _end=1, _order="", _sort="", _start=0):
        """
        获取 Navidrome 歌曲列表
        
        Args:
          _end: 获取数据结束位置
          _order: 排序规则
          _sort: 排序字段
          _start: 获取数据开始位置
        Returns:
           返回一个字典，其中 'data' 字段包含歌曲列表，'x-total-count' 字段包含响应头中的总数
        """
        params = {
            "_end": _end,
            "_order": _order,
            "_sort": _sort,
            "_start": _start
        }
        endpoint = "/api/song"

        response = self._make_request("GET", endpoint, params=params)
        if response and response['status'] == 'success':
           return {
                "data": response['data'],
                 "x-total-count": response['headers']['x-total-count'] if 'x-total-count' in response['headers'] else 0
            }
        else:
           return None

    def get_artists(self, _end=1, _order="", _sort="", _start=0):
        """
        获取 Navidrome 艺术家列表
        
        Args:
          _end: 获取数据结束位置
          _order: 排序规则
          _sort: 排序字段
          _start: 获取数据开始位置
        Returns:
           返回一个字典，其中 'data' 字段包含艺术家列表，'x-total-count' 字段包含响应头中的总数
        """
        params = {
            "_end": _end,
            "_order": _order,
            "_sort": _sort,
            "_start": _start
        }
        endpoint = "/api/artist"
        response = self._make_request("GET", endpoint, params=params)
        if response and response['status'] == 'success':
           return {
                "data": response['data'],
                 "x-total-count": response['headers']['x-total-count'] if 'x-total-count' in response['headers'] else 0
            }
        else:
           return None

    def get_radios(self, _end=1, _order="", _sort="", _start=0):
        """
        获取 Navidrome 电台列表

        Args:
          _end: 获取数据结束位置
          _order: 排序规则
          _sort: 排序字段
          _start: 获取数据开始位置
        Returns:
          返回一个字典，其中 'data' 字段包含电台列表，'x-total-count' 字段包含响应头中的总数
        """
        params = {
            "_end": _end,
            "_order": _order,
            "_sort": _sort,
            "_start": _start
        }
        endpoint = "/api/radio"
        response = self._make_request("GET", endpoint, params=params)
        if response and response['status'] == 'success':
           return {
                "data": response['data'],
                 "x-total-count": response['headers']['x-total-count'] if 'x-total-count' in response['headers'] else 0
            }
        else:
           return None