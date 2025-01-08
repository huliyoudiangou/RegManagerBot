# app/utils/api_clients/__init__.py

import sys
from config import settings
from app.utils.logger import logger

def init_service(service_type=None):
    service_type = service_type if service_type is not None else settings.SERVICE_TYPE
    match service_type:
        case "navidrome":
            from app.utils.api_clients.navidrome import NavidromeAPIClient
            service_api_client = NavidromeAPIClient()
            logger.info(f"Navidrome 服务启动中")
            return service_api_client
        case "emby":
            from app.utils.api_clients.emby import EmbyAPIClient
            service_api_client = EmbyAPIClient()
            logger.info(f"Emby 服务启动中")
            return service_api_client
        case "audiobookshelf":
            from app.utils.api_clients.audiobookshelf import AudiobookshelfAPIClient
            service_api_client = AudiobookshelfAPIClient()
            logger.info(f"Audiobookshelf 服务启动中")
            return service_api_client
        case _:
            logger.error("不支持的服务！")
            sys.exit(1) 
            
service_api_client = init_service()
# # from .navidrome import NavidromeAPIClient
# # from .emby import EmbyAPIClient
# from .audiobookshelf import AudiobookshelfAPIClient

# # 初始化 API 客户端
# # navidrome_api_client = NavidromeAPIClient()
# # emby_api_client = EmbyAPIClient()
# # audiobookshelf_api_client = AudiobookshelfAPIClient()

# # service_mapping = {
# #         "navidrome": navidrome_api_client,
# #         "emby": emby_api_client,
# #         "audiobookshelf": audiobookshelf_api_client
# #     }

# service_mapping = {
#         # "navidrome": NavidromeAPIClient(),
#         # "emby": EmbyAPIClient(),
#         "audiobookshelf": AudiobookshelfAPIClient()
#     }

# def get_api_client(service_type=None):
#     service_type = service_type if service_type is not None else settings.SERVICE_TYPE
#     return service_mapping.get(service_type)

# service_api_client = get_api_client()
# 如果你还有其他的 API 客户端，例如 EmbyAPIClient，也需要在这里导入并初始化
# from .emby import EmbyAPIClient
# emby_api_client = EmbyAPIClient()