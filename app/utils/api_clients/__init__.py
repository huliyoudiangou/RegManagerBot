# app/utils/api_clients/__init__.py

from .navidrome import NavidromeAPIClient
from .emby import EmbyAPIClient

# 初始化 API 客户端
navidrome_api_client = NavidromeAPIClient()
emby_api_client = EmbyAPIClient()
# 如果你还有其他的 API 客户端，例如 EmbyAPIClient，也需要在这里导入并初始化
# from .emby import EmbyAPIClient
# emby_api_client = EmbyAPIClient()