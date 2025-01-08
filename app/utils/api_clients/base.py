from abc import ABC, abstractmethod

# 需要安装的模块：无 (abc 是 Python 内置模块)

class BaseAPIClient(ABC):
    """
    API 客户端基类，定义通用接口
    """

    def __init__(self, api_url, username=None, password=None, token=None, auth_type='basic'):
        """
        初始化 API 客户端
        Args:
            api_url: API 地址
            username: 用户名 (可选)
            password: 密码 (可选)
            token: 令牌 (可选)
            auth_type: 认证类型，'basic' 或 'token'，默认为 'basic'
        """
        self.api_url = api_url
        self.username = username
        self.password = password
        self.token = token
        self.auth_type = auth_type

    @abstractmethod
    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        """发送 API 请求 (抽象方法，需要在子类中实现)"""
        pass

    @abstractmethod
    def get_user(self, user_id):
        """获取单个用户信息"""
        pass

    @abstractmethod
    def get_users(self):
        """获取所有用户列表"""
        pass

    @abstractmethod
    def create_user(self, username, password):
        """创建用户"""
        pass

    @abstractmethod
    def update_user(self, user_id, username, password):
        """更新用户信息"""
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """删除用户"""
        pass