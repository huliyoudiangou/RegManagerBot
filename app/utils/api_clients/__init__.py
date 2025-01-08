# app/utils/api_clients/__init__.py

from config import settings
from .navidrome import NavidromeAPIClient
from .emby import EmbyAPIClient

# 初始化 API 客户端
navidrome_api_client = NavidromeAPIClient()
emby_api_client = EmbyAPIClient()

service_mapping = {
        "navidrome": navidrome_api_client,
        "emby": emby_api_client,
    }

def get_api_client(service_type=None):
    service_type = service_type if service_type is not None else settings.SERVICE_TYPE
    return service_mapping.get(service_type)

service_api_client = get_api_client()
# 如果你还有其他的 API 客户端，例如 EmbyAPIClient，也需要在这里导入并初始化
# from .emby import EmbyAPIClient
# emby_api_client = EmbyAPIClient()